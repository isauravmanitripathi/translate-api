# File: translation_service.py

from deep_translator import GoogleTranslator
from fastapi import HTTPException
from typing import Dict, List
import asyncio

# Mapping for special language codes to standard codes
LANGUAGE_CODE_MAPPING = {
    # North America
    "english_us": "en",
    "english_canada": "en",
    "spanish_mexico": "es",
    
    # South America
    "portuguese_brazil": "pt",
    "spanish_argentina": "es",
    "spanish_chile": "es",
    "spanish_colombia": "es",
    "spanish_peru": "es",
    "spanish_venezuela": "es",
    
    # Europe
    "french": "fr",
    "german": "de",
    "italian": "it",
    "spanish_spain": "es",
    
    # India
    "hindi": "hi",
    "bengali": "bn",
    "telugu": "te",
    "marathi": "mr",
    "tamil": "ta",
    "urdu": "ur",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
    
    # East Asia
    "chinese_simplified": "zh-CN",
    "chinese_traditional": "zh-TW",
    "japanese": "ja",
    "korean": "ko"
}

# Organized dictionary of supported languages by region
LANGUAGE_REGIONS = {
    "North_America": {
        "English (US)": "english_us",
        "English (Canada)": "english_canada",
        "Spanish (Mexico)": "spanish_mexico"
    },
    "South_America": {
        "Portuguese (Brazil)": "portuguese_brazil",
        "Spanish (Argentina)": "spanish_argentina",
        "Spanish (Chile)": "spanish_chile",
        "Spanish (Colombia)": "spanish_colombia",
        "Spanish (Peru)": "spanish_peru",
        "Spanish (Venezuela)": "spanish_venezuela"
    },
    "Europe": {
        "French": "french",
        "German": "german",
        "Italian": "italian",
        "Spanish (Spain)": "spanish_spain"
    },
    "India": {
        "Hindi": "hindi",
        "Bengali": "bengali",
        "Telugu": "telugu",
        "Marathi": "marathi",
        "Tamil": "tamil",
        "Urdu": "urdu",
        "Gujarati": "gujarati",
        "Kannada": "kannada",
        "Malayalam": "malayalam",
        "Punjabi": "punjabi"
    },
    "East_Asia": {
        "Chinese (Simplified)": "chinese_simplified",
        "Chinese (Traditional)": "chinese_traditional",
        "Japanese": "japanese",
        "Korean": "korean"
    }
}

def get_language_regions() -> Dict[str, Dict[str, str]]:
    """Return languages organized by region"""
    return LANGUAGE_REGIONS

def get_supported_languages() -> Dict[str, str]:
    """Return flat dictionary of supported languages"""
    return LANGUAGE_CODE_MAPPING

def get_standard_language_code(lang_code: str) -> str:
    """Convert our custom language codes to standard codes"""
    if lang_code == 'auto':
        return 'auto'
    
    # First, try to get from our mapping
    standard_code = LANGUAGE_CODE_MAPPING.get(lang_code.lower())
    if standard_code:
        return standard_code
        
    # If not in our mapping, return as is (might be a direct language code)
    return lang_code.lower()

async def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> str:
    """
    Translate text to target language
    """
    try:
        # Convert to standard language codes
        target_lang_code = get_standard_language_code(target_lang)
        source_lang_code = get_standard_language_code(source_lang)
        
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

async def translate_text_to_multiple_languages(
    text: str, 
    target_languages: List[str], 
    source_lang: str = 'auto'
) -> Dict[str, str]:
    """
    Translate text to multiple target languages simultaneously
    """
    if len(target_languages) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 target languages are allowed per request"
        )
    
    try:
        # Convert source language to standard code
        source_lang_code = get_standard_language_code(source_lang)
        
        translations = {}
        tasks = []
        
        async def translate_single(target_lang: str) -> tuple:
            try:
                target_lang_code = get_standard_language_code(target_lang)
                translator = GoogleTranslator(source=source_lang_code, target=target_lang_code)
                
                if len(text) > 5000:
                    chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
                    translated_chunks = [translator.translate(chunk) for chunk in chunks]
                    translated_text = ' '.join(translated_chunks)
                else:
                    translated_text = translator.translate(text)
                    
                return target_lang, translated_text
            except Exception as e:
                return target_lang, f"Translation failed for {target_lang}: {str(e)}"
        
        # Create tasks for all target languages
        tasks = [translate_single(lang) for lang in target_languages]
        results = await asyncio.gather(*tasks)
        
        # Organize results
        translations = {lang: text for lang, text in results}
        return translations
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Translation failed: {str(e)}"
        )