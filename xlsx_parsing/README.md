# XLSX Parsing Microservice

## Install Dependencies
- `python3.12 -m venv .venv`  
- `source .venv/bin/activate`
- `pip install -r xlsx_parsing/requirements.txt`

## Run the API
From the base `saas25-20` directory execute
```bash
cd xlsx_parsing/xlsx_parsing
fastapi run app.py
```

## Docs
- Open `http://127.0.0.1:8000/docs` to see documentation
- Click on the endpoint and `Try it out` to test it using an xlsx file

## Test the app via terminal command
```bash
curl -X POST -F "file=@/your_path_to/clearSKY-question3.xlsx" http://localhost:8000/parse-grades/
```

## Test the app using Postman
- Open Postman and Click the "+" button to create a new request tab
- Set the request method to POST
- Enter the URL: http://localhost:8000/parse-grades/
- Postman will automatically add some headers
- Make sure Content-Type is not set manually (it should be automatically set to multipart/form-data when you add the file)
- Click on the "Body" tab and Select form-data
- Add a key named file (must match the parameter name in the endpoint file: UploadFile = File(...))
- Hover over the key name and select "File" from the dropdown (instead of "Text")
- Click "Select Files" and choose your XLSX file
- Click the "Send" button and wait for the response

## Test using pytest
From the base `saas25-20` directory execute
```bash
cd xlsx_parsing
pytest
```

## Containerize xlsx_parsing
- ensure `Docker Desktop` is working
- inside `xlsx_parsing` folder, execute the command `docker init`
- In the questions, `Python 3.12.9` is used and the command `fastapi run xlsx_parsing/app.py --port 8003`
- When integrating many containers in one app the `compose.yaml` on the root (saas25-20) dir should contain an entry like:
```yaml
services:
  server:
    build:
      context: xlsx_parsing/
    ports:
      - 8003:8003
```
- You may want to do port modifications
- `docker compose up --build`
- Access docs through the url http://127.0.0.1:8003/docs