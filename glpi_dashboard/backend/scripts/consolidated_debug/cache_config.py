
"""
Configuração de Cache - GLPI Dashboard
Configuração automática para usar Drive B: como cache

Gerado em: 30/08/2025 01:46:16
"""

import os

# Configuração de cache no Drive B:
CACHE_CONFIG = {
    'root': r"B:\ai_models_cache",
    'transformers': r"B:\ai_models_cache\transformers",
    'huggingface': r"B:\ai_models_cache\huggingface",
    'torch': r"B:\ai_models_cache\torch",
    'datasets': r"B:\ai_models_cache\datasets",
    'temp': r"B:\ai_models_cache\temp",
    'models': r"B:\ai_models_cache\models",
    'checkpoints': r"B:\ai_models_cache\checkpoints"
}

# Aplicar configurações automaticamente
def setup_cache_environment():
    """Configura ambiente de cache automaticamente."""
    env_vars = {
        'TRANSFORMERS_CACHE': CACHE_CONFIG['transformers'],
        'HF_HOME': CACHE_CONFIG['huggingface'],
        'TORCH_HOME': CACHE_CONFIG['torch'],
        'HF_DATASETS_CACHE': CACHE_CONFIG['datasets'],
        'PYTORCH_KERNEL_CACHE_PATH': os.path.join(CACHE_CONFIG['torch'], 'kernels'),
        'CUDA_CACHE_PATH': os.path.join(CACHE_CONFIG['root'], 'cuda')
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"Cache configurado: {var} -> {value}")
    
    return True

# Configurar automaticamente ao importar
if __name__ != "__main__":
    setup_cache_environment()

# Funções utilitárias
def get_cache_path(cache_type: str) -> str:
    """Retorna caminho do cache especificado."""
    return CACHE_CONFIG.get(cache_type, CACHE_CONFIG['root'])

def get_cache_usage():
    """Retorna informações de uso do cache."""
    import shutil
    
    usage = {}
    for name, path in CACHE_CONFIG.items():
        if os.path.exists(path):
            try:
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except (OSError, PermissionError):
                            continue
                
                usage[name] = {
                    'size_gb': total_size / (1024**3),
                    'file_count': file_count,
                    'path': path
                }
            except Exception as e:
                usage[name] = {'error': str(e), 'path': path}
        else:
            usage[name] = {'status': 'not_created', 'path': path}
    
    return usage

def clear_cache(cache_type: str = None):
    """Limpa cache especificado ou todos."""
    import shutil
    
    if cache_type and cache_type in CACHE_CONFIG:
        paths_to_clear = [CACHE_CONFIG[cache_type]]
    else:
        paths_to_clear = list(CACHE_CONFIG.values())
    
    cleared = []
    for path in paths_to_clear:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                os.makedirs(path, exist_ok=True)
                cleared.append(path)
            except Exception as e:
                print(f"Erro ao limpar {path}: {e}")
    
    return cleared

if __name__ == "__main__":
    print("Configuração de Cache - Drive B:")
    print("=" * 40)
    
    setup_cache_environment()
    
    print("\nCaminhos configurados:")
    for name, path in CACHE_CONFIG.items():
        print(f"- {name}: {path}")
    
    print("\nUso do cache:")
    usage = get_cache_usage()
    for name, info in usage.items():
        if 'size_gb' in info:
            print(f"- {name}: {info['size_gb']:.2f}GB ({info['file_count']} arquivos)")
        else:
            print(f"- {name}: {info.get('status', 'erro')}")
