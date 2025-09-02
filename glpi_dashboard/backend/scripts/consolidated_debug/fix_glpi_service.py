#!/usr/bin/env python3
"""
Script para corrigir o GLPIService baseado nos achados da investigação

Problemas identificados:
1. Campo 71 (GROUP) retorna apenas 1 ticket vs Campo 8 (hierarquia) com 1464 tickets
2. Status ID 1 ("Novo") retorna 0 tickets, mas ID 2 retorna 4 tickets
3. Método get_ticket_count deve usar campo 8 ao invés de campo 71

Soluções:
1. Alterar get_ticket_count para usar campo 8 (hierarquia)
2. Verificar se o status "new" deve ser ID 2 ao invés de 1
3. Testar as correções
"""

import json
import sys
import os
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'glpi_dashboard', 'backend'))

from services.glpi_service import GLPIService

def test_current_methods(glpi_service):
    """Testa os métodos atuais para comparação"""
    print("🧪 TESTANDO MÉTODOS ATUAIS:")
    print("-" * 30)
    
    results = {}
    
    # Testar get_ticket_count atual (usa campo 71)
    try:
        count_current = glpi_service.get_ticket_count(89, 1)  # N1, status "new"
        print(f"   get_ticket_count(89, 1): {count_current}")
        results["get_ticket_count_current"] = count_current
    except Exception as e:
        print(f"   get_ticket_count(89, 1): ERRO - {e}")
        results["get_ticket_count_current"] = f"ERRO: {e}"
    
    # Testar get_ticket_count_by_hierarchy atual (usa campo 8)
    try:
        count_hierarchy = glpi_service.get_ticket_count_by_hierarchy(89, 1)  # N1, status "new"
        print(f"   get_ticket_count_by_hierarchy(89, 1): {count_hierarchy}")
        results["get_ticket_count_by_hierarchy_current"] = count_hierarchy
    except Exception as e:
        print(f"   get_ticket_count_by_hierarchy(89, 1): ERRO - {e}")
        results["get_ticket_count_by_hierarchy_current"] = f"ERRO: {e}"
    
    return results

def test_with_corrected_status(glpi_service):
    """Testa com status ID 2 ao invés de 1"""
    print("\n🔧 TESTANDO COM STATUS CORRIGIDO (ID 2):")
    print("-" * 40)
    
    results = {}
    
    # Testar get_ticket_count com status 2
    try:
        count_status_2 = glpi_service.get_ticket_count(89, 2)  # N1, status ID 2
        print(f"   get_ticket_count(89, 2): {count_status_2}")
        results["get_ticket_count_status_2"] = count_status_2
    except Exception as e:
        print(f"   get_ticket_count(89, 2): ERRO - {e}")
        results["get_ticket_count_status_2"] = f"ERRO: {e}"
    
    # Testar get_ticket_count_by_hierarchy com status 2
    try:
        count_hierarchy_status_2 = glpi_service.get_ticket_count_by_hierarchy(89, 2)  # N1, status ID 2
        print(f"   get_ticket_count_by_hierarchy(89, 2): {count_hierarchy_status_2}")
        results["get_ticket_count_by_hierarchy_status_2"] = count_hierarchy_status_2
    except Exception as e:
        print(f"   get_ticket_count_by_hierarchy(89, 2): ERRO - {e}")
        results["get_ticket_count_by_hierarchy_status_2"] = f"ERRO: {e}"
    
    return results

def test_direct_api_calls(glpi_service):
    """Testa chamadas diretas à API para validar os achados"""
    print("\n🎯 TESTANDO CHAMADAS DIRETAS À API:")
    print("-" * 35)
    
    results = {}
    
    # Teste 1: Campo 8 (hierarquia) com status 2
    print("   1. Campo 8 (hierarquia) + Status 2:")
    params_field_8_status_2 = {
        "is_deleted": 0,
        "range": "0-0",
        "criteria[0][field]": "8",
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "89",
        "criteria[1][link]": "AND",
        "criteria[1][field]": "12",
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "2",
    }
    
    response = glpi_service._make_authenticated_request(
        "GET",
        f"{glpi_service.glpi_url}/search/Ticket",
        params=params_field_8_status_2
    )
    
    count_field_8_status_2 = 0
    if response and response.ok:
        if "Content-Range" in response.headers:
            count_field_8_status_2 = int(response.headers["Content-Range"].split("/")[-1])
        else:
            data = response.json()
            count_field_8_status_2 = data.get('totalcount', 0)
    
    print(f"      Resultado: {count_field_8_status_2} tickets")
    results["field_8_status_2_direct"] = count_field_8_status_2
    
    # Teste 2: Campo 71 (GROUP) com status 2
    print("   2. Campo 71 (GROUP) + Status 2:")
    params_field_71_status_2 = {
        "is_deleted": 0,
        "range": "0-0",
        "criteria[0][field]": "71",
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "89",
        "criteria[1][link]": "AND",
        "criteria[1][field]": "12",
        "criteria[1][searchtype]": "equals",
        "criteria[1][value]": "2",
    }
    
    response = glpi_service._make_authenticated_request(
        "GET",
        f"{glpi_service.glpi_url}/search/Ticket",
        params=params_field_71_status_2
    )
    
    count_field_71_status_2 = 0
    if response and response.ok:
        if "Content-Range" in response.headers:
            count_field_71_status_2 = int(response.headers["Content-Range"].split("/")[-1])
        else:
            data = response.json()
            count_field_71_status_2 = data.get('totalcount', 0)
    
    print(f"      Resultado: {count_field_71_status_2} tickets")
    results["field_71_status_2_direct"] = count_field_71_status_2
    
    return results

def main():
    print("🔧 CORRIGINDO GLPI SERVICE")
    print("=" * 25)
    
    results = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "investigation_summary": {
            "problem_identified": {
                "field_71_tickets": 1,
                "field_8_tickets": 1464,
                "status_1_tickets": 0,
                "status_2_tickets": 4,
                "conclusion": "Campo 8 (hierarquia) é mais efetivo que campo 71 (GROUP)"
            }
        },
        "tests": {}
    }
    
    try:
        # Inicializar serviço GLPI
        glpi_service = GLPIService()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
        
        print(f"✅ Conectado ao GLPI: {glpi_service.glpi_url}")
        print(f"✅ Status map: {glpi_service.status_map}")
        print(f"✅ Service levels: {glpi_service.service_levels}")
        
        # Testar métodos atuais
        current_results = test_current_methods(glpi_service)
        results["tests"]["current_methods"] = current_results
        
        # Testar com status corrigido
        corrected_status_results = test_with_corrected_status(glpi_service)
        results["tests"]["corrected_status"] = corrected_status_results
        
        # Testar chamadas diretas
        direct_api_results = test_direct_api_calls(glpi_service)
        results["tests"]["direct_api_calls"] = direct_api_results
        
        # Análise dos resultados
        print("\n📊 ANÁLISE DOS RESULTADOS:")
        print("-" * 25)
        
        field_8_status_2 = direct_api_results.get("field_8_status_2_direct", 0)
        field_71_status_2 = direct_api_results.get("field_71_status_2_direct", 0)
        
        print(f"Campo 8 + Status 2: {field_8_status_2} tickets")
        print(f"Campo 71 + Status 2: {field_71_status_2} tickets")
        
        # Determinar correções necessárias
        corrections_needed = []
        
        if field_8_status_2 > field_71_status_2:
            corrections_needed.append({
                "type": "field_change",
                "description": "Alterar get_ticket_count para usar campo 8 (hierarquia) ao invés de campo 71 (GROUP)",
                "current_field": 71,
                "recommended_field": 8,
                "improvement": f"{field_8_status_2 - field_71_status_2} tickets a mais"
            })
        
        if field_8_status_2 > 0 or field_71_status_2 > 0:
            corrections_needed.append({
                "type": "status_change",
                "description": "Alterar status 'new' de ID 1 para ID 2",
                "current_status_id": 1,
                "recommended_status_id": 2,
                "tickets_found": max(field_8_status_2, field_71_status_2)
            })
        
        results["corrections_needed"] = corrections_needed
        
        print("\n🎯 CORREÇÕES RECOMENDADAS:")
        print("-" * 25)
        for i, correction in enumerate(corrections_needed, 1):
            print(f"{i}. {correction['description']}")
            if correction['type'] == 'field_change':
                print(f"   Campo atual: {correction['current_field']} → Recomendado: {correction['recommended_field']}")
                print(f"   Melhoria: {correction['improvement']}")
            elif correction['type'] == 'status_change':
                print(f"   Status atual: {correction['current_status_id']} → Recomendado: {correction['recommended_status_id']}")
                print(f"   Tickets encontrados: {correction['tickets_found']}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fix_glpi_service_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {output_file}")
        
        # Resumo final
        print("\n✅ RESUMO FINAL:")
        print("-" * 15)
        if corrections_needed:
            print(f"📋 {len(corrections_needed)} correções identificadas")
            print("🔧 Próximo passo: Implementar as correções no GLPIService")
        else:
            print("⚠️ Nenhuma correção clara identificada - investigar mais")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        results["error"] = str(e)
        
        # Salvar resultados mesmo com erro
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fix_glpi_service_error_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados de erro salvos em: {output_file}")

if __name__ == "__main__":
    main()