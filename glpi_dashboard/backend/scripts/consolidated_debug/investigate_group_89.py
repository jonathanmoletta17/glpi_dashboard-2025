#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar o grupo ID 89 (N1) no GLPI
"""

import json
from datetime import datetime
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'glpi_dashboard', 'backend'))

from config.settings import Config
from services.glpi_service import GLPIService

def main():
    results = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "group_investigation": {},
        "ticket_search_methods": {},
        "sample_tickets": []
    }
    
    try:
        print("🔍 Investigando Grupo ID 89 (N1) no GLPI")
        print("=" * 50)
        
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        glpi_service.discover_field_ids()
        
        print(f"📊 Field IDs: {glpi_service.field_ids}")
        print()
        
        # 1. Verificar se o grupo 89 existe
        print("🔍 1. Verificando se o grupo ID 89 existe:")
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/Group/89"
        )
        
        if response and response.ok:
            group_data = response.json()
            print(f"   ✅ Grupo encontrado: {group_data.get('name', 'N/A')}")
            results["group_investigation"]["group_89"] = {
                "exists": True,
                "data": group_data
            }
        else:
            print(f"   ❌ Grupo não encontrado (HTTP {response.status_code if response else 'None'})")
            results["group_investigation"]["group_89"] = {
                "exists": False,
                "error": f"HTTP {response.status_code if response else 'None'}"
            }
        
        print()
        
        # 2. Buscar tickets que mencionam o grupo 89 de diferentes formas
        search_methods = [
            ("Busca por campo GROUP (71)", {
                "criteria[0][field]": "71",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "89"
            }),
            ("Busca por campo 8 (hierarquia)", {
                "criteria[0][field]": "8",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "89"
            }),
            ("Busca por campo groups_id_assign", {
                "criteria[0][field]": "groups_id_assign",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "89"
            }),
            ("Busca por campo groups_id_requester", {
                "criteria[0][field]": "groups_id_requester",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": "89"
            }),
            ("Busca textual por 'N1'", {
                "criteria[0][field]": "view",
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "N1"
            })
        ]
        
        print("🔍 2. Testando diferentes métodos de busca:")
        results["ticket_search_methods"] = {}
        
        for method_name, search_criteria in search_methods:
            print(f"   🧪 {method_name}:")
            
            search_params = {
                "is_deleted": 0,
                "range": "0-4",  # Buscar até 5 tickets
                **search_criteria
            }
            
            response = glpi_service._make_authenticated_request(
                "GET",
                f"{glpi_service.glpi_url}/search/Ticket",
                params=search_params
            )
            
            if response and response.ok:
                data = response.json()
                total = 0
                
                # Tentar extrair total de diferentes formas
                if "Content-Range" in response.headers:
                    total = int(response.headers["Content-Range"].split("/")[-1])
                elif isinstance(data, dict) and 'totalcount' in data:
                    total = data['totalcount']
                elif isinstance(data, list):
                    total = len(data)
                
                print(f"      📊 Total encontrado: {total}")
                results["ticket_search_methods"][method_name] = {
                    "total_tickets": total,
                    "search_params": search_params,
                    "response_type": type(data).__name__
                }
                
                # Se encontrou tickets, salvar alguns exemplos
                if total > 0 and isinstance(data, list):
                    for i, ticket in enumerate(data[:3]):  # Primeiros 3 tickets
                        print(f"         Ticket {ticket.get('2', 'N/A')}: {ticket.get('1', 'N/A')}")
                        if method_name not in [item["method"] for item in results["sample_tickets"]]:
                            results["sample_tickets"].append({
                                "method": method_name,
                                "ticket_id": ticket.get('2', 'N/A'),
                                "ticket_name": ticket.get('1', 'N/A'),
                                "ticket_data": ticket
                            })
            else:
                error_code = response.status_code if response else 'None'
                print(f"      ❌ Erro: HTTP {error_code}")
                results["ticket_search_methods"][method_name] = {
                    "error": f"HTTP {error_code}",
                    "search_params": search_params
                }
        
        print()
        
        # 3. Buscar alguns tickets aleatórios para ver sua estrutura
        print("🔍 3. Analisando estrutura de tickets aleatórios:")
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Ticket",
            params={"is_deleted": 0, "range": "0-2"}
        )
        
        if response and response.ok:
            tickets = response.json()
            if isinstance(tickets, list) and tickets:
                for ticket in tickets[:2]:
                    ticket_id = ticket.get('2', 'N/A')
                    print(f"   📋 Ticket {ticket_id}:")
                    
                    # Buscar detalhes completos do ticket
                    detail_response = glpi_service._make_authenticated_request(
                        "GET",
                        f"{glpi_service.glpi_url}/Ticket/{ticket_id}"
                    )
                    
                    if detail_response and detail_response.ok:
                        ticket_detail = detail_response.json()
                        group_fields = {}
                        for key, value in ticket_detail.items():
                            if 'group' in key.lower() or key in ['8', '71', '142', '113']:
                                group_fields[key] = value
                                print(f"      {key}: {value}")
                        
                        results["sample_tickets"].append({
                            "method": "random_sample",
                            "ticket_id": ticket_id,
                            "group_fields": group_fields,
                            "full_data": ticket_detail
                        })
        
        # Salvar resultados
        filename = f"investigate_group_89_{results['timestamp']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print()
        print(f"✅ Investigação concluída! Resultados salvos em {filename}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        results["error"] = str(e)
        
        # Salvar resultados mesmo com erro
        filename = f"investigate_group_89_{results['timestamp']}_error.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()