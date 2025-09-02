#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Problemas do Dashboard GLPI usando IA Multiagente
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig

class DashboardIssueAnalyzer:
    def __init__(self):
        config = OrchestratorConfig()
        self.orchestrator = UnifiedOrchestrator(config)
        self.base_path = Path("../glpi_data")
        self.analysis_results = {}
        
    def load_documents(self):
        """Carrega todos os documentos de análise"""
        documents = {
            "licoes_aprendidas": self.base_path / "README_licoes_aprendidas.md",
            "vulnerabilidades": self.base_path / "analise_vulnerabilidades_melhorias.md",
            "diretrizes_seguranca": self.base_path / "diretrizes_desenvolvimento_seguro.md",
            "sumario_logs": self.base_path / "sumario_tecnico_19_logs.md",
            "readme_principal": self.base_path / "README.md"
        }
        
        loaded_docs = {}
        for name, path in documents.items():
            try:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        loaded_docs[name] = f.read()
                    print(f"✅ Carregado: {name}")
                else:
                    print(f"❌ Não encontrado: {path}")
            except Exception as e:
                print(f"❌ Erro ao carregar {name}: {str(e)}")
        
        return loaded_docs
    
    def analyze_http_206_issue(self, docs):
        """Análise específica do problema HTTP 206"""
        print("\n🔍 ANÁLISE: Problema HTTP 206")
        
        # Extrair informações sobre o problema HTTP 206
        http_206_analysis = {
            "problema_identificado": "Tratamento inadequado do status HTTP 206 (Partial Content) como erro",
            "metodos_afetados": "19+ métodos críticos do dashboard",
            "impacto": "Dashboard zerado por horas",
            "causa_raiz": "Uso de response.ok que considera 206 como falha",
            "solucao_aplicada": "Verificação explícita de status_code in [200, 206]"
        }
        
        # Usar IA para analisar os logs
        if "sumario_logs" in docs:
            log_analysis = self.orchestrator.analyze_glpi_log(docs["sumario_logs"])
            http_206_analysis["ai_analysis"] = log_analysis
        
        return http_206_analysis
    
    def analyze_cache_implementation(self, docs):
        """Análise da implementação de cache que causou problemas"""
        print("\n🔍 ANÁLISE: Implementação de Cache")
        
        cache_analysis = {
            "objetivo_original": "Otimizar performance do dashboard (8-22s para carregamento)",
            "problema_encontrado": "Cache implementation broke dashboard functionality",
            "lições_aprendidas": [
                "Mudanças simultâneas sem isolamento",
                "Falta de ambiente de teste adequado",
                "Ausência de estratégia de rollback",
                "Validação inadequada de códigos HTTP"
            ]
        }
        
        # Analisar com IA
        if "licoes_aprendidas" in docs:
            cache_text = docs["licoes_aprendidas"]
            ai_analysis = self.orchestrator.analyze_glpi_log(cache_text)
            cache_analysis["ai_analysis"] = ai_analysis
        
        return cache_analysis
    
    def generate_recovery_plan(self):
        """Gera plano de recuperação baseado na análise"""
        print("\n🛠️ GERANDO PLANO DE RECUPERAÇÃO")
        
        recovery_plan = {
            "fase_1_emergencial": {
                "prioridade": "CRÍTICA",
                "ações": [
                    "Verificar status atual do dashboard",
                    "Identificar arquivos de cache problemáticos",
                    "Fazer backup do estado atual",
                    "Reverter implementação de cache se necessário"
                ]
            },
            "fase_2_correção": {
                "prioridade": "ALTA",
                "ações": [
                    "Aplicar correção HTTP 206 em todos os métodos",
                    "Implementar validação adequada de status codes",
                    "Testar cada método individualmente",
                    "Validar métricas do dashboard"
                ]
            },
            "fase_3_validação": {
                "prioridade": "MÉDIA",
                "ações": [
                    "Executar testes de integração",
                    "Monitorar logs por 24h",
                    "Documentar correções aplicadas",
                    "Implementar alertas preventivos"
                ]
            }
        }
        
        return recovery_plan
    
    def run_analysis(self):
        """Executa análise completa"""
        print("🚀 INICIANDO ANÁLISE DE PROBLEMAS DO DASHBOARD GLPI")
        print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Dispositivo IA: {self.orchestrator.get_status()['device']}")
        
        # Carregar documentos
        docs = self.load_documents()
        
        # Análises específicas
        self.analysis_results["http_206_issue"] = self.analyze_http_206_issue(docs)
        self.analysis_results["cache_implementation"] = self.analyze_cache_implementation(docs)
        self.analysis_results["recovery_plan"] = self.generate_recovery_plan()
        
        # Salvar resultados
        self.save_analysis_results()
        
        return self.analysis_results
    
    def save_analysis_results(self):
        """Salva resultados da análise"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"dashboard_analysis_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Análise salva em: {output_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar análise: {str(e)}")
    
    def print_summary(self):
        """Imprime resumo da análise"""
        print("\n" + "="*60)
        print("📋 RESUMO DA ANÁLISE")
        print("="*60)
        
        if "http_206_issue" in self.analysis_results:
            http_analysis = self.analysis_results["http_206_issue"]
            print(f"\n🔴 PROBLEMA PRINCIPAL: {http_analysis['problema_identificado']}")
            print(f"📊 MÉTODOS AFETADOS: {http_analysis['metodos_afetados']}")
            print(f"💥 IMPACTO: {http_analysis['impacto']}")
            print(f"🎯 CAUSA RAIZ: {http_analysis['causa_raiz']}")
            print(f"✅ SOLUÇÃO: {http_analysis['solucao_aplicada']}")
        
        if "recovery_plan" in self.analysis_results:
            print("\n🛠️ PLANO DE RECUPERAÇÃO:")
            for fase, detalhes in self.analysis_results["recovery_plan"].items():
                print(f"\n{fase.upper().replace('_', ' ')}: {detalhes['prioridade']}")
                for acao in detalhes['ações']:
                    print(f"  • {acao}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    analyzer = DashboardIssueAnalyzer()
    results = analyzer.run_analysis()
    analyzer.print_summary()