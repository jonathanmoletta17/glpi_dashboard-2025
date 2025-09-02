#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação de Integração GLPI - Dashboard AI
Testa a integração completa com cenários reais do GLPI
"""

import os
import sys
import json
import yaml
import torch
import logging
from datetime import datetime
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/glpi_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GLPIValidator:
    def __init__(self, config_path="../../config/system.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'scenarios': {},
            'performance': {},
            'summary': {}
        }
        
    def load_config(self):
        """Carrega configuração do sistema"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def load_ai_model(self, model_name="microsoft/DialoGPT-small"):
        """Carrega modelo AI para testes"""
        logger.info(f"🤖 Carregando modelo: {model_name}")
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            logger.info(f"  ✅ Modelo carregado com sucesso")
            return tokenizer, model
            
        except Exception as e:
            logger.error(f"  ❌ Erro ao carregar modelo: {e}")
            return None, None
    
    def generate_response(self, tokenizer, model, prompt, max_length=100):
        """Gera resposta usando o modelo AI"""
        try:
            inputs = tokenizer.encode(prompt, return_tensors='pt')
            if torch.cuda.is_available():
                inputs = inputs.cuda()
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(prompt):].strip()
            
        except Exception as e:
            logger.error(f"Erro na geração: {e}")
            return None
    
    def validate_ticket_management(self, tokenizer, model):
        """Valida cenários de gerenciamento de tickets"""
        logger.info("🎫 Validando gerenciamento de tickets...")
        
        scenarios = [
            {
                'name': 'Criação de Ticket',
                'prompt': 'Como criar um novo ticket de suporte no GLPI para problema de impressora?',
                'expected_keywords': ['ticket', 'suporte', 'impressora', 'criar']
            },
            {
                'name': 'Status de Ticket',
                'prompt': 'Qual o status atual do ticket #12345 no sistema GLPI?',
                'expected_keywords': ['status', 'ticket', '12345', 'sistema']
            },
            {
                'name': 'Atribuição de Ticket',
                'prompt': 'Como atribuir o ticket #67890 para o técnico João Silva?',
                'expected_keywords': ['atribuir', 'ticket', 'técnico', 'João']
            }
        ]
        
        results = []
        
        for scenario in scenarios:
            logger.info(f"  🔍 Testando: {scenario['name']}")
            
            response = self.generate_response(tokenizer, model, scenario['prompt'])
            
            if response:
                # Verificar palavras-chave
                keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                                   if keyword.lower() in response.lower())
                keyword_score = keywords_found / len(scenario['expected_keywords'])
                
                result = {
                    'scenario': scenario['name'],
                    'prompt': scenario['prompt'],
                    'response': response,
                    'keyword_score': keyword_score,
                    'success': keyword_score > 0.3
                }
                
                logger.info(f"    📊 Score: {keyword_score:.1%}")
                logger.info(f"    🤖 Resposta: {response[:100]}...")
            else:
                result = {
                    'scenario': scenario['name'],
                    'success': False,
                    'error': 'Falha na geração'
                }
            
            results.append(result)
        
        self.validation_results['scenarios']['ticket_management'] = results
        success_rate = sum(1 for r in results if r.get('success', False)) / len(results)
        
        logger.info(f"  📈 Taxa de sucesso: {success_rate:.1%}")
        return success_rate > 0.6
    
    def validate_asset_management(self, tokenizer, model):
        """Valida cenários de gerenciamento de ativos"""
        logger.info("💻 Validando gerenciamento de ativos...")
        
        scenarios = [
            {
                'name': 'Consulta de Equipamento',
                'prompt': 'Mostrar informações do computador com ID 12345 no inventário GLPI',
                'expected_keywords': ['computador', 'ID', '12345', 'inventário']
            },
            {
                'name': 'Status de Manutenção',
                'prompt': 'Verificar status de manutenção da impressora HP LaserJet no setor TI',
                'expected_keywords': ['manutenção', 'impressora', 'HP', 'setor']
            },
            {
                'name': 'Localização de Ativo',
                'prompt': 'Onde está localizado o servidor DELL-SRV-001 no GLPI?',
                'expected_keywords': ['localizado', 'servidor', 'DELL', 'GLPI']
            }
        ]
        
        results = []
        
        for scenario in scenarios:
            logger.info(f"  🔍 Testando: {scenario['name']}")
            
            response = self.generate_response(tokenizer, model, scenario['prompt'])
            
            if response:
                keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                                   if keyword.lower() in response.lower())
                keyword_score = keywords_found / len(scenario['expected_keywords'])
                
                result = {
                    'scenario': scenario['name'],
                    'prompt': scenario['prompt'],
                    'response': response,
                    'keyword_score': keyword_score,
                    'success': keyword_score > 0.3
                }
                
                logger.info(f"    📊 Score: {keyword_score:.1%}")
            else:
                result = {
                    'scenario': scenario['name'],
                    'success': False,
                    'error': 'Falha na geração'
                }
            
            results.append(result)
        
        self.validation_results['scenarios']['asset_management'] = results
        success_rate = sum(1 for r in results if r.get('success', False)) / len(results)
        
        logger.info(f"  📈 Taxa de sucesso: {success_rate:.1%}")
        return success_rate > 0.6
    
    def validate_reporting(self, tokenizer, model):
        """Valida cenários de relatórios"""
        logger.info("📊 Validando geração de relatórios...")
        
        scenarios = [
            {
                'name': 'Relatório de Incidentes',
                'prompt': 'Gerar relatório mensal de incidentes por categoria no GLPI',
                'expected_keywords': ['relatório', 'mensal', 'incidentes', 'categoria']
            },
            {
                'name': 'Dashboard de Performance',
                'prompt': 'Criar dashboard com métricas de performance do help desk',
                'expected_keywords': ['dashboard', 'métricas', 'performance', 'help desk']
            },
            {
                'name': 'Análise de Tendências',
                'prompt': 'Analisar tendências de chamados dos últimos 6 meses',
                'expected_keywords': ['analisar', 'tendências', 'chamados', 'meses']
            }
        ]
        
        results = []
        
        for scenario in scenarios:
            logger.info(f"  🔍 Testando: {scenario['name']}")
            
            response = self.generate_response(tokenizer, model, scenario['prompt'])
            
            if response:
                keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                                   if keyword.lower() in response.lower())
                keyword_score = keywords_found / len(scenario['expected_keywords'])
                
                result = {
                    'scenario': scenario['name'],
                    'prompt': scenario['prompt'],
                    'response': response,
                    'keyword_score': keyword_score,
                    'success': keyword_score > 0.3
                }
                
                logger.info(f"    📊 Score: {keyword_score:.1%}")
            else:
                result = {
                    'scenario': scenario['name'],
                    'success': False,
                    'error': 'Falha na geração'
                }
            
            results.append(result)
        
        self.validation_results['scenarios']['reporting'] = results
        success_rate = sum(1 for r in results if r.get('success', False)) / len(results)
        
        logger.info(f"  📈 Taxa de sucesso: {success_rate:.1%}")
        return success_rate > 0.6
    
    def measure_performance(self, tokenizer, model):
        """Mede performance do sistema"""
        logger.info("⚡ Medindo performance...")
        
        import time
        
        test_prompts = [
            "Status do ticket 123",
            "Criar novo chamado",
            "Relatório mensal",
            "Localizar equipamento",
            "Atualizar inventário"
        ]
        
        response_times = []
        
        for prompt in test_prompts:
            start_time = time.time()
            response = self.generate_response(tokenizer, model, prompt, max_length=50)
            end_time = time.time()
            
            if response:
                response_time = end_time - start_time
                response_times.append(response_time)
                logger.info(f"  ⏱️ '{prompt}': {response_time:.2f}s")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            self.validation_results['performance'] = {
                'average_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'total_tests': len(response_times)
            }
            
            logger.info(f"  📊 Tempo médio: {avg_response_time:.2f}s")
            logger.info(f"  📊 Tempo máximo: {max_response_time:.2f}s")
            logger.info(f"  📊 Tempo mínimo: {min_response_time:.2f}s")
            
            return avg_response_time < 5.0  # Menos de 5 segundos em média
        
        return False
    
    def run_validation(self):
        """Executa validação completa"""
        logger.info("🚀 Iniciando validação GLPI...")
        
        # Carregar modelo
        tokenizer, model = self.load_ai_model()
        
        if tokenizer is None or model is None:
            logger.error("❌ Falha no carregamento do modelo")
            return False
        
        # Executar validações
        ticket_ok = self.validate_ticket_management(tokenizer, model)
        asset_ok = self.validate_asset_management(tokenizer, model)
        report_ok = self.validate_reporting(tokenizer, model)
        performance_ok = self.measure_performance(tokenizer, model)
        
        # Calcular resumo
        total_scenarios = 9  # 3 + 3 + 3
        successful_scenarios = 0
        
        for category in self.validation_results['scenarios'].values():
            successful_scenarios += sum(1 for r in category if r.get('success', False))
        
        overall_success = all([ticket_ok, asset_ok, report_ok, performance_ok])
        
        self.validation_results['summary'] = {
            'total_scenarios': total_scenarios,
            'successful_scenarios': successful_scenarios,
            'scenario_success_rate': successful_scenarios / total_scenarios,
            'ticket_management': ticket_ok,
            'asset_management': asset_ok,
            'reporting': report_ok,
            'performance': performance_ok,
            'overall_success': overall_success
        }
        
        # Relatório final
        logger.info("\n" + "="*60)
        logger.info("RELATÓRIO DE VALIDAÇÃO GLPI")
        logger.info("="*60)
        logger.info(f"✅ Cenários bem-sucedidos: {successful_scenarios}/{total_scenarios}")
        logger.info(f"📊 Taxa de sucesso: {(successful_scenarios/total_scenarios):.1%}")
        logger.info(f"🎫 Gerenciamento de Tickets: {'✅' if ticket_ok else '❌'}")
        logger.info(f"💻 Gerenciamento de Ativos: {'✅' if asset_ok else '❌'}")
        logger.info(f"📊 Relatórios: {'✅' if report_ok else '❌'}")
        logger.info(f"⚡ Performance: {'✅' if performance_ok else '❌'}")
        
        if overall_success:
            logger.info("🎉 Sistema validado para produção GLPI!")
        else:
            logger.warning("⚠️ Sistema precisa de ajustes antes da produção")
        
        # Salvar resultados
        self.save_results()
        
        return overall_success
    
    def save_results(self):
        """Salva resultados da validação"""
        results_path = Path("reports/glpi_validation_results.json")
        results_path.parent.mkdir(exist_ok=True)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados salvos em: {results_path}")

def main():
    """Função principal"""
    print("🎯 GLPI Dashboard - Validação de Integração AI")
    print("="*50)
    
    validator = GLPIValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎉 Validação concluída com sucesso!")
        return 0
    else:
        print("\n❌ Validação falhou. Verifique os logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())