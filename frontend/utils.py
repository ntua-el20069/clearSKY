import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import json

import streamlit as st

from orchestrator.user_management.user_management_ops import check_access


def require_role(allowed_roles: str | list[str]) -> None:
    if "token" not in st.session_state or st.session_state.token == "NULL":
        st.error("Unauthorized. Please log in.")
        st.stop()

    response = asyncio.run(check_access(st.session_state.token))
    response_body = json.loads(response.body)
    user_privilege = response_body["privilege"]

    if user_privilege not in ["Admin", "InstitutionRepresentative"]:
        st.error("Access denied: You do not have permission to view this page.")
        st.stop()
