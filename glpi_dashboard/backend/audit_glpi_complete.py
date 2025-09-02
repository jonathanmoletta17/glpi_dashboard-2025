#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria Completa do GLPI Dashboard
Testa conectividade, autenticação, mapeamento de status e recuperação de dados
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import logging

# Configurar logging mínimo
logging.basicConfig(level=logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from services.glpi_service import GLPIService
    from config.settings import get_config
    
    # Obter configuração ativa
    config = get_config()
    GLPI_CONFIG = {
        'base_url': config.GLPI_URL,
        'user_token': config.GLPI_USER_TOKEN,
        'app_token': config.GLPI_APP_TOKEN
    }
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def print_section(title):
    """Imprime uma seção formatada"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_glpi_connectivity():
    """Testa conectividade básica com GLPI"""
    print_section("1. TESTE DE CONECTIVIDADE GLPI")
    
    try:
        # Testar URL base
        base_url = GLPI_CONFIG.get('base_url', '')
        print(f"🔗 URL Base: {base_url}")
        
        if not base_url:
            print("❌ URL base não configurada")
            return False
            
        # Teste de ping básico
        response = requests.get(f"{base_url}/status", timeout=10)
        print(f"📡 Status HTTP: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        return False

def test_glpi_authentication():
    """Testa autenticação com GLPI"""
    print_section("2. TESTE DE AUTENTICAÇÃO")
    
    try:
        glpi_service = GLPIService()
        
        # Verificar configurações
        print(f"🔑 User Token: {'✓' if GLPI_CONFIG.get('user_token') else '❌'}")
        print(f"🎫 App Token: {'✓' if GLPI_CONFIG.get('app_token') else '❌'}")
        
        # Testar inicialização do serviço
        if hasattr(glpi_service, 'session_token'):
            print(f"🎯 Session Token: {'✓' if glpi_service.session_token else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro de autenticação: {e}")
        return False

def test_direct_api_calls():
    """Testa chamadas diretas à API GLPI"""
    print_section("3. TESTE DE CHAMADAS DIRETAS À API")
    
    try:
        glpi_service = GLPIService()
        base_url = GLPI_CONFIG.get('base_url')
        
        # Headers para autenticação
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"user_token {GLPI_CONFIG.get('user_token')}",
            'App-Token': GLPI_CONFIG.get('app_token')
        }
        
        # Teste 1: Listar tickets (primeiros 5)
        print("\n📋 Testando listagem de tickets...")
        tickets_url = f"{base_url}/Ticket?range=0-4"
        response = requests.get(tickets_url, headers=headers, timeout=30)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            tickets = response.json()
            print(f"✓ Tickets encontrados: {len(tickets)}")
            if tickets:
                print(f"  Primeiro ticket ID: {tickets[0].get('id', 'N/A')}")
                print(f"  Status: {tickets[0].get('status', 'N/A')}")
        else:
            print(f"❌ Erro: {response.text}")
            
        # Teste 2: Contar total de tickets
        print("\n🔢 Testando contagem total de tickets...")
        count_url = f"{base_url}/Ticket?range=0-0"
        response = requests.get(count_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            content_range = response.headers.get('Content-Range', '')
            print(f"✓ Content-Range: {content_range}")
            if '/' in content_range:
                total = content_range.split('/')[-1]
                print(f"✓ Total de tickets no sistema: {total}")
        
        # Teste 3: Verificar status disponíveis
        print("\n📊 Testando status disponíveis...")
        # Buscar tickets agrupados por status
        search_criteria = {
            "criteria": [
                {
                    "field": "12",  # Campo status
                    "searchtype": "equals",
                    "value": "1"  # Status 1 (novo)
                }
            ]
        }
        
        search_url = f"{base_url}/search/Ticket"
        response = requests.get(search_url, 
                              headers=headers, 
                              params={'criteria': json.dumps(search_criteria)},
                              timeout=30)
        
        print(f"Status busca: {response.status_code}")
        if response.status_code == 200:
            search_result = response.json()
            print(f"✓ Resultado da busca: {len(search_result.get('data', []))} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas chamadas diretas: {e}")
        return False

def test_status_mapping():
    """Testa o mapeamento de status"""
    print_section("4. TESTE DE MAPEAMENTO DE STATUS")
    
    try:
        glpi_service = GLPIService()
        
        # Verificar se o mapeamento existe
        if hasattr(glpi_service, 'status_map'):
            status_map = glpi_service.status_map
            print(f"✓ Status map encontrado: {len(status_map)} status")
            
            for status_name, status_id in status_map.items():
                print(f"  {status_name}: {status_id}")
        else:
            print("❌ Status map não encontrado")
            
        # Verificar field_ids
        if hasattr(glpi_service, 'field_ids'):
            field_ids = glpi_service.field_ids
            print(f"\n✓ Field IDs encontrados: {len(field_ids)} campos")
            
            for field_name, field_id in field_ids.items():
                print(f"  {field_name}: {field_id}")
        else:
            print("❌ Field IDs não encontrados")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no mapeamento: {e}")
        return False

def test_dashboard_metrics_detailed():
    """Testa o método get_dashboard_metrics em detalhes"""
    print_section("5. TESTE DETALHADO DO GET_DASHBOARD_METRICS")
    
    try:
        glpi_service = GLPIService()
        
        # Teste sem filtros
        print("\n🎯 Testando sem filtros de data...")
        result = glpi_service.get_dashboard_metrics()
        
        print(f"✓ Resultado obtido: {result.get('success', False)}")
        print(f"  Timestamp: {result.get('generated_at', 'N/A')}")
        
        general = result.get('general', {})
        print(f"\n📊 Métricas Gerais:")
        print(f"  Novos: {general.get('new', 0)}")
        print(f"  Pendentes: {general.get('pending', 0)}")
        print(f"  Em Progresso: {general.get('in_progress', 0)}")
        print(f"  Resolvidos: {general.get('solved', 0)}")
        print(f"  Total: {general.get('total', 0)}")
        
        levels = result.get('levels', {})
        print(f"\n🎚️ Métricas por Nível:")
        for level, data in levels.items():
            if isinstance(data, dict):
                total = data.get('total', 0)
                print(f"  {level}: {total} tickets")
        
        # Teste com filtros de data (últimos 30 dias)
        print("\n📅 Testando com filtros de data (últimos 30 dias)...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result_filtered = glpi_service.get_dashboard_metrics(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        general_filtered = result_filtered.get('general', {})
        print(f"  Total com filtro: {general_filtered.get('total', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de métricas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de auditoria"""
    print("🔍 AUDITORIA COMPLETA DO GLPI DASHBOARD")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'connectivity': test_glpi_connectivity(),
        'authentication': test_glpi_authentication(),
        'direct_api': test_direct_api_calls(),
        'status_mapping': test_status_mapping(),
        'dashboard_metrics': test_dashboard_metrics_detailed()
    }
    
    print_section("RESUMO DA AUDITORIA")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name.upper()}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 RESULTADO GERAL: {'✅ TODOS OS TESTES PASSARAM' if all_passed else '❌ ALGUNS TESTES FALHARAM'}")
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()