# Translation API with B2 Storage Integration

A comprehensive FastAPI-based translation service that supports text and file translations across multiple languages with Backblaze B2 storage integration.

## Features
- Text and file translation support
- Multi-language translation (up to 5 languages)
- API key authentication
- Backblaze B2 storage integration
- Job status tracking
- Support for multiple language regions
- Asynchronous file processing

## Installation & Setup

1. Clone the repository and create virtual environment:
```bash
git clone <repository-url>
cd translation-api
python -m venv .venv

# For Unix/macOS:
source .venv/bin/activate
# For Windows:
.venv\Scripts\activate
```

2. Install required packages:
```bash
pip install fastapi uvicorn python-multipart deep-translator python-dotenv sqlalchemy b2sdk
```

3. Create a `.env` file with your credentials:
```env
ADMIN_ACCESS_KEY=test123
B2_APPLICATION_KEY_ID=your_b2_key_id
B2_APPLICATION_KEY=your_b2_key
B2_BUCKET_NAME=your_bucket_name
```

4. Create required directories:
```bash
mkdir upload
mkdir storage
```

5. Run the application:
```bash
python main.py
```

## API Authentication

The API uses key-based authentication. All requests must include an `X-API-Key` header.

## Curl Commands Guide

### Admin Operations

1. Generate a new API key:
```bash
curl -X POST "http://localhost:8000/admin/generate-key" \
     -H "X-API-Key: test123" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "New API Key",
       "created_by": "Admin"
     }'

# Example Response:
{
  "key": "9K7nGYA2vveYFK39hfnGou7TygsIFeS3ySyKT_rGZcE",
  "description": "New API Key",
  "created_at": "2024-11-06T08:41:48.388284",
  "created_by": "Admin",
  "is_active": true
}
```

2. List all API keys:
```bash
curl -X GET "http://localhost:8000/admin/list-keys" \
     -H "X-API-Key: test123"
```

3. Deactivate an API key:
```bash
curl -X POST "http://localhost:8000/admin/deactivate-key" \
     -H "X-API-Key: test123" \
     -H "Content-Type: application/json" \
     -d '"key_to_deactivate"'
```

### Language Information

1. Get supported languages by region:
```bash
curl -X GET "http://localhost:8000/languages" \
     -H "X-API-Key: your_api_key"

# Example Response:
{
  "North_America": {
    "English (US)": "english_us",
    "English (Canada)": "english_canada",
    "Spanish (Mexico)": "spanish_mexico"
  },
  "India": {
    "Hindi": "hindi",
    "Bengali": "bengali",
    ...
  },
  ...
}
```

2. Get flat list of languages:
```bash
curl -X GET "http://localhost:8000/languages/flat" \
     -H "X-API-Key: your_api_key"
```

### Text Translation

1. Single language translation:
```bash
curl -X POST "http://localhost:8000/translate/text" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello, how are you?",
       "target_language": "hindi",
       "source_language": "en"
     }'

# Example Response:
{
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "en",
  "target_language": "hindi"
}
```

2. Multi-language translation:
```bash
curl -X POST "http://localhost:8000/translate/multi" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello, how are you?",
       "target_languages": ["hindi", "spanish", "french"],
       "source_language": "en"
     }'

# Example Response:
{
  "translations": {
    "hindi": "नमस्ते, आप कैसे हैं?",
    "spanish": "¿Hola, cómo estás?",
    "french": "Bonjour comment allez-vous?"
  },
  "source_language": "en",
  "original_text": "Hello, how are you?"
}
```

### File Translation

1. Single language file translation:
```bash
curl -X POST "http://localhost:8000/translate/file" \
     -H "X-API-Key: your_api_key" \
     -F "file=@/path/to/your/file.txt" \
     -F "target_language=hindi" \
     -F "source_language=en"

# Example Response:
{
  "job_id": "3cba1695-b45e-4548-9043-14cd321f7975",
  "message": "Translation job started"
}
```

2. Multi-language file translation:
```bash
curl -X POST "http://localhost:8000/translate/file/multi" \
     -H "X-API-Key: your_api_key" \
     -F "file=@/path/to/your/file.txt" \
     -F "target_languages=hindi" \
     -F "target_languages=spanish" \
     -F "target_languages=french" \
     -F "source_language=en"
```

### Job Status and File Download

1. Check translation job status:
```bash
curl -X GET "http://localhost:8000/translation/status/your_job_id" \
     -H "X-API-Key: your_api_key"

# Example Response:
{
  "job_id": "3cba1695-b45e-4548-9043-14cd321f7975",
  "status": "completed",
  "filename": "test.txt",
  "total_languages": 1,
  "processed_languages": 1,
  "current_processing_language": null,
  "error_message": null,
  "created_at": "2024-11-06T08:44:37.645490",
  "updated_at": "2024-11-06T08:44:40.983355",
  "files": [
    {
      "language": "original",
      "status": "completed",
      "download_url": "https://s3.us-east-005.backblazeb2.com/..."
    },
    {
      "language": "hindi",
      "status": "completed",
      "download_url": "https://s3.us-east-005.backblazeb2.com/..."
    }
  ]
}
```

2. Download translated files:
```bash
# Download original file
curl -o original.txt "download_url_from_status_response"

# Download translated file
curl -o translated.txt "download_url_from_status_response"
```

3. Alternative download using API endpoint:
```bash
# Download specific language
curl -X GET "http://localhost:8000/download/job_id?language=hindi" \
     -H "X-API-Key: your_api_key" \
     -o translated.txt

# Get all download URLs
curl -X GET "http://localhost:8000/download/job_id" \
     -H "X-API-Key: your_api_key"
```

## Windows PowerShell Commands

For Windows users, use this format:
```powershell
curl.exe -X POST "http://localhost:8000/translate/file" `
    -H "X-API-Key: your_api_key" `
    -F "file=@C:/path/to/your/file.txt" `
    -F "target_language=hindi" `
    -F "source_language=en"
```

## Limitations
- Maximum 5 target languages per request
- Only .txt files supported
- File size limit: 10MB
- Text chunk size limit: 5000 characters

## Status Codes
- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Invalid API key
- 403: Admin access required
- 404: Resource not found
- 500: Server error

## Tips
1. Always check job status after file translation
2. Use language codes from the `/languages/flat` endpoint
3. Monitor processed_languages vs total_languages for progress
4. Save job_id for status checking
5. Download files as soon as they're ready

## Error Handling
The API returns detailed error messages:
```json
{
  "detail": "Error message here"
}
```

## Support
For issues or questions:
1. Check API documentation at `/docs`
2. Verify API key is active
3. Confirm language codes are correct
4. Check file format and size