import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio

import streamlit as st

from orchestrator.user_management.user_management_ops import (
    register_instructor,
    register_student,
)

with st.container():
    st.header("Users")
    type = st.selectbox("User type", ["Instructor", "Student"])
    with st.form("add_user"):
        username = st.text_input(
            "username(the academic ID of the user)", label_visibility="visible"
        )
        email = st.text_input("email", label_visibility="visible")
        password = st.text_input(
            "password", label_visibility="visible", type="password"
        )
        name = st.text_input("Name", label_visibility="visible")
        if type == "Instructor":
            department = st.text_input("Department", label_visibility="visible")
            phone = st.text_input("Phone", label_visibility="visible")
            office = st.text_input("Office", label_visibility="visible")
        else:
            enrollment_year = st.number_input(
                "Enrollment year", min_value=0, max_value=datetime.now().year
            )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button(label="add_user"):
                if type == "Instructor":
                    instructor = {
                        "instructor_id": username,
                        "email": email,
                        "password": password,
                        "name": name,
                        "institution": st.session_state.institution,
                        "department": department,
                        "phone": phone,
                        "office": office,
                    }
                    response = asyncio.run(register_instructor(instructor))
                    response_body = json.loads(response.body)

                    if response.status_code != 200:
                        st.error(
                            f"Error while registering instructor: {username} | {response_body['detail']}"
                        )
                    else:
                        st.success(f"Successfully registered instructor: {username}")
                elif type == "Student":
                    student = {
                        "student_id": username,
                        "email": email,
                        "password": password,
                        "name": name,
                        "institution": st.session_state.institution,
                        "enrollment_year": str(enrollment_year),
                    }

                    response = asyncio.run(register_student(student))
                    response_body = json.loads(response.body)

                    if response.status_code != 200:
                        st.error(
                            f"Error while registering student: {username} | {response_body['detail']}"
                        )
                    else:
                        st.success(f"Successfully registered student: {username}")

        with col2:
            if st.form_submit_button("Cancel"):
                st.rerun()
