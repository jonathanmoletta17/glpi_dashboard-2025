#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador Mínimo de IA - GLPI Dashboard
Compatibilidade com UnifiedOrchestrator
"""

import logging
import sys
import time
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from glpi_dashboard.backend.ai import UnifiedOrchestrator, OrchestratorConfig

class GLPIAIOrchestrator(UnifiedOrchestrator):
    def __init__(self):
        config = OrchestratorConfig()
        super().__init__(config)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🚀 Orquestrador mínimo iniciado")
            
    
    async def analyze_glpi_log(self, log_text):
        """Análise básica de logs GLPI usando o UnifiedOrchestrator"""
        try:
            # Usar o método analyze_code do UnifiedOrchestrator
            result = await self.analyze_code(log_text, "log_analysis")
            return {
                "status": "analyzed",
                "log_length": len(log_text),
                "contains_error": "error" in log_text.lower(),
                "analysis_result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Erro ao analisar log: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def get_status(self):
        """Status do orquestrador"""
        return {
            "status": "running",
            "agents_available": len(self.agents),
            "workflows_available": len(self.predefined_workflows),
            "models_initialized": self.models_initialized,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Teste básico
        orchestrator = GLPIAIOrchestrator()
        print("Status:", orchestrator.get_status())
        
        # Teste de análise de log
        test_log = "Error connecting to database: connection timeout"
        result = await orchestrator.analyze_glpi_log(test_log)
        print("Análise:", result)
    
    # Executar teste assíncrono
    asyncio.run(main())
