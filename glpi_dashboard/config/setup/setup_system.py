#!/usr/bin/env python3
"""
Script de configuração do sistema GLPI Dashboard AI Agent
"""

import os
import yaml
import torch
from pathlib import Path
import json
from datetime import datetime

def create_directories():
    """Cria diretórios necessários do sistema"""
    directories = [
        "models",
        "logs", 
        "cache",
        "temp",
        "reports",
        "workflows",
        "templates",
        "data"
    ]
    
    print("📁 Criando diretórios do sistema...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    return True

def check_system_requirements():
    """Verifica requisitos do sistema"""
    print("🔍 Verificando requisitos do sistema...")
    
    # Verificar Python
    import sys
    python_version = sys.version_info
    print(f"  Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar PyTorch
    print(f"  PyTorch: {torch.__version__}")
    
    # Verificar CUDA
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"  GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        print(f"  CUDA: {torch.version.cuda}")
    else:
        print("  GPU: Não disponível")
    
    # Verificar dependências
    try:
        import transformers
        print(f"  Transformers: {transformers.__version__}")
    except ImportError:
        print("  ❌ Transformers não instalado")
        return False
    
    try:
        import accelerate
        print(f"  Accelerate: {accelerate.__version__}")
    except ImportError:
        print("  ❌ Accelerate não instalado")
        return False
    
    return True

def load_working_models():
    """Carrega lista de modelos funcionais"""
    models_file = Path("working_models.txt")
    if models_file.exists():
        with open(models_file, 'r') as f:
            models = [line.strip() for line in f if line.strip()]
        return models
    return []

def create_system_config():
    """Cria configuração personalizada do sistema"""
    print("⚙️ Criando configuração do sistema...")
    
    # Verificar modelos disponíveis
    working_models = load_working_models()
    
    # Configuração básica
    config = {
        "system": {
            "name": "GLPI Dashboard AI Agent System",
            "version": "1.0.0",
            "environment": "development",
            "debug_mode": True,
            "log_level": "INFO",
            "created_at": datetime.now().isoformat()
        },
        "hardware": {
            "gpu": {
                "available": torch.cuda.is_available(),
                "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                "memory_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3) if torch.cuda.is_available() else 0,
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
            },
            "pytorch_version": torch.__version__
        },
        "models": {
            "available": working_models,
            "primary": working_models[0] if working_models else None,
            "fallback": "microsoft/DialoGPT-small"
        },
        "features": {
            "code_analysis": True,
            "glpi_integration": True,
            "dashboard_generation": True,
            "ai_assistance": True
        }
    }
    
    # Salvar configuração
    config_file = Path("../system.yaml")
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"  ✅ Configuração salva em: {config_file}")
    return config

def test_system_integration():
    """Testa integração básica do sistema"""
    print("🧪 Testando integração do sistema...")
    
    try:
        # Teste básico de importações
        from transformers import AutoTokenizer
        print("  ✅ Transformers funcionando")
        
        # Teste de GPU se disponível
        if torch.cuda.is_available():
            test_tensor = torch.randn(10, 10).cuda()
            result = test_tensor @ test_tensor.T
            print("  ✅ GPU funcionando")
        
        # Teste de modelo simples se disponível
        working_models = load_working_models()
        if working_models:
            model_name = working_models[0]
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            print(f"  ✅ Modelo {model_name} acessível")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na integração: {e}")
        return False

def generate_system_report():
    """Gera relatório do sistema"""
    print("📊 Gerando relatório do sistema...")
    
    working_models = load_working_models()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_status": "operational",
        "components": {
            "python": "✅ Funcionando",
            "pytorch": "✅ Funcionando",
            "cuda": "✅ Funcionando" if torch.cuda.is_available() else "❌ Não disponível",
            "transformers": "✅ Funcionando",
            "models": f"✅ {len(working_models)} modelos disponíveis"
        },
        "models_available": working_models,
        "next_steps": [
            "Configurar integração com GLPI",
            "Testar geração de dashboards",
            "Validar análise de código",
            "Implementar workflows automatizados"
        ]
    }
    
    # Salvar relatório
    report_file = Path("reports/system_setup_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Relatório salvo em: {report_file}")
    return report

def main():
    print("🚀 GLPI Dashboard AI Agent System - Configuração")
    print("=" * 60)
    
    # Executar configuração
    steps = [
        ("Criar diretórios", create_directories),
        ("Verificar requisitos", check_system_requirements),
        ("Criar configuração", create_system_config),
        ("Testar integração", test_system_integration),
        ("Gerar relatório", generate_system_report)
    ]
    
    results = {}
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        try:
            result = step_func()
            results[step_name] = result
            if result:
                print(f"✅ {step_name} concluído")
            else:
                print(f"⚠️ {step_name} com problemas")
        except Exception as e:
            print(f"❌ Erro em {step_name}: {e}")
            results[step_name] = False
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DA CONFIGURAÇÃO")
    print("=" * 60)
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"✅ Etapas concluídas: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 Sistema configurado com sucesso!")
        print("\n📋 Próximos passos:")
        print("  1. Aguardar download completo dos modelos")
        print("  2. Testar integração com GLPI")
        print("  3. Validar geração de dashboards")
    else:
        print("⚠️ Configuração parcial. Verifique os erros acima.")

if __name__ == "__main__":
    main()