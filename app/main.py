
import os 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "StudyRag API")
VERSION = os.getenv("VERSION", "1.0.0")
API_V1_STR = os.getenv("API_V1_STR", "/api/v1")

app = FastAPI( title=PROJECT_NAME, 
            version=VERSION,
            description="Backend con Motor Rag para la aplicación StudyRag academica a través de una API",
            docs_url = "/docs",
            redoc_url = "/redoc",
            openapi_url = f"{API_V1_STR}/openapi.json"
            )

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def health_check():
    """
    Verifica que el servicio esté corriendo y devuelve la metadata inicial
    
    """
    return {"status": "ok", 
            "project": PROJECT_NAME, 
            "version": VERSION,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "services": {
                "database": "pending",
                "vector_db": "pending",
            }
            }


