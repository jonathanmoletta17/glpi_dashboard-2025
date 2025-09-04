#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Tickets With Solutions
Busca tickets que tenham soluções
"""

import json
import sys
from pathlib import Path

import requests

# Adicionar o diretório do backend ao path
backend_path = Path(__file__).parent / "glpi_dashboard" / "backend"
sys.path.insert(0, str(backend_path))


def find_tickets_with_solutions():
    """Busca tickets que tenham soluções"""

    print("🔍 BUSCANDO TICKETS COM SOLUÇÕES")
    print("=" * 40)

    try:
        from config.settings import get_config

        config = get_config()

        # Configurações do GLPI
        GLPI_URL = config.GLPI_URL
        GLPI_APP_TOKEN = config.GLPI_APP_TOKEN
        GLPI_USER_TOKEN = config.GLPI_USER_TOKEN

        # Iniciar sessão
        session_url = f"{GLPI_URL}/initSession"
        headers = {
            "App-Token": GLPI_APP_TOKEN,
            "Authorization": f"user_token {GLPI_USER_TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.get(session_url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Erro na sessão: {response.status_code}")
            return

        session_data = response.json()
        session_token = session_data.get("session_token")

        # Buscar tickets com soluções
        search_url = f"{GLPI_URL}/search/Ticket"
        search_headers = {
            "App-Token": GLPI_APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }

        # Tentar diferentes critérios para encontrar tickets com soluções
        search_params = {
            "criteria[0][field]": "12",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",
            "criteria[1][field]": "17",  # Solução
            "criteria[1][searchtype]": "notcontains",
            "criteria[1][value]": "",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "4",  # Nome
            "forcedisplay[2]": "5",  # Conteúdo
            "forcedisplay[3]": "17",  # Solução
            "range": "0-20",
        }

        response = requests.get(
            search_url, headers=search_headers, params=search_params, timeout=60
        )

        if response.status_code in [200, 206]:
            data = response.json()
            tickets = data.get("data", [])
            total = data.get("totalcount", 0)

            print(f"✅ Encontrados {len(tickets)} tickets (Total: {total})")

            tickets_with_solutions = []

            for i, ticket in enumerate(tickets):
                ticket_id = ticket.get("2", "N/A")
                name = ticket.get("4", "N/A")
                content = ticket.get("5", "N/A")
                solution = ticket.get("17", "N/A")

                print(f"\n📋 TICKET {i+1}:")
                print(f"   ID: {ticket_id}")
                print(f"   Nome: {name[:50]}...")
                print(f"   Conteúdo: {content[:50]}...")
                print(f"   Solução: {solution[:50]}...")

                # Verificar se tem solução
                if solution and str(solution).strip() != "" and str(solution) != "N/A":
                    print(f"   ✅ TEM SOLUÇÃO!")
                    tickets_with_solutions.append(ticket_id)
                else:
                    print(f"   ❌ SEM SOLUÇÃO")

            print(f"\n📊 RESUMO:")
            print(f"   Tickets com soluções: {len(tickets_with_solutions)}")
            print(f"   IDs com soluções: {tickets_with_solutions}")

            if tickets_with_solutions:
                print(f"\n🔍 TESTANDO PRIMEIRO TICKET COM SOLUÇÃO:")
                test_ticket_id = tickets_with_solutions[0]
                print(f"   Testando ticket ID: {test_ticket_id}")

                # Buscar ticket individual
                item_url = f"{GLPI_URL}/Ticket/{test_ticket_id}"
                item_headers = {
                    "App-Token": GLPI_APP_TOKEN,
                    "Session-Token": session_token,
                    "Content-Type": "application/json",
                }

                item_response = requests.get(item_url, headers=item_headers, timeout=30)

                if item_response.status_code == 200:
                    ticket_data = item_response.json()
                    solution = ticket_data.get("solution", "")
                    print(f"   Solução encontrada: {solution[:100]}...")
                    print(f"   Tamanho da solução: {len(str(solution))}")
                else:
                    print(f"   ❌ Erro ao buscar ticket individual: {item_response.status_code}")

        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"Resposta: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Função principal"""
    find_tickets_with_solutions()


if __name__ == "__main__":
    main()
