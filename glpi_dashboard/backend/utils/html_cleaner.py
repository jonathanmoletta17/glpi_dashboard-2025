# -*- coding: utf-8 -*-
import html
import re
from typing import Optional


def clean_html_content(text: Optional[str]) -> str:
    """
    Decodifica entidades HTML e remove tags HTML usando apenas bibliotecas nativas do Python.
    
    Esta função substitui o HTMLDecoder.clean_html_content() com uma implementação mais simples
    que usa apenas html.unescape() e regex básico para limpeza de HTML.
    
    Args:
        text: Texto com entidades e tags HTML
        
    Returns:
        Texto limpo sem HTML
    """
    if not text or not isinstance(text, str):
        return ""
    
    try:
        # Decodificar entidades HTML usando biblioteca nativa
        decoded = html.unescape(text)
        
        # Remover tags HTML com regex simples
        clean_text = re.sub(r'<[^>]*>', '', decoded)
        
        # Limpar espaços extras e quebras de linha
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
        
    except Exception:
        # Se houver qualquer erro, retornar o texto original
        return text