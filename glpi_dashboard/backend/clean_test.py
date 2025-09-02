#!/usr/bin/env python3
"""
Teste limpo do dashboard metrics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Desabilitar COMPLETAMENTE o logging
import logging
logging.disable(logging.CRITICAL)

# Desabilitar warnings
import warnings
warnings.filterwarnings('ignore')

from services.glpi_service import GLPIService
from config.settings import active_config
import json

def main():
    print("=== TESTE DASHBOARD METRICS ===")
    
    try:
        # Inicializar GLPIService
        glpi_service = GLPIService()
        print("✅ GLPIService inicializado")
        
        # Testar get_dashboard_metrics
        print("\n--- Testando get_dashboard_metrics() ---")
        result = glpi_service.get_dashboard_metrics()
        
        print(f"\n🔍 RESULTADO COMPLETO:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result and result.get('success'):
            print("\n✅ get_dashboard_metrics() funcionou!")
            
            data = result.get('data', {})
            
            # Mostrar totais gerais
            general = data.get('general', {})
            print(f"\n📊 TOTAIS GERAIS ({len(general)} items):")
            for key, value in general.items():
                print(f"  {key}: {value}")
            
            # Mostrar métricas por nível
            levels = data.get('levels', {})
            print(f"\n📈 MÉTRICAS POR NÍVEL ({len(levels)} items):")
            for level_name, level_data in levels.items():
                print(f"  {level_name}: {level_data}")
            
            # Mostrar trends
            trends = data.get('trends', {})
            print(f"\n📈 TRENDS ({len(trends)} items):")
            for key, value in trends.items():
                print(f"  {key}: {value}")
            
        else:
            print("❌ get_dashboard_metrics() falhou")
            if result:
                print(f"Erro: {result.get('error', 'Erro desconhecido')}")
            else:
                print("Resultado é None")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print("\n=== TESTE CONCLUÍDO ===")