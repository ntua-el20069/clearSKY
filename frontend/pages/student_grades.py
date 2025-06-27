# pages/student_grades.py
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

from orchestrator.review.review_ops import get_reviews
from orchestrator.statistics.statistics_ops import (
    get_status_of_grades,
    get_student_grades,
)

# Configuration - using the same cookie setup as main app
# Get student ID from session (set during login)
if "username" not in st.session_state:
    st.error("Please log in to view grades")
    st.stop()

STUDENT_ID = st.session_state.username


def fetch_student_grades(
    student_ids: List[str],
    years: Optional[List[int]] = None,
    exam_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, Union[List[str], List[int]]] = {"student_ids": student_ids}
    if years:
        params["years"] = years
    if exam_types:
        params["exam_types"] = exam_types

    try:
        response = asyncio.run(get_student_grades(students=params))
        response_body = json.loads(response.body)
        if response.status_code == 200:
            grades = response_body.get("grades", [])
            return grades if isinstance(grades, list) else []
        st.error(f"Error fetching grades: {response_body.text}")
        return []
    except Exception as e:
        st.error(f"API connection failed: {str(e)}")
        return []


def fetch_reviews(
    student_ids: List[str],
    years: Optional[List[int]] = None,
    exam_types: Optional[List[str]] = None,
    course_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    try:
        response = asyncio.run(
            get_reviews(
                {
                    "student_ids": student_ids,
                    "course_ids": course_ids,
                    "exam_types": exam_types,
                    "years": years,
                }
            )
        )
        response_body = json.loads(response.body)
        if response.status_code == 200:
            reviews = response_body.get("reviews", [])
            return reviews if isinstance(reviews, list) else []
        st.error(f"Error fetching reviews: {response_body.text}")
        return []
    except Exception as e:
        st.error(f"API connection failed: {str(e)}")
        return []


def main() -> None:
    st.title("📊 My Grades")

    # Filters
    with st.sidebar:
        st.header("Filters")
        years: List[int] = st.multiselect(
            "Select years",
            options=list(range(2000, datetime.now().year + 1)),
            default=[datetime.now().year - 1],
        )
        exam_types: List[str] = st.multiselect(
            "Select exam types",
            options=["Winter", "Summer", "Re-take", "Special"],
            default=["Winter", "Summer"],
        )

    # Fetch grades
    grades_data = fetch_student_grades([STUDENT_ID], years, exam_types)

    if not grades_data:
        st.warning("No grades found for selected filters.")
        return

    df = pd.DataFrame(grades_data)

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Courses", len(df))
    with col2:
        st.metric("Average Grade", f"{df['grade'].mean():.2f}")
    with col3:
        st.metric("Total ECTS", df.get("ects", "N/A"))

    # Grades table - simplified view
    st.subheader("Your Grades")
    st.dataframe(
        df[["course_id", "exam_type", "year", "grade"]].rename(
            columns={
                "course_id": "Course ID",
                "exam_type": "Exam Type",
                "year": "Year",
                "grade": "Grade",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    # Detailed grade selection
    st.subheader("Grade Details")

    # Create unique identifier for each grade
    grade_options = {
        f"{row['course_id']} - {row['exam_type']} {row['year']}": row
        for _, row in df.iterrows()
    }

    selected_grade_key = st.selectbox(
        "Select a grade to view details", options=list(grade_options.keys())
    )

    if not selected_grade_key:
        return

    selected_grade = grade_options[selected_grade_key]

    st.markdown("### 📄 Grade Details")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Course ID", value=f"📘 {selected_grade['course_id']}")
    with col2:
        st.metric(label="Exam Type", value=f"📝 {selected_grade['exam_type']}")
    with col3:
        st.metric(label="Year", value=f"📅 {selected_grade['year']}")
    with col4:
        grade = float(selected_grade["grade"])
        grade_color = "#2ca02c" if grade >= 5 else "#d62728"  # green or red
        # You can also use "green"/"red" but hex ensures compatibility
        st.markdown(
            f'<div style="font-size:2em; color:{grade_color}; font-weight:bold;">🏆 {grade}</div>',
            unsafe_allow_html=True,
        )
        st.caption("Final Grade")

    response = asyncio.run(
        get_status_of_grades(
            selected_grade["course_id"],
            selected_grade["exam_type"],
            selected_grade["year"],
        )
    )
    response_body = json.loads(response.body)
    if response.status_code != 200:
        st.error(f"Error while fetching status of grades: {response_body['detail']}")
        st.stop()
        st.write(f"**Grade Status:** {response_body['grades_status']}")

    # Question breakdown
    if "question_grades" in selected_grade and selected_grade["question_grades"]:
        st.subheader("Question Breakdown")
        questions_df = pd.DataFrame(
            {
                "Question": [
                    f"Q{i + 1:02d}"
                    for i in range(len(selected_grade["question_grades"]))
                ],
                "Score": selected_grade["question_grades"],
                "Weight": selected_grade["grade_weights"],
                "Weighted Score": [
                    q * w / 10
                    for q, w in zip(
                        selected_grade["question_grades"],
                        selected_grade["grade_weights"],
                    )
                ],
            }
        )
        st.dataframe(questions_df, hide_index=True)
        st.bar_chart(questions_df.set_index("Question")["Score"])

    # Review section
    st.divider()
    st.subheader("Grade Review")

    existing_reviews = fetch_reviews(
        [STUDENT_ID],
        [int(selected_grade["year"])],
        [selected_grade["exam_type"]],
        [selected_grade["course_id"]],
    )
    print(f"Existing reviews: {existing_reviews}")
    if existing_reviews:
        st.write("**Your existing review requests:**")
        for review in existing_reviews:
            with st.expander(
                f"Review from {STUDENT_ID} for {selected_grade['course_id']} - {selected_grade['exam_type']} {selected_grade['year']}"
            ):
                status = (
                    "✅ Replied" if review.get("is_replied", False) else "⏳ Pending"
                )
                st.write(f"**Status:** {status}")
                st.write(
                    f"**Your request:** {review.get('review_text', 'No text provided')}"
                )

                if review.get("is_replied", False) and review.get("reply_text"):
                    st.divider()
                    st.write(f"**Instructor's reply:** {review['reply_text']}")
    else:
        st.info("No existing review requests for this grade.")

    # New review form
    # if the grade is finalized, display a message that reviews are not allowed
    # else allow review request submission
    if response_body["grades_status"] == "FINAL":
        st.warning("Reviews are not allowed for finalized grades.")
    else:
        with st.form("review_form"):
            review_text = st.text_area(
                "Review Request",
                placeholder="Explain why you're requesting a review of this grade...",
                help="Provide detailed explanation (minimum 10 characters required)",
                max_chars=1000,
            )

            submitted = st.form_submit_button("Submit Review Request")

            if submitted:
                if len(review_text) < 10:
                    st.error("Review text must be at least 10 characters long")
                else:
                    review_data = {
                        "student_id": STUDENT_ID,
                        "course_id": selected_grade["course_id"],
                        "exam_type": selected_grade["exam_type"],
                        "year": selected_grade["year"],
                        "review_text": review_text,
                    }

                    with st.spinner("Submitting review request..."):
                        from orchestrator.review.review_ops import submit_review

                        response = asyncio.run(submit_review(review_data))
                        response_body = json.loads(response.body)
                        if response.status_code == 200:
                            st.success("Review request submitted successfully!")
                            st.rerun()
                        else:
                            st.error(
                                f"Failed to submit review: {response_body.get('detail', 'Unknown error')}"
                            )


if __name__ == "__main__":
    main()
