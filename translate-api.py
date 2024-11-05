from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from deep_translator import GoogleTranslator
import uvicorn
from pydantic import BaseModel
import tempfile
import os
import time
from typing import Optional

app = FastAPI(title="Hindi Translation API")
translator = GoogleTranslator(source='en', target='hi')

class TextTranslation(BaseModel):
    text: str

async def translate_text(text: str, retries: int = 3) -> Optional[str]:
    """Translate text with retry mechanism"""
    for attempt in range(retries):
        try:
            if not text.strip():
                return ""
            # deep_translator has a character limit, so we need to handle long texts
            if len(text) > 5000:
                # Split into smaller chunks at sentence boundaries
                chunks = text.split('. ')
                translated_chunks = []
                current_chunk = ""
                
                for chunk in chunks:
                    if len(current_chunk) + len(chunk) < 5000:
                        current_chunk += chunk + ". "
                    else:
                        if current_chunk:
                            translated_chunks.append(translator.translate(current_chunk))
                        current_chunk = chunk + ". "
                
                if current_chunk:
                    translated_chunks.append(translator.translate(current_chunk))
                
                return " ".join(translated_chunks)
            else:
                return translator.translate(text)
        except Exception as e:
            if attempt == retries - 1:
                raise HTTPException(
                    status_code=500,
                    detail=f"Translation failed after {retries} attempts: {str(e)}"
                )
            time.sleep(2 ** attempt)  # Exponential backoff

async def process_file(file_path: str) -> str:
    """Process a text file and translate its contents"""
    output_path = file_path + "_translated.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as input_file:
            text = input_file.read()
            
        paragraphs = text.split('\n\n')
        translated_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                translated_text = await translate_text(paragraph)
                if translated_text:
                    translated_paragraphs.append(translated_text)
        
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write('\n\n'.join(translated_paragraphs))
            
        return output_path
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )

@app.post("/translate/text")
async def translate_text_endpoint(translation: TextTranslation):
    """
    Translate text from English to Hindi
    
    curl -X POST "http://localhost:8000/translate/text" \
         -H "Content-Type: application/json" \
         -d '{"text": "Hello, how are you?"}'
    """
    try:
        translated_text = await translate_text(translation.text)
        return {"translated_text": translated_text}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

@app.post("/translate/file")
async def translate_file_endpoint(file: UploadFile = File(...)):
    """
    Upload a text file and get back translated version
    
    curl -X POST "http://localhost:8000/translate/file" \
         -F "file=@/path/to/your/file.txt"
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported"
        )
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_path, 'wb') as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Process the file
        output_path = await process_file(temp_path)
        
        # Return the translated file
        return FileResponse(
            output_path,
            media_type='text/plain',
            filename=f"translated_{file.filename}"
        )
    
    finally:
        # Cleanup temporary files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_path + "_translated.txt"):
            os.remove(temp_path + "_translated.txt")
        os.rmdir(temp_dir)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)