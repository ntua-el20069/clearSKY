# pages/course_statistics.py
import asyncio
import json
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

from orchestrator.statistics.statistics_ops import get_course_stats

# Check authentication
if "username" not in st.session_state or "role" not in st.session_state:
    st.error("Please log in to access this page")
    st.stop()

# Check if user has permission to view statistics
allowed_roles = ["InstitutionRepresentative", "Instructor", "Student"]
if st.session_state.role not in allowed_roles:
    st.error("You don't have permission to view course statistics")
    st.stop()

st.title("📈 Course Statistics Dashboard")

# Initialize session state for filters
if "filters" not in st.session_state:
    st.session_state.filters = {
        "years": [datetime.now().year],
        "exam_types": ["Winter", "Summer"],
        "course_id": None,
    }


async def fetch_course_stats(course_id: str, exam_year: int, exam_type: str):  # type: ignore
    """Fetch statistics for a specific course exam period"""
    try:
        response = await get_course_stats(course_id, exam_year, exam_type)
        response_body = json.loads(response.body)
        if response.status_code == 200:
            return response_body
        st.error(f"Error fetching stats: {response_body['detail']}")
        return None
    except Exception as e:
        st.error(f"API connection failed: {str(e)}")
        return None


def display_success_pie(stats_data: dict) -> None:
    """Display a pie chart of success (pass/fail) rates using Altair."""
    grades_dist = stats_data.get("grades_dist", {})
    if not grades_dist:
        st.warning("No grade distribution data available for success rate")
        return

    pass_count = 0
    fail_count = 0
    for grade_str, count in grades_dist.items():
        try:
            grade = float(grade_str)
        except ValueError:
            continue
        if grade >= 5:
            pass_count += count
        else:
            fail_count += count

    total = pass_count + fail_count
    if total == 0:
        st.warning("No graded students to calculate success rate")
        return

    df = pd.DataFrame({"Result": ["Pass", "Fail"], "Count": [pass_count, fail_count]})

    # Pie chart with Altair
    chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=40, outerRadius=100)
        .encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(
                field="Result",
                type="nominal",
                scale=alt.Scale(range=["#2ca02c", "#d62728"]),
            ),
            tooltip=[
                "Result",
                "Count",
                alt.Tooltip("Count", title="Percent", format=".1%"),
            ],
        )
        .properties(width=300, height=300, title="Success Rate (Pass/Fail)")
    )

    st.subheader("Success Rate")
    st.altair_chart(chart, use_container_width=False)


def display_grade_distribution(stats_data: dict) -> None:
    """Display grade distribution charts using Streamlit's native functions"""
    st.subheader("Grade Distribution")

    color_palette = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    grades_dist = stats_data.get("grades_dist", {})
    if grades_dist:
        df_grades = pd.DataFrame(list(grades_dist.items()), columns=["Grade", "Count"])
        df_grades["Grade"] = pd.to_numeric(df_grades["Grade"], errors="coerce")

        df_grades = df_grades.sort_values("Grade")
        chart = (
            alt.Chart(df_grades)
            .mark_bar(color=color_palette[0])
            .encode(
                x=alt.X("Grade:O", title="Grade"),
                y=alt.Y("Count:Q", title="Count"),
            )
            .properties(width="container")
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No grade distribution data available")

    all_questions_stats = stats_data.get("question_grades_dist", [])
    if not all_questions_stats:
        st.warning("No question-wise grade distribution data available")
        return
    st.subheader("Question-wise Grade Distribution")
    for q_num, q_data in enumerate(all_questions_stats):
        df_q = pd.DataFrame(list(q_data.items()), columns=["Score", "Count"])
        df_q["Score"] = pd.to_numeric(df_q["Score"], errors="coerce")
        df_q = df_q.sort_values("Score")

        color_idx = (q_num + 1) % len(color_palette)
        chart = (
            alt.Chart(df_q)
            .mark_bar(color=color_palette[color_idx])
            .encode(
                x=alt.X("Score:O", title="Score"),
                y=alt.Y("Count:Q", title="Count"),
            )
            .properties(width="container")
        )

        st.write(f"Question {int(q_num) + 1}")
        st.altair_chart(chart, use_container_width=True)


def main():  # type: ignore
    # Filters sidebar
    with st.sidebar:
        st.header("Filters")

        # Year filter
        selected_years = st.multiselect(
            "Select years",
            options=list(range(2000, datetime.now().year + 1)),
            default=[datetime.now().year - 1],
            key="year_filter",
        )

        # Exam type filter
        selected_exam_types = st.multiselect(
            "Select exam types",
            options=["Winter", "Summer", "Re-take", "Special"],
            default=st.session_state.filters["exam_types"],
            key="exam_type_filter",
        )

        # Course ID input
        course_id = st.text_input(
            "Enter Course ID",
            value=st.session_state.filters.get("course_id", "3205"),
            key="course_id_input",
        )

        # Update session state
        st.session_state.filters = {
            "years": selected_years,
            "exam_types": selected_exam_types,
            "course_id": course_id,
        }

    # Main content area
    if not course_id:
        st.warning("Please enter a Course ID to view statistics")
        return

    # Display statistics for each selected year and exam type
    for year in selected_years:
        for exam_type in selected_exam_types:
            st.header(f"Statistics for {course_id} - {exam_type} {year}")

            with st.spinner(f"Loading statistics for {exam_type} {year}..."):
                stats_data = asyncio.run(fetch_course_stats(course_id, year, exam_type))

                if stats_data:
                    display_grade_distribution(stats_data)
                    display_success_pie(stats_data)
                else:
                    st.warning(f"No statistics available for {exam_type} {year}")


if __name__ == "__main__":
    main()  # type: ignore
