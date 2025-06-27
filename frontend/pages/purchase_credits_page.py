import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio

import streamlit as st

from orchestrator.credits.credits_ops import add_credits

st.markdown("# Purchase credits for your institution")

with st.container():
    st.header("Purchase credits")

    with st.form("credit_purchase_form"):
        credits = st.number_input("Credits to purchase")

        submitted = st.form_submit_button("Submit purchase")

        if submitted:
            response = asyncio.run(
                add_credits(
                    {"institution": st.session_state.institution, "credits": credits}
                )
            )
            response_body = json.loads(response.body)

            if response.status_code == 200:
                st.success("Credits purchased successfully")
            else:
                st.warning(
                    f"An error occured while purchasing {credits} credits for {st.session_state.institution}"
                )
