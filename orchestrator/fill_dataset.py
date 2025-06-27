import asyncio
import json

# from statistics.statistics_ops import add_grades, get_student_grades, update_grades
from statistics.statistics_ops import update_grades

import streamlit as st

# from xlsx_parsing.xlsx_parsing_ops import parse_grades

file = st.file_uploader("Upload xlsx", type=["xlsx"], key="file_uploader")

if file:
    # res = asyncio.run(parse_grades(file))
    # print(json.loads(res.body.decode()))

    # grades = [
    #     {
    #         "student_id": "0000002",
    #         "course_id": "NTU_CS101",
    #         "exam_type": "Winter",
    #         "year": 2024,
    #         "grade": 6.0,
    #         "question_grades": [9.0, 3.0, 5.0, 7.0],
    #         "grade_weights": [1.0, 1.0, 1.0, 1.0],
    #     },
    #     {
    #         "student_id": "0000001",
    #         "course_id": "NTU_CS101",
    #         "exam_type": "Winter",
    #         "year": 2024,
    #         "grade": 9.5,
    #         "question_grades": [10.0, 9.0, 9.5, 9.5],
    #         "grade_weights": [1.0, 1.0, 1.0, 1.0],
    #     },
    #     {
    #         "student_id": "0000003",
    #         "course_id": "NTU_CS101",
    #         "exam_type": "Winter",
    #         "year": 2024,
    #         "grade": 9.0,
    #         "question_grades": [9.0, 9.0, 9.0, 9.0],
    #         "grade_weights": [1.0, 1.0, 1.0, 1.0],
    #     },
    # ]

    # response = asyncio.run(add_grades(grades))
    # print(json.loads(response.body.decode()))

    # params = {
    #     "student_ids": ["0000001", "0000002"],
    #     "years": [2024],
    #     "exam_types": "Winter",
    # }

    updated_grades = [
        {
            "student_id": "0000002",
            "name": "teg",
            "course_id": "NTU_CS202",
            "exam_type": "Winter",
            "year": 2021,
            "grade": 4.0,
            "question_grades": [9.0, 3.0, 5.0, 7.0],
            "grade_weights": [1.0, 1.0, 1.0, 1.0],
        }
    ]

    response = asyncio.run(update_grades(updated_grades))
    print(json.loads(response.body.decode()))
