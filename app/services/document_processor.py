
import os
from typing import List, Dict, Any
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessorService:
    def __init__(self):
        """
        Inicializa el servicio configurando el divisor de texto (Text Splitter).
        Usamos la estrategia recursiva para dividir el documento respetando los saltos
        de línea y espacios, evitando romper palabras de forma abrupta.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,       
            chunk_overlap=200,     
            length_function=len, 
            separators=["\n\n", "\n", " ", ""] 
        )

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Paso A: Lee el archivo PDF físicamente del disco y extrae el texto por páginas.
        Mantiene el número de página original para cumplir con la regla de poder citar las fuentes.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo en la ruta especificada no existe: {file_path}")

        pages_content = []
        reader = PdfReader(file_path)
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            
            if text and text.strip():
                pages_content.append({
                    "page": page_num,
                    "text": text.strip()
                })
                
        return pages_content

    def create_chunks(self, pages_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Paso B: Toma el texto extraído en el paso anterior y lo divide en fragmentos pequeños.
        Garantiza que cada fragmento final retenga a qué número de página pertenecía originalmente.
        """
        all_chunks = []

        for page_data in pages_content:
            page_number = page_data["page"]
            page_text = page_data["text"]

            chunks_of_page = self.text_splitter.split_text(page_text)

            for chunk in chunks_of_page:
                all_chunks.append({
                    "page": page_number,
                    "content": chunk
                })

        return all_chunks

    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Método Orquestador: Coordina el flujo completo de la Fase 1.
        Recibe la ruta del archivo y devuelve la lista estructurada con los fragmentos y sus páginas.
        """
        extracted_pages = self.extract_text_from_pdf(file_path)
        
        final_chunks = self.create_chunks(extracted_pages)
        
        return final_chunks