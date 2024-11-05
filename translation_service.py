# File: translation_service.py
from deep_translator import GoogleTranslator
from fastapi import HTTPException
from typing import Dict, List

# Organized dictionary of supported languages by region
LANGUAGE_REGIONS = {
    "North_America": {
        "English (US)": "en-US",
        "English (Canada)": "en-CA",
        "Spanish (Mexico)": "es-MX"
    },
    "South_America": {
        "Portuguese (Brazil)": "pt-BR",
        "Spanish (Argentina)": "es-AR",
        "Spanish (Chile)": "es-CL",
        "Spanish (Colombia)": "es-CO",
        "Spanish (Peru)": "es-PE",
        "Spanish (Venezuela)": "es-VE"
    },
    "Europe": {
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Spanish (Spain)": "es-ES"
    },
    "India": {
        "Hindi": "hi",
        "Bengali": "bn",
        "Telugu": "te",
        "Marathi": "mr",
        "Tamil": "ta",
        "Urdu": "ur",
        "Gujarati": "gu",
        "Kannada": "kn",
        "Malayalam": "ml",
        "Punjabi": "pa"
    },
    "East_Asia": {
        "Chinese (Simplified)": "zh-CN",
        "Chinese (Traditional)": "zh-TW",
        "Japanese": "ja",
        "Korean": "ko"
    }
}

# Flatten language dictionary for easy lookup
SUPPORTED_LANGUAGES = {
    name.lower().replace(" ", "_"): code
    for region in LANGUAGE_REGIONS.values()
    for name, code in region.items()
}

def get_language_regions() -> Dict[str, Dict[str, str]]:
    """Return languages organized by region"""
    return LANGUAGE_REGIONS

def get_supported_languages() -> Dict[str, str]:
    """Return flat dictionary of supported languages"""
    return SUPPORTED_LANGUAGES

def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> str:
    """
    Translate text to target language
    """
    try:
        # Convert language name to code if full name is provided
        target_lang = target_lang.lower().replace(" ", "_")
        source_lang = source_lang.lower().replace(" ", "_")
        
        target_lang_code = SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        source_lang_code = SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        
        translator = GoogleTranslator(source=source_lang_code, target=target_lang_code)
        
        # Handle long text by splitting if necessary (5000 chars limit)
        if len(text) > 5000:
            chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            return ' '.join(translated_chunks)
        
        return translator.translate(text)
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Translation failed: {str(e)}. Make sure the language code is valid."
        )