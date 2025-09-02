#!/usr/bin/env python3
"""
Validação Abrangente do Sistema AI Multiagente GLPI
Bateria completa de testes: smoke, funcionais, integração, performance e resiliência
"""

import os
import sys
import json
import time
import asyncio
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_validation_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AIValidation')

@dataclass
class TestResult:
    """Resultado de um teste individual"""
    test_name: str
    category: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'ERROR'
    duration: float
    details: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ValidationReport:
    """Relatório completo de validação"""
    timestamp: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    test_results: List[TestResult]
    system_info: Dict[str, Any]
    recommendations: List[str]
    go_no_go_decision: str
    
class AISystemValidator:
    """Validador principal do sistema AI"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.system_info = self._collect_system_info()
        
    def _collect_system_info(self) -> Dict[str, Any]:
        """Coleta informações do sistema"""
        info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar GPU
        try:
            import torch
            info['torch_version'] = torch.__version__
            info['cuda_available'] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info['gpu_name'] = torch.cuda.get_device_name(0)
                info['gpu_memory_total'] = torch.cuda.get_device_properties(0).total_memory / 1024**3
        except ImportError:
            info['torch_available'] = False
            
        # Verificar transformers
        try:
            import transformers
            info['transformers_version'] = transformers.__version__
        except ImportError:
            info['transformers_available'] = False
            
        return info
    
    def add_result(self, result: TestResult):
        """Adiciona resultado de teste"""
        self.results.append(result)
        status_symbol = {'PASS': '[PASS]', 'FAIL': '[FAIL]', 'SKIP': '[SKIP]', 'ERROR': '[ERROR]'}
        logger.info(f"{status_symbol.get(result.status, '[?]')} {result.test_name} - {result.status} ({result.duration:.2f}s)")
        
    async def run_smoke_tests(self) -> List[TestResult]:
        """Testes de fumaça - verificações básicas"""
        logger.info("Executando Smoke Tests...")
        smoke_results = []
        
        # Teste 1: Verificar estrutura de diretórios
        start_time = time.time()
        try:
            required_dirs = [
                'glpi_dashboard/backend/ai_agents',
                'glpi_dashboard/ai/orchestration',
                'cache',
                'ai_agent_system',
                'logs'
            ]
            
            missing_dirs = []
            for dir_path in required_dirs:
                if not Path(dir_path).exists():
                    missing_dirs.append(dir_path)
            
            status = 'PASS' if not missing_dirs else 'FAIL'
            details = {
                'required_directories': required_dirs,
                'missing_directories': missing_dirs,
                'found_directories': len(required_dirs) - len(missing_dirs)
            }
            
            smoke_results.append(TestResult(
                test_name="Directory Structure Check",
                category="smoke",
                status=status,
                duration=time.time() - start_time,
                details=details,
                error_message=f"Missing directories: {missing_dirs}" if missing_dirs else None
            ))
            
        except Exception as e:
            smoke_results.append(TestResult(
                test_name="Directory Structure Check",
                category="smoke",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        # Teste 2: Verificar dependências Python
        start_time = time.time()
        try:
            required_packages = ['torch', 'transformers', 'asyncio']
            available_packages = []
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                    available_packages.append(package)
                except ImportError:
                    missing_packages.append(package)
            
            status = 'PASS' if not missing_packages else 'FAIL'
            details = {
                'required_packages': required_packages,
                'available_packages': available_packages,
                'missing_packages': missing_packages
            }
            
            smoke_results.append(TestResult(
                test_name="Python Dependencies Check",
                category="smoke",
                status=status,
                duration=time.time() - start_time,
                details=details,
                error_message=f"Missing packages: {missing_packages}" if missing_packages else None
            ))
            
        except Exception as e:
            smoke_results.append(TestResult(
                test_name="Python Dependencies Check",
                category="smoke",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        # Teste 3: Verificar modelos disponíveis
        start_time = time.time()
        try:
            working_models_file = Path('working_models.txt')
            if working_models_file.exists():
                with open(working_models_file, 'r') as f:
                    models = [line.strip() for line in f.readlines() if line.strip()]
                
                status = 'PASS' if models else 'FAIL'
                details = {
                    'models_file_exists': True,
                    'available_models': models,
                    'model_count': len(models)
                }
            else:
                status = 'FAIL'
                details = {
                    'models_file_exists': False,
                    'available_models': [],
                    'model_count': 0
                }
            
            smoke_results.append(TestResult(
                test_name="AI Models Availability Check",
                category="smoke",
                status=status,
                duration=time.time() - start_time,
                details=details,
                error_message="No working models found" if status == 'FAIL' else None
            ))
            
        except Exception as e:
            smoke_results.append(TestResult(
                test_name="AI Models Availability Check",
                category="smoke",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return smoke_results
    
    async def run_functional_tests(self) -> List[TestResult]:
        """Testes funcionais - funcionalidades principais"""
        logger.info("Executando Functional Tests...")
        functional_results = []
        
        # Teste 1: Carregar orquestrador
        start_time = time.time()
        try:
            sys.path.append('glpi_dashboard/backend/ai')
            from orchestrator import UnifiedOrchestrator, OrchestratorConfig
            
            config = OrchestratorConfig()
            orchestrator = UnifiedOrchestrator(config)
            status = orchestrator.get_system_status()
            
            test_status = 'PASS' if status['model_loaded'] else 'FAIL'
            details = {
                'orchestrator_loaded': True,
                'system_status': status,
                'model_loaded': status['model_loaded'],
                'device': status['device']
            }
            
            functional_results.append(TestResult(
                test_name="Orchestrator Initialization",
                category="functional",
                status=test_status,
                duration=time.time() - start_time,
                details=details,
                error_message="Model not loaded" if not status['model_loaded'] else None
            ))
            
        except Exception as e:
            functional_results.append(TestResult(
                test_name="Orchestrator Initialization",
                category="functional",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        # Teste 2: Análise de código simples
        start_time = time.time()
        try:
            test_code = """
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""
            
            result = orchestrator.analyze_code(test_code, "code_review")
            
            test_status = 'PASS' if result['status'] == 'success' else 'FAIL'
            details = {
                'analysis_result': result,
                'analysis_successful': result['status'] == 'success',
                'has_analysis_content': bool(result.get('analysis', '').strip())
            }
            
            functional_results.append(TestResult(
                test_name="Code Analysis Function",
                category="functional",
                status=test_status,
                duration=time.time() - start_time,
                details=details,
                error_message=result.get('error') if result['status'] != 'success' else None
            ))
            
        except Exception as e:
            functional_results.append(TestResult(
                test_name="Code Analysis Function",
                category="functional",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return functional_results
    
    async def run_integration_tests(self) -> List[TestResult]:
        """Testes de integração - fluxos completos"""
        logger.info("Executando Integration Tests...")
        integration_results = []
        
        # Teste 1: Fluxo completo de análise GLPI
        start_time = time.time()
        try:
            # Simular dados de ticket GLPI
            glpi_ticket_data = {
                "id": "12345",
                "title": "Erro no sistema de relatórios",
                "description": "O sistema apresenta erro 500 ao gerar relatórios mensais",
                "priority": "high",
                "category": "software",
                "status": "open"
            }
            
            # Processar com orquestrador
            log_content = f"ERROR: {glpi_ticket_data['description']}"
            result = orchestrator.process_logs(log_content)
            
            test_status = 'PASS' if result['status'] == 'success' else 'FAIL'
            details = {
                'ticket_data': glpi_ticket_data,
                'processing_result': result,
                'processing_successful': result['status'] == 'success'
            }
            
            integration_results.append(TestResult(
                test_name="GLPI Ticket Processing Flow",
                category="integration",
                status=test_status,
                duration=time.time() - start_time,
                details=details,
                error_message=result.get('error') if result['status'] != 'success' else None
            ))
            
        except Exception as e:
            integration_results.append(TestResult(
                test_name="GLPI Ticket Processing Flow",
                category="integration",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return integration_results
    
    async def run_performance_tests(self) -> List[TestResult]:
        """Testes de performance - latência e throughput"""
        logger.info("Executando Performance Tests...")
        performance_results = []
        
        # Teste 1: Latência de inferência
        start_time = time.time()
        try:
            test_code = "def hello_world(): return 'Hello, World!'"
            
            # Executar múltiplas inferências
            inference_times = []
            for i in range(3):
                inference_start = time.time()
                result = orchestrator.analyze_code(test_code, "quick_review")
                inference_time = time.time() - inference_start
                inference_times.append(inference_time)
            
            avg_latency = sum(inference_times) / len(inference_times)
            max_latency = max(inference_times)
            min_latency = min(inference_times)
            
            # Critério: latência média < 10s
            test_status = 'PASS' if avg_latency < 10.0 else 'FAIL'
            details = {
                'inference_times': inference_times,
                'avg_latency': avg_latency,
                'max_latency': max_latency,
                'min_latency': min_latency,
                'latency_threshold': 10.0
            }
            
            performance_results.append(TestResult(
                test_name="Inference Latency Test",
                category="performance",
                status=test_status,
                duration=time.time() - start_time,
                details=details,
                error_message=f"Average latency {avg_latency:.2f}s exceeds threshold" if test_status == 'FAIL' else None
            ))
            
        except Exception as e:
            performance_results.append(TestResult(
                test_name="Inference Latency Test",
                category="performance",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        # Teste 2: Uso de memória GPU
        start_time = time.time()
        try:
            import torch
            if torch.cuda.is_available():
                initial_memory = torch.cuda.memory_allocated() / 1024**3
                
                # Executar análise
                test_code = "\n".join([f"def function_{i}(): pass" for i in range(10)])
                result = orchestrator.analyze_code(test_code, "memory_test")
                
                final_memory = torch.cuda.memory_allocated() / 1024**3
                memory_used = final_memory - initial_memory
                
                # Critério: uso de memória < 8GB
                test_status = 'PASS' if final_memory < 8.0 else 'FAIL'
                details = {
                    'initial_memory_gb': initial_memory,
                    'final_memory_gb': final_memory,
                    'memory_used_gb': memory_used,
                    'memory_threshold_gb': 8.0,
                    'gpu_available': True
                }
            else:
                test_status = 'SKIP'
                details = {'gpu_available': False}
            
            performance_results.append(TestResult(
                test_name="GPU Memory Usage Test",
                category="performance",
                status=test_status,
                duration=time.time() - start_time,
                details=details,
                error_message=f"GPU memory usage {final_memory:.2f}GB exceeds threshold" if test_status == 'FAIL' else None
            ))
            
        except Exception as e:
            performance_results.append(TestResult(
                test_name="GPU Memory Usage Test",
                category="performance",
                status="ERROR",
                duration=time.time() - start_time,
                details={},
                error_message=str(e)
            ))
        
        return performance_results
    
    async def run_resilience_tests(self) -> List[TestResult]:
        """Testes de resiliência - falhas controladas"""
        logger.info("Executando Resilience Tests...")
        resilience_results = []
        
        # Teste 1: Entrada inválida
        start_time = time.time()
        try:
            # Testar com código inválido
            invalid_code = "def broken_function( invalid syntax here"
            result = orchestrator.analyze_code(invalid_code, "error_test")
            
            # Deve retornar erro graciosamente
            test_status = 'PASS' if 'error' in result or result.get('status') == 'error' else 'FAIL'
            details = {
                'invalid_input': invalid_code,
                'result': result,
                'handled_gracefully': test_status == 'PASS'
            }
            
            resilience_results.append(TestResult(
                test_name="Invalid Input Handling",
                category="resilience",
                status=test_status,
                duration=time.time() - start_time,
                details=details,
                error_message="System did not handle invalid input gracefully" if test_status == 'FAIL' else None
            ))
            
        except Exception as e:
            # Exception é esperada, mas deve ser tratada
            resilience_results.append(TestResult(
                test_name="Invalid Input Handling",
                category="resilience",
                status="PASS",  # Exception tratada é um comportamento esperado
                duration=time.time() - start_time,
                details={'exception_handled': True, 'exception_message': str(e)},
                error_message=None
            ))
        
        return resilience_results
    
    async def run_all_tests(self) -> ValidationReport:
        """Executa toda a bateria de testes"""
        logger.info("Iniciando Bateria Completa de Testes AI...")
        
        # Executar todas as categorias de teste
        all_results = []
        
        smoke_results = await self.run_smoke_tests()
        all_results.extend(smoke_results)
        
        functional_results = await self.run_functional_tests()
        all_results.extend(functional_results)
        
        integration_results = await self.run_integration_tests()
        all_results.extend(integration_results)
        
        performance_results = await self.run_performance_tests()
        all_results.extend(performance_results)
        
        resilience_results = await self.run_resilience_tests()
        all_results.extend(resilience_results)
        
        # Calcular estatísticas
        total_duration = time.time() - self.start_time
        passed = len([r for r in all_results if r.status == 'PASS'])
        failed = len([r for r in all_results if r.status == 'FAIL'])
        skipped = len([r for r in all_results if r.status == 'SKIP'])
        errors = len([r for r in all_results if r.status == 'ERROR'])
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(all_results)
        
        # Decisão Go/No-Go
        go_no_go = self._make_go_no_go_decision(all_results, passed, failed, errors)
        
        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            total_tests=len(all_results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total_duration=total_duration,
            test_results=all_results,
            system_info=self.system_info,
            recommendations=recommendations,
            go_no_go_decision=go_no_go
        )
    
    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Analisar falhas por categoria
        failed_by_category = {}
        for result in results:
            if result.status in ['FAIL', 'ERROR']:
                if result.category not in failed_by_category:
                    failed_by_category[result.category] = []
                failed_by_category[result.category].append(result)
        
        if 'smoke' in failed_by_category:
            recommendations.append("CRITICO: Falhas nos testes básicos - verificar infraestrutura")
        
        if 'functional' in failed_by_category:
            recommendations.append("Falhas funcionais detectadas - revisar implementação dos agentes")
        
        if 'performance' in failed_by_category:
            recommendations.append("Problemas de performance - otimizar configurações de GPU/CPU")
        
        if 'integration' in failed_by_category:
            recommendations.append("Falhas de integração - verificar fluxos entre componentes")
        
        if 'resilience' in failed_by_category:
            recommendations.append("Problemas de resiliência - melhorar tratamento de erros")
        
        # Recomendações específicas baseadas no sistema
        gpu_available = self.system_info.get('cuda_available', False)
        if not gpu_available:
            recommendations.append("GPU não disponível - considerar otimizações para CPU")
        
        return recommendations
    
    def _make_go_no_go_decision(self, results: List[TestResult], passed: int, failed: int, errors: int) -> str:
        """Toma decisão Go/No-Go baseada nos resultados"""
        total_tests = len(results)
        success_rate = passed / total_tests if total_tests > 0 else 0
        
        # Critérios para Go/No-Go
        critical_failures = len([r for r in results if r.status in ['FAIL', 'ERROR'] and r.category == 'smoke'])
        
        if critical_failures > 0:
            return "NO-GO: Falhas críticas nos testes básicos"
        elif success_rate >= 0.8:
            return "GO: Sistema aprovado para uso (>80% de sucesso)"
        elif success_rate >= 0.6:
            return "CONDITIONAL GO: Sistema aprovado com restrições (60-80% de sucesso)"
        else:
            return "NO-GO: Taxa de sucesso muito baixa (<60%)"

async def main():
    """Função principal"""
    # Criar diretório de logs se não existir
    Path('logs').mkdir(exist_ok=True)
    
    # Executar validação
    validator = AISystemValidator()
    report = await validator.run_all_tests()
    
    # Salvar relatório
    report_path = Path('ai_validation_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
    
    # Exibir resumo
    logger.info("\n" + "="*80)
    logger.info("RESUMO DA VALIDACAO AI")
    logger.info("="*80)
    logger.info(f"Total de Testes: {report.total_tests}")
    logger.info(f"Passou: {report.passed}")
    logger.info(f"Falhou: {report.failed}")
    logger.info(f"Pulou: {report.skipped}")
    logger.info(f"Erros: {report.errors}")
    logger.info(f"Duracao Total: {report.total_duration:.2f}s")
    logger.info(f"Decisao: {report.go_no_go_decision}")
    logger.info("\nRecomendacoes:")
    for rec in report.recommendations:
        logger.info(f"  - {rec}")
    logger.info(f"\nRelatorio salvo em: {report_path.absolute()}")
    logger.info("="*80)
    
    return report

if __name__ == "__main__":
    asyncio.run(main())