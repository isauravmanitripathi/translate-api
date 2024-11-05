# Multi-Language Translation API

A FastAPI-based translation service that supports multiple languages across different regions, including North America, South America, Europe, India, and East Asia. The API provides secure endpoints with API key authentication and admin capabilities for managing API keys.

## Features

- Multi-language translation support with regional variants
- API key authentication
- Admin panel for API key management
- Support for both direct text translation and file uploads
- Automatic language detection
- Comprehensive language support for:
  - North American languages (US English, Canadian English, Mexican Spanish)
  - South American languages (Brazilian Portuguese, regional Spanish variants)
  - European languages (French, German, Italian, Spanish)
  - Indian languages (Hindi, Bengali, Telugu, Marathi, Tamil, etc.)
  - East Asian languages (Chinese - Simplified/Traditional, Japanese, Korean)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd translation-api
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# For Unix/macOS:
source .venv/bin/activate
# For Windows:
.venv\Scripts\activate
```

3. Install required packages:
```bash
pip install fastapi uvicorn python-multipart deep-translator python-dotenv sqlalchemy
```

4. Create a `.env` file in the root directory:
```bash
echo "ADMIN_ACCESS_KEY=your_admin_key_here" > .env
```

## Project Structure

```
translation-api/
├── .env
├── main.py
├── database.py
├── auth.py
├── api_key_manager.py
├── translation_service.py
└── translation_api.db  # Will be created automatically
```

## Running the API

Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

## API Usage

### Authentication

All endpoints require an API key to be passed in the `X-API-Key` header.

### Admin Operations

1. Generate a new API key:
```bash
curl -X POST "http://localhost:8000/admin/generate-key" \
     -H "X-API-Key: your_admin_key_here" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "Test API Key",
       "created_by": "Admin"
     }'
```

2. List all API keys:
```bash
curl -X GET "http://localhost:8000/admin/list-keys" \
     -H "X-API-Key: your_admin_key_here"
```

3. Deactivate an API key:
```bash
curl -X POST "http://localhost:8000/admin/deactivate-key" \
     -H "X-API-Key: your_admin_key_here" \
     -H "Content-Type: application/json" \
     -d '"api_key_to_deactivate"'
```

### Translation Operations

1. Get list of supported languages by region:
```bash
curl -X GET "http://localhost:8000/languages" \
     -H "X-API-Key: your_api_key"
```

2. Get flat list of supported languages:
```bash
curl -X GET "http://localhost:8000/languages/flat" \
     -H "X-API-Key: your_api_key"
```

3. Translate text (with auto language detection):
```bash
curl -X POST "http://localhost:8000/translate/text" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello, how are you?",
       "target_language": "hindi"
     }'
```

4. Translate text (with specified source language):
```bash
curl -X POST "http://localhost:8000/translate/text" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello, how are you?",
       "target_language": "spanish_mexico",
       "source_language": "english_us"
     }'
```

### Example Language Codes

You can use either the full language name (lowercase with underscores) or language codes:

- English (US): `english_us` or `en-US`
- Spanish (Mexico): `spanish_mexico` or `es-MX`
- Hindi: `hindi` or `hi`
- French: `french` or `fr`
- Japanese: `japanese` or `ja`
- Portuguese (Brazil): `portuguese_brazil` or `pt-BR`

## Response Formats

### Successful Translation Response
```json
{
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "english_us",
  "target_language": "hindi"
}
```

### Error Response
```json
{
  "detail": "Translation failed: Invalid language code"
}
```

## Error Handling

The API includes comprehensive error handling for:
- Invalid API keys
- Invalid language codes
- Translation service failures
- Rate limiting
- Server errors

## Development

To add new features or modify the API:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Limitations

- Maximum text length per request: 5000 characters (longer texts are automatically chunked)
- Rate limiting may apply based on the translation service
- Some language pairs might not be directly translatable

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.