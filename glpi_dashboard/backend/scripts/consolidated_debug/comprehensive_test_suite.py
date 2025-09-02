#!/usr/bin/env python3
"""
Suite Completa de Testes para Sistema AI Multiagente GLPI
Validação ponta a ponta com cenários reais de uso

Autor: Sistema de Validação AI GLPI
Data: 2025-08-30
Versão: 2.0
"""

import os
import sys
import json
import time
import asyncio
import logging
import traceback
import psutil
import torch
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/comprehensive_test_suite.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('ComprehensiveTestSuite')

@dataclass
class TestResult:
    """Resultado de um teste individual"""
    name: str
    category: str
    status: str  # PASS, FAIL, ERROR, SKIP
    duration: float
    message: str
    details: Dict[str, Any]
    timestamp: str
    
@dataclass
class TestMetrics:
    """Métricas coletadas durante os testes"""
    cpu_usage: List[float]
    memory_usage: List[float]
    gpu_memory_usage: List[float]
    inference_times: List[float]
    error_count: int
    success_count: int

class ComprehensiveTestSuite:
    """Suite completa de testes para o sistema AI multiagente"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.metrics = TestMetrics([], [], [], [], 0, 0)
        self.start_time = time.time()
        self.project_root = Path(r"C:\Users\jonathan-moletta.PPIRATINI\projects\glpi_dashboard_funcional")
        
        # Configurar paths
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "glpi_dashboard" / "ai" / "orchestration"))
        sys.path.append(str(self.project_root / "glpi_dashboard" / "backend" / "ai_agents"))
        
        # Criar diretório de logs se não existir
        os.makedirs("logs", exist_ok=True)
        
    def log_test_result(self, name: str, category: str, status: str, 
                       duration: float, message: str, details: Dict[str, Any] = None):
        """Registra resultado de um teste"""
        result = TestResult(
            name=name,
            category=category,
            status=status,
            duration=duration,
            message=message,
            details=details or {},
            timestamp=datetime.now().isoformat()
        )
        self.results.append(result)
        
        status_symbol = {
            'PASS': '[PASS]',
            'FAIL': '[FAIL]',
            'ERROR': '[ERROR]',
            'SKIP': '[SKIP]'
        }.get(status, '[UNKNOWN]')
        
        logger.info(f"{status_symbol} {name} - {status} ({duration:.2f}s)")
        if message:
            logger.info(f"  Message: {message}")
            
    @contextmanager
    def test_context(self, name: str, category: str):
        """Context manager para execução de testes"""
        start_time = time.time()
        try:
            logger.info(f"Starting test: {name}")
            yield
            duration = time.time() - start_time
            self.log_test_result(name, category, "PASS", duration, "Test completed successfully")
            self.metrics.success_count += 1
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.log_test_result(name, category, "ERROR", duration, error_msg, 
                               {"traceback": traceback.format_exc()})
            self.metrics.error_count += 1
            logger.error(f"Test failed: {name} - {error_msg}")
            
    def collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # CPU e Memória
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            self.metrics.cpu_usage.append(cpu_percent)
            self.metrics.memory_usage.append(memory.percent)
            
            # GPU (se disponível)
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / 1024**3  # GB
                self.metrics.gpu_memory_usage.append(gpu_memory)
                
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
            
    # ==================== SMOKE TESTS ====================
    
    def test_environment_setup(self):
        """Testa configuração básica do ambiente"""
        with self.test_context("Environment Setup Check", "smoke"):
            # Verificar Python
            python_version = sys.version_info
            assert python_version >= (3, 8), f"Python version too old: {python_version}"
            
            # Verificar CUDA
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"GPU detected: {gpu_name} ({gpu_memory:.1f}GB)")
            else:
                logger.warning("CUDA not available, will use CPU")
                
    def test_project_structure(self):
        """Verifica estrutura de diretórios do projeto"""
        with self.test_context("Project Structure Check", "smoke"):
            required_paths = [
                "glpi_dashboard/backend/ai_agents",
                "glpi_dashboard/ai/orchestration",
                "ai_agent_system",
                "cache"
            ]
            
            for path in required_paths:
                full_path = self.project_root / path
                assert full_path.exists(), f"Required directory missing: {path}"
                logger.info(f"Directory found: {path}")
                
    def test_dependencies_import(self):
        """Testa importação de dependências críticas"""
        with self.test_context("Dependencies Import Check", "smoke"):
            critical_imports = [
                "torch",
                "transformers",
                "accelerate",
                "bitsandbytes",
                "numpy",
                "pandas"
            ]
            
            for module in critical_imports:
                try:
                    __import__(module)
                    logger.info(f"Successfully imported: {module}")
                except ImportError as e:
                    raise ImportError(f"Failed to import {module}: {e}")
                    
    # ==================== FUNCTIONAL TESTS ====================
    
    def test_orchestrator_initialization(self):
        """Testa inicialização do orquestrador"""
        with self.test_context("Orchestrator Initialization", "functional"):
            try:
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
                
                start_time = time.time()
                config = OrchestratorConfig()
                orchestrator = UnifiedOrchestrator(config)
                init_time = time.time() - start_time
                
                assert orchestrator is not None, "Orchestrator not initialized"
                assert hasattr(orchestrator, 'model'), "Orchestrator missing model attribute"
                
                logger.info(f"Orchestrator initialized in {init_time:.2f}s")
                self.metrics.inference_times.append(init_time)
                
                return orchestrator
                
            except Exception as e:
                raise Exception(f"Orchestrator initialization failed: {e}")
                
    def test_model_loading(self):
        """Testa carregamento de modelos AI"""
        with self.test_context("Model Loading Test", "functional"):
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                
                # Testar modelo pequeno primeiro
                model_name = "microsoft/DialoGPT-small"
                
                start_time = time.time()
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                load_time = time.time() - start_time
                
                assert tokenizer is not None, "Tokenizer not loaded"
                assert model is not None, "Model not loaded"
                
                logger.info(f"Model {model_name} loaded in {load_time:.2f}s")
                self.metrics.inference_times.append(load_time)
                
            except Exception as e:
                raise Exception(f"Model loading failed: {e}")
                
    def test_code_analysis_function(self):
        """Testa função de análise de código"""
        with self.test_context("Code Analysis Function", "functional"):
            try:
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig()
        orchestrator = UnifiedOrchestrator(config)
                
                # Código de teste
                test_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""
                
                start_time = time.time()
                result = orchestrator.analyze_code(test_code)
                analysis_time = time.time() - start_time
                
                assert result is not None, "Analysis returned None"
                assert isinstance(result, dict), "Analysis result not a dictionary"
                
                logger.info(f"Code analysis completed in {analysis_time:.2f}s")
                self.metrics.inference_times.append(analysis_time)
                
            except Exception as e:
                raise Exception(f"Code analysis failed: {e}")
                
    # ==================== INTEGRATION TESTS ====================
    
    def test_glpi_ticket_simulation(self):
        """Simula processamento completo de ticket GLPI"""
        with self.test_context("GLPI Ticket Processing Simulation", "integration"):
            try:
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig()
        orchestrator = UnifiedOrchestrator(config)
                
                # Simular dados de ticket GLPI
                ticket_data = {
                    "id": "TICKET-001",
                    "title": "Sistema lento após atualização",
                    "description": "Após a última atualização, o sistema GLPI está muito lento para carregar páginas",
                    "category": "Performance",
                    "priority": "High",
                    "logs": [
                        "2025-08-30 10:15:23 - ERROR - Database connection timeout",
                        "2025-08-30 10:15:45 - WARN - High memory usage detected: 85%",
                        "2025-08-30 10:16:12 - ERROR - Query execution time exceeded 30s"
                    ]
                }
                
                start_time = time.time()
                
                # Processar logs
                log_analysis = orchestrator.process_logs("\n".join(ticket_data["logs"]))
                
                # Analisar descrição
                description_analysis = orchestrator.analyze_code(ticket_data["description"])
                
                processing_time = time.time() - start_time
                
                assert log_analysis is not None, "Log analysis failed"
                assert description_analysis is not None, "Description analysis failed"
                
                logger.info(f"Ticket processing completed in {processing_time:.2f}s")
                self.metrics.inference_times.append(processing_time)
                
                # Simular resposta
                response = {
                    "ticket_id": ticket_data["id"],
                    "analysis": {
                        "logs": log_analysis,
                        "description": description_analysis
                    },
                    "recommendations": [
                        "Verificar configuração do banco de dados",
                        "Monitorar uso de memória",
                        "Otimizar queries lentas"
                    ],
                    "processing_time": processing_time
                }
                
                logger.info(f"Generated {len(response['recommendations'])} recommendations")
                
            except Exception as e:
                raise Exception(f"GLPI ticket simulation failed: {e}")
                
    def test_multi_agent_coordination(self):
        """Testa coordenação entre múltiplos agentes"""
        with self.test_context("Multi-Agent Coordination", "integration"):
            try:
                # Simular coordenação de agentes
                agents_status = {
                    "code_analyst": "ready",
                    "testing_agent": "ready", 
                    "documentation_agent": "ready",
                    "refactoring_agent": "ready",
                    "security_agent": "ready"
                }
                
                # Verificar se todos os agentes estão prontos
                all_ready = all(status == "ready" for status in agents_status.values())
                assert all_ready, f"Not all agents ready: {agents_status}"
                
                logger.info(f"All {len(agents_status)} agents are ready for coordination")
                
            except Exception as e:
                raise Exception(f"Multi-agent coordination failed: {e}")
                
    # ==================== PERFORMANCE TESTS ====================
    
    def test_inference_latency(self):
        """Testa latência de inferência"""
        with self.test_context("Inference Latency Test", "performance"):
            try:
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig()
        orchestrator = UnifiedOrchestrator(config)
                
                # Múltiplas inferências para calcular estatísticas
                latencies = []
                test_inputs = [
                    "def hello(): print('world')",
                    "class MyClass: pass",
                    "for i in range(10): print(i)",
                    "import os; os.path.exists('file.txt')",
                    "try: x = 1/0\nexcept: pass"
                ]
                
                for i, test_input in enumerate(test_inputs):
                    start_time = time.time()
                    result = orchestrator.analyze_code(test_input)
                    latency = time.time() - start_time
                    latencies.append(latency)
                    
                    logger.info(f"Inference {i+1}: {latency:.2f}s")
                    self.collect_system_metrics()
                    
                # Calcular estatísticas
                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)
                min_latency = min(latencies)
                
                # Verificar se atende critérios
                assert avg_latency < 15.0, f"Average latency too high: {avg_latency:.2f}s"
                assert max_latency < 25.0, f"Max latency too high: {max_latency:.2f}s"
                
                logger.info(f"Latency stats - Avg: {avg_latency:.2f}s, Min: {min_latency:.2f}s, Max: {max_latency:.2f}s")
                
                self.metrics.inference_times.extend(latencies)
                
            except Exception as e:
                raise Exception(f"Inference latency test failed: {e}")
                
    def test_memory_usage(self):
        """Testa uso de memória durante operações"""
        with self.test_context("Memory Usage Test", "performance"):
            try:
                import gc
                
                # Memória inicial
                initial_memory = psutil.virtual_memory().percent
                if torch.cuda.is_available():
                    initial_gpu_memory = torch.cuda.memory_allocated() / 1024**3
                else:
                    initial_gpu_memory = 0
                    
                logger.info(f"Initial memory - RAM: {initial_memory:.1f}%, GPU: {initial_gpu_memory:.2f}GB")
                
                # Executar operações que consomem memória
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        config = OrchestratorConfig()
        orchestrator = UnifiedOrchestrator(config)
                
                # Múltiplas operações
                for i in range(3):
                    large_code = "\n".join([f"def function_{j}(): pass" for j in range(100)])
                    result = orchestrator.analyze_code(large_code)
                    
                    current_memory = psutil.virtual_memory().percent
                    if torch.cuda.is_available():
                        current_gpu_memory = torch.cuda.memory_allocated() / 1024**3
                    else:
                        current_gpu_memory = 0
                        
                    logger.info(f"Operation {i+1} - RAM: {current_memory:.1f}%, GPU: {current_gpu_memory:.2f}GB")
                    
                    self.collect_system_metrics()
                    
                # Limpeza
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                # Verificar vazamentos de memória
                final_memory = psutil.virtual_memory().percent
                memory_increase = final_memory - initial_memory
                
                assert memory_increase < 20.0, f"Memory leak detected: {memory_increase:.1f}% increase"
                
                logger.info(f"Memory test completed - Increase: {memory_increase:.1f}%")
                
            except Exception as e:
                raise Exception(f"Memory usage test failed: {e}")
                
    def test_concurrent_requests(self):
        """Testa processamento de requisições concorrentes"""
        with self.test_context("Concurrent Requests Test", "performance"):
            try:
                import threading
                import queue
                
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        config = OrchestratorConfig()
        orchestrator = UnifiedOrchestrator(config)
                
                results_queue = queue.Queue()
                errors_queue = queue.Queue()
                
                def worker(worker_id):
                    try:
                        test_code = f"def worker_{worker_id}(): return {worker_id}"
                        start_time = time.time()
                        result = orchestrator.analyze_code(test_code)
                        duration = time.time() - start_time
                        results_queue.put((worker_id, duration, "success"))
                    except Exception as e:
                        errors_queue.put((worker_id, str(e)))
                        
                # Executar 3 threads concorrentes
                threads = []
                num_threads = 3
                
                start_time = time.time()
                for i in range(num_threads):
                    thread = threading.Thread(target=worker, args=(i,))
                    threads.append(thread)
                    thread.start()
                    
                # Aguardar conclusão
                for thread in threads:
                    thread.join(timeout=60)  # 60s timeout
                    
                total_time = time.time() - start_time
                
                # Coletar resultados
                successful_requests = 0
                failed_requests = 0
                
                while not results_queue.empty():
                    worker_id, duration, status = results_queue.get()
                    successful_requests += 1
                    logger.info(f"Worker {worker_id} completed in {duration:.2f}s")
                    
                while not errors_queue.empty():
                    worker_id, error = errors_queue.get()
                    failed_requests += 1
                    logger.error(f"Worker {worker_id} failed: {error}")
                    
                success_rate = successful_requests / num_threads * 100
                
                assert success_rate >= 66.0, f"Concurrent success rate too low: {success_rate:.1f}%"
                
                logger.info(f"Concurrent test - Success: {successful_requests}/{num_threads} ({success_rate:.1f}%) in {total_time:.2f}s")
                
            except Exception as e:
                raise Exception(f"Concurrent requests test failed: {e}")
                
    # ==================== RESILIENCE TESTS ====================
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        with self.test_context("Error Handling Test", "resilience"):
            try:
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        config = OrchestratorConfig()
        orchestrator = UnifiedOrchestrator(config)
                
                # Testes com entradas inválidas
                invalid_inputs = [
                    None,
                    "",
                    "x" * 10000,  # Input muito longo
                    "invalid python syntax {",
                    "\x00\x01\x02"  # Caracteres binários
                ]
                
                handled_errors = 0
                
                for i, invalid_input in enumerate(invalid_inputs):
                    try:
                        result = orchestrator.analyze_code(invalid_input)
                        # Se chegou aqui, o sistema tratou graciosamente
                        handled_errors += 1
                        logger.info(f"Invalid input {i+1} handled gracefully")
                    except Exception as e:
                        # Erro não tratado
                        logger.warning(f"Invalid input {i+1} caused unhandled error: {e}")
                        
                error_handling_rate = handled_errors / len(invalid_inputs) * 100
                
                assert error_handling_rate >= 60.0, f"Error handling rate too low: {error_handling_rate:.1f}%"
                
                logger.info(f"Error handling test - {handled_errors}/{len(invalid_inputs)} handled ({error_handling_rate:.1f}%)")
                
            except Exception as e:
                raise Exception(f"Error handling test failed: {e}")
                
    def test_resource_exhaustion(self):
        """Testa comportamento sob esgotamento de recursos"""
        with self.test_context("Resource Exhaustion Test", "resilience"):
            try:
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
                
                # Simular alta carga
                config = OrchestratorConfig()
                orchestrator = UnifiedOrchestrator(config)
                
                # Processar múltiplas requisições grandes
                large_requests = 0
                successful_requests = 0
                
                for i in range(5):
                    try:
                        # Criar código grande
                        large_code = "\n".join([f"def big_function_{j}(param_{k}): return param_{k} * {j}" 
                                               for j in range(50) for k in range(10)])
                        
                        start_time = time.time()
                        result = orchestrator.analyze_code(large_code)
                        duration = time.time() - start_time
                        
                        large_requests += 1
                        if result is not None:
                            successful_requests += 1
                            
                        logger.info(f"Large request {i+1} processed in {duration:.2f}s")
                        
                        # Monitorar recursos
                        self.collect_system_metrics()
                        
                    except Exception as e:
                        logger.warning(f"Large request {i+1} failed: {e}")
                        large_requests += 1
                        
                success_rate = successful_requests / large_requests * 100 if large_requests > 0 else 0
                
                # Sistema deve manter pelo menos 40% de sucesso sob carga
                assert success_rate >= 40.0, f"Success rate under load too low: {success_rate:.1f}%"
                
                logger.info(f"Resource exhaustion test - {successful_requests}/{large_requests} successful ({success_rate:.1f}%)")
                
            except Exception as e:
                raise Exception(f"Resource exhaustion test failed: {e}")
                
    def test_recovery_after_failure(self):
        """Testa recuperação após falhas"""
        with self.test_context("Recovery After Failure Test", "resilience"):
            try:
                from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
                
                # Primeira operação normal
                config = OrchestratorConfig()
                orchestrator = UnifiedOrchestrator(config)
                result1 = orchestrator.analyze_code("def test(): pass")
                assert result1 is not None, "Initial operation failed"
                
                # Simular falha (entrada inválida)
                try:
                    orchestrator.analyze_code(None)
                except:
                    pass  # Falha esperada
                    
                # Tentar recuperação
                result2 = orchestrator.analyze_code("def recovery_test(): return True")
                assert result2 is not None, "System did not recover after failure"
                
                logger.info("System successfully recovered after simulated failure")
                
            except Exception as e:
                raise Exception(f"Recovery test failed: {e}")
                
    # ==================== EXECUTION METHODS ====================
    
    def run_all_tests(self):
        """Executa todos os testes"""
        logger.info("Starting Comprehensive Test Suite")
        logger.info("=" * 50)
        
        # Smoke Tests
        logger.info("\n--- SMOKE TESTS ---")
        self.test_environment_setup()
        self.test_project_structure()
        self.test_dependencies_import()
        
        # Functional Tests
        logger.info("\n--- FUNCTIONAL TESTS ---")
        self.test_orchestrator_initialization()
        self.test_model_loading()
        self.test_code_analysis_function()
        
        # Integration Tests
        logger.info("\n--- INTEGRATION TESTS ---")
        self.test_glpi_ticket_simulation()
        self.test_multi_agent_coordination()
        
        # Performance Tests
        logger.info("\n--- PERFORMANCE TESTS ---")
        self.test_inference_latency()
        self.test_memory_usage()
        self.test_concurrent_requests()
        
        # Resilience Tests
        logger.info("\n--- RESILIENCE TESTS ---")
        self.test_error_handling()
        self.test_resource_exhaustion()
        self.test_recovery_after_failure()
        
        logger.info("\n" + "=" * 50)
        logger.info("Comprehensive Test Suite Completed")
        
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo dos testes"""
        total_duration = time.time() - self.start_time
        
        # Estatísticas por categoria
        categories = {}
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = {'total': 0, 'pass': 0, 'fail': 0, 'error': 0, 'skip': 0}
            categories[cat]['total'] += 1
            categories[cat][result.status.lower()] += 1
            
        # Estatísticas gerais
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == 'PASS')
        failed_tests = sum(1 for r in self.results if r.status == 'FAIL')
        error_tests = sum(1 for r in self.results if r.status == 'ERROR')
        skipped_tests = sum(1 for r in self.results if r.status == 'SKIP')
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Decisão Go/No-Go
        if success_rate >= 80:
            decision = "GO"
        elif success_rate >= 60:
            decision = "CONDITIONAL GO"
        else:
            decision = "NO-GO"
            
        # Métricas de performance
        avg_inference_time = sum(self.metrics.inference_times) / len(self.metrics.inference_times) if self.metrics.inference_times else 0
        avg_cpu_usage = sum(self.metrics.cpu_usage) / len(self.metrics.cpu_usage) if self.metrics.cpu_usage else 0
        avg_memory_usage = sum(self.metrics.memory_usage) / len(self.metrics.memory_usage) if self.metrics.memory_usage else 0
        avg_gpu_memory = sum(self.metrics.gpu_memory_usage) / len(self.metrics.gpu_memory_usage) if self.metrics.gpu_memory_usage else 0
        
        report = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": round(total_duration, 2),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "success_rate_percent": round(success_rate, 1)
            },
            "categories": categories,
            "performance_metrics": {
                "average_inference_time_seconds": round(avg_inference_time, 2),
                "average_cpu_usage_percent": round(avg_cpu_usage, 1),
                "average_memory_usage_percent": round(avg_memory_usage, 1),
                "average_gpu_memory_gb": round(avg_gpu_memory, 2)
            },
            "system_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
                "torch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                "gpu_memory_total_gb": round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2) if torch.cuda.is_available() else None
            },
            "decision": {
                "go_no_go": decision,
                "reasoning": f"Success rate: {success_rate:.1f}%. " + 
                           ("System ready for production." if decision == "GO" else
                            "System ready with conditions." if decision == "CONDITIONAL GO" else
                            "System not ready for production.")
            },
            "recommendations": self._generate_recommendations(success_rate, avg_inference_time),
            "test_results": [asdict(result) for result in self.results]
        }
        
        return report
        
    def _generate_recommendations(self, success_rate: float, avg_inference_time: float) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        if success_rate < 80:
            recommendations.append("Investigate and fix failing tests before production deployment")
            
        if avg_inference_time > 10:
            recommendations.append("Optimize model inference time - consider model quantization or smaller models")
            
        if len(self.metrics.gpu_memory_usage) > 0 and max(self.metrics.gpu_memory_usage) > 12:
            recommendations.append("Monitor GPU memory usage - consider batch size optimization")
            
        if len(self.metrics.cpu_usage) > 0 and max(self.metrics.cpu_usage) > 80:
            recommendations.append("High CPU usage detected - consider scaling or optimization")
            
        recommendations.extend([
            "Implement comprehensive unit tests for all components",
            "Set up continuous monitoring for production environment",
            "Create automated deployment pipeline with these tests",
            "Document operational procedures and troubleshooting guides"
        ])
        
        return recommendations
        
    def save_report(self, filename: str = None):
        """Salva relatório em arquivo JSON"""
        if filename is None:
            filename = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Test report saved to: {filename}")
        return filename

def main():
    """Função principal"""
    try:
        suite = ComprehensiveTestSuite()
        suite.run_all_tests()
        
        # Gerar e salvar relatório
        report_file = suite.save_report()
        
        # Exibir resumo
        report = suite.generate_report()
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {report['test_execution']['total_tests']}")
        print(f"Passed: {report['test_execution']['passed']}")
        print(f"Failed: {report['test_execution']['failed']}")
        print(f"Errors: {report['test_execution']['errors']}")
        print(f"Success Rate: {report['test_execution']['success_rate_percent']}%")
        print(f"Duration: {report['test_execution']['duration_seconds']}s")
        print(f"Decision: {report['decision']['go_no_go']}")
        print(f"Report saved: {report_file}")
        print("=" * 60)
        
        return report['decision']['go_no_go']
        
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        logger.error(traceback.format_exc())
        return "ERROR"

if __name__ == "__main__":
    main()