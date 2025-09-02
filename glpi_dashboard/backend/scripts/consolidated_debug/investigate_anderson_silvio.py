#!/usr/bin/env python3
"""
Script para investigar detalhadamente os tickets de Anderson e Silvio
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'glpi_dashboard', 'backend'))

from services.glpi_service import GLPIService
from config.settings import get_config

def investigate_technician_tickets():
    """Investiga detalhadamente os tickets dos técnicos Anderson e Silvio"""
    
    print("=== INVESTIGAÇÃO DETALHADA DOS TICKETS ===\n")
    
    # Configurar ambiente
    os.environ['FLASK_ENV'] = 'development'
    config = get_config()
    
    # Inicializar serviço GLPI
    glpi_service = GLPIService()
    
    # IDs dos técnicos
    anderson_id = 696
    silvio_id = 32
    
    print(f"Investigando técnicos:")
    print(f"- Anderson (ID: {anderson_id})")
    print(f"- Silvio (ID: {silvio_id})\n")
    
    # 1. Verificar se os usuários existem no GLPI
    print("1. VERIFICANDO EXISTÊNCIA DOS USUÁRIOS NO GLPI")
    print("=" * 50)
    
    for tech_id, tech_name in [(anderson_id, "Anderson"), (silvio_id, "Silvio")]:
        try:
            response = glpi_service._make_authenticated_request(
                "GET", f"{glpi_service.glpi_url}/User/{tech_id}"
            )
            
            if response and response.ok:
                user_data = response.json()
                print(f"✓ {tech_name} (ID: {tech_id}) encontrado:")
                print(f"  - Nome: {user_data.get('name', 'N/A')}")
                print(f"  - Realname: {user_data.get('realname', 'N/A')}")
                print(f"  - Firstname: {user_data.get('firstname', 'N/A')}")
                print(f"  - Ativo: {user_data.get('is_active', 'N/A')}")
                print(f"  - Entidade: {user_data.get('entities_id', 'N/A')}")
            else:
                status = response.status_code if response else "No response"
                print(f"✗ {tech_name} (ID: {tech_id}) NÃO encontrado (Status: {status})")
        except Exception as e:
            print(f"✗ Erro ao buscar {tech_name} (ID: {tech_id}): {e}")
        print()
    
    # 2. Buscar tickets com diferentes critérios
    print("2. BUSCANDO TICKETS COM DIFERENTES CRITÉRIOS")
    print("=" * 50)
    
    search_criteria = [
        ("users_id_assign", "Atribuído diretamente"),
        ("users_id_recipient", "Solicitante"),
        ("users_id_lastupdater", "Último atualizador")
    ]
    
    for tech_id, tech_name in [(anderson_id, "Anderson"), (silvio_id, "Silvio")]:
        print(f"\n--- {tech_name} (ID: {tech_id}) ---")
        
        for field, description in search_criteria:
            try:
                # Buscar tickets com critério específico
                search_params = {
                    "criteria[0][field]": field,
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(tech_id),
                    "range": "0-10"
                }
                
                response = glpi_service._make_authenticated_request(
                    "GET", f"{glpi_service.glpi_url}/search/Ticket", params=search_params
                )
                
                if response and response.ok:
                    tickets = response.json()
                    count = tickets.get('totalcount', 0)
                    print(f"  {description}: {count} tickets")
                    
                    if count > 0 and 'data' in tickets and len(tickets['data']) > 0:
                        print(f"    Primeiros tickets:")
                        for i, ticket in enumerate(tickets['data'][:3]):
                            print(f"      {i+1}. ID: {ticket.get('2', 'N/A')} - Título: {ticket.get('1', 'N/A')[:50]}...")
                else:
                    print(f"  {description}: 0 tickets")
                    
            except Exception as e:
                print(f"  Erro ao buscar por {description}: {e}")
    
    # 3. Verificar grupos dos técnicos
    print("\n3. VERIFICANDO GRUPOS DOS TÉCNICOS")
    print("=" * 50)
    
    for tech_id, tech_name in [(anderson_id, "Anderson"), (silvio_id, "Silvio")]:
        try:
            # Buscar grupos do usuário
            response = glpi_service._make_authenticated_request(
                "GET", f"{glpi_service.glpi_url}/User/{tech_id}/Group_User"
            )
            
            if response and response.ok:
                groups = response.json()
                if groups:
                    print(f"\n{tech_name} (ID: {tech_id}) pertence aos grupos:")
                    for group in groups:
                        group_id = group.get('groups_id')
                        if group_id:
                            # Buscar detalhes do grupo
                            group_response = glpi_service._make_authenticated_request(
                                "GET", f"{glpi_service.glpi_url}/Group/{group_id}"
                            )
                            if group_response and group_response.ok:
                                group_details = group_response.json()
                                print(f"  - Grupo ID: {group_id} - Nome: {group_details.get('name', 'N/A')}")
                else:
                    print(f"\n{tech_name} (ID: {tech_id}) não pertence a nenhum grupo")
            else:
                print(f"\n{tech_name} (ID: {tech_id}) - Erro ao buscar grupos")
                
        except Exception as e:
            print(f"\nErro ao buscar grupos de {tech_name}: {e}")
    
    # 4. Buscar tickets por grupos
    print("\n4. BUSCANDO TICKETS POR GRUPOS")
    print("=" * 50)
    
    for tech_id, tech_name in [(anderson_id, "Anderson"), (silvio_id, "Silvio")]:
        try:
            # Buscar grupos do usuário
            response = glpi_service._make_authenticated_request(
                "GET", f"{glpi_service.glpi_url}/User/{tech_id}/Group_User"
            )
            
            if response and response.ok:
                groups = response.json()
                if groups:
                    print(f"\n{tech_name} - Tickets por grupo:")
                    for group in groups:
                        group_id = group.get('groups_id')
                        if group_id:
                            # Buscar tickets atribuídos ao grupo
                            search_params = {
                                "criteria[0][field]": "groups_id_assign",
                                "criteria[0][searchtype]": "equals",
                                "criteria[0][value]": str(group_id),
                                "range": "0-5"
                            }
                            
                            tickets_response = glpi_service._make_authenticated_request(
                                "GET", f"{glpi_service.glpi_url}/search/Ticket", params=search_params
                            )
                            
                            if tickets_response and tickets_response.ok:
                                tickets = tickets_response.json()
                                count = tickets.get('totalcount', 0)
                                print(f"  Grupo {group_id}: {count} tickets")
                            else:
                                print(f"  Grupo {group_id}: 0 tickets")
                            
        except Exception as e:
            print(f"Erro ao buscar tickets por grupos de {tech_name}: {e}")
    
    # 5. Verificar tickets recentes (últimos 30 dias)
    print("\n5. VERIFICANDO TICKETS RECENTES (ÚLTIMOS 30 DIAS)")
    print("=" * 50)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for tech_id, tech_name in [(anderson_id, "Anderson"), (silvio_id, "Silvio")]:
        try:
            search_params = {
                "criteria[0][field]": "users_id_assign",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(tech_id),
                "criteria[1][field]": "date",
                "criteria[1][searchtype]": "morethan",
                "criteria[1][value]": start_date.strftime("%Y-%m-%d"),
                "range": "0-10"
            }
            
            response = glpi_service._make_authenticated_request(
                "GET", f"{glpi_service.glpi_url}/search/Ticket", params=search_params
            )
            
            if response and response.ok:
                tickets = response.json()
                count = tickets.get('totalcount', 0)
                print(f"{tech_name}: {count} tickets nos últimos 30 dias")
                
                if count > 0 and 'data' in tickets:
                    print(f"  Tickets encontrados:")
                    for i, ticket in enumerate(tickets['data'][:5]):
                        print(f"    {i+1}. ID: {ticket.get('2', 'N/A')} - Data: {ticket.get('15', 'N/A')}")
            else:
                print(f"{tech_name}: 0 tickets nos últimos 30 dias")
                
        except Exception as e:
            print(f"Erro ao buscar tickets recentes de {tech_name}: {e}")
    
    print("\n=== INVESTIGAÇÃO CONCLUÍDA ===\n")

if __name__ == "__main__":
    investigate_technician_tickets()