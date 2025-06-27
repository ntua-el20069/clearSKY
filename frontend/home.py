import json
import os
import sys
from urllib.parse import urlencode

import jwt
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
REDIRECT_URI = "http://localhost:8001/google_login/google_login"  # FastAPI redirect ## change to your FastAPI URL in production
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPE = "openid email profile"
APP_FRONTEND_URL = "http://localhost:8501"  # Streamlit URL ## change to your Streamlit URL in production
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")

st.set_page_config(
    page_title="ClearSKY",
    layout="wide",
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio

from streamlit_cookies_manager import EncryptedCookieManager

from orchestrator.user_management.user_management_ops import check_access, login, logout

cookies = EncryptedCookieManager(
    prefix="clearSKY_",
    password="super-secret-password",  # Replace with secure key in prod
)

if not cookies.ready():
    st.stop()

if "token" not in st.session_state:
    st.session_state.token = cookies.get("token") or "NULL"
    st.session_state.institution = cookies.get("institution") or None
    st.session_state.username = cookies.get("username")
    st.session_state.password = cookies.get("password")

if "role" not in st.session_state:
    if st.session_state.token != "NULL":
        try:
            response = asyncio.run(check_access(st.session_state.token))
            st.session_state.role = json.loads(response.body)["privilege"]
        except Exception:
            st.session_state.role = None
    else:
        st.session_state.role = None

if "has_logged_out" not in st.session_state:
    st.session_state.has_logged_out = False

if "has_logged_in_with_googel" not in st.session_state:
    st.session_state.has_logged_in_with_googel = False

if "has_error_msg" not in st.session_state:
    st.session_state.has_error_msg = False


auth_token = st.query_params.get("auth", None)
error_msg = st.query_params.get("error", None)

if auth_token:
    try:
        decoded = jwt.decode(auth_token, SECRET_KEY, algorithms=["HS256"])
        google_token = decoded.get("token")
        institution_google = decoded.get("institution")
        username_google = decoded.get("username")
        password_google = decoded.get("password")
    except jwt.InvalidTokenError:
        st.error("Invalid authentication token.")
else:
    google_token = None
    institution_google = None
    username_google = None
    password_google = None

if error_msg and st.session_state.has_error_msg is False:
    st.sidebar.error(f"{error_msg}")
    st.session_state.has_error_msg = True


def home_page() -> None:
    st.markdown(
        """
        <style>
        /* Dark glassy background gradient */
        .stApp {
            background: linear-gradient(135deg, #181825 0%, #232946 100%) !important;
            min-height: 100vh;
        }
        /* Glassmorphism hero card */
        .dark-hero-card {
            margin: 2.5em auto 1.5em auto;
            padding: 2.2em 2em 2.5em 2em;
            max-width: 700px;
            background: rgba(30,30,40, 0.76);
            border-radius: 24px;
            box-shadow: 0 4px 32px 0 rgba(0,0,0,0.44);
            backdrop-filter: blur(18px);
            border: 1.5px solid rgba(255,255,255,0.08);
            text-align: center;
            color: #fff;
        }
        .dark-hero-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 2.8em;
            font-weight: 800;
            margin-bottom: 0.18em;
            color: #fff;
            letter-spacing: 1px;
            text-shadow: 1px 3px 24px #0008;
        }
        .dark-hero-desc {
            font-size: 1.22em;
            color: #b0b7be;
            margin-bottom: 1.6em;
        }
        .dark-feature-list {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 2em;
            margin-top: 1.1em;
            margin-bottom: 1.7em;
        }
        .dark-feature-card {
            background: rgba(40,40,60,0.42);
            border-radius: 16px;
            padding: 1em 1.3em;
            min-width: 170px;
            color: #f4f4f6;
            box-shadow: 0 2px 20px 0 rgba(0,0,0,0.17);
            transition: transform 0.14s;
            font-size: 1.08em;
            border: 1px solid rgba(255,255,255,0.06);
        }
        .dark-feature-card:hover {
            transform: translateY(-7px) scale(1.045);
            background: rgba(60,60,90,0.55);
        }
        .dark-hero-logo {
            margin-bottom: 1.5em;
            width: 88px;
            height: 88px;
            border-radius: 50%;
            background: #191a22;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 24px 0 rgba(0,0,0,0.28);
            margin-left: auto;
            margin-right: auto;
            border: 2.5px solid #232946;
        }
        .dark-cta {
            background:#20212a;
            color: #a3f7bf;
            border-radius:14px;
            padding:0.7em 1.3em;
            font-weight:600;
            font-size:1.13em;
            box-shadow:0 2px 16px 0 rgba(0,0,0,0.13);
            display:inline-block;
            margin-top: 1.2em;
            letter-spacing: 0.5px;
        }
        </style>

        <div class="dark-hero-card">
            <div class="dark-hero-logo">
                <img src="https://cdn-icons-png.flaticon.com/512/4149/4149643.png" width="56" height="56" alt="ClearSKY Logo"/>
            </div>
            <div class="dark-hero-title">Welcome to ClearSKY</div>
            <div class="dark-hero-desc">
                <b>Next-generation grading platform.</b><br>
                Reliable, transparent, and easy-to-use for students, instructors, and institutions.<br>
                Instant statistics. Interactive student-professor communication. Modern tools.
            </div>
            <div class="dark-feature-list">
                <div class="dark-feature-card">📊 Analyze course statistics</div>
                <div class="dark-feature-card">✅ Post and review grades</div>
                <div class="dark-feature-card">🔒 Secure Google login</div>
                <div class="dark-feature-card">💬 Feedback & reviews</div>
            </div>
            <span class="dark-cta">
                👉 Log in from the sidebar to get started!
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def login_logout() -> None:
    home_page()
    with st.sidebar:
        if google_token is not None:
            if st.session_state.has_logged_in_with_googel is False:
                st.session_state.has_logged_in_with_googel = True
                st.session_state.has_logged_out = False

                privilege_response = asyncio.run(check_access(google_token))
                response_data = json.loads(privilege_response.body)
                privilege = response_data["privilege"]

                st.session_state.token = google_token
                st.session_state.username = username_google
                st.session_state.password = password_google
                st.session_state.role = privilege
                st.session_state.institution = institution_google

                cookies["token"] = google_token
                cookies["institution"] = institution_google
                cookies["username"] = username_google
                cookies["password"] = password_google
                cookies.save()

                st.rerun()

        with st.form(key="login"):
            username = st.text_input(
                "username", label_visibility="visible", placeholder="username"
            )
            password = st.text_input(
                "password",
                label_visibility="visible",
                placeholder="password",
                type="password",
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button(label="login")
            with col2:
                login_with_google = st.form_submit_button(label="Continue with Google")

            if login_button:
                if username and password:
                    response = asyncio.run(
                        login({"username": username, "password": password})
                    )
                    response_body = json.loads(response.body)
                    if response.status_code == 200:
                        token = response_body["token"]
                        institution = response_body["institution"]
                        privilege_response = asyncio.run(check_access(token))
                        response_data = json.loads(privilege_response.body)
                        privilege = response_data["privilege"]

                        # Update session state
                        st.session_state.token = token
                        st.session_state.username = username
                        st.session_state.password = password
                        st.session_state.role = privilege
                        st.session_state.institution = institution

                        cookies["token"] = token
                        cookies["institution"] = institution
                        cookies["username"] = username
                        cookies["password"] = password  # Optional
                        cookies.save()

                        st.session_state.has_logged_out = False

                        st.rerun()
                    else:
                        message = response_body.get("detail")
                        st.error(f"{message}")
                else:
                    st.warning(
                        "Please make sure you provided both a username and a password"
                    )

            if login_with_google:
                # Google OAuth Authorization URL
                login_url = f"{AUTH_URI}?" + urlencode(
                    {
                        "client_id": GOOGLE_CLIENT_ID,
                        "redirect_uri": REDIRECT_URI,
                        "response_type": "code",
                        "scope": SCOPE,
                        "access_type": "offline",
                        "prompt": "consent",
                    }
                )

                st.markdown(
                    f"""
                    <meta http-equiv="refresh" content="0; url='{login_url}'" />
                    """,
                    unsafe_allow_html=True,
                )
                st.stop()

        logout_button = st.button(label="logout")

        if logout_button:
            if st.session_state.get("token") and st.session_state.token != "NULL":
                response = asyncio.run(logout(st.session_state.token))
                st.session_state.has_logged_out = True
            else:
                st.session_state.has_logged_out = False
                st.rerun()

            st.session_state.token = "NULL"
            st.session_state.username = None
            st.session_state.password = None
            st.session_state.role = None
            st.session_state.institution = None

            cookies["token"] = ""
            cookies["username"] = ""
            cookies["password"] = ""
            cookies["institution"] = ""
            cookies.save()

            st.rerun()


account_pages = [st.Page(login_logout, title="Log in/Log out")]

admin_pages = [
    st.Page(
        "pages/purchase_credits_page.py", title="Purchase credits for your institution"
    ),
    st.Page(
        "pages/add_course_students_page.py",
        title="Register a course to your institution",
    ),
    st.Page(
        "pages/user_management_page.py",
        title="User management for your institution",
    ),
]

representative_pages = [
    st.Page(
        "pages/purchase_credits_page.py", title="Purchase credits for your institution"
    ),
    st.Page(
        "pages/add_course_students_page.py",
        title="Register a course to your institution",
    ),
    st.Page(
        "pages/user_management_page.py",
        title="User management for your institution",
    ),
    st.Page("pages/course_statistics.py", title="View course statistics"),
]

instructor_pages = [
    st.Page("pages/post_grades_page.py", title="Post grades"),
    st.Page("pages/course_statistics.py", title="View course statistics"),
    st.Page("pages/reply_review.py", title="Reply to reviews"),
]

student_pages: list = [
    st.Page("pages/student_grades.py", title="View grades (student)"),
    st.Page("pages/course_statistics.py", title="View course statistics"),
]

page_dict = {}
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages
elif st.session_state.role == "InstitutionRepresentative":
    page_dict["InstitutionRepresentative"] = representative_pages
elif st.session_state.role == "Instructor":
    page_dict["Instructor"] = instructor_pages
elif st.session_state.role == "Student":
    page_dict["Student"] = student_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login_logout)])

if st.session_state.token != "NULL":
    st.sidebar.success(
        f"Logged in as {st.session_state.username}: {st.session_state.role} | {st.session_state.institution}"
    )

if st.session_state.has_logged_out is True:
    st.sidebar.success("Successfully logged out!")

pg.run()
