from gtts import gTTS
import os
from langdetect import detect
import sys
from datetime import datetime

def detect_language(text):
    """
    Detect the language of the text
    Returns language code compatible with gTTS
    """
    try:
        # Detect language
        lang = detect(text)
        # Map some common language codes that might differ
        lang_map = {
            'zh-cn': 'zh-CN',
            'zh-tw': 'zh-TW',
            'zh': 'zh-CN'
        }
        return lang_map.get(lang, lang)
    except:
        # Default to English if detection fails
        return 'en'

def convert_text_file_to_speech(input_file_path):
    """
    Convert text file content to speech
    Args:
        input_file_path: Path to the input text file
    """
    try:
        # Check if file exists
        if not os.path.exists(input_file_path):
            print(f"Error: File '{input_file_path}' not found!")
            return

        # Read the text file
        print(f"Reading file: {input_file_path}")
        with open(input_file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        if not text.strip():
            print("Error: File is empty!")
            return

        # Detect language
        language = detect_language(text)
        print(f"Detected language: {language}")

        # Create output filename based on input filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file = f"{base_name}_{timestamp}.mp3"

        # Convert to speech
        print("Converting text to speech...")
        tts = gTTS(text=text, lang=language)
        
        # Save the audio file
        print(f"Saving audio file as: {output_file}")
        tts.save(output_file)
        
        print("\nConversion completed successfully!")
        print(f"Output file: {os.path.abspath(output_file)}")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

def main():
    # Get file path from user
    while True:
        file_path = input("\nPlease enter the path to your text file (or 'q' to quit): ").strip()
        
        if file_path.lower() == 'q':
            print("Goodbye!")
            break
            
        convert_text_file_to_speech(file_path)
        print("\n" + "="*50)

if __name__ == "__main__":
    # Print welcome message
    print("="*50)
    print("Text File to Speech Converter")
    print("This program will convert your text file to an MP3 audio file.")
    print("Supported languages will be automatically detected.")
    print("="*50)
    
    main()