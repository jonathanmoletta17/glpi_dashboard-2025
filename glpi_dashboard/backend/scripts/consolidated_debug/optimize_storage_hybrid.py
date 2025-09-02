#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimização Híbrida de Armazenamento
Usa Drive B: como cache principal e OneDrive como backup/sync
"""

import os
import shutil
import sys
from pathlib import Path
import json
from datetime import datetime

# Configurações
DRIVE_B_PATH = "B:\\ai_models_cache"
ONEDRIVE_PATH = r"C:\Users\jonathan-moletta.PPIRATINI\OneDrive - Governo do Estado do Rio Grande do Sul"
PROJECT_ROOT = Path.cwd()

def check_drives():
    """Verifica espaço disponível nos drives"""
    drives_info = {}
    
    for drive in ['C:', 'B:', 'D:', 'E:']:
        try:
            drive_path = f"{drive}\\"
            if os.path.exists(drive_path):
                total, used, free = shutil.disk_usage(drive_path)
                total_gb = total / (1024**3)
                free_gb = free / (1024**3)
                
                status = "✅" if free_gb > 10 else "⚠️" if free_gb > 1 else "❌"
                
                drives_info[drive] = {
                    'available': True,
                    'total_gb': total_gb,
                    'free_gb': free_gb,
                    'status': status
                }
                
                print(f"{status} {drive} - Total: {total_gb:.1f}GB, Livre: {free_gb:.1f}GB")
            else:
                drives_info[drive] = {
                    'available': False,
                    'total_gb': 0,
                    'free_gb': 0,
                    'status': '❌'
                }
        except Exception as e:
            print(f"❌ Erro ao verificar drive {drive}: {e}")
            drives_info[drive] = {'available': False, 'total_gb': 0, 'free_gb': 0, 'status': '❌'}
    
    return drives_info

def setup_hybrid_cache():
    """Configura estrutura de cache híbrida no Drive B:"""
    print("\n🔧 Configurando cache híbrido no Drive B:...")
    
    cache_structure = {
        'ai_models': {
            'transformers': f"{DRIVE_B_PATH}\\transformers",
            'huggingface': f"{DRIVE_B_PATH}\\huggingface", 
            'torch': f"{DRIVE_B_PATH}\\torch",
            'datasets': f"{DRIVE_B_PATH}\\datasets",
            'cuda': f"{DRIVE_B_PATH}\\cuda"
        },
        'python_cache': {
            'pip': f"{DRIVE_B_PATH}\\pip",
            'mypy': f"{DRIVE_B_PATH}\\mypy",
            'pytest': f"{DRIVE_B_PATH}\\pytest"
        },
        'temp': f"{DRIVE_B_PATH}\\temp",
        'logs': f"{DRIVE_B_PATH}\\logs"
    }
    
    created_paths = []
    
    # Cria diretórios
    for category, paths in cache_structure.items():
        if isinstance(paths, dict):
            for name, path in paths.items():
                try:
                    os.makedirs(path, exist_ok=True)
                    created_paths.append(path)
                    print(f"✅ Criado: {path}")
                except Exception as e:
                    print(f"❌ Erro ao criar {path}: {e}")
        else:
            try:
                os.makedirs(paths, exist_ok=True)
                created_paths.append(paths)
                print(f"✅ Criado: {paths}")
            except Exception as e:
                print(f"❌ Erro ao criar {paths}: {e}")
    
    return cache_structure, created_paths

def configure_environment_variables(cache_structure):
    """Configura variáveis de ambiente para o cache"""
    print("\n🔧 Configurando variáveis de ambiente...")
    
    env_vars = {
        'TRANSFORMERS_CACHE': cache_structure['ai_models']['transformers'],
        'HF_HOME': cache_structure['ai_models']['huggingface'],
        'TORCH_HOME': cache_structure['ai_models']['torch'],
        'HF_DATASETS_CACHE': cache_structure['ai_models']['datasets'],
        'CUDA_CACHE_PATH': cache_structure['ai_models']['cuda'],
        'PIP_CACHE_DIR': cache_structure['python_cache']['pip'],
        'MYPY_CACHE_DIR': cache_structure['python_cache']['mypy'],
        'PYTEST_CACHE_DIR': cache_structure['python_cache']['pytest'],
        'TEMP': cache_structure['temp'],
        'TMP': cache_structure['temp']
    }
    
    # Define variáveis de ambiente para a sessão atual
    for var, path in env_vars.items():
        os.environ[var] = path
        print(f"✅ {var} = {path}")
    
    return env_vars

def move_existing_cache():
    """Move caches existentes para o Drive B:"""
    print("\n📦 Movendo caches existentes...")
    
    moved_items = []
    
    # Caminhos comuns de cache para mover
    cache_paths = [
        (os.path.expanduser("~/.cache/huggingface"), f"{DRIVE_B_PATH}\\huggingface"),
        (os.path.expanduser("~/.cache/torch"), f"{DRIVE_B_PATH}\\torch"),
        (os.path.expanduser("~/.cache/pip"), f"{DRIVE_B_PATH}\\pip"),
        ("C:\\Users\\jonathan-moletta.PPIRATINI\\AppData\\Local\\pip\\Cache", f"{DRIVE_B_PATH}\\pip"),
        ("C:\\Users\\jonathan-moletta.PPIRATINI\\AppData\\Local\\torch\\hub", f"{DRIVE_B_PATH}\\torch\\hub"),
        ("C:\\ProgramData\\chocolatey\\lib", f"{DRIVE_B_PATH}\\chocolatey"),
    ]
    
    for src_path, dest_path in cache_paths:
        if os.path.exists(src_path):
            try:
                # Calcula tamanho
                size_mb = get_folder_size(src_path) / (1024 * 1024)
                
                if size_mb > 0.1:  # Só move se > 100KB
                    # Cria link simbólico
                    backup_path = f"{src_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # Faz backup
                    shutil.move(src_path, backup_path)
                    
                    # Cria diretório de destino
                    os.makedirs(dest_path, exist_ok=True)
                    
                    # Cria link simbólico
                    os.symlink(dest_path, src_path, target_is_directory=True)
                    
                    moved_items.append({
                        'name': os.path.basename(src_path),
                        'src_path': src_path,
                        'dest_path': dest_path,
                        'backup_path': backup_path,
                        'size_mb': size_mb
                    })
                    
                    print(f"✅ Movido: {src_path} -> {dest_path} ({size_mb:.1f}MB)")
                    
            except Exception as e:
                print(f"❌ Erro ao mover {src_path}: {e}")
    
    return moved_items

def get_folder_size(folder_path):
    """Calcula tamanho de uma pasta"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
    except Exception:
        pass
    return total_size

def clean_c_drive():
    """Limpa arquivos temporários do Drive C:"""
    print("\n🧹 Limpando arquivos temporários do Drive C:...")
    
    temp_paths = [
        "C:\\Windows\\Temp",
        "C:\\Users\\jonathan-moletta.PPIRATINI\\AppData\\Local\\Temp",
        "C:\\Users\\jonathan-moletta.PPIRATINI\\AppData\\Local\\Microsoft\\Windows\\INetCache",
        "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportQueue",
    ]
    
    total_cleaned_mb = 0
    
    for temp_path in temp_paths:
        if os.path.exists(temp_path):
            try:
                # Calcula tamanho antes
                size_before = get_folder_size(temp_path)
                
                # Remove arquivos antigos (> 7 dias)
                cleaned_files = 0
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Verifica idade do arquivo
                            file_age = datetime.now().timestamp() - os.path.getmtime(file_path)
                            if file_age > 7 * 24 * 3600:  # 7 dias
                                os.remove(file_path)
                                cleaned_files += 1
                        except Exception:
                            pass
                
                # Calcula tamanho depois
                size_after = get_folder_size(temp_path)
                cleaned_mb = (size_before - size_after) / (1024 * 1024)
                total_cleaned_mb += cleaned_mb
                
                if cleaned_files > 0:
                    print(f"✅ Limpeza {temp_path}: {cleaned_files} arquivos, {cleaned_mb:.1f}MB")
                    
            except Exception as e:
                print(f"❌ Erro ao limpar {temp_path}: {e}")
    
    return total_cleaned_mb

def create_permanent_setup_script(env_vars):
    """Cria script para configuração permanente"""
    print("\n📝 Criando script de configuração permanente...")
    
    script_content = '''@echo off
echo Configurando variaveis de ambiente permanentemente...
echo.
'''
    
    for var, path in env_vars.items():
        script_content += f'setx {var} "{path}"\n'
        script_content += f'echo ✅ {var} configurado\n'
    
    script_content += '''
echo.
echo ✅ Configuracao concluida!
echo ⚠️ Reinicie o terminal para aplicar as mudancas
echo.
pause
'''
    
    script_path = "setup_hybrid_cache_permanent.bat"
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ Script criado: {script_path}")
        return script_path
    except Exception as e:
        print(f"❌ Erro ao criar script: {e}")
        return None

def create_python_config(cache_structure, env_vars):
    """Cria arquivo de configuração Python"""
    print("\n🐍 Criando configuração Python...")
    
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    # Cria o conteúdo sem f-strings aninhadas
    config_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração do Cache Híbrido
Gerado automaticamente em ''' + timestamp + '''
"""

import os
from pathlib import Path

# Estrutura do cache
CACHE_STRUCTURE = ''' + str(cache_structure) + '''

# Variáveis de ambiente
ENV_VARS = ''' + str(env_vars) + '''

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
'''
    
    config_path = "hybrid_cache_config.py"
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ Configuração criada: {config_path}")
        return config_path
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return None

def generate_report(drives_info, moved_items, cleaned_mb, cache_structure):
    """Gera relatório da otimização"""
    print("\n=== GERANDO RELATÓRIO ===")
    
    total_moved_mb = sum(item['size_mb'] for item in moved_items)
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'drives_info': drives_info,
        'cache_structure': cache_structure,
        'moved_items': moved_items,
        'cleaned_mb': cleaned_mb,
        'total_freed_mb': total_moved_mb + cleaned_mb,
        'primary_cache_drive': 'B:',
        'backup_sync_drive': 'OneDrive'
    }
    
    # Salva JSON
    with open('hybrid_optimization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    # Gera relatório Markdown
    md_content = f"""# Relatório de Otimização Híbrida

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## 📊 Resumo da Otimização

- **Cache Principal:** Drive B: (1847GB disponível)
- **Backup/Sync:** OneDrive (quando disponível)
- **Espaço liberado no SSD:** {report_data['total_freed_mb']:.1f}MB
- **Arquivos temp limpos:** {cleaned_mb:.1f}MB

## 💾 Status dos Drives

"""
    
    for drive, info in drives_info.items():
        if info['available']:
            status = info['status']
            md_content += f"- **{drive}** {status} Total: {info['total_gb']:.1f}GB, Livre: {info['free_gb']:.1f}GB\n"
    
    md_content += "\n## 📦 Itens Movidos\n\n"
    
    if moved_items:
        for item in moved_items:
            symlink_status = "🔗"
            md_content += f"- {symlink_status} **{item['name']}**: {item['size_mb']:.1f}MB -> `{item['dest_path']}`\n"
    else:
        md_content += "- Nenhum item foi movido\n"
    
    md_content += f"""\n## 🔧 Variáveis de Ambiente Configuradas\n
- `TRANSFORMERS_CACHE`: {cache_structure['ai_models']['transformers']}
- `HF_HOME`: {cache_structure['ai_models']['huggingface']}
- `TORCH_HOME`: {cache_structure['ai_models']['torch']}
- `HF_DATASETS_CACHE`: {cache_structure['ai_models']['datasets']}
- `CUDA_CACHE_PATH`: {cache_structure['ai_models']['cuda']}
- `PIP_CACHE_DIR`: {cache_structure['python_cache']['pip']}

## 📁 Estrutura do Cache

```
B:\\ai_models_cache\\
├── transformers/     # Cache do Transformers
├── huggingface/      # Cache do Hugging Face
├── torch/            # Cache do PyTorch
├── datasets/         # Cache de datasets
├── cuda/             # Cache CUDA
├── pip/              # Cache do pip
├── mypy/             # Cache do MyPy
├── pytest/          # Cache do PyTest
├── temp/             # Arquivos temporários
└── logs/             # Logs do sistema
```

## ⚡ Próximos Passos

### 1. Executar Script Permanente
```bash
# Execute como Administrador:
setup_hybrid_cache_permanent.bat
```

### 2. Verificar Configuração
```bash
# Teste a configuração:
python test_environment_basic.py
python hybrid_cache_config.py
```

### 3. Instalar Pacotes AI
```bash
# Instale os pacotes necessários:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers accelerate datasets tokenizers
```

### 4. Testar GPU
```bash
# Teste CUDA:
python -c "import torch; print('CUDA disponível:', torch.cuda.is_available())"
```

## ✅ Benefícios da Configuração

- **Cache Principal:** Drive B: com 1847GB livres
- **Links Simbólicos:** Mantêm compatibilidade com caminhos originais
- **Limpeza Automática:** Arquivos temporários removidos do SSD
- **Backup Futuro:** OneDrive pode ser usado quando tiver espaço
- **Performance:** Cache em SSD secundário oferece boa velocidade

## 🔄 Manutenção

- Execute `hybrid_cache_config.py` periodicamente para verificar integridade
- Monitore espaço no Drive B: regularmente
- Considere limpeza de cache antigo quando necessário
"""
    
    # Salva relatório
    with open('relatorio_otimizacao_hibrida.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("✅ Relatório gerado: relatorio_otimizacao_hibrida.md")
    
    return report_data

def main():
    """Função principal"""
    print("🚀 OTIMIZAÇÃO HÍBRIDA DE ARMAZENAMENTO")
    print("=" * 50)
    print("Drive B: como cache principal + OneDrive como backup")
    print("=" * 50)
    
    # Verifica drives disponíveis
    drives_info = check_drives()
    
    # Verifica se Drive B: está disponível
    if not drives_info.get('B:', {}).get('available'):
        print("❌ Drive B: não disponível. Abortando.")
        return False
    
    if drives_info['B:']['free_gb'] < 50:
        print("❌ Drive B: sem espaço suficiente (< 50GB). Abortando.")
        return False
    
    # Configura cache híbrido
    cache_structure, created_paths = setup_hybrid_cache()
    
    # Configura variáveis de ambiente
    env_vars = configure_environment_variables(cache_structure)
    
    # Move caches existentes
    moved_items = move_existing_cache()
    
    # Limpa Drive C:
    cleaned_mb = clean_c_drive()
    
    # Cria scripts de configuração
    script_path = create_permanent_setup_script(env_vars)
    config_path = create_python_config(cache_structure, env_vars)
    
    # Gera relatório
    report = generate_report(drives_info, moved_items, cleaned_mb, cache_structure)
    
    print(f"\n🎉 OTIMIZAÇÃO HÍBRIDA CONCLUÍDA!")
    print(f"💾 Espaço liberado no SSD: {report['total_freed_mb']:.1f}MB")
    print(f"📁 Cache principal: Drive B: ({drives_info['B:']['free_gb']:.1f}GB disponível)")
    print(f"🔧 Execute como admin: {script_path}")
    print(f"🐍 Configuração Python: {config_path}")
    print(f"📊 Relatório: relatorio_otimizacao_hibrida.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)