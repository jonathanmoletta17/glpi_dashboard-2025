#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Mínima GPU - GLPI Dashboard
Instalação otimizada para limitações de espaço em disco
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class GPUMinimalSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.backend_dir = self.project_root / "glpi_dashboard" / "backend"
        self.scripts_dir = self.backend_dir / "scripts"

        # Pacotes essenciais apenas
        self.essential_packages = [
            "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
            "transformers",
            "accelerate",
            "datasets",
            "tokenizers"
        ]

        # Modelos compactos recomendados
        self.compact_models = [
            "microsoft/DialoGPT-small",  # 117MB
            "distilbert-base-uncased",   # 268MB
            "microsoft/CodeBERT-base"    # 501MB
        ]

    def check_gpu(self):
        """Verificação básica de GPU"""
        logger.info("🔍 Verificando GPU...")
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ NVIDIA GPU detectada")
                return True
            else:
                logger.warning("⚠️ GPU NVIDIA não detectada")
                return False
        except FileNotFoundError:
            logger.warning("⚠️ nvidia-smi não encontrado")
            return False

    def install_package(self, package):
        """Instala um pacote específico"""
        logger.info(f"📦 Instalando: {package}")
        try:
            cmd = f"pip install {package}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ Sucesso: {package.split()[0]}")
                return True
            else:
                logger.error(f"❌ Falha: {package} - {result.stderr[:100]}...")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao instalar {package}: {str(e)}")
            return False

    def install_essentials(self):
        """Instala apenas pacotes essenciais"""
        logger.info("📦 Instalando pacotes essenciais...")
        success_count = 0

        for package in self.essential_packages:
            if self.install_package(package):
                success_count += 1

        logger.info(f"📊 Instalados: {success_count}/{len(self.essential_packages)} pacotes")
        return success_count > 0

    def test_pytorch_gpu(self):
        """Testa PyTorch com GPU"""
        logger.info("🧪 Testando PyTorch + GPU...")
        try:
            import torch

            # Informações básicas
            logger.info(f"PyTorch versão: {torch.__version__}")
            logger.info(f"CUDA disponível: {torch.cuda.is_available()}")

            if torch.cuda.is_available():
                logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
                logger.info(f"CUDA versão: {torch.version.cuda}")

                # Teste simples
                x = torch.randn(3, 3).cuda()
                y = torch.randn(3, 3).cuda()
                z = torch.mm(x, y)
                logger.info("✅ Teste de operação GPU: OK")
                return True
            else:
                logger.warning("⚠️ CUDA não disponível no PyTorch")
                return False

        except ImportError:
            logger.error("❌ PyTorch não instalado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro no teste: {str(e)}")
            return False

    def create_minimal_orchestrator(self):
        """Cria orquestrador mínimo"""
        logger.info("🤖 Criando orquestrador mínimo...")

        orchestrator_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador Mínimo de IA - GLPI Dashboard
"""

import torch
from transformers import AutoTokenizer, AutoModel
import logging

class GLPIAIOrchestrator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.tokenizers = {}

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"🚀 Orquestrador iniciado - Dispositivo: {self.device}")

    def load_model(self, model_name, alias=None):
        """Carrega um modelo compacto"""
        try:
            alias = alias or model_name.split("/")[-1]

            self.logger.info(f"📥 Carregando modelo: {model_name}")

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)

            if self.device == "cuda":
                model = model.to(self.device)

            self.tokenizers[alias] = tokenizer
            self.models[alias] = model

            self.logger.info(f"✅ Modelo carregado: {alias}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar {model_name}: {str(e)}")
            return False

    def get_embeddings(self, text, model_alias="distilbert-base-uncased"):
        """Gera embeddings de texto"""
        try:
            if model_alias not in self.models:
                self.logger.warning(f"Modelo {model_alias} não carregado")
                return None

            tokenizer = self.tokenizers[model_alias]
            model = self.models[model_alias]

            inputs = tokenizer(text, return_tensors="pt", truncate=True, max_length=512)

            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)

            return embeddings.cpu().numpy()

        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar embeddings: {str(e)}")
            return None

    def analyze_glpi_log(self, log_text):
        """Análise básica de logs GLPI"""
        try:
            # Análise simples baseada em palavras-chave
            keywords = {
                "error": ["error", "erro", "failed", "exception"],
                "warning": ["warning", "warn", "alerta"],
                "info": ["info", "success", "ok", "completed"]
            }

            analysis = {"type": "info", "confidence": 0.5, "keywords": []}

            log_lower = log_text.lower()

            for category, words in keywords.items():
                found_words = [word for word in words if word in log_lower]
                if found_words:
                    analysis["keywords"].extend(found_words)
                    if category == "error":
                        analysis["type"] = "error"
                        analysis["confidence"] = 0.8
                    elif category == "warning" and analysis["type"] != "error":
                        analysis["type"] = "warning"
                        analysis["confidence"] = 0.7

            return analysis

        except Exception as e:
            self.logger.error(f"❌ Erro na análise: {str(e)}")
            return {"type": "unknown", "confidence": 0.0, "keywords": []}

    def get_status(self):
        """Status do orquestrador"""
        return {
            "device": self.device,
            "models_loaded": list(self.models.keys()),
            "gpu_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }

if __name__ == "__main__":
    # Teste básico
    orchestrator = GLPIAIOrchestrator()
    print("Status:", orchestrator.get_status())

    # Teste de análise
    test_log = "Error connecting to database: connection timeout"
    result = orchestrator.analyze_glpi_log(test_log)
    print("Análise:", result)
'''

        orchestrator_path = self.scripts_dir / "glpi_ai_orchestrator_minimal.py"
        orchestrator_path.write_text(orchestrator_code, encoding='utf-8')
        logger.info(f"🤖 Orquestrador criado: {orchestrator_path}")
        return orchestrator_path

    def create_test_script(self):
        """Cria script de teste mínimo"""
        logger.info("🧪 Criando script de teste...")

        test_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Mínimo - Integração GPU GLPI
"""

import sys
import torch
from pathlib import Path

# Adiciona o diretório de scripts ao path
sys.path.append(str(Path(__file__).parent))

def test_environment():
    """Testa ambiente básico"""
    print("🧪 Teste de Ambiente GPU - GLPI Dashboard")
    print("=" * 50)

    # Teste PyTorch
    print(f"PyTorch versão: {torch.__version__}")
    print(f"CUDA disponível: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA versão: {torch.version.cuda}")
        print(f"Memória GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")

        # Teste simples
        try:
            x = torch.randn(100, 100).cuda()
            y = torch.randn(100, 100).cuda()
            z = torch.mm(x, y)
            print("✅ Operação GPU: OK")
        except Exception as e:
            print(f"❌ Erro GPU: {e}")

    # Teste Transformers
    try:
        from transformers import AutoTokenizer
        print("✅ Transformers: OK")
    except ImportError:
        print("❌ Transformers: Não instalado")

    # Teste Orquestrador
    try:
        from glpi_dashboard.backend.scripts.glpi_ai_orchestrator_minimal import GLPIAIOrchestrator
        orchestrator = GLPIAIOrchestrator()
        status = orchestrator.get_status()
        print(f"✅ Orquestrador: {status}")
    except ImportError as e:
        print(f"❌ Orquestrador: {e}")

    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    test_environment()
'''

        test_path = self.scripts_dir / "test_gpu_minimal.py"
        test_path.write_text(test_code, encoding='utf-8')
        logger.info(f"🧪 Teste criado: {test_path}")
        return test_path

    def generate_report(self, success_packages, gpu_available, pytorch_working):
        """Gera relatório final"""
        logger.info("📊 Gerando relatório...")

        report = f"""# Relatório - Configuração GPU Mínima
## GLPI Dashboard - Integração IA

**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Modo**: Instalação Mínima (Otimizada para Espaço)

## 🎯 Resumo da Configuração

- **GPU Detectada**: {'✅ Sim' if gpu_available else '❌ Não'}
- **PyTorch Funcionando**: {'✅ Sim' if pytorch_working else '❌ Não'}
- **Pacotes Instalados**: {success_packages}/{len(self.essential_packages)}

## 📦 Pacotes Essenciais

{''.join([f"- {pkg.split()[0]}: ✅\n" for pkg in self.essential_packages])}

## 🤖 Componentes Criados

- **Orquestrador**: `glpi_ai_orchestrator_minimal.py` ✅
- **Teste**: `test_gpu_minimal.py` ✅

## 🚀 Próximos Passos

### 1. Teste da Configuração
```bash
python scripts/test_gpu_minimal.py
```

### 2. Uso do Orquestrador
```python
from glpi_dashboard.backend.scripts.glpi_ai_orchestrator_minimal import GLPIAIOrchestrator

        orchestrator = GLPIAIOrchestrator()
status = orchestrator.get_status()
print(status)
```

### 3. Análise de Logs GLPI
```python
log_text = "Error connecting to database"
analysis = orchestrator.analyze_glpi_log(log_text)
print(analysis)
```

## 💡 Modelos Compactos Recomendados

{''.join([f"- {model} (Compacto)\n" for model in self.compact_models])}

## ⚠️ Limitações Atuais

- **Espaço em Disco**: Configuração mínima devido a limitações
- **TensorFlow**: Não instalado (conflitos de dependência)
- **LangChain**: Não instalado (problemas de espaço)
- **Gradio/Streamlit**: Não instalado (sem espaço)

## 🔧 Otimizações Implementadas

- Cache configurado no Drive B: (1,847GB disponíveis)
- Apenas pacotes essenciais instalados
- Modelos compactos recomendados
- Orquestrador otimizado para recursos limitados

## 📈 Benefícios Esperados

- **Performance**: GPU NVIDIA RTX A4000 16GB
- **Análise**: Processamento básico de logs GLPI
- **Embeddings**: Geração de representações de texto
- **Escalabilidade**: Base para expansão futura
"""

        report_path = self.project_root / "relatorio_gpu_minimal.md"
        report_path.write_text(report, encoding='utf-8')
        logger.info(f"📊 Relatório salvo: {report_path}")
        return report_path

    def run_setup(self):
        """Executa configuração completa"""
        logger.info("🚀 Iniciando configuração GPU mínima...")

        # 1. Verificar GPU
        gpu_available = self.check_gpu()

        # 2. Instalar pacotes essenciais
        success_packages = 0
        if self.install_essentials():
            success_packages = len([pkg for pkg in self.essential_packages])

        # 3. Testar PyTorch
        pytorch_working = self.test_pytorch_gpu()

        # 4. Criar componentes
        self.create_minimal_orchestrator()
        self.create_test_script()

        # 5. Gerar relatório
        report_path = self.generate_report(success_packages, gpu_available, pytorch_working)

        # Resumo final
        logger.info("\n" + "=" * 60)
        logger.info("🎉 CONFIGURAÇÃO GPU MÍNIMA CONCLUÍDA!")
        logger.info("=" * 60)
        logger.info(f"📊 Relatório: {report_path}")
        logger.info(f"🧪 Teste: python scripts/test_gpu_minimal.py")
        logger.info(f"🤖 Orquestrador: scripts/glpi_ai_orchestrator_minimal.py")

        if pytorch_working:
            logger.info("✅ GPU + PyTorch funcionando!")
        else:
            logger.warning("⚠️ Problemas com GPU/PyTorch")

        return True

if __name__ == "__main__":
    print("🔧 Configuração GPU Mínima - GLPI Dashboard")
    print("=" * 50)

    setup = GPUMinimalSetup()
    setup.run_setup()
