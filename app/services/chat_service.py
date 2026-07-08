
from sqlalchemy.orm import Session
from google import genai
from app.core.config import settings
from app.services.search_service import SearchService

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.search_service = SearchService(db)

    def answer_question_from_document(self, document_id: str, question: str) -> str:
        """
        Responde a una pregunta específica basada en el contenido de un documento PDF previamente cargado y procesado.
        1. Obtiene los trozos de texto más relevantes desde la Fase 2.
        2. Construye un prompt con el contexto del documento.
        3. Genera una respuesta exacta usando Gemini.
        """
        relevant_chunks = self.search_service.search_context_for_question(
            document_id=document_id,
            question=question,
            limit=4  
        )

        if not relevant_chunks:
            return "No se encontró información relevante en el documento para responder a esta pregunta."

        context_text = "\n\n".join([
            f"[Fragmento de Página {c['page']}]: {c['content']}" 
            for c in relevant_chunks
        ])

        prompt = f"""
Eres un asistente educativo inteligente para la plataforma StudyRAG. Tu objetivo es responder la duda del estudiante utilizando únicamente el contexto proporcionado del documento PDF.

Instrucciones estrictas:
1. Responde de forma clara, directa y estructurada.
2. Si la respuesta no se encuentra en el contexto proporcionado, di amablemente: "Lo siento, la información para responder a tu pregunta no se encuentra en este documento." No inventes datos.
3. Mantén un tono empático y profesional.

---
CONTEXTO EXTRAÍDO DEL DOCUMENTO:
{context_text}
---

PREGUNTA DEL ESTUDIANTE:
{question}

RESPUESTA INTERACTIVE:
"""

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        return response.text