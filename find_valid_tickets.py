#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Valid Tickets
Encontra tickets válidos para análise
"""

import json
import sys
from pathlib import Path

import requests

# Adicionar o diretório do backend ao path
backend_path = Path(__file__).parent / "glpi_dashboard" / "backend"
sys.path.insert(0, str(backend_path))


def find_valid_tickets():
    """Encontra tickets válidos"""

    print("🔍 BUSCANDO TICKETS VÁLIDOS")
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

        # Buscar tickets em lotes pequenos
        search_url = f"{GLPI_URL}/search/Ticket"
        search_headers = {
            "App-Token": GLPI_APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }

        search_params = {
            "criteria[0][field]": "12",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",
            "forcedisplay[0]": "2",  # ID
            "forcedisplay[1]": "4",  # Nome
            "forcedisplay[2]": "5",  # Conteúdo
            "forcedisplay[3]": "17",  # Solução
            "range": "0-10",
        }

        response = requests.get(
            search_url, headers=search_headers, params=search_params, timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            tickets = data.get("data", [])
            total = data.get("totalcount", 0)

            print(f"✅ Encontrados {len(tickets)} tickets (Total: {total})")

            for i, ticket in enumerate(tickets[:5]):  # Mostrar apenas os primeiros 5
                ticket_id = ticket.get("2", "N/A")
                name = ticket.get("4", "N/A")
                content = ticket.get("5", "N/A")
                solution = ticket.get("17", "N/A")

                print(f"\n📋 TICKET {i+1}:")
                print(f"   ID: {ticket_id}")
                print(f"   Nome: {name[:100]}...")
                print(f"   Conteúdo: {content[:100]}...")
                print(f"   Solução: {solution[:100]}...")
                print(f"   Solução vazia: {not solution or str(solution).strip() == ''}")

                # Verificar se tem solução
                if solution and str(solution).strip() != "":
                    print(f"   ✅ TEM SOLUÇÃO - Pode ser analisado")
                else:
                    print(f"   ❌ SEM SOLUÇÃO - Será rejeitado")

            # Mostrar alguns IDs para teste
            print(f"\n🔍 IDs PARA TESTE:")
            for ticket in tickets[:3]:
                ticket_id = ticket.get("2", "N/A")
                print(f"   Ticket ID: {ticket_id}")

        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"Resposta: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Função principal"""
    find_valid_tickets()


if __name__ == "__main__":
    main()
