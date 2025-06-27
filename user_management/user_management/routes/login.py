import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash

from user_management.user_management.models.models import Session, User, UserModel

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
serializer = URLSafeTimedSerializer(SECRET_KEY)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/check_access")  # type: ignore
async def check_access(token: str) -> JSONResponse:
    """
    Checks if a logged in user with a specific token can perform an operation

    :param token: The passed token of the logged in user
    :type token: str
    """
    try:
        searched_token = Session.objects(token=token).first()

        if not searched_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"privilege": searched_token.role}
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/login",
    response_description="User logged in successfully",
)  # type: ignore
async def login(user_data: UserModel) -> JSONResponse:
    """
    Authenticate a user based on their user ID, password, and role.
    If the user is already logged in or credentials are invalid, appropriate errors are raised.

    :param user_data: User login information (user ID, password, and role)
    :type user_data: BaseModel (see model.py)
    """
    try:
        user = User.objects(username=user_data.username).first()
        if not user or not check_password_hash(user.password, user_data.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if Session.objects(username=user.username):
            raise HTTPException(status_code=402, detail="Already logged in")

        if len(Session.objects()) == 1:
            Session.objects().delete()

        token = str(serializer.dumps(user.username))
        Session(token=token, username=user.username, role=user.role).save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "token": token,
                "institution": user.institution,
            },
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/logout",
    response_description="User logged out successfully",
)  # type: ignore
async def logout(token: str = Depends(oauth2_scheme)) -> Response:
    """
    Log out a user based on the authentication token.
    Deletes the corresponding session if the token is valid.

    :param token: Bearer token used for authenticating the session
    :type token: str (provided via OAuth2 scheme)
    """
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    try:
        session = Session.objects(token=token).first()
        if not session:
            raise HTTPException(
                status_code=401, detail="Invalid token or already logged out"
            )

        session.delete()

        return Response(status_code=204)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
