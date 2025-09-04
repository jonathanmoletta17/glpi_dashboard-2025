#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search Solutions Alternative
Busca soluções em endpoints alternativos do GLPI
"""

import requests
import json
import sys
from pathlib import Path

# Adicionar o diretório do backend ao path
backend_path = Path(__file__).parent / "glpi_dashboard" / "backend"
sys.path.insert(0, str(backend_path))

def search_solutions_alternative():
    """Busca soluções em endpoints alternativos"""
    
    print("🔍 BUSCANDO SOLUÇÕES EM ENDPOINTS ALTERNATIVOS")
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
            'App-Token': GLPI_APP_TOKEN,
            'Authorization': f'user_token {GLPI_USER_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(session_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erro na sessão: {response.status_code}")
            return
        
        session_data = response.json()
        session_token = session_data.get('session_token')
        
        # Testar com um ticket específico
        test_ticket_id = "3028"
        
        print(f"🔍 Testando ticket ID: {test_ticket_id}")
        
        # 1. Buscar ticket individual completo
        print(f"\n1️⃣ BUSCANDO TICKET INDIVIDUAL COMPLETO:")
        item_url = f"{GLPI_URL}/Ticket/{test_ticket_id}"
        item_headers = {
            'App-Token': GLPI_APP_TOKEN,
            'Session-Token': session_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(item_url, headers=item_headers, timeout=30)
        
        if response.status_code == 200:
            ticket_data = response.json()
            print(f"   ✅ Ticket encontrado")
            print(f"   Campos disponíveis: {list(ticket_data.keys())}")
            
            # Verificar campos que podem conter soluções
            solution_fields = ['solution', 'content', 'description', 'comment', 'followup', 'note']
            for field in solution_fields:
                if field in ticket_data:
                    value = ticket_data[field]
                    print(f"   Campo '{field}': {value}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
        
        # 2. Buscar followups do ticket
        print(f"\n2️⃣ BUSCANDO FOLLOWUPS:")
        followup_url = f"{GLPI_URL}/Ticket/{test_ticket_id}/ITILFollowup"
        followup_headers = {
            'App-Token': GLPI_APP_TOKEN,
            'Session-Token': session_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(followup_url, headers=followup_headers, timeout=30)
        
        if response.status_code == 200:
            followups = response.json()
            print(f"   ✅ Followups encontrados: {len(followups)}")
            for i, followup in enumerate(followups):
                print(f"   Followup {i+1}: {followup}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
        
        # 3. Buscar soluções ITIL
        print(f"\n3️⃣ BUSCANDO SOLUÇÕES ITIL:")
        solution_url = f"{GLPI_URL}/Ticket/{test_ticket_id}/ITILSolution"
        solution_headers = {
            'App-Token': GLPI_APP_TOKEN,
            'Session-Token': session_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(solution_url, headers=solution_headers, timeout=30)
        
        if response.status_code == 200:
            solutions = response.json()
            print(f"   ✅ Soluções ITIL encontradas: {len(solutions)}")
            for i, solution in enumerate(solutions):
                print(f"   Solução {i+1}: {solution}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
        
        # 4. Buscar tarefas do ticket
        print(f"\n4️⃣ BUSCANDO TAREFAS:")
        task_url = f"{GLPI_URL}/Ticket/{test_ticket_id}/TicketTask"
        task_headers = {
            'App-Token': GLPI_APP_TOKEN,
            'Session-Token': session_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(task_url, headers=task_headers, timeout=30)
        
        if response.status_code == 200:
            tasks = response.json()
            print(f"   ✅ Tarefas encontradas: {len(tasks)}")
            for i, task in enumerate(tasks):
                print(f"   Tarefa {i+1}: {task}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
        
        # 5. Buscar validações do ticket
        print(f"\n5️⃣ BUSCANDO VALIDAÇÕES:")
        validation_url = f"{GLPI_URL}/Ticket/{test_ticket_id}/TicketValidation"
        validation_headers = {
            'App-Token': GLPI_APP_TOKEN,
            'Session-Token': session_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(validation_url, headers=validation_headers, timeout=30)
        
        if response.status_code == 200:
            validations = response.json()
            print(f"   ✅ Validações encontradas: {len(validations)}")
            for i, validation in enumerate(validations):
                print(f"   Validação {i+1}: {validation}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
        
        # 6. Buscar histórico de mudanças
        print(f"\n6️⃣ BUSCANDO HISTÓRICO DE MUDANÇAS:")
        history_url = f"{GLPI_URL}/Ticket/{test_ticket_id}/TicketLog"
        history_headers = {
            'App-Token': GLPI_APP_TOKEN,
            'Session-Token': session_token,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(history_url, headers=history_headers, timeout=30)
        
        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ Histórico encontrado: {len(history)}")
            for i, log in enumerate(history):
                print(f"   Log {i+1}: {log}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
        
        print(f"\n📊 RESUMO DA BUSCA:")
        print(f"   Verificados 6 endpoints diferentes")
        print(f"   Ticket ID: {test_ticket_id}")
        print(f"   Objetivo: Encontrar onde estão as soluções")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    search_solutions_alternative()

if __name__ == "__main__":
    main()
