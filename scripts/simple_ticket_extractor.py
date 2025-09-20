#!/usr/bin/env python3
"""
Extrator simples de tickets do GLPI.

Extrai dados de tickets do GLPI e salva em CSV.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Adiciona o diretório backend ao path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Imports após modificação do sys.path
from config.settings import get_settings  # noqa: E402

from services.glpi_service import GLPIService  # noqa: E402


def format_ticket_data(ticket: Dict) -> Dict:
    """Formata dados do ticket para CSV."""
    try:
        # Linha longa quebrada para atender limite de 100 caracteres
        created_date = (
            datetime.fromisoformat(
                ticket.get(
                    "date",
                    "").replace(
                    "Z",
                    "+00:00")).strftime("%Y-%m-%d %H:%M:%S") if ticket.get("date") else "")

        return {
            "id": ticket.get("id", ""),
            "name": ticket.get("name", ""),
            "status": ticket.get("status", ""),
            "priority": ticket.get("priority", ""),
            "created_date": created_date,
            "requester": ticket.get("requester", ""),
            "technician": ticket.get("technician", ""),
            "category": ticket.get("category", ""),
            "description": ticket.get("content", "")[:200] + "..."
            if len(ticket.get("content", "")) > 200
            else ticket.get("content", ""),
        }
    except Exception as e:
        print(f"Erro ao formatar ticket {ticket.get('id', 'unknown')}: {e}")
        return {}


def main():
    """Função principal."""
    try:
        settings = get_settings()
        glpi_service = GLPIService(settings)

        print("Iniciando extração de tickets...")

        # Buscar tickets
        tickets = glpi_service.get_tickets()

        if not tickets:
            print("Nenhum ticket encontrado")
            return

        # Preparar dados para CSV
        csv_data = []
        for ticket in tickets:
            formatted_ticket = format_ticket_data(ticket)
            if formatted_ticket:
                csv_data.append(formatted_ticket)

        # Salvar em CSV
        output_file = Path(__file__).parent / "tickets_export.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

        print(f"Tickets exportados para: {output_file}")
        print(f"Total de tickets: {len(csv_data)}")

    except Exception as e:
        print(f"Erro na execução: {e}")
        return 1

    return 0


def process_tickets_batch(tickets: List[Dict]) -> List[Dict]:
    """Processa lote de tickets."""
    processed = []

    for ticket in tickets:
        try:
            formatted = format_ticket_data(ticket)
            if formatted:
                processed.append(formatted)
        except Exception as e:
            print(f"Erro ao processar ticket: {e}")
            continue

    return processed


def save_to_csv(data: List[Dict], filename: str) -> bool:
    """Salva dados em arquivo CSV."""
    try:
        output_path = Path(__file__).parent / filename

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

        print("Dados salvos em CSV com sucesso")
        print("Arquivo criado com sucesso")
        return True

    except Exception as e:
        print(f"Erro ao salvar CSV: {e}")
        return False


if __name__ == "__main__":
    sys.exit(main())
