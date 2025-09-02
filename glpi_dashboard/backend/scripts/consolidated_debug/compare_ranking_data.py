#!/usr/bin/env python3
"""
Script para comparar dados reais do GLPI com dados retornados pela API
Para identificar discrepâncias críticas no ranking de técnicos
"""

import requests
import json
from datetime import datetime
from typing import Dict, List

# Configuração
BASE_URL = "http://localhost:5000/api"
TEST_PERIOD = {
    'start_date': '2025-07-29',
    'end_date': '2025-08-28'
}

# Dados REAIS do GLPI fornecidos pelo usuário
GLPI_REAL_DATA = [
    {"name": "Anderson da Silva Morim de Oliveira", "tickets": 133},
    {"name": "Jorge Antonio Vicente Júnior", "tickets": 130},
    {"name": "Silvio Godinho Valim", "tickets": 123},
    {"name": "Miguelangelo Ferreira", "tickets": 56},
    {"name": "Thales Vinicius Paz Leite", "tickets": 53},
    {"name": "Jonathan Nascimento Moletta", "tickets": 53},
    {"name": "Luciano Marcelino da Silva", "tickets": 51},
    {"name": "Gabriel Silva Machado", "tickets": 44},
    {"name": "Pablo Hebling Guimaraes", "tickets": 39},
    {"name": "Alessandro Carbonera Vieira", "tickets": 29},
    {"name": "Edson Joel dos Santos Silva", "tickets": 19},
    {"name": "Leonardo Trojan Repiso Riela", "tickets": 15},
    {"name": "Gabriel Andrade da Conceicao", "tickets": 15},
    {"name": "Nicolas Fernando Muniz Nunez", "tickets": 7},
    {"name": "Luciano de Araujo Silva", "tickets": 5},
    {"name": "Wagner Mengue", "tickets": 1},
    {"name": "Joao Pedro Wilson Dias", "tickets": 1},
    {"name": "Alexandre Rovinski Almoarqueg", "tickets": 1}
]

def get_api_ranking_data() -> Dict:
    """Obtém dados do ranking via API"""
    print("🔍 Obtendo dados da API...")
    
    params = {
        'start_date': TEST_PERIOD['start_date'],
        'end_date': TEST_PERIOD['end_date'],
        'limit': 50  # Limite alto para pegar todos
    }
    
    try:
        response = requests.get(f"{BASE_URL}/technicians/ranking", params=params, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API respondeu com {len(data.get('data', []))} técnicos")
            return data
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return {}

def normalize_name(name: str) -> str:
    """Normaliza nomes para comparação"""
    return name.strip().lower().replace('  ', ' ')

def compare_data(api_data: Dict, real_data: List[Dict]) -> Dict:
    """Compara dados da API com dados reais do GLPI"""
    print("\n📊 COMPARAÇÃO DETALHADA - API vs GLPI REAL")
    print("=" * 80)
    
    api_technicians = api_data.get('data', [])
    
    # Criar dicionários para comparação
    api_dict = {normalize_name(tech['name']): tech for tech in api_technicians}
    real_dict = {normalize_name(tech['name']): tech for tech in real_data}
    
    comparison_results = {
        'matches': [],
        'discrepancies': [],
        'missing_in_api': [],
        'extra_in_api': [],
        'total_real': sum(tech['tickets'] for tech in real_data),
        'total_api': sum(tech.get('total', 0) for tech in api_technicians)
    }
    
    print(f"📈 TOTAIS GERAIS:")
    print(f"   GLPI Real: {comparison_results['total_real']} tickets")
    print(f"   API:       {comparison_results['total_api']} tickets")
    print(f"   Diferença: {comparison_results['total_api'] - comparison_results['total_real']} tickets")
    print()
    
    # Comparar técnico por técnico
    print("👥 COMPARAÇÃO POR TÉCNICO:")
    print(f"{'Técnico':<35} {'GLPI Real':<12} {'API':<12} {'Diferença':<12} {'Status'}")
    print("-" * 80)
    
    for real_name, real_tech in real_dict.items():
        if real_name in api_dict:
            api_tech = api_dict[real_name]
            api_tickets = api_tech.get('total', 0)
            real_tickets = real_tech['tickets']
            difference = api_tickets - real_tickets
            
            status = "✅ OK" if difference == 0 else f"❌ ERRO ({difference:+d})"
            
            print(f"{real_tech['name'][:34]:<35} {real_tickets:<12} {api_tickets:<12} {difference:+12d} {status}")
            
            if difference == 0:
                comparison_results['matches'].append({
                    'name': real_tech['name'],
                    'tickets': real_tickets
                })
            else:
                comparison_results['discrepancies'].append({
                    'name': real_tech['name'],
                    'real_tickets': real_tickets,
                    'api_tickets': api_tickets,
                    'difference': difference
                })
        else:
            print(f"{real_tech['name'][:34]:<35} {real_tech['tickets']:<12} {'AUSENTE':<12} {'N/A':<12} ❌ FALTANDO")
            comparison_results['missing_in_api'].append(real_tech)
    
    # Verificar técnicos extras na API
    for api_name, api_tech in api_dict.items():
        if api_name not in real_dict:
            print(f"{api_tech['name'][:34]:<35} {'N/A':<12} {api_tech.get('total', 0):<12} {'N/A':<12} ⚠️ EXTRA")
            comparison_results['extra_in_api'].append(api_tech)
    
    return comparison_results

def analyze_discrepancies(comparison: Dict) -> None:
    """Analisa as discrepâncias encontradas"""
    print("\n🔍 ANÁLISE DE DISCREPÂNCIAS")
    print("=" * 50)
    
    if comparison['discrepancies']:
        print(f"❌ {len(comparison['discrepancies'])} técnicos com valores incorretos:")
        for disc in comparison['discrepancies']:
            print(f"   • {disc['name']}: Real={disc['real_tickets']}, API={disc['api_tickets']} (diff: {disc['difference']:+d})")
    
    if comparison['missing_in_api']:
        print(f"\n❌ {len(comparison['missing_in_api'])} técnicos ausentes na API:")
        for missing in comparison['missing_in_api']:
            print(f"   • {missing['name']}: {missing['tickets']} tickets")
    
    if comparison['extra_in_api']:
        print(f"\n⚠️ {len(comparison['extra_in_api'])} técnicos extras na API:")
        for extra in comparison['extra_in_api']:
            print(f"   • {extra['name']}: {extra.get('total', 0)} tickets")
    
    if comparison['matches']:
        print(f"\n✅ {len(comparison['matches'])} técnicos com valores corretos")
    
    # Calcular precisão
    total_real_technicians = len(GLPI_REAL_DATA)
    correct_matches = len(comparison['matches'])
    accuracy = (correct_matches / total_real_technicians) * 100 if total_real_technicians > 0 else 0
    
    print(f"\n📊 RESUMO DA PRECISÃO:")
    print(f"   Técnicos corretos: {correct_matches}/{total_real_technicians} ({accuracy:.1f}%)")
    print(f"   Total de tickets - Real: {comparison['total_real']}, API: {comparison['total_api']}")
    print(f"   Diferença total: {comparison['total_api'] - comparison['total_real']} tickets")

def save_comparison_report(api_data: Dict, comparison: Dict) -> None:
    """Salva relatório detalhado da comparação"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_period': TEST_PERIOD,
        'glpi_real_data': GLPI_REAL_DATA,
        'api_response': api_data,
        'comparison_results': comparison,
        'summary': {
            'total_discrepancies': len(comparison['discrepancies']),
            'missing_in_api': len(comparison['missing_in_api']),
            'extra_in_api': len(comparison['extra_in_api']),
            'correct_matches': len(comparison['matches']),
            'accuracy_percentage': (len(comparison['matches']) / len(GLPI_REAL_DATA)) * 100
        }
    }
    
    filename = f"ranking_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {filename}")

def main():
    """Função principal"""
    print("🚨 AUDITORIA CRÍTICA - RANKING DE TÉCNICOS")
    print(f"📅 Período: {TEST_PERIOD['start_date']} a {TEST_PERIOD['end_date']}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Obter dados da API
    api_data = get_api_ranking_data()
    
    if not api_data:
        print("❌ Não foi possível obter dados da API. Abortando comparação.")
        return
    
    # Comparar dados
    comparison = compare_data(api_data, GLPI_REAL_DATA)
    
    # Analisar discrepâncias
    analyze_discrepancies(comparison)
    
    # Salvar relatório
    save_comparison_report(api_data, comparison)
    
    print("\n🎯 CONCLUSÃO:")
    if comparison['discrepancies'] or comparison['missing_in_api']:
        print("❌ DADOS INCONSISTENTES DETECTADOS!")
        print("   A API está retornando valores incorretos.")
        print("   É necessária investigação profunda da lógica de cálculo.")
    else:
        print("✅ Dados consistentes entre API e GLPI real.")

if __name__ == "__main__":
    main()