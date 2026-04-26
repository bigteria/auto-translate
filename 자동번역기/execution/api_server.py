from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from execution.translator_engine import TranslatorEngine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Automatic Translator API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from 'web' directory
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/")
async def read_index():
    return FileResponse('web/index.html')

engine = TranslatorEngine()

class TranslationRequest(BaseModel):
    text: str

@app.post("/translate")
async def translate_text(request: TranslationRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    result = engine.translate(request.text)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.get("/health")
async def health_check():
    return {"status": "ok", "kb_size": len(engine.kb_data)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
