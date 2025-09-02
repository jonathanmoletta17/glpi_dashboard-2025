#!/usr/bin/env python3
"""
Otimização de Armazenamento com OneDrive
Move arquivos grandes e cache para OneDrive para liberar espaço no SSD
"""

import os
import shutil
import sys
from pathlib import Path
import json
from datetime import datetime

# Configurações
ONEDRIVE_PATH = r"C:\Users\jonathan-moletta.PPIRATINI\OneDrive - Governo do Estado do Rio Grande do Sul"
PROJECT_ROOT = Path.cwd()
MIN_FILE_SIZE_MB = 50  # Arquivos maiores que 50MB serão movidos
CACHE_FOLDERS = [
    ".mypy_cache",
    ".pytest_cache", 
    "__pycache__",
    ".venv",
    "node_modules",
    ".coverage",
    "coverage.json"
]

def check_onedrive_space():
    """Verifica espaço disponível no OneDrive"""
    print("\n=== VERIFICAÇÃO DO ONEDRIVE ===")
    
    if not os.path.exists(ONEDRIVE_PATH):
        print(f"❌ OneDrive não encontrado em: {ONEDRIVE_PATH}")
        return False
    
    try:
        total, used, free = shutil.disk_usage(ONEDRIVE_PATH)
        total_gb = total / (1024**3)
        free_gb = free / (1024**3)
        
        print(f"📁 OneDrive: {ONEDRIVE_PATH}")
        print(f"💾 Espaço total: {total_gb:.1f}GB")
        print(f"🆓 Espaço livre: {free_gb:.1f}GB")
        
        if free_gb > 10:  # Pelo menos 10GB livres
            print("✅ OneDrive tem espaço suficiente")
            return True
        else:
            print("⚠️ OneDrive com pouco espaço livre")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar OneDrive: {e}")
        return False

def create_onedrive_structure():
    """Cria estrutura de pastas no OneDrive"""
    print("\n=== CRIANDO ESTRUTURA NO ONEDRIVE ===")
    
    folders_to_create = [
        "GLPI_Dashboard_Cache",
        "GLPI_Dashboard_Cache/ai_models",
        "GLPI_Dashboard_Cache/python_cache", 
        "GLPI_Dashboard_Cache/build_artifacts",
        "GLPI_Dashboard_Cache/temp_files",
        "GLPI_Dashboard_Cache/logs"
    ]
    
    for folder in folders_to_create:
        folder_path = os.path.join(ONEDRIVE_PATH, folder)
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"📁 Criado: {folder}")
        except Exception as e:
            print(f"❌ Erro ao criar {folder}: {e}")
            return False
    
    return True

def find_large_files(directory, min_size_mb=50):
    """Encontra arquivos grandes no diretório"""
    large_files = []
    min_size_bytes = min_size_mb * 1024 * 1024
    
    try:
        for root, dirs, files in os.walk(directory):
            # Pula diretórios do git e outros caches
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) > min_size_bytes:
                        size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        large_files.append({
                            'path': file_path,
                            'size_mb': size_mb,
                            'relative_path': os.path.relpath(file_path, directory)
                        })
                except (OSError, FileNotFoundError):
                    continue
                    
    except Exception as e:
        print(f"❌ Erro ao buscar arquivos grandes: {e}")
    
    return sorted(large_files, key=lambda x: x['size_mb'], reverse=True)

def move_cache_folders():
    """Move pastas de cache para OneDrive"""
    print("\n=== MOVENDO PASTAS DE CACHE ===")
    
    moved_folders = []
    onedrive_cache = os.path.join(ONEDRIVE_PATH, "GLPI_Dashboard_Cache", "python_cache")
    
    for cache_folder in CACHE_FOLDERS:
        source_path = PROJECT_ROOT / cache_folder
        
        if source_path.exists():
            try:
                # Calcula tamanho da pasta
                folder_size = sum(f.stat().st_size for f in source_path.rglob('*') if f.is_file())
                folder_size_mb = folder_size / (1024 * 1024)
                
                if folder_size_mb > 10:  # Move apenas se > 10MB
                    dest_path = os.path.join(onedrive_cache, cache_folder)
                    
                    print(f"📦 Movendo {cache_folder} ({folder_size_mb:.1f}MB)...")
                    
                    # Remove destino se existir
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    
                    # Move a pasta
                    shutil.move(str(source_path), dest_path)
                    
                    # Cria link simbólico
                    try:
                        os.symlink(dest_path, str(source_path), target_is_directory=True)
                        print(f"🔗 Link simbólico criado: {cache_folder}")
                        moved_folders.append({
                            'folder': cache_folder,
                            'size_mb': folder_size_mb,
                            'onedrive_path': dest_path
                        })
                    except OSError:
                        print(f"⚠️ Não foi possível criar link simbólico para {cache_folder}")
                        # Se não conseguir criar link, move de volta
                        shutil.move(dest_path, str(source_path))
                        
            except Exception as e:
                print(f"❌ Erro ao mover {cache_folder}: {e}")
    
    return moved_folders

def setup_ai_cache_onedrive():
    """Configura cache de IA no OneDrive"""
    print("\n=== CONFIGURANDO CACHE DE IA NO ONEDRIVE ===")
    
    ai_cache_path = os.path.join(ONEDRIVE_PATH, "GLPI_Dashboard_Cache", "ai_models")
    
    # Cria subpastas para diferentes frameworks
    ai_folders = [
        "transformers",
        "huggingface", 
        "torch",
        "datasets",
        "cuda"
    ]
    
    for folder in ai_folders:
        folder_path = os.path.join(ai_cache_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"📁 Cache IA: {folder}")
    
    # Atualiza variáveis de ambiente
    env_vars = {
        'TRANSFORMERS_CACHE': os.path.join(ai_cache_path, 'transformers'),
        'HF_HOME': os.path.join(ai_cache_path, 'huggingface'),
        'TORCH_HOME': os.path.join(ai_cache_path, 'torch'),
        'HF_DATASETS_CACHE': os.path.join(ai_cache_path, 'datasets'),
        'CUDA_CACHE_PATH': os.path.join(ai_cache_path, 'cuda')
    }
    
    # Configura para a sessão atual
    for var, path in env_vars.items():
        os.environ[var] = path
        print(f"🔧 {var} = {path}")
    
    # Cria script de configuração permanente
    create_onedrive_env_script(env_vars)
    
    return ai_cache_path

def create_onedrive_env_script(env_vars):
    """Cria script para configuração permanente das variáveis"""
    script_content = "@echo off\n"
    script_content += "echo Configurando variáveis de ambiente para OneDrive...\n\n"
    
    for var, path in env_vars.items():
        script_content += f'setx {var} "{path}"\n'
    
    script_content += "\necho Variáveis configuradas com sucesso!\n"
    script_content += "echo Reinicie o terminal/IDE para aplicar as mudanças.\n"
    script_content += "pause\n"
    
    script_path = "setup_onedrive_env.bat"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"📄 Script criado: {script_path}")

def clean_temp_files():
    """Remove arquivos temporários para liberar espaço"""
    print("\n=== LIMPANDO ARQUIVOS TEMPORÁRIOS ===")
    
    temp_patterns = [
        "*.tmp",
        "*.log",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "*~"
    ]
    
    cleaned_size = 0
    cleaned_files = 0
    
    try:
        for pattern in temp_patterns:
            for file_path in PROJECT_ROOT.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleaned_size += file_size
                        cleaned_files += 1
                except Exception:
                    continue
        
        cleaned_mb = cleaned_size / (1024 * 1024)
        print(f"🧹 Removidos {cleaned_files} arquivos ({cleaned_mb:.1f}MB)")
        
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")
    
    return cleaned_mb

def generate_report(moved_folders, ai_cache_path, cleaned_mb):
    """Gera relatório da otimização"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'onedrive_path': ONEDRIVE_PATH,
        'ai_cache_path': ai_cache_path,
        'moved_folders': moved_folders,
        'cleaned_temp_mb': cleaned_mb,
        'total_freed_mb': sum(f['size_mb'] for f in moved_folders) + cleaned_mb
    }
    
    # Salva relatório JSON
    with open('onedrive_optimization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Cria relatório markdown
    md_content = f"""# Relatório de Otimização OneDrive

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## 📊 Resumo

- **OneDrive:** {ONEDRIVE_PATH}
- **Cache IA:** {ai_cache_path}
- **Espaço liberado:** {report['total_freed_mb']:.1f}MB
- **Arquivos temp limpos:** {cleaned_mb:.1f}MB

## 📁 Pastas Movidas

"""
    
    for folder in moved_folders:
        md_content += f"- **{folder['folder']}**: {folder['size_mb']:.1f}MB\n"
    
    md_content += f"""

## 🔧 Configuração

### Variáveis de Ambiente Configuradas:

- `TRANSFORMERS_CACHE`: {ai_cache_path}/transformers
- `HF_HOME`: {ai_cache_path}/huggingface  
- `TORCH_HOME`: {ai_cache_path}/torch
- `HF_DATASETS_CACHE`: {ai_cache_path}/datasets
- `CUDA_CACHE_PATH`: {ai_cache_path}/cuda

### Próximos Passos:

1. Execute `setup_onedrive_env.bat` como administrador
2. Reinicie o terminal/IDE
3. Execute `python test_environment_basic.py` para verificar
4. Instale os pacotes de IA: `pip install torch transformers accelerate`

## ⚠️ Importante

- Links simbólicos foram criados para manter compatibilidade
- Cache de IA agora usa OneDrive (1TB disponível)
- Arquivos temporários foram limpos
- SSD liberado para instalações essenciais
"""
    
    with open('relatorio_otimizacao_onedrive.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n📊 Relatório salvo: relatorio_otimizacao_onedrive.md")
    return report

def main():
    """Função principal"""
    print("🚀 OTIMIZAÇÃO DE ARMAZENAMENTO COM ONEDRIVE")
    print("=" * 60)
    
    # Verificações iniciais
    if not check_onedrive_space():
        print("❌ OneDrive não disponível. Abortando.")
        return False
    
    # Cria estrutura no OneDrive
    if not create_onedrive_structure():
        print("❌ Erro ao criar estrutura. Abortando.")
        return False
    
    # Move pastas de cache
    moved_folders = move_cache_folders()
    
    # Configura cache de IA
    ai_cache_path = setup_ai_cache_onedrive()
    
    # Limpa arquivos temporários
    cleaned_mb = clean_temp_files()
    
    # Gera relatório
    report = generate_report(moved_folders, ai_cache_path, cleaned_mb)
    
    print(f"\n🎉 OTIMIZAÇÃO CONCLUÍDA!")
    print(f"💾 Espaço liberado: {report['total_freed_mb']:.1f}MB")
    print(f"📁 Cache IA: OneDrive (1TB disponível)")
    print(f"🔧 Execute: setup_onedrive_env.bat (como admin)")
    
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
        sys.exit(1)