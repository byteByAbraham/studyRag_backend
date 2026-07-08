
from typing import List
from google import genai
from google.genai import types
from app.core.config import settings  

class EmbeddingService:

    def __init__(self):
        """
        Inicializa el servicio de embeddings configurando el cliente moderno de GenAI
        usando las variables validadas por Pydantic.
        """
        api_key = settings.GEMINI_API_KEY
        
        if not api_key:
            raise ValueError("No se encontró la clave GEMINI_API_KEY configurada en las configuraciones del sistema.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-embedding-2"

    def generate_embedding(self, text: str) -> List[float]:
        """
        Toma un fragmento de texto plano y llama a la API moderna de Gemini para
        convertirlo en un vector numérico.
        """
        if not text.strip():
            raise ValueError("El texto proporcionado para generar el embedding está vacío.")

        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )
        
        return response.embeddings[0].values