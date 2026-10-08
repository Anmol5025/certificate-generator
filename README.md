# Bulk Certificate Generator

A backend API built with FastAPI and SQLite to generate certificates in bulk based on a predefined template.

## Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Run the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can also access the Swagger UI documentation at `http://127.0.0.1:8000/docs`.

## Running Tests

Run the tests using pytest:

```bash
pytest
```

## API Usage

### Submit a Certificate Generation Request

Make a `POST` request to `/jobs` with a list of recipients:

```bash
curl -X POST "http://127.0.0.1:8000/jobs" \
     -H "Content-Type: application/json" \
     -d '{
           "recipients": [
             {
               "name": "John Doe",
               "email": "john@example.com",
               "course": "Introduction to Python"
             },
             {
               "name": "Jane Smith",
               "email": "jane@example.com",
               "course": "Advanced FastAPI"
             }
           ]
         }'
```

The response will contain a `job_id`.

### Check Progress and Retrieve Results

Make a `GET` request to `/jobs/{job_id}`:

```bash
curl "http://127.0.0.1:8000/jobs/1"
```

This returns the status of the job (`pending`, `processing`, or `completed`) and the status of each certificate.

### Download a Generated Certificate

Once a certificate has a status of `success`, you can download it using its `id`:

```bash
curl -O -J "http://127.0.0.1:8000/certificates/1/download"
```

## Implementation & Design Decisions

- **FastAPI**: Chosen for its speed, automatic interactive API documentation, and built-in validation using Pydantic.
- **SQLite & SQLAlchemy**: Used a lightweight relational database to store job and certificate tracking information. SQLAlchemy provides an ORM for easy database interaction.
- **Background Processing**: FastAPI's `BackgroundTasks` is used to handle certificate generation asynchronously. This ensures the client receives a fast response when submitting a large list, rather than waiting for all images to be generated before the HTTP request returns.
- **Pillow**: Used for simple and efficient image manipulation and text drawing on a predefined certificate template. If a template image is missing, a default placeholder is automatically created.
- **Error Handling**: A failure in generating a single certificate is caught and logged within its own record (`status="failed"`, with an `error_message`), ensuring the rest of the batch continues processing seamlessly.
