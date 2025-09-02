#!/usr/bin/env python3
"""Script de instalação e configuração do Sistema de Agentes AI.

Este script automatiza a instalação, configuração e verificação
do sistema de múltiplos agentes AI para o GLPI Dashboard.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import platform
import argparse
from datetime import datetime

# Cores para output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class AIAgentSetup:
    """Classe principal para setup do sistema de agentes"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.ai_agents_dir = Path(__file__).parent
        self.venv_dir = self.project_root / "venv_ai_agents"
        self.config_dir = self.ai_agents_dir / "config"
        self.logs_dir = self.ai_agents_dir / "logs"
        self.models_dir = self.ai_agents_dir / "models"

        self.python_executable = sys.executable
        self.pip_executable = None

        # Status da instalação
        self.installation_log = []
        self.errors = []
        self.warnings = []

    def log(self, message: str, level: str = "INFO"):
        """Log com cores"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        color_map = {
            "INFO": Colors.CYAN,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "HEADER": Colors.MAGENTA + Colors.BOLD
        }

        color = color_map.get(level, Colors.WHITE)
        print(f"{color}[{timestamp}] {message}{Colors.END}")

        # Adicionar ao log
        self.installation_log.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })

        if level == "ERROR":
            self.errors.append(message)
        elif level == "WARNING":
            self.warnings.append(message)

    def run_command(self, command: List[str], cwd: Optional[Path] = None,
                   capture_output: bool = True) -> Tuple[bool, str, str]:
        """Executa comando e retorna resultado"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minutos timeout
            )

            success = result.returncode == 0
            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", "Comando expirou (timeout)"
        except Exception as e:
            return False, "", str(e)

    def check_system_requirements(self) -> bool:
        """Verifica requisitos do sistema"""
        self.log("🔍 Verificando requisitos do sistema...", "HEADER")

        # Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            self.log(f"❌ Python {python_version.major}.{python_version.minor} não suportado. Mínimo: 3.8", "ERROR")
            return False
        else:
            self.log(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}", "SUCCESS")

        # Sistema operacional
        system = platform.system()
        self.log(f"💻 Sistema: {system} {platform.release()}", "INFO")

        # Verificar GPU NVIDIA
        gpu_available = self.check_nvidia_gpu()
        if not gpu_available:
            self.log("⚠️ GPU NVIDIA não detectada. Alguns modelos podem não funcionar otimamente.", "WARNING")

        # Verificar espaço em disco
        free_space_gb = shutil.disk_usage(self.project_root).free / (1024**3)
        if free_space_gb < 10:
            self.log(f"⚠️ Pouco espaço em disco: {free_space_gb:.1f}GB. Recomendado: >10GB", "WARNING")
        else:
            self.log(f"💾 Espaço disponível: {free_space_gb:.1f}GB", "SUCCESS")

        return True

    def check_nvidia_gpu(self) -> bool:
        """Verifica se há GPU NVIDIA disponível"""
        try:
            # Tentar nvidia-smi
            success, stdout, stderr = self.run_command(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])

            if success and stdout.strip():
                gpus = stdout.strip().split('\n')
                self.log(f"🎮 GPU(s) NVIDIA detectada(s): {len(gpus)}", "SUCCESS")

                for i, gpu_info in enumerate(gpus):
                    name, memory = gpu_info.split(', ')
                    memory_gb = int(memory) / 1024
                    self.log(f"  GPU {i}: {name} ({memory_gb:.1f}GB)", "INFO")

                return True
            else:
                return False

        except Exception:
            return False

    def create_virtual_environment(self) -> bool:
        """Cria ambiente virtual"""
        self.log("🐍 Configurando ambiente virtual...", "HEADER")

        if self.venv_dir.exists():
            self.log(f"📁 Ambiente virtual já existe: {self.venv_dir}", "INFO")
            response = input("Deseja recriar? (y/N): ").lower().strip()
            if response == 'y':
                self.log("🗑️ Removendo ambiente virtual existente...", "INFO")
                shutil.rmtree(self.venv_dir)
            else:
                return self.activate_virtual_environment()

        # Criar novo ambiente virtual
        self.log(f"📦 Criando ambiente virtual em {self.venv_dir}...", "INFO")
        success, stdout, stderr = self.run_command([self.python_executable, "-m", "venv", str(self.venv_dir)])

        if not success:
            self.log(f"❌ Erro ao criar ambiente virtual: {stderr}", "ERROR")
            return False

        self.log("✅ Ambiente virtual criado", "SUCCESS")
        return self.activate_virtual_environment()

    def activate_virtual_environment(self) -> bool:
        """Ativa ambiente virtual"""
        # Determinar executáveis do ambiente virtual
        if platform.system() == "Windows":
            self.python_executable = str(self.venv_dir / "Scripts" / "python.exe")
            self.pip_executable = str(self.venv_dir / "Scripts" / "pip.exe")
        else:
            self.python_executable = str(self.venv_dir / "bin" / "python")
            self.pip_executable = str(self.venv_dir / "bin" / "pip")

        # Verificar se existem
        if not Path(self.python_executable).exists():
            self.log(f"❌ Python não encontrado no ambiente virtual: {self.python_executable}", "ERROR")
            return False

        if not Path(self.pip_executable).exists():
            self.log(f"❌ Pip não encontrado no ambiente virtual: {self.pip_executable}", "ERROR")
            return False

        self.log(f"✅ Ambiente virtual ativado: {self.venv_dir}", "SUCCESS")
        return True

    def install_dependencies(self) -> bool:
        """Instala dependências"""
        self.log("📦 Instalando dependências...", "HEADER")

        # Atualizar pip
        self.log("🔄 Atualizando pip...", "INFO")
        success, stdout, stderr = self.run_command([self.pip_executable, "install", "--upgrade", "pip"])

        if not success:
            self.log(f"⚠️ Aviso ao atualizar pip: {stderr}", "WARNING")

        # Instalar wheel e setuptools
        self.log("🛠️ Instalando ferramentas básicas...", "INFO")
        success, stdout, stderr = self.run_command([self.pip_executable, "install", "wheel", "setuptools"])

        if not success:
            self.log(f"⚠️ Aviso ao instalar ferramentas: {stderr}", "WARNING")

        # Instalar dependências do requirements.txt
        requirements_file = self.ai_agents_dir / "requirements.txt"

        if not requirements_file.exists():
            self.log(f"❌ Arquivo requirements.txt não encontrado: {requirements_file}", "ERROR")
            return False

        self.log(f"📋 Instalando dependências de {requirements_file}...", "INFO")
        success, stdout, stderr = self.run_command([
            self.pip_executable, "install", "-r", str(requirements_file)
        ])

        if not success:
            self.log(f"❌ Erro ao instalar dependências: {stderr}", "ERROR")
            return False

        self.log("✅ Dependências instaladas com sucesso", "SUCCESS")
        return True

    def setup_directories(self) -> bool:
        """Cria estrutura de diretórios"""
        self.log("📁 Criando estrutura de diretórios...", "HEADER")

        directories = [
            self.config_dir,
            self.logs_dir,
            self.models_dir,
            self.models_dir / "cache",
            self.models_dir / "downloads",
            self.ai_agents_dir / "workflows",
            self.ai_agents_dir / "templates",
            self.ai_agents_dir / "data"
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.log(f"  ✓ {directory.relative_to(self.project_root)}", "SUCCESS")
            except Exception as e:
                self.log(f"  ❌ Erro ao criar {directory}: {str(e)}", "ERROR")
                return False

        return True

    def create_default_config(self) -> bool:
        """Cria configuração padrão"""
        self.log("⚙️ Criando configuração padrão...", "HEADER")

        config_file = self.config_dir / "default_config.yaml"

        if config_file.exists():
            self.log(f"📄 Configuração já existe: {config_file}", "INFO")
            return True

        # Configuração padrão
        default_config = {
            "project_name": "GLPI Dashboard AI Agents",
            "version": "1.0.0",
            "environment": "development",
            "logs_dir": str(self.logs_dir),
            "models_dir": str(self.models_dir),
            "default_timeout": 300,
            "max_retries": 3,

            "hardware": {
                "gpu_memory_gb": 16,
                "cpu_cores": 8,
                "ram_gb": 32,
                "enable_gpu": True,
                "enable_quantization": True,
                "quantization_bits": 8
            },

            "models": {
                "nemotron_nano": {
                    "model_name": "nvidia/NVIDIA-Nemotron-Nano-9B-v2",
                    "model_type": "causal_lm",
                    "quantization": "8bit",
                    "max_length": 4096,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            },

            "agents": {
                "code_analyst": {
                    "agent_type": "code_analyst",
                    "model_config": "nemotron_nano",
                    "enabled": True,
                    "priority": "high",
                    "timeout": 120,
                    "max_retries": 2
                },
                "testing_agent": {
                    "agent_type": "testing",
                    "model_config": "nemotron_nano",
                    "enabled": True,
                    "priority": "medium",
                    "timeout": 180,
                    "max_retries": 2
                },
                "documentation_agent": {
                    "agent_type": "documentation",
                    "model_config": "nemotron_nano",
                    "enabled": True,
                    "priority": "medium",
                    "timeout": 150,
                    "max_retries": 2
                },
                "refactoring_agent": {
                    "agent_type": "refactoring",
                    "model_config": "nemotron_nano",
                    "enabled": True,
                    "priority": "low",
                    "timeout": 200,
                    "max_retries": 3
                },
                "security_agent": {
                    "agent_type": "security",
                    "model_config": "nemotron_nano",
                    "enabled": True,
                    "priority": "high",
                    "timeout": 100,
                    "max_retries": 1
                }
            },

            "telemetry": {
                "enable_metrics": True,
                "enable_alerts": True,
                "log_level": "INFO",
                "metrics_retention_days": 30,
                "export_format": "json"
            },

            "quality_gates": {
                "enable_gates": True,
                "min_quality_score": 7.0,
                "max_complexity": 10,
                "min_test_coverage": 80.0,
                "max_security_issues": 0,
                "max_processing_time": 300
            }
        }

        try:
            import yaml
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True, indent=2)

            self.log(f"✅ Configuração criada: {config_file}", "SUCCESS")
            return True

        except ImportError:
            # Fallback para JSON se YAML não estiver disponível
            config_file = config_file.with_suffix('.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

            self.log(f"✅ Configuração criada (JSON): {config_file}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao criar configuração: {str(e)}", "ERROR")
            return False

    def test_installation(self) -> bool:
        """Testa a instalação"""
        self.log("🧪 Testando instalação...", "HEADER")

        # Teste básico de importação
        test_script = f"""
import sys
sys.path.insert(0, r'{self.ai_agents_dir}')

try:
    # Testar imports básicos
    import torch
    import transformers
    import numpy as np
    import pandas as pd

    # Testar imports do sistema
    from config import get_config
    from base_agent import BaseAgent

    print("✅ Todos os imports funcionaram")
    print(f"PyTorch: {torch.__version__}")
    print(f"Transformers: {transformers.__version__}")
    print(f"CUDA disponível: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memória GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")

except Exception as e:
    print(f"❌ Erro no teste: {{str(e)}}")
    sys.exit(1)
"""

        # Salvar script de teste
        test_file = self.ai_agents_dir / "test_installation.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)

        # Executar teste
        success, stdout, stderr = self.run_command([self.python_executable, str(test_file)])

        # Remover arquivo de teste
        test_file.unlink()

        if success:
            self.log("✅ Teste de instalação passou", "SUCCESS")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}", "INFO")
            return True
        else:
            self.log(f"❌ Teste de instalação falhou: {stderr}", "ERROR")
            return False

    def create_activation_script(self) -> bool:
        """Cria script de ativação"""
        self.log("📜 Criando script de ativação...", "HEADER")

        if platform.system() == "Windows":
            # Script .bat para Windows
            script_file = self.project_root / "activate_ai_agents.bat"
            script_content = f"""@echo off
echo 🤖 Ativando Sistema de Agentes AI...
call "{self.venv_dir}\\Scripts\\activate.bat"
echo ✅ Ambiente ativado. Use 'python -m ai_agents.main --help' para começar.
cmd /k
"""
        else:
            # Script .sh para Unix/Linux/Mac
            script_file = self.project_root / "activate_ai_agents.sh"
            script_content = f"""#!/bin/bash
echo "🤖 Ativando Sistema de Agentes AI..."
source "{self.venv_dir}/bin/activate"
echo "✅ Ambiente ativado. Use 'python -m ai_agents.main --help' para começar."
bash
"""

        try:
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # Tornar executável no Unix
            if platform.system() != "Windows":
                os.chmod(script_file, 0o755)

            self.log(f"✅ Script criado: {script_file}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao criar script: {str(e)}", "ERROR")
            return False

    def generate_installation_report(self) -> bool:
        """Gera relatório de instalação"""
        report_file = self.logs_dir / f"installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "project_root": str(self.project_root),
                "venv_dir": str(self.venv_dir)
            },
            "installation_log": self.installation_log,
            "errors": self.errors,
            "warnings": self.warnings,
            "success": len(self.errors) == 0
        }

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            self.log(f"📊 Relatório salvo: {report_file}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao salvar relatório: {str(e)}", "ERROR")
            return False

    def run_full_setup(self) -> bool:
        """Executa setup completo"""
        self.log("🚀 Iniciando instalação do Sistema de Agentes AI", "HEADER")
        self.log(f"📁 Diretório do projeto: {self.project_root}", "INFO")

        steps = [
            ("Verificar requisitos", self.check_system_requirements),
            ("Criar ambiente virtual", self.create_virtual_environment),
            ("Instalar dependências", self.install_dependencies),
            ("Configurar diretórios", self.setup_directories),
            ("Criar configuração", self.create_default_config),
            ("Testar instalação", self.test_installation),
            ("Criar script de ativação", self.create_activation_script),
            ("Gerar relatório", self.generate_installation_report)
        ]

        for step_name, step_func in steps:
            self.log(f"\n{'='*50}", "INFO")
            self.log(f"📋 Executando: {step_name}", "HEADER")

            try:
                if not step_func():
                    self.log(f"❌ Falha na etapa: {step_name}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"❌ Erro na etapa {step_name}: {str(e)}", "ERROR")
                return False

        # Resumo final
        self.log(f"\n{'='*50}", "INFO")
        self.log("🎉 INSTALAÇÃO CONCLUÍDA!", "HEADER")

        if self.warnings:
            self.log(f"⚠️ {len(self.warnings)} aviso(s) encontrado(s)", "WARNING")

        self.log("\n📋 Próximos passos:", "INFO")

        if platform.system() == "Windows":
            self.log("  1. Execute: activate_ai_agents.bat", "INFO")
        else:
            self.log("  1. Execute: ./activate_ai_agents.sh", "INFO")

        self.log("  2. Teste: python -m ai_agents.main --status", "INFO")
        self.log("  3. Exemplo: python -m ai_agents.main --action analyze --files src/", "INFO")

        return True


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Setup do Sistema de Agentes AI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--skip-venv', action='store_true', help='Pular criação do ambiente virtual')
    parser.add_argument('--skip-deps', action='store_true', help='Pular instalação de dependências')
    parser.add_argument('--skip-test', action='store_true', help='Pular teste de instalação')
    parser.add_argument('--force', action='store_true', help='Forçar reinstalação')

    args = parser.parse_args()

    setup = AIAgentSetup()

    try:
        success = setup.run_full_setup()
        return 0 if success else 1

    except KeyboardInterrupt:
        setup.log("\n⏹️ Instalação interrompida pelo usuário", "WARNING")
        return 130

    except Exception as e:
        setup.log(f"❌ Erro inesperado: {str(e)}", "ERROR")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
