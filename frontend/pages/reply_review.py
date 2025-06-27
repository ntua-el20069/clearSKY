# pages/instructor_reviews.py
import asyncio
import json
from typing import Any, Dict, List

import streamlit as st

from orchestrator.review.review_ops import get_reviews, reply_to_review

# Authentication and role check
if "username" not in st.session_state or "role" not in st.session_state:
    st.error("Please log in to access this page")
    st.stop()

if st.session_state.role != "Instructor":
    st.error("Only instructors can access this page")
    st.stop()

st.title("📝 Grade Review Responses")


async def fetch_reviews(
    instructor_id: str, pending: bool = True
) -> List[Dict[str, Any]]:
    """Fetch reviews needing responses for courses taught by this instructor"""
    try:

        response = await get_reviews(
            {}
        )  # TODO: Implement filtering by instructor_id (now we get all reviews)
        if response.status_code == 200:
            all_reviews = json.loads(response.body).get("reviews", [])

            # In a real app, you would filter for courses taught by this instructor
            # This is a placeholder - implement your actual course/instructor mapping
            if pending:
                return [r for r in all_reviews if not r["is_replied"]]
            else:  # answered reviews
                return [r for r in all_reviews if r["is_replied"]]

        st.error(f"Error fetching reviews: {response.text}")
        return []
    except Exception as e:
        st.error(f"API connection failed: {str(e)}")
        return []


async def submit_reply(
    student_id: str, course_id: str, year: int, exam_type: str, reply_text: str
) -> bool:
    """Submit instructor's reply to a review"""
    try:
        response = await reply_to_review(
            {
                "student_id": student_id,
                "course_id": course_id,
                "year": year,
                "exam_type": exam_type,
                "reply_text": reply_text,
                "instructor_id": st.session_state.username,
            }
        )
        if response.status_code == 200:
            st.success("Reply submitted successfully!")
            return True
        else:
            st.error(f"Failed to submit reply: {response.text}")
            return False
    except Exception as e:
        st.error(f"Failed to submit reply: {str(e)}")
        return False


def display_review(review: Dict[str, Any]) -> None:
    """Display a single review with reply form"""
    with st.expander(f"Review from {review.get('student_id', 'Unknown')}"):
        st.write(f"**Course:** {review.get('course_id', 'Unknown')}")
        st.write(
            f"**Exam:** {review.get('exam_type', 'Unknown')} {review.get('year', '')}"
        )
        st.write(f"**Submitted:** {review.get('created_at', 'Unknown')}")
        st.markdown("---")
        st.write("**Student's Request:**")
        st.write(review.get("review_text", "No content provided"))
        st.markdown("---")
        st.write("**Instructor's Response:**")
        if review.get("reply_text"):
            st.write(review["reply_text"])
            st.write(f"**Replied on:** {review.get('replied_at', 'Unknown')}")
        else:
            st.write("No response yet")

        # Reply form
        if review["is_replied"]:
            return  # If already replied, skip the form
        # Only show form if not replied
        with st.form(
            key=f"reply_form_{review['student_id']} for course {review['course_id']}: {review['year']}_{review['exam_type']}"
        ):
            reply_text = st.text_area(
                "Your response",
                placeholder="Type your response to the student here...",
                height=150,
            )

            submitted = st.form_submit_button("Submit Response")
            if submitted:
                if len(reply_text.strip()) < 10:
                    st.error(
                        "Please write a meaningful response (at least 10 characters)"
                    )
                else:
                    with st.spinner("Submitting your response..."):
                        success = asyncio.run(
                            submit_reply(
                                student_id=review["student_id"],
                                course_id=review["course_id"],
                                year=review["year"],
                                exam_type=review["exam_type"],
                                reply_text=reply_text,
                            )
                        )
                        if success:
                            st.success("Response submitted successfully!")
                            # st.rerun()
                        else:
                            st.error("Failed to submit response")


def main() -> None:
    """Main page layout and logic"""
    st.header("Pending Review Requests")

    with st.spinner("Loading pending reviews..."):
        reviews = asyncio.run(fetch_reviews(st.session_state.username, pending=True))

    if not reviews:
        st.info("No pending review requests found")
    else:
        # Display all pending reviews
        for review in reviews:
            display_review(review)

    st.markdown("---")
    st.subheader("Answered Reviews")
    with st.spinner("Loading answered reviews..."):
        answered_reviews = asyncio.run(
            fetch_reviews(st.session_state.username, pending=False)
        )

    if not answered_reviews:
        st.info("No answered review requests found")
    else:
        # Display all answered reviews
        for review in answered_reviews:
            display_review(review)


if __name__ == "__main__":
    main()
