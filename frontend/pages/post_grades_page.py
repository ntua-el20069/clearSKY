import json
import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio

import streamlit as st

from orchestrator.credits.credits_ops import get_credits, remove_credits
from orchestrator.statistics.statistics_ops import (
    add_grades,
    finalize_course,
    get_status_of_grades,
    initialize_course_grades,
    update_grades,
)
from orchestrator.xlsx_parsing.xlsx_parsing_ops import parse_grades

CREDITS_TO_REMOVE = 1

if "course" not in st.session_state:
    st.session_state.course = ""

if "exam_period" not in st.session_state:
    st.session_state.exam_period = ""

if "n_grades" not in st.session_state:
    st.session_state.n_grades = 0

if "grades" not in st.session_state:
    st.session_state.grades = []

if "year" not in st.session_state:
    st.session_state.year = 0

if "status_of_grades" not in st.session_state:
    st.session_state.status_of_grades = "default"


def change_status_of_grades():  # type: ignore
    """ "Change the status of grades based on the current state."""
    if st.session_state.status_of_grades == "UNKNOWN":
        response = asyncio.run(
            initialize_course_grades(
                st.session_state.course,
                st.session_state.exam_period,
                st.session_state.year,
            )
        )
        response_body = json.loads(response.body)
        if response.status_code != 200:
            print(f"response body: {response_body}")
            print(f"status code: {response.status_code}")
            st.error(
                f"Error while initializing course grades: {response_body['detail']}"
            )
            st.stop()
        else:
            st.success("Successfully initialized course grades!")

    elif st.session_state.status_of_grades == "INITIAL":
        response = asyncio.run(
            finalize_course(
                st.session_state.course,
                st.session_state.exam_period,
                st.session_state.year,
            )
        )
        response_body = json.loads(response.body)
        if response.status_code != 200:
            print(f"response body: {response_body}")
            print(f"status code: {response.status_code}")
            st.error(f"Error while finalizing course grades: {response_body['detail']}")
            st.stop()
        else:
            st.success("Successfully finalized course grades!")


with st.container():
    st.header("Grades posting")

    file = st.file_uploader(
        "Select file to upload or drag and drop",
        type=["xlsx"],
        key=st.session_state.get("file_uploader_key", "initial_uploader"),
    )

    if file:
        response = asyncio.run(parse_grades(file))
        response_body = json.loads(response.body)
        if response is None or response.status_code != 200:
            st.error(
                f"Error while parsing the grades file: {response_body['detail']['error']}"
            )
        else:
            st.session_state.course = response_body["result"]["data"][0]["course_id"]
            st.session_state.exam_period = response_body["result"]["data"][0][
                "exam_type"
            ]
            st.session_state.year = response_body["result"]["data"][0]["year"]
            st.session_state.n_grades = len(response_body["result"]["data"])
            st.session_state.grades = response_body["result"]["data"]

            response = asyncio.run(
                get_status_of_grades(
                    st.session_state.course,
                    st.session_state.exam_period,
                    st.session_state.year,
                )
            )
            response_body = json.loads(response.body)
            if response.status_code != 200:
                st.error(
                    f"Error while fetching status of grades: {response_body['detail']}"
                )
                st.session_state.status_of_grades = None
            else:
                st.session_state.status_of_grades = response_body["grades_status"]

with st.container():
    st.text_input("Course: ", value=st.session_state.course, disabled=True)
    st.text_input("Exam period: ", value=st.session_state.exam_period, disabled=True)
    st.text_input("Year: ", value=st.session_state.year, disabled=True)
    st.text_input("n. of grades: ", value=st.session_state.n_grades, disabled=True)

    if st.session_state.status_of_grades is None:
        st.error("Possible issue finding the course or getting status of grades.")
        st.stop()
    elif st.session_state.status_of_grades == "default":
        st.info(
            "Upload a valid xlsx in order to post initial/final grades. You can post grades up to 2 times per (course_id, exam_period, year)."
        )
        st.stop()
    elif st.session_state.status_of_grades == "UNKNOWN":
        st.info("Initial post grades.")
        response = asyncio.run(
            get_credits(
                st.session_state.institution,
            )
        )
        response_body = json.loads(response.body)
        if response.status_code != 200:
            st.error(f"Error while fetching credits: {response_body['detail']}")
            st.stop()
        else:
            st.session_state.credits = response_body["credits"]
            if st.session_state.credits < CREDITS_TO_REMOVE:
                st.error(
                    "You have not enough credits left to post grades. Please contact the institution representative to purchase credits for your institution."
                )
                st.stop()
    elif st.session_state.status_of_grades == "INITIAL":
        st.info("Final post grades.")
    elif st.session_state.status_of_grades == "FINAL":
        st.error(
            f"Grades for {st.session_state.course} in {st.session_state.exam_period} {st.session_state.year} are already finalized. You cannot change them anymore."
        )
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm"):
            remove_credits_also = False
            if st.session_state.status_of_grades == "UNKNOWN":
                response = asyncio.run(add_grades(st.session_state.grades))
                remove_credits_also = True
            else:
                response = asyncio.run(update_grades(st.session_state.grades))
            response_body = json.loads(response.body)
            if response.status_code != 200:
                st.error(
                    f"Error while posting extracted grades: {response_body['detail']}"
                )
            else:
                # change_status_of_grades()  # Not need to call this function here as
                # the status of grades is already set to INITIAL or FINAL inside /add_grades or /update_grades
                if remove_credits_also:
                    response = asyncio.run(
                        remove_credits(
                            {
                                "institution": st.session_state.institution,
                                "credits": CREDITS_TO_REMOVE,
                            }
                        )
                    )
                    response_body = json.loads(response.body)
                    if response.status_code != 200:
                        st.error(
                            f"Error while removing credits: {response_body['detail']}"
                        )
                        st.stop()
                    else:
                        st.success(f"Credits: {response_body['description']}")
                st.success("Successfully extracted and posted grades!")
    with col2:
        if st.button("Cancel"):
            st.session_state.course = ""
            st.session_state.exam_period = ""
            st.session_state.year = 0
            st.session_state.status_of_grades = "default"
            st.session_state.n_grades = 0
            st.session_state.grades = []
            st.session_state.file_uploader_key = str(uuid.uuid4())

            st.rerun()
