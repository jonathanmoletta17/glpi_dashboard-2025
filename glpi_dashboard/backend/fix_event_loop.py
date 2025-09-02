#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o event loop do asyncio no Windows para compatibilidade com aiodns.
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def configure_event_loop():
    """Configura o event loop correto para Windows."""
    if sys.platform == 'win32':
        # No Windows, usar SelectorEventLoop para compatibilidade com aiodns
        print("🔧 Configurando SelectorEventLoop para Windows...")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print("✅ Event loop configurado com sucesso")
    else:
        print("ℹ️ Sistema não é Windows, mantendo configuração padrão")

def test_glpi_service():
    """Testa o GLPIService após configurar o event loop."""
    print("\n🧪 Testando GLPIService...")
    
    try:
        from services.glpi_service import GLPIService
        
        # Criar instância do serviço
        glpi_service = GLPIService()
        print("✅ GLPIService criado com sucesso")
        
        # Testar obtenção de métricas de forma síncrona
        import asyncio
        
        async def test_metrics():
            try:
                metrics = await glpi_service.get_metrics()
                print(f"✅ Métricas obtidas: {type(metrics)}")
                return True
            except Exception as e:
                print(f"❌ Erro ao obter métricas: {e}")
                return False
        
        # Executar teste
        result = asyncio.run(test_metrics())
        return result
        
    except Exception as e:
        print(f"❌ Erro no teste do GLPIService: {e}")
        return False

def main():
    """Função principal."""
    print("CORREÇÃO DO EVENT LOOP PARA GLPI DASHBOARD")
    print("=" * 50)
    
    # Configurar event loop
    configure_event_loop()
    
    # Testar GLPIService
    if test_glpi_service():
        print("\n✅ CORREÇÃO APLICADA COM SUCESSO!")
        print("\n📋 Próximos passos:")
        print("1. Aplicar a correção no app.py principal")
        print("2. Reiniciar o servidor Flask")
        print("3. Testar os endpoints que usam GLPI")
    else:
        print("\n❌ AINDA HÁ PROBLEMAS COM O GLPI SERVICE")
        print("\n🔍 Verifique:")
        print("1. Configurações do GLPI (URL, tokens)")
        print("2. Conectividade de rede")
        print("3. Status do servidor GLPI")

if __name__ == "__main__":
    main()