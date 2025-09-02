#!/usr/bin/env python3
"""
Script para corrigir o problema de campo de grupo no GLPIService

Baseado na investigação:
- Campo 71 (GROUP): retorna apenas 1 ticket para grupo N1 (ID 89)
- Campo 8 (hierarquia): retorna 1464 tickets para grupo N1 (ID 89)

O problema parece ser que o método get_ticket_count está usando o campo GROUP (71)
quando deveria usar o campo 8 (hierarquia) para buscar tickets atribuídos ao grupo.
"""

import json
import sys
import os
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'glpi_dashboard', 'backend'))

from services.glpi_service import GLPIService

def main():
    print("🔧 CORRIGINDO PROBLEMA DE CAMPO DE GRUPO")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "investigation": {},
        "field_comparison": {},
        "recommended_fix": {},
        "validation_tests": {}
    }
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
        
        if not glpi_service.discover_field_ids():
            print("❌ Falha ao descobrir field_ids")
            return
        
        print(f"✅ Field IDs descobertos: {glpi_service.field_ids}")
        results["investigation"]["field_ids"] = glpi_service.field_ids
        
        # Testar diferentes campos para grupo N1 (ID 89) com status Novo (ID 1)
        group_id = 89  # N1
        status_id = 1  # Novo
        
        print(f"\n🧪 TESTANDO CAMPOS PARA GRUPO N1 (ID {group_id}) COM STATUS NOVO (ID {status_id})")
        print("-" * 60)
        
        # Teste 1: Campo GROUP (71) - método atual
        print("\n1️⃣ Campo GROUP (71) - Método atual do get_ticket_count:")
        field_71_params = {
            "is_deleted": 0,
            "range": "0-0",
            "criteria[0][field]": "71",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": str(group_id),
            "criteria[1][link]": "AND",
            "criteria[1][field]": glpi_service.field_ids["STATUS"],
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": str(status_id),
        }
        
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Ticket",
            params=field_71_params
        )
        
        field_71_count = 0
        if response and response.ok:
            if "Content-Range" in response.headers:
                field_71_count = int(response.headers["Content-Range"].split("/")[-1])
            else:
                data = response.json()
                field_71_count = data.get('totalcount', 0)
        
        print(f"   Resultado: {field_71_count} tickets")
        results["field_comparison"]["field_71_group"] = {
            "count": field_71_count,
            "params": field_71_params
        }
        
        # Teste 2: Campo 8 (hierarquia) - método alternativo
        print("\n2️⃣ Campo 8 (hierarquia) - Método do get_ticket_count_by_hierarchy:")
        field_8_params = {
            "is_deleted": 0,
            "range": "0-0",
            "criteria[0][field]": "8",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": str(group_id),
            "criteria[1][link]": "AND",
            "criteria[1][field]": glpi_service.field_ids["STATUS"],
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": str(status_id),
        }
        
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Ticket",
            params=field_8_params
        )
        
        field_8_count = 0
        if response and response.ok:
            if "Content-Range" in response.headers:
                field_8_count = int(response.headers["Content-Range"].split("/")[-1])
            else:
                data = response.json()
                field_8_count = data.get('totalcount', 0)
        
        print(f"   Resultado: {field_8_count} tickets")
        results["field_comparison"]["field_8_hierarchy"] = {
            "count": field_8_count,
            "params": field_8_params
        }
        
        # Teste 3: Comparar com métodos existentes
        print("\n3️⃣ Testando métodos existentes:")
        
        # get_ticket_count (usa campo GROUP)
        count_by_group = glpi_service.get_ticket_count(group_id, status_id)
        print(f"   get_ticket_count(89, 1): {count_by_group}")
        results["field_comparison"]["get_ticket_count"] = count_by_group
        
        # get_ticket_count_by_hierarchy (usa campo 8)
        count_by_hierarchy = glpi_service.get_ticket_count_by_hierarchy("89", status_id)
        print(f"   get_ticket_count_by_hierarchy('89', 1): {count_by_hierarchy}")
        results["field_comparison"]["get_ticket_count_by_hierarchy"] = count_by_hierarchy
        
        # Análise dos resultados
        print("\n📊 ANÁLISE DOS RESULTADOS:")
        print("-" * 30)
        
        if field_8_count > field_71_count:
            print(f"✅ Campo 8 (hierarquia) retorna mais tickets: {field_8_count} vs {field_71_count}")
            print("💡 RECOMENDAÇÃO: Modificar get_ticket_count para usar campo 8 em vez de campo GROUP (71)")
            
            results["recommended_fix"] = {
                "issue": "Campo GROUP (71) retorna poucos tickets",
                "solution": "Usar campo 8 (hierarquia) em get_ticket_count",
                "field_71_count": field_71_count,
                "field_8_count": field_8_count,
                "improvement": field_8_count - field_71_count
            }
            
            # Testar outros grupos para validar a solução
            print("\n🧪 VALIDANDO SOLUÇÃO COM OUTROS GRUPOS:")
            print("-" * 40)
            
            test_groups = {
                "N2": glpi_service.service_levels.get("N2"),
                "N3": glpi_service.service_levels.get("N3"),
                "N4": glpi_service.service_levels.get("N4")
            }
            
            for level_name, level_id in test_groups.items():
                if level_id:
                    print(f"\n   Testando {level_name} (ID {level_id}):")
                    
                    # Campo 71
                    params_71 = {
                        "is_deleted": 0,
                        "range": "0-0",
                        "criteria[0][field]": "71",
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(level_id),
                        "criteria[1][link]": "AND",
                        "criteria[1][field]": glpi_service.field_ids["STATUS"],
                        "criteria[1][searchtype]": "equals",
                        "criteria[1][value]": str(status_id),
                    }
                    
                    response = glpi_service._make_authenticated_request(
                        "GET",
                        f"{glpi_service.glpi_url}/search/Ticket",
                        params=params_71
                    )
                    
                    count_71 = 0
                    if response and response.ok:
                        if "Content-Range" in response.headers:
                            count_71 = int(response.headers["Content-Range"].split("/")[-1])
                        else:
                            data = response.json()
                            count_71 = data.get('totalcount', 0)
                    
                    # Campo 8
                    params_8 = {
                        "is_deleted": 0,
                        "range": "0-0",
                        "criteria[0][field]": "8",
                        "criteria[0][searchtype]": "equals",
                        "criteria[0][value]": str(level_id),
                        "criteria[1][link]": "AND",
                        "criteria[1][field]": glpi_service.field_ids["STATUS"],
                        "criteria[1][searchtype]": "equals",
                        "criteria[1][value]": str(status_id),
                    }
                    
                    response = glpi_service._make_authenticated_request(
                        "GET",
                        f"{glpi_service.glpi_url}/search/Ticket",
                        params=params_8
                    )
                    
                    count_8 = 0
                    if response and response.ok:
                        if "Content-Range" in response.headers:
                            count_8 = int(response.headers["Content-Range"].split("/")[-1])
                        else:
                            data = response.json()
                            count_8 = data.get('totalcount', 0)
                    
                    print(f"     Campo 71: {count_71} tickets")
                    print(f"     Campo 8:  {count_8} tickets")
                    
                    results["validation_tests"][level_name] = {
                        "level_id": level_id,
                        "field_71_count": count_71,
                        "field_8_count": count_8,
                        "difference": count_8 - count_71
                    }
        
        else:
            print(f"⚠️ Campo GROUP (71) retorna mais ou igual tickets: {field_71_count} vs {field_8_count}")
            results["recommended_fix"] = {
                "issue": "Campo 8 não retorna mais tickets que campo 71",
                "solution": "Investigar outros campos ou abordagens",
                "field_71_count": field_71_count,
                "field_8_count": field_8_count
            }
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fix_group_field_issue_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {output_file}")
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Analisar os resultados salvos")
        print("2. Implementar a correção no GLPIService se necessário")
        print("3. Testar a correção com dados reais")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        results["error"] = str(e)
        
        # Salvar resultados mesmo com erro
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fix_group_field_issue_error_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados de erro salvos em: {output_file}")

if __name__ == "__main__":
    main()