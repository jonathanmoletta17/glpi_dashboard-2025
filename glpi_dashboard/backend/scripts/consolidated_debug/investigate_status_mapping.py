#!/usr/bin/env python3
"""
Script para investigar o mapeamento de status no GLPI

O problema pode estar no status ID usado. Vamos verificar:
1. Quais status existem no GLPI
2. Qual é o ID correto para "Novo"
3. Testar com diferentes status
"""

import json
import sys
import os
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'glpi_dashboard', 'backend'))

from services.glpi_service import GLPIService

def main():
    print("🔍 INVESTIGANDO MAPEAMENTO DE STATUS")
    print("=" * 40)
    
    results = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "status_investigation": {},
        "ticket_tests": {},
        "group_tests": {}
    }
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
        
        print(f"✅ Status map atual: {glpi_service.status_map}")
        results["status_investigation"]["current_status_map"] = glpi_service.status_map
        
        print(f"✅ Service levels: {glpi_service.service_levels}")
        results["status_investigation"]["service_levels"] = glpi_service.service_levels
        
        # Buscar todos os status disponíveis
        print("\n📋 BUSCANDO TODOS OS STATUS DISPONÍVEIS:")
        print("-" * 45)
        
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/Ticket",
            params={"range": "0-10", "expand_dropdowns": "true"}
        )
        
        if response and response.ok:
            tickets = response.json()
            if tickets:
                print(f"✅ Encontrados {len(tickets)} tickets para análise")
                
                # Analisar status dos tickets
                status_found = set()
                for ticket in tickets:
                    if 'status' in ticket:
                        status_found.add((ticket.get('status'), ticket.get('id')))
                
                print("\n📊 Status encontrados nos tickets:")
                for status, ticket_id in status_found:
                    print(f"   Status: {status} (Ticket ID: {ticket_id})")
                
                results["status_investigation"]["status_found_in_tickets"] = list(status_found)
        
        # Testar busca de tickets sem filtro de status
        print("\n🧪 TESTANDO BUSCA SEM FILTRO DE STATUS:")
        print("-" * 42)
        
        group_id = 89  # N1
        
        # Teste com campo 71 (GROUP)
        print("\n1️⃣ Campo 71 (GROUP) sem filtro de status:")
        params_71_no_status = {
            "is_deleted": 0,
            "range": "0-5",
            "criteria[0][field]": "71",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": str(group_id),
        }
        
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Ticket",
            params=params_71_no_status
        )
        
        count_71_no_status = 0
        tickets_71 = []
        if response and response.ok:
            if "Content-Range" in response.headers:
                count_71_no_status = int(response.headers["Content-Range"].split("/")[-1])
            
            data = response.json()
            if 'data' in data:
                tickets_71 = data['data'][:5]  # Primeiros 5 tickets
                print(f"   Total: {count_71_no_status} tickets")
                print("   Primeiros tickets:")
                for ticket in tickets_71:
                    print(f"     ID: {ticket.get('2')}, Status: {ticket.get('12')}, Grupo: {ticket.get('71')}")
            else:
                count_71_no_status = data.get('totalcount', 0)
                print(f"   Total: {count_71_no_status} tickets (sem dados detalhados)")
        else:
            print(f"   ❌ Erro na busca: {response.status_code if response else 'None'}")
        
        results["ticket_tests"]["field_71_no_status"] = {
            "count": count_71_no_status,
            "sample_tickets": tickets_71
        }
        
        # Teste com campo 8 (hierarquia)
        print("\n2️⃣ Campo 8 (hierarquia) sem filtro de status:")
        params_8_no_status = {
            "is_deleted": 0,
            "range": "0-5",
            "criteria[0][field]": "8",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": str(group_id),
        }
        
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Ticket",
            params=params_8_no_status
        )
        
        count_8_no_status = 0
        tickets_8 = []
        if response and response.ok:
            if "Content-Range" in response.headers:
                count_8_no_status = int(response.headers["Content-Range"].split("/")[-1])
            
            data = response.json()
            if 'data' in data:
                tickets_8 = data['data'][:5]  # Primeiros 5 tickets
                print(f"   Total: {count_8_no_status} tickets")
                print("   Primeiros tickets:")
                for ticket in tickets_8:
                    print(f"     ID: {ticket.get('2')}, Status: {ticket.get('12')}, Hierarquia: {ticket.get('8')}")
            else:
                count_8_no_status = data.get('totalcount', 0)
                print(f"   Total: {count_8_no_status} tickets (sem dados detalhados)")
        else:
            print(f"   ❌ Erro na busca: {response.status_code if response else 'None'}")
        
        results["ticket_tests"]["field_8_no_status"] = {
            "count": count_8_no_status,
            "sample_tickets": tickets_8
        }
        
        # Testar com diferentes status IDs
        print("\n🎯 TESTANDO COM DIFERENTES STATUS:")
        print("-" * 35)
        
        # Status comuns no GLPI
        test_status = {
            "Novo": [1, 2],  # IDs possíveis para "Novo"
            "Em andamento": [3, 4],
            "Resolvido": [5, 6],
            "Fechado": [6, 7]
        }
        
        for status_name, possible_ids in test_status.items():
            print(f"\n   Testando status '{status_name}':")
            
            for status_id in possible_ids:
                # Teste com campo 8 (que mostrou mais resultados anteriormente)
                params = {
                    "is_deleted": 0,
                    "range": "0-0",
                    "criteria[0][field]": "8",
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(group_id),
                    "criteria[1][link]": "AND",
                    "criteria[1][field]": "12",  # Campo status
                    "criteria[1][searchtype]": "equals",
                    "criteria[1][value]": str(status_id),
                }
                
                response = glpi_service._make_authenticated_request(
                    "GET",
                    f"{glpi_service.glpi_url}/search/Ticket",
                    params=params
                )
                
                count = 0
                if response and response.ok:
                    if "Content-Range" in response.headers:
                        count = int(response.headers["Content-Range"].split("/")[-1])
                    else:
                        data = response.json()
                        count = data.get('totalcount', 0)
                
                print(f"     Status ID {status_id}: {count} tickets")
                
                if status_name not in results["ticket_tests"]:
                    results["ticket_tests"][status_name] = {}
                results["ticket_tests"][status_name][f"status_id_{status_id}"] = count
        
        # Testar outros grupos
        print("\n🏢 TESTANDO OUTROS GRUPOS:")
        print("-" * 25)
        
        test_groups = {
            "N2": glpi_service.service_levels.get("N2"),
            "N3": glpi_service.service_levels.get("N3"),
            "N4": glpi_service.service_levels.get("N4")
        }
        
        for group_name, group_id_test in test_groups.items():
            if group_id_test:
                print(f"\n   Testando grupo {group_name} (ID {group_id_test}):")
                
                # Teste sem filtro de status
                params = {
                    "is_deleted": 0,
                    "range": "0-0",
                    "criteria[0][field]": "8",
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": str(group_id_test),
                }
                
                response = glpi_service._make_authenticated_request(
                    "GET",
                    f"{glpi_service.glpi_url}/search/Ticket",
                    params=params
                )
                
                count = 0
                if response and response.ok:
                    if "Content-Range" in response.headers:
                        count = int(response.headers["Content-Range"].split("/")[-1])
                    else:
                        data = response.json()
                        count = data.get('totalcount', 0)
                
                print(f"     Total tickets: {count}")
                results["group_tests"][group_name] = {
                    "group_id": group_id_test,
                    "total_tickets": count
                }
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"investigate_status_mapping_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {output_file}")
        
        # Resumo dos achados
        print("\n📋 RESUMO DOS ACHADOS:")
        print("-" * 20)
        print(f"Campo 71 (GROUP) sem status: {count_71_no_status} tickets")
        print(f"Campo 8 (hierarquia) sem status: {count_8_no_status} tickets")
        
        if count_8_no_status > count_71_no_status:
            print("✅ Campo 8 (hierarquia) retorna mais tickets - usar este campo")
        elif count_71_no_status > count_8_no_status:
            print("✅ Campo 71 (GROUP) retorna mais tickets - manter campo atual")
        else:
            print("⚠️ Ambos os campos retornam a mesma quantidade - investigar mais")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        results["error"] = str(e)
        
        # Salvar resultados mesmo com erro
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"investigate_status_mapping_error_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados de erro salvos em: {output_file}")

if __name__ == "__main__":
    main()