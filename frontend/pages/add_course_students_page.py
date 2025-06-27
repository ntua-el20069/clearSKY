import json
import os
import sys
import uuid
from typing import Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio

import streamlit as st

from orchestrator.statistics.statistics_ops import add_course, enroll_students
from orchestrator.user_management.user_management_ops import fetch_instructors
from orchestrator.xlsx_parsing.xlsx_parsing_ops import parse_enrolled_students

if "students" not in st.session_state:
    st.session_state.students = []

if "course" not in st.session_state:
    st.session_state.course = ""

if "n_students" not in st.session_state:
    st.session_state.n_students = 0

if "exam_period" not in st.session_state:
    st.session_state.exam_period = ""

if "year" not in st.session_state:
    st.session_state.year = 0


def get_instructors_response() -> Any:
    response = asyncio.run(fetch_instructors(st.session_state.institution))

    if response.status_code == 200:
        response_body = json.loads(response.body)
        return response_body["instructors"]

    return None


with st.container():
    st.header("Publish course and enroll students to courses")

    with st.form("add_course"):
        course_id = st.text_input("Course ID")

        # fetching instructors
        fetched_instructors = get_instructors_response()
        if fetched_instructors is None:
            st.error("Error while fetching instructors. Please refresh and try again.")

        instructors_options = [
            instructor["instructor_id"] for instructor in fetched_instructors
        ]
        instructors = st.multiselect("Select instructors", instructors_options)
        name = st.text_input("Course name")
        semester = st.number_input("Semester", min_value=1, max_value=10)
        ects = st.number_input("ECTS", min_value=1, max_value=1000)

        if st.form_submit_button("Submit"):
            if not instructors:
                st.error("Please select at least one instructor.")
            elif not name.strip():
                st.error("Please enter the course name.")
            else:
                st.success("All inputs are valid!")
                load = {
                    "course_id": course_id,
                    "institution": st.session_state.institution,
                    "instructors": instructors,
                    "name": name,
                    "semester": semester,
                    "ects": ects,
                    "current_registered_students": [],
                    "grades": [],
                    "finalized": {},
                }

                response = asyncio.run(add_course(load))
                response_body = json.loads(response.body)
                if response.status_code != 200:
                    st.error(f"Error while adding course: {response_body['detail']}")
                else:
                    st.success("Successfully added course!")

    student_excel = st.file_uploader(
        "Enroll students to course",
        type=["xlsx"],
        key=st.session_state.get("student_file_uploader_key", "students_uploader"),
    )

    st.info(
        """
        This is the student excel sheet to extract the students of the course. The excel sheet must contain
        a column with the academic ID of the students so that we can extract and later add them as the registered students
        of the coure. It doesn't matter if your excel sheet contains more columns than that.
        """
    )
    if student_excel:
        response = asyncio.run(parse_enrolled_students(student_excel))
        response_body = json.loads(response.body)
        if response is None or response.status_code != 200:
            st.error(
                f"Error while parsing students file: {response_body['detail']['error']}"
            )
        else:
            st.session_state.students = response_body["result"]["student_ids"]
            st.session_state.n_students = len(st.session_state.students)
            st.session_state.course = response_body["result"]["course_id"]
            st.session_state.exam_period = response_body["result"]["exam_type"]
            st.session_state.year = response_body["result"]["year"]

        with st.container():
            st.text_input(
                "n. of students: ", value=st.session_state.n_students, disabled=True
            )
            st.text_input("Course: ", value=st.session_state.course, disabled=True)
            st.text_input(
                "Exam period: ", value=st.session_state.exam_period, disabled=True
            )
            st.text_input("Year: ", value=st.session_state.year, disabled=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Submit"):
                    response = asyncio.run(
                        enroll_students(
                            st.session_state.course, st.session_state.students
                        )
                    )
                    response_body = json.loads(response.body)
                    if response.status_code != 200:
                        st.error(
                            f"Error while adding students to course: {st.session_state.course} | {response_body['detail']}. Please try again"
                        )
                    else:
                        st.success(
                            f"Successfully enrolled {st.session_state.n_students} students to {st.session_state.course} course!"
                        )

            with col2:
                if st.button("Cancel"):
                    st.session_state.students = []
                    st.session_state.n_students = 0
                    st.session_state.course = ""
                    st.session_state.exam_period = ""
                    st.session_state.year = 0
                    st.session_state.student_file_uploader_key = str(uuid.uuid4())

                    st.rerun()
