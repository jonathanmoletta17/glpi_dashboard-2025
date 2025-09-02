#!/usr/bin/env python3
"""
Script de Configuração Automática - Integração GPU e Modelos Complementares
GLPI Dashboard Project

Este script automatiza a configuração do ambiente para integração de GPU
e modelos complementares de IA para o projeto GLPI Dashboard.

Autor: Sistema de IA Colaborativo
Data: 30/01/2025
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class GPUIntegrationSetup:
    """Classe para configuração automática da integração GPU."""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.requirements = {
            'cuda_version': '11.8',
            'python_version': '3.8+',
            'min_vram': 8,  # GB
            'min_ram': 16   # GB
        }
        self.setup_log = []
        
    def _get_system_info(self) -> Dict:
        """Coleta informações do sistema."""
        info = {
            'os': platform.system(),
            'python_version': sys.version,
            'platform': platform.platform()
        }
        return info
    
    def _log_step(self, message: str, status: str = "INFO"):
        """Registra passos da configuração."""
        log_entry = f"[{status}] {message}"
        print(log_entry)
        self.setup_log.append(log_entry)
    
    def check_gpu_availability(self) -> Tuple[bool, Dict]:
        """Verifica disponibilidade e capacidades da GPU."""
        self._log_step("Verificando disponibilidade da GPU...")
        
        gpu_info = {
            'available': False,
            'name': None,
            'vram': 0,
            'cuda_version': None
        }
        
        try:
            # Tentar importar torch para verificar CUDA
            import torch
            if torch.cuda.is_available():
                gpu_info['available'] = True
                gpu_info['name'] = torch.cuda.get_device_name(0)
                gpu_info['vram'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                gpu_info['cuda_version'] = torch.version.cuda
                
                self._log_step(f"GPU encontrada: {gpu_info['name']}", "SUCCESS")
                self._log_step(f"VRAM disponível: {gpu_info['vram']:.1f}GB", "SUCCESS")
                self._log_step(f"CUDA Version: {gpu_info['cuda_version']}", "SUCCESS")
            else:
                self._log_step("CUDA não disponível", "WARNING")
                
        except ImportError:
            self._log_step("PyTorch não instalado - será instalado posteriormente", "INFO")
        except Exception as e:
            self._log_step(f"Erro ao verificar GPU: {e}", "ERROR")
            
        return gpu_info['available'], gpu_info
    
    def install_cuda_dependencies(self) -> bool:
        """Instala dependências CUDA e PyTorch."""
        self._log_step("Instalando dependências CUDA...")
        
        commands = [
            # PyTorch com suporte CUDA
            "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
            
            # TensorFlow com GPU
            "pip install tensorflow[and-cuda]",
            
            # Transformers e dependências para modelos
            "pip install transformers accelerate bitsandbytes",
            
            # Frameworks de orquestração
            "pip install langchain langchain-community",
            "pip install autogen-agentchat",
            "pip install crewai",
            
            # Utilitários adicionais
            "pip install datasets tokenizers sentencepiece",
            "pip install gradio streamlit",
            
            # Monitoramento e logging
            "pip install wandb tensorboard",
            "pip install psutil GPUtil"
        ]
        
        success_count = 0
        for cmd in commands:
            try:
                self._log_step(f"Executando: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    success_count += 1
                    self._log_step(f"✅ Sucesso: {cmd.split()[2]}", "SUCCESS")
                else:
                    self._log_step(f"❌ Falha: {cmd} - {result.stderr}", "ERROR")
            except Exception as e:
                self._log_step(f"❌ Erro ao executar {cmd}: {e}", "ERROR")
        
        success_rate = success_count / len(commands)
        self._log_step(f"Taxa de sucesso: {success_rate:.1%}", "INFO")
        
        return success_rate > 0.8
    
    def download_recommended_model(self, model_name: str = "codellama/CodeLlama-7b-Python-hf") -> bool:
        """Baixa modelo recomendado do Hugging Face."""
        self._log_step(f"Baixando modelo: {model_name}...")
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Verificar VRAM disponível
            if torch.cuda.is_available():
                vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                if vram_gb < 12:
                    model_name = "codellama/CodeLlama-7b-Python-hf"  # Modelo menor
                    self._log_step(f"VRAM limitada ({vram_gb:.1f}GB), usando modelo 7B", "WARNING")
            
            # Download do tokenizer
            self._log_step("Baixando tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Download do modelo (apenas metadados inicialmente)
            self._log_step("Baixando modelo (pode demorar)...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                device_map="auto" if torch.cuda.is_available() else "cpu"
            )
            
            self._log_step(f"✅ Modelo {model_name} baixado com sucesso", "SUCCESS")
            return True
            
        except Exception as e:
            self._log_step(f"❌ Erro ao baixar modelo: {e}", "ERROR")
            return False
    
    def create_orchestration_framework(self) -> bool:
        """Cria framework básico de orquestração."""
        self._log_step("Criando framework de orquestração...")
        
        framework_code = '''
"""
Framework de Orquestração - GLPI Dashboard
Sistema de IA Colaborativo com GPU
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

class GLPIAIOrchestrator:
    """Orquestrador principal para sistema de IA colaborativo."""
    
    def __init__(self, model_name: str = "codellama/CodeLlama-7b-Python-hf"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.logger = self._setup_logger()
        
        self.logger.info(f"Inicializando orquestrador com {self.device}")
        self._load_model()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura sistema de logging."""
        logger = logging.getLogger("GLPIOrchestrator")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _load_model(self):
        """Carrega modelo local na GPU."""
        try:
            self.logger.info(f"Carregando modelo {self.model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            self.logger.info("✅ Modelo carregado com sucesso")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar modelo: {e}")
            raise
    
    def analyze_code(self, code: str, task_type: str = "general") -> Dict[str, Any]:
        """Analisa código usando modelo local."""
        self.logger.info(f"Analisando código - Tipo: {task_type}")
        
        prompt = f"""
        Analise o seguinte código Python e forneça insights:
        
        Código:
        {code}
        
        Tipo de análise: {task_type}
        
        Forneça:
        1. Possíveis problemas
        2. Sugestões de melhoria
        3. Padrões identificados
        
        Análise:
        """
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            analysis = response.split("Análise:")[-1].strip()
            
            return {
                "status": "success",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model_name
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_logs(self, log_content: str) -> Dict[str, Any]:
        """Processa logs do GLPI Dashboard."""
        self.logger.info("Processando logs...")
        
        prompt = f"""
        Analise os seguintes logs do sistema GLPI Dashboard:
        
        Logs:
        {log_content}
        
        Identifique:
        1. Erros críticos
        2. Padrões de falha
        3. Sugestões de correção
        4. Métricas importantes
        
        Análise:
        """
        
        return self.analyze_code(log_content, "log_analysis")
    
    def generate_tests(self, function_code: str) -> Dict[str, Any]:
        """Gera testes automatizados para funções."""
        self.logger.info("Gerando testes automatizados...")
        
        prompt = f"""
        Gere testes unitários pytest para a seguinte função:
        
        {function_code}
        
        Inclua:
        1. Casos de teste normais
        2. Casos extremos
        3. Testes de erro
        4. Mocks se necessário
        
        Testes:
        """
        
        return self.analyze_code(function_code, "test_generation")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de orquestração."""
        status = {
            "model_loaded": self.model is not None,
            "device": self.device,
            "model_name": self.model_name,
            "timestamp": datetime.now().isoformat()
        }
        
        if torch.cuda.is_available():
            status["gpu_info"] = {
                "name": torch.cuda.get_device_name(0),
                "memory_allocated": torch.cuda.memory_allocated(0) / 1024**3,
                "memory_total": torch.cuda.get_device_properties(0).total_memory / 1024**3
            }
        
        return status

# Exemplo de uso
if __name__ == "__main__":
    orchestrator = GLPIAIOrchestrator()
    
    # Teste básico
    test_code = """
    def calculate_metrics(data):
        if not data:
            return 0
        return sum(data) / len(data)
    """
    
    result = orchestrator.analyze_code(test_code, "code_review")
    print("Resultado da análise:")
    print(result)
    
    # Status do sistema
    status = orchestrator.get_system_status()
    print("\nStatus do sistema:")
    print(status)
'''
        
        try:
            framework_path = Path("../../backend/ai/orchestrator.py")
            framework_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(framework_path, 'w', encoding='utf-8') as f:
                f.write(framework_code)
            
            self._log_step(f"✅ Framework criado em: {framework_path}", "SUCCESS")
            return True
            
        except Exception as e:
            self._log_step(f"❌ Erro ao criar framework: {e}", "ERROR")
            return False
    
    def create_test_script(self) -> bool:
        """Cria script de teste para validar a configuração."""
        self._log_step("Criando script de teste...")
        
        test_script = '''
#!/usr/bin/env python3
"""
Script de Teste - Integração GPU e Modelos Complementares
GLPI Dashboard Project
"""

import sys
import torch
import time
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent))

def test_gpu_availability():
    """Testa disponibilidade da GPU."""
    print("=== Teste de GPU ===")
    print(f"CUDA disponível: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        print(f"CUDA Version: {torch.version.cuda}")
        
        # Teste de alocação de memória
        try:
            test_tensor = torch.randn(1000, 1000).cuda()
            print("✅ Teste de alocação GPU: SUCESSO")
            del test_tensor
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"❌ Teste de alocação GPU: FALHA - {e}")
    else:
        print("❌ GPU não disponível")

def test_model_loading():
    """Testa carregamento de modelo."""
    print("\n=== Teste de Modelo ===")
    
    try:
            from glpi_dashboard.backend.ai.orchestrator import UnifiedOrchestrator, OrchestratorConfig
        
        print("Inicializando orquestrador...")
        start_time = time.time()
        
        config = OrchestratorConfig()
        orchestrator = UnifiedOrchestrator(config)
        
        load_time = time.time() - start_time
        print(f"✅ Modelo carregado em {load_time:.2f}s")
        
        # Teste de análise
        test_code = "def hello(): return 'world'"
        result = orchestrator.analyze_code(test_code)
        
        if result["status"] == "success":
            print("✅ Teste de análise: SUCESSO")
        else:
            print(f"❌ Teste de análise: FALHA - {result.get('error')}")
            
        # Status do sistema
        status = orchestrator.get_system_status()
        print(f"Status: {status}")
        
    except Exception as e:
        print(f"❌ Erro no teste de modelo: {e}")

def test_performance():
    """Testa performance do sistema."""
    print("\n=== Teste de Performance ===")
    
    if torch.cuda.is_available():
        # Teste de throughput GPU
        sizes = [100, 500, 1000, 2000]
        
        for size in sizes:
            start_time = time.time()
            
            # Operação matricial na GPU
            a = torch.randn(size, size).cuda()
            b = torch.randn(size, size).cuda()
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            
            elapsed = time.time() - start_time
            print(f"Matriz {size}x{size}: {elapsed:.4f}s")
            
            del a, b, c
            torch.cuda.empty_cache()
    else:
        print("GPU não disponível para teste de performance")

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes de integração GPU...\n")
    
    test_gpu_availability()
    test_model_loading()
    test_performance()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
'''
        
        try:
            test_path = Path("../tests/test_gpu_integration.py")
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_path, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            self._log_step(f"✅ Script de teste criado em: {test_path}", "SUCCESS")
            return True
            
        except Exception as e:
            self._log_step(f"❌ Erro ao criar script de teste: {e}", "ERROR")
            return False
    
    def generate_setup_report(self) -> str:
        """Gera relatório final da configuração."""
        report = f"""
# Relatório de Configuração - Integração GPU
## GLPI Dashboard Project

**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Sistema**: {self.system_info['os']} - {self.system_info['platform']}

## Log de Configuração

"""
        
        for log_entry in self.setup_log:
            report += f"{log_entry}\n"
        
        report += f"""

## Próximos Passos

1. **Executar testes**: `python tests/test_gpu_integration.py`
2. **Verificar framework**: Importar `GLPIAIOrchestrator`
3. **Integrar com dashboard**: Usar orquestração colaborativa
4. **Monitorar performance**: Acompanhar uso de GPU

## Arquivos Criados

- `glpi_dashboard/backend/ai/orchestrator.py` - Framework principal
- `tests/test_gpu_integration.py` - Script de validação
- `setup_gpu_integration.py` - Este script de configuração

## Comandos Úteis

```bash
# Verificar status da GPU
nvidia-smi

# Monitorar uso em tempo real
watch -n 1 nvidia-smi

# Testar PyTorch GPU
python -c "import torch; print(torch.cuda.is_available())"

# Executar orquestrador
python -m glpi_dashboard.backend.ai.orchestrator
```

---
**Status**: Configuração concluída ✅
"""
        
        return report
    
    def run_full_setup(self) -> bool:
        """Executa configuração completa."""
        self._log_step("🚀 Iniciando configuração completa da integração GPU...", "INFO")
        
        steps = [
            ("Verificação de GPU", self.check_gpu_availability),
            ("Instalação de dependências", self.install_cuda_dependencies),
            ("Download de modelo", self.download_recommended_model),
            ("Criação de framework", self.create_orchestration_framework),
            ("Criação de testes", self.create_test_script)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            self._log_step(f"Executando: {step_name}...")
            try:
                if step_name == "Verificação de GPU":
                    available, info = step_func()
                    if available:
                        success_count += 1
                else:
                    if step_func():
                        success_count += 1
            except Exception as e:
                self._log_step(f"❌ Erro em {step_name}: {e}", "ERROR")
        
        success_rate = success_count / len(steps)
        
        # Gerar relatório final
        report = self.generate_setup_report()
        report_path = Path("setup_report.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self._log_step(f"📊 Relatório salvo em: {report_path}", "INFO")
        self._log_step(f"✅ Configuração concluída - Taxa de sucesso: {success_rate:.1%}", "SUCCESS")
        
        return success_rate > 0.6

def main():
    """Função principal."""
    print("🔧 Configuração Automática - Integração GPU GLPI Dashboard")
    print("=" * 60)
    
    setup = GPUIntegrationSetup()
    
    try:
        success = setup.run_full_setup()
        
        if success:
            print("\n🎉 Configuração concluída com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Execute: python tests/test_gpu_integration.py")
            print("2. Verifique: python -m glpi_dashboard.backend.ai.orchestrator")
            print("3. Integre com o dashboard principal")
        else:
            print("\n⚠️ Configuração parcialmente concluída")
            print("Verifique o relatório para detalhes dos erros")
            
    except KeyboardInterrupt:
        print("\n❌ Configuração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal na configuração: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())