import html
import re
from typing import Any, Dict, List, Union


class HTMLDecoder:
    """
    Utilitário para decodificar entidades HTML em dados do GLPI.
    
    O GLPI retorna dados com entidades HTML codificadas (ex: &#60; para <, &#62; para >)
    que precisam ser decodificadas para exibição correta no frontend.
    """
    
    @staticmethod
    def decode_html_entities(text: str) -> str:
        """
        Decodifica entidades HTML em uma string.
        
        Args:
            text: String com entidades HTML codificadas
            
        Returns:
            String com entidades HTML decodificadas
        """
        if not isinstance(text, str):
            return text
            
        # Decodifica entidades HTML numéricas e nomeadas
        decoded = html.unescape(text)
        
        # Decodifica entidades numéricas específicas que podem não ser capturadas
        # pelo html.unescape (como &#60; e &#62;)
        numeric_entities = {
            '&#60;': '<',
            '&#62;': '>',
            '&#38;': '&',
            '&#34;': '"',
            '&#39;': "'",
            '&#160;': ' ',  # non-breaking space
        }
        
        for entity, char in numeric_entities.items():
            decoded = decoded.replace(entity, char)
            
        return decoded
    
    @staticmethod
    def decode_ticket_data(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decodifica entidades HTML em dados de um ticket.
        
        Args:
            ticket_data: Dicionário com dados do ticket
            
        Returns:
            Dicionário com entidades HTML decodificadas
        """
        if not isinstance(ticket_data, dict):
            return ticket_data
            
        decoded_data = ticket_data.copy()
        
        # Campos que comumente contêm HTML
        html_fields = ['description', 'title', 'content', 'entities_id', 'name']
        
        for field in html_fields:
            if field in decoded_data and isinstance(decoded_data[field], str):
                decoded_data[field] = HTMLDecoder.decode_html_entities(decoded_data[field])
                
        return decoded_data
    
    @staticmethod
    def decode_tickets_list(tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Decodifica entidades HTML em uma lista de tickets.
        
        Args:
            tickets: Lista de dicionários com dados dos tickets
            
        Returns:
            Lista com entidades HTML decodificadas
        """
        if not isinstance(tickets, list):
            return tickets
            
        return [HTMLDecoder.decode_ticket_data(ticket) for ticket in tickets]
    
    @staticmethod
    def decode_nested_data(data: Union[Dict, List, str, Any]) -> Union[Dict, List, str, Any]:
        """
        Decodifica entidades HTML recursivamente em estruturas de dados aninhadas.
        
        Args:
            data: Dados que podem conter entidades HTML
            
        Returns:
            Dados com entidades HTML decodificadas
        """
        if isinstance(data, str):
            return HTMLDecoder.decode_html_entities(data)
        elif isinstance(data, dict):
            return {key: HTMLDecoder.decode_nested_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [HTMLDecoder.decode_nested_data(item) for item in data]
        else:
            return data