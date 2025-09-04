#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check GLPI Field Mapping
Verifica o mapeamento correto dos campos da API GLPI
"""

import json
import sys
from pathlib import Path

import requests

# Adicionar o diretório do backend ao path
backend_path = Path(__file__).parent / "glpi_dashboard" / "backend"
sys.path.insert(0, str(backend_path))


def check_field_mapping():
    """Verifica o mapeamento dos campos"""

    print("🔍 VERIFICANDO MAPEAMENTO DE CAMPOS GLPI")
    print("=" * 50)

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

        # Buscar tickets com todos os campos possíveis
        search_url = f"{GLPI_URL}/search/Ticket"
        search_headers = {
            "App-Token": GLPI_APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }

        # Forçar exibição de muitos campos para entender o mapeamento
        search_params = {
            "criteria[0][field]": "12",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": "6",
            "forcedisplay[0]": "1",  # ID
            "forcedisplay[1]": "2",  # ID (alternativo)
            "forcedisplay[2]": "3",  # Status
            "forcedisplay[3]": "4",  # Nome
            "forcedisplay[4]": "5",  # Conteúdo
            "forcedisplay[5]": "6",  # Prioridade
            "forcedisplay[6]": "7",  # Categoria
            "forcedisplay[7]": "8",  # Tipo
            "forcedisplay[8]": "9",  # Urgência
            "forcedisplay[9]": "10",  # Impacto
            "forcedisplay[10]": "11",  # Data criação
            "forcedisplay[11]": "12",  # Status
            "forcedisplay[12]": "13",  # Data modificação
            "forcedisplay[13]": "14",  # Data fechamento
            "forcedisplay[14]": "15",  # Data criação
            "forcedisplay[15]": "16",  # Data fechamento
            "forcedisplay[16]": "17",  # Solução
            "forcedisplay[17]": "18",  # Tempo ação
            "forcedisplay[18]": "19",  # Técnico
            "forcedisplay[19]": "20",  # Usuário
            "forcedisplay[20]": "21",  # Usuário
            "forcedisplay[21]": "22",  # Tempo resolução
            "range": "0-3",
        }

        response = requests.get(
            search_url, headers=search_headers, params=search_params, timeout=60
        )

        if response.status_code in [200, 206]:
            data = response.json()
            tickets = data.get("data", [])

            print(f"✅ Encontrados {len(tickets)} tickets")

            for i, ticket in enumerate(tickets):
                print(f"\n📋 TICKET {i+1} - MAPEAMENTO DE CAMPOS:")
                print(f"   Dados completos: {json.dumps(ticket, indent=2, ensure_ascii=False)}")

                # Tentar identificar cada campo
                print(f"\n🔍 ANÁLISE DE CAMPOS:")
                for key, value in ticket.items():
                    print(f"   Campo {key}: {value} (tipo: {type(value).__name__})")

                # Tentar identificar campos específicos
                print(f"\n🎯 IDENTIFICAÇÃO DE CAMPOS:")

                # Procurar por ID
                id_fields = [k for k, v in ticket.items() if isinstance(v, int) and v > 1000]
                print(f"   Possíveis IDs: {id_fields}")

                # Procurar por texto longo (conteúdo)
                text_fields = [k for k, v in ticket.items() if isinstance(v, str) and len(v) > 50]
                print(f"   Possíveis conteúdos: {text_fields}")

                # Procurar por datas
                date_fields = [
                    k for k, v in ticket.items() if isinstance(v, str) and "-" in v and ":" in v
                ]
                print(f"   Possíveis datas: {date_fields}")

                # Procurar por números pequenos (prioridade, status)
                small_numbers = [
                    k for k, v in ticket.items() if isinstance(v, int) and 0 <= v <= 10
                ]
                print(f"   Possíveis prioridades/status: {small_numbers}")

                break  # Analisar apenas o primeiro ticket

        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"Resposta: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Função principal"""
    check_field_mapping()


if __name__ == "__main__":
    main()
