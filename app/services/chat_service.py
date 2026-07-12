import json
from typing import Generator

from sqlalchemy.orm import Session
from google import genai
from app.core.config import settings
from app.services.search_service import SearchService

class ChatService:

    def __init__(self, db: Session):
        self.db = db
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.search_service = SearchService(db)

    def answer_question_stream(self, document_id: str, question: str) -> Generator[str, None, None]:
        """
        Genera una respuesta a una pregunta basada en el contenido de un documento, utilizando streaming.
        1. Obtiene los trozos de texto más relevantes.
        2. Envía las páginas fuente inmediatamente como metadatos SSE (con acentos nativos).
        3. Transmite el texto generado por Gemini palabra por palabra.
        """
        relevant_chunks = self.search_service.search_context_for_question(
            document_id=document_id,
            question=question,
            limit=4  
        )

        if not relevant_chunks:
            yield "data: " + json.dumps({'error': 'No se encontró información relevante.'}, ensure_ascii=False) + "\n\n"
            return

        pages_cited = sorted(list({chunk['page'] for chunk in relevant_chunks}))
        yield "data: " + json.dumps({'pages_cited': pages_cited}, ensure_ascii=False) + "\n\n"
        
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

        response_stream = self.client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        for chunk in response_stream:
            if chunk.text:
                yield "data: " + json.dumps({'text': chunk.text}, ensure_ascii=False) + "\n\n"
                