#!/usr/bin/env python3
"""
Pre-commit Hook para Validação de Dependências

Este script deve ser configurado como um pre-commit hook para validar
dependências antes de cada commit.

Instalação:
    1. Copie este arquivo para .git/hooks/pre-commit
    2. Torne-o executável: chmod +x .git/hooks/pre-commit
    3. Ou use com pre-commit framework:
       - Adicione ao .pre-commit-config.yaml
       - Execute: pre-commit install
"""

import os
import sys
import subprocess
from pathlib import Path


def get_changed_python_files():
    """Obtém lista de arquivos Python modificados no commit"""
    try:
        # Obter arquivos staged para commit
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Filtrar apenas arquivos Python no diretório ai/
        python_files = [
            f for f in files 
            if f.endswith('.py') and ('ai/' in f or 'backend/' in f)
        ]
        
        return python_files
        
    except subprocess.CalledProcessError:
        return []


def run_dependency_check():
    """Executa a validação de dependências"""
    try:
        # Mudar para o diretório backend
        backend_dir = Path(__file__).parent.parent
        os.chdir(backend_dir)
        
        # Executar validação
        result = subprocess.run(
            [sys.executable, 'ai/monitor_dependencies.py', '--fail-on-circular', '--quiet'],
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0, result.stderr
        
    except Exception as e:
        return False, str(e)


def main():
    print("🔍 Verificando dependências circulares...")
    
    # Verificar se há arquivos Python modificados
    changed_files = get_changed_python_files()
    
    if not changed_files:
        print("✅ Nenhum arquivo Python modificado. Pulando validação.")
        return 0
    
    print(f"📁 Arquivos Python modificados: {len(changed_files)}")
    for file in changed_files[:5]:  # Mostrar apenas os primeiros 5
        print(f"   • {file}")
    if len(changed_files) > 5:
        print(f"   • ... e mais {len(changed_files) - 5} arquivos")
    
    # Executar validação
    is_valid, error_msg = run_dependency_check()
    
    if is_valid:
        print("✅ Validação de dependências passou!")
        return 0
    else:
        print("❌ FALHA na validação de dependências!")
        print("\n🔧 Para ver detalhes, execute:")
        print("   cd backend && python ai/monitor_dependencies.py")
        print("\n💡 Dicas para resolver dependências circulares:")
        print("   • Use injeção de dependências")
        print("   • Mova código comum para módulos base")
        print("   • Use imports tardios (lazy imports)")
        print("   • Refatore para quebrar ciclos")
        
        if error_msg:
            print(f"\n🐛 Erro: {error_msg}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())