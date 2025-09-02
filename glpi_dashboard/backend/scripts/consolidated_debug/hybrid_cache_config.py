#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração do Cache Híbrido
Gerado automaticamente em 30/08/2025 02:03:19
"""

import os
from pathlib import Path

# Estrutura do cache
CACHE_STRUCTURE = {'ai_models': {'transformers': 'B:\\ai_models_cache\\transformers', 'huggingface': 'B:\\ai_models_cache\\huggingface', 'torch': 'B:\\ai_models_cache\\torch', 'datasets': 'B:\\ai_models_cache\\datasets', 'cuda': 'B:\\ai_models_cache\\cuda'}, 'python_cache': {'pip': 'B:\\ai_models_cache\\pip', 'mypy': 'B:\\ai_models_cache\\mypy', 'pytest': 'B:\\ai_models_cache\\pytest'}, 'temp': 'B:\\ai_models_cache\\temp', 'logs': 'B:\\ai_models_cache\\logs'}

# Variáveis de ambiente
ENV_VARS = {'TRANSFORMERS_CACHE': 'B:\\ai_models_cache\\transformers', 'HF_HOME': 'B:\\ai_models_cache\\huggingface', 'TORCH_HOME': 'B:\\ai_models_cache\\torch', 'HF_DATASETS_CACHE': 'B:\\ai_models_cache\\datasets', 'CUDA_CACHE_PATH': 'B:\\ai_models_cache\\cuda', 'PIP_CACHE_DIR': 'B:\\ai_models_cache\\pip', 'MYPY_CACHE_DIR': 'B:\\ai_models_cache\\mypy', 'PYTEST_CACHE_DIR': 'B:\\ai_models_cache\\pytest', 'TEMP': 'B:\\ai_models_cache\\temp', 'TMP': 'B:\\ai_models_cache\\temp'}

def setup_cache_env():
    """Configura variáveis de ambiente"""
    for var, path in ENV_VARS.items():
        os.environ[var] = path
    print("✅ Variáveis de ambiente configuradas")

def get_cache_path(category, subcategory=None):
    """Obtém caminho do cache"""
    if subcategory:
        return CACHE_STRUCTURE.get(category, {}).get(subcategory)
    return CACHE_STRUCTURE.get(category)

def verify_cache_structure():
    """Verifica integridade da estrutura do cache"""
    print("🔍 Verificando estrutura do cache...")
    missing_paths = []
    
    for cat, paths in CACHE_STRUCTURE.items():
        if isinstance(paths, dict):
            for name, path in paths.items():
                if not os.path.exists(path):
                    missing_entry = f"{cat}.{name}: {path}"
                    missing_paths.append(missing_entry)
        else:
            if not os.path.exists(paths):
                missing_entry = f"{cat}: {paths}"
                missing_paths.append(missing_entry)
    
    if missing_paths:
        print("⚠️ Caminhos de cache ausentes:")
        for path in missing_paths:
            print(f"  - {path}")
        return False
    else:
        print("✅ Estrutura do cache verificada")
        return True

if __name__ == "__main__":
    print("🔧 Configuração do Cache Híbrido")
    setup_cache_env()
    verify_cache_structure()
