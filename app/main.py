
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router




app = FastAPI( title=settings.PROJECT_NAME, 
            version=settings.VERSION,
            description="Backend con Motor Rag para la aplicación StudyRag academica a través de una API",
            docs_url = "/docs",
            redoc_url = "/redoc",
            openapi_url = f"{settings.API_V1_STR}/openapi.json"
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

app.include_router(api_router, prefix=settings.API_V1_STR)



@app.get("/", tags=["Root"])
async def health_check():
    """
    Verifica que el servicio esté corriendo y devuelve la metadata inicial
    
    """
    return {"status": "ok", 
            "project": settings.PROJECT_NAME, 
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "services": {
                "database": "active",
                "vector_db": "pending",
            }
            }


