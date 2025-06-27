import os

import jwt
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer

load_dotenv()

from user_management.user_management.models.models import Session, User

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
serializer = URLSafeTimedSerializer(SECRET_KEY)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = "http://localhost:8501" # Change to your Streamlit URL in production


@router.get(
    "/google_login",
    response_description="User logged in successfully",
)  # type: ignore
async def google_login(request: Request) -> RedirectResponse:
    """
    Authenticate a user via Google Sign-In token. Needs the user to be registered with the same email.
    If the user is already logged in or credentials are invalid, appropriate errors are raised.
    """
    try:
        code = request.query_params.get("code")

        # Exchange code for tokens
        google_token = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": "http://localhost:8001/google_login/google_login", # Change to your FastAPI URL in production
                "grant_type": "authorization_code",
            },
        ).json()

        if not google_token:
            return RedirectResponse(f"{FRONTEND_URL}/?error=Google token missing")

        try:
            _ = google_token.get("id_token")
            access_token = google_token.get("access_token")

            user_info = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                params={"access_token": access_token},
            ).json()

            email = user_info.get("email")

            if not email:
                return RedirectResponse(
                    f"{FRONTEND_URL}/?error=Email not found in Google user info"
                )

            user = User.objects(email=email).first()

            if not user:
                return RedirectResponse(f"{FRONTEND_URL}/?error=Invalid credentials")

        except ValueError:
            return RedirectResponse(f"{FRONTEND_URL}/?error=Invalid Google token")

        role_obj = user.role
        username_obj = user.username

        if Session.objects(username=username_obj):
            return RedirectResponse(f"{FRONTEND_URL}/?error=Already logged in")

        if len(Session.objects()) == 1:
            Session.objects().delete()

        token = str(serializer.dumps(username_obj))
        Session(token=token, username=username_obj, role=role_obj).save()

        payload = {
            "token": token,
            "institution": user.institution,
            "username": user.username,
            "password": user.password,
        }

        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return RedirectResponse(f"{FRONTEND_URL}/?auth={jwt_token}")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
