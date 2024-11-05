# Multi-Language Translation API

A robust FastAPI-based translation service that supports multiple languages across different regions. The API provides secure endpoints with API key authentication and includes features for both single and multiple language translations. It supports languages from North America, South America, Europe, India, and East Asia.

## Features

- Single and multi-language translation support (up to 5 languages at once)
- Regional language variants
- API key authentication system
- Admin panel for API key management
- Automatic language detection
- Support for long text translations
- Comprehensive language coverage:
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
├── .env                    # Environment variables
├── main.py                # Main FastAPI application
├── database.py            # Database models and configuration
├── auth.py               # Authentication logic
├── api_key_manager.py    # API key management
├── translation_service.py # Translation logic
└── translation_api.db    # SQLite database (auto-created)
```

## Running the API

Start the server:
```bash
python main.py
```

The API will be running at:
- API Endpoints: `http://localhost:8000`
- Interactive Documentation: `http://localhost:8000/docs`

## API Usage Guide

### Language Information

1. Get list of supported languages by region:
```bash
curl -X GET "http://localhost:8000/languages" \
     -H "X-API-Key: your_api_key"
```

2. Get flat list of all supported languages:
```bash
curl -X GET "http://localhost:8000/languages/flat" \
     -H "X-API-Key: your_api_key"
```

### Translation Endpoints

1. Single Language Translation:
```bash
curl -X POST "http://localhost:8000/translate/text" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello, how are you?",
       "target_language": "hindi",
       "source_language": "english_us"
     }'
```

2. Multi-Language Translation (up to 5 languages):
```bash
curl -X POST "http://localhost:8000/translate/multi" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello, how are you?",
       "target_languages": ["hindi", "spanish", "french", "japanese", "german"],
       "source_language": "english_us"
     }'
```

3. Auto-detect source language:
```bash
curl -X POST "http://localhost:8000/translate/text" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Bonjour, comment allez-vous?",
       "target_language": "hindi"
     }'
```

### Admin Operations

1. Generate new API key:
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

## Response Formats

### Single Language Translation Response
```json
{
  "translated_text": "नमस्ते, आप कैसे हैं?",
  "source_language": "english_us",
  "target_language": "hindi"
}
```

### Multi-Language Translation Response
```json
{
  "translations": {
    "hindi": "नमस्ते, आप कैसे हैं?",
    "spanish": "¡Hola! ¿Cómo estás?",
    "french": "Bonjour, comment allez-vous?",
    "japanese": "こんにちは、お元気ですか？",
    "german": "Hallo, wie geht es dir?"
  },
  "source_language": "english_us",
  "original_text": "Hello, how are you?"
}
```

## Supported Languages

### Example Language Codes
You can use either the full language name (lowercase with underscores) or language codes:

North America:
- English (US): `english_us` or `en-US`
- English (Canada): `english_canada` or `en-CA`
- Spanish (Mexico): `spanish_mexico` or `es-MX`

Europe:
- French: `french` or `fr`
- German: `german` or `de`
- Italian: `italian` or `it`
- Spanish (Spain): `spanish_spain` or `es-ES`

India:
- Hindi: `hindi` or `hi`
- Bengali: `bengali` or `bn`
- Telugu: `telugu` or `te`
- Tamil: `tamil` or `ta`

East Asia:
- Japanese: `japanese` or `ja`
- Korean: `korean` or `ko`
- Chinese (Simplified): `chinese_simplified` or `zh-CN`
- Chinese (Traditional): `chinese_traditional` or `zh-TW`

## Error Handling

The API includes comprehensive error handling for:
- Invalid API keys
- Invalid language codes
- Maximum language limit exceeded (multi-translation)
- Translation service failures
- Server errors

Common error responses:
```json
{
  "detail": "Invalid API key"
}
```
```json
{
  "detail": "Maximum 5 target languages are allowed per request"
}
```

## Limitations

- Maximum 5 target languages per multi-translation request
- Maximum text length: 5000 characters per chunk (automatically handled)
- Rate limiting may apply based on the translation service
- Some language pairs might not be directly translatable

## Security

- All endpoints require API key authentication
- Admin operations require special admin API key
- API keys can be deactivated if compromised
- Database is SQLite with proper security practices

## Support

For support:
1. Check the API documentation at `/docs`
2. Ensure you're using supported language codes
3. Verify your API key is active
4. Contact support if issues persist

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For the latest updates and more information, please visit our [GitHub repository](repository-url).