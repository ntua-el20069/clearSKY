![statistics microservice](https://github.com/ntua/saas25-20/actions/workflows/statistics-backend-tests.yml/badge.svg)
![credits microservice](https://github.com/ntua/saas25-20/actions/workflows/credits-backend-tests.yml/badge.svg)
![xlsx parsing microservice](https://github.com/ntua/saas25-20/actions/workflows/xlsx_parsing-backend-tests.yml/badge.svg)
![user management microservice](https://github.com/ntua/saas25-20/actions/workflows/user_management-tests.yml/badge.svg)
![review microservice](https://github.com/ntua/saas25-20/actions/workflows/review-backend-tests.yml/badge.svg)
![pre-commit](https://github.com/ntua/saas25-20/actions/workflows/pre-commit.yml/badge.svg)

# ClearSKY Grading System
<div align="center">
    <img
        src=https://github.com/ntua/saas25-20/blob/main/assets/clear_sky.png
        alt="clearSKY"
        width="300"
    >
</div>

ClearSKY is a web application for courses/grading management by universities. It
supports interactive student-professor reviews, multiple statistics per course,
grading management for professors and much more. For the **full documentation**
please visit our OpenAPI 3.0 documentation at `/docs` once you run the backend.

clearSKY functionalities are demonstrated in this quick youtube [demo](https://www.youtube.com/watch?v=fGAhwPX3sPU).


## Manual Run
To start the application manually, you can just run:
`docker compose up --build`

your application will be available at `http://localhost:8501`. Note that we use
microservices as our backend architecture, each microservice is running on it's
own port. For example, user management is running at 8001, credits at 8002,
parsing at 8003, etc. You can see the documentation of each microservice at
their corresponding port + `/docs`(i.e. `http://localhost:{PORT}/docs`).

### Google login
To enable Google login, you need to set the `GOOGLE_CLIENT_ID` and
`GOOGLE_CLIENT_SECRET` environment variables in the `.env` file. You can
obtain these credentials by creating a project in the Google Developer Console
and enabling the Google OAuth 2.0 API. Make sure to set the redirect URI to the appropriate endpoint.

## Contributors
- Spiros Maggioros
- Dimitrios Minagias
- Stasinos Ntaveas
- Nikolaos Papakonstantopoulos
- Reidi Pasai 