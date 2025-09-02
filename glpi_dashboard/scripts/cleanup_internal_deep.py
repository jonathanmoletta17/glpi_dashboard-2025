#!/usr/bin/env python3
"""
Script para limpeza interna profunda do projeto GLPI Dashboard
Remove documentação de desenvolvimento, testes excessivos e configurações obsoletas
Mantém apenas código funcional e configurações essenciais
"""

import os
import shutil
import sys
from pathlib import Path

def get_project_root():
    """Retorna o diretório raiz do projeto"""
    return Path(__file__).parent.parent

def get_files_to_remove():
    """Lista de arquivos e pastas para remoção"""
    return [
        # Documentação de Desenvolvimento na Raiz
        "ANALISE_LIMPEZA_RAIZ.md",
        "CORRECOES_FINAIS_APLICADAS.md",
        "RELATORIO_LIMPEZA_FINAL.md",
        "RELATORIO_EVIDENCIAS_TECNICOS_GLPI.txt",
        
        # Backend - Documentação de Desenvolvimento
        "backend/docs/",
        "backend/Makefile",
        "backend/pyproject.toml",
        "backend/pytest.ini",
        "backend/logs/",
        
        # Config - Scripts de Setup Obsoletos
        "config/setup/",
        "config/README.md",
        
        # Docs - Documentação de Desenvolvimento
        "docs/analysis/",
        "docs/archive/",
        "docs/AI_ASSISTANT_CONTEXT.md",
        "docs/AI_INTEGRATION_GUIDE.md",
        "docs/AUDITORIA_COMPLETA_RESULTADOS.md",
        "docs/DATA_FLOW_DOCUMENTATION.md",
        "docs/GUIA_IMPLEMENTACAO_FILTROS_DATA_GLPI.md",
        "docs/RELATORIO_EVIDENCIAS_TECNICOS_GLPI.txt",
        "docs/resultado_teste.txt",
        "docs/SISTEMA_TRATAMENTO_ERROS.md",
        "docs/TESTING_GUIDE.md",
        "docs/validacao_dados_corrigidos.txt",
        
        # Frontend - Testes Excessivos
        "frontend/src/__tests__/",
        "frontend/src/test/",
        "frontend/src/test-setup.ts",
        "frontend/src/mocks/",
        "frontend/src/styles/",
        "frontend/src/utils/",
        "frontend/RELATORIO_TESTES.md",
        "frontend/jest.config.js",
        "frontend/playwright.config.e2e.ts",
        "frontend/playwright.config.ts",
        "frontend/vitest.config.integration.ts",
        "frontend/vitest.config.unit.ts",
        "frontend/test-api.html",
        
        # Scripts - Validação de Acessibilidade
        "scripts/validate-accessibility.js",
    ]

def get_files_to_keep():
    """Lista de arquivos essenciais que devem ser mantidos"""
    return [
        # Configuração e Infraestrutura
        "config/system.yaml",
        "requirements.txt",
        "pyproject.toml",
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        
        # Documentação Técnica da API
        "docs/api/openapi.yaml",
        "docs/api/README.md",
        "docs/GLPI_KNOWLEDGE_BASE.md",
        
        # Scripts de Validação Essenciais
        "validar_filtros_data.py",
        "scripts/cleanup_project.py",
        "scripts/cleanup_root.py",
        "scripts/validate_cleanup.py",
        
        # Estrutura do Projeto
        "backend/",
        "frontend/",
        "monitoring/",
        "config/",
        "docs/",
        "scripts/",
    ]

def remove_file_or_dir(path):
    """Remove arquivo ou diretório de forma segura"""
    try:
        if path.is_file():
            path.unlink()
            print(f"✅ Removido arquivo: {path}")
        elif path.is_dir():
            shutil.rmtree(path)
            print(f"✅ Removido diretório: {path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao remover {path}: {e}")
        return False

def validate_essential_files():
    """Valida se arquivos essenciais ainda existem"""
    root = get_project_root()
    essential_files = [
        "backend/app.py",
        "frontend/package.json",
        "config/system.yaml",
        "requirements.txt",
        "docker-compose.yml",
        "docs/api/openapi.yaml",
        "docs/GLPI_KNOWLEDGE_BASE.md"
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not (root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ ATENÇÃO: Arquivos essenciais não encontrados:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Todos os arquivos essenciais estão presentes")
    return True

def count_files_in_directory(directory):
    """Conta arquivos em um diretório recursivamente"""
    count = 0
    if directory.exists():
        for item in directory.rglob('*'):
            if item.is_file():
                count += 1
    return count

def main():
    """Função principal de limpeza interna profunda"""
    print("🔍 INICIANDO LIMPEZA INTERNA PROFUNDA DO PROJETO GLPI DASHBOARD")
    print("=" * 70)
    
    root = get_project_root()
    files_to_remove = get_files_to_remove()
    
    # Contagem de arquivos antes da limpeza
    print("\n📊 CONTAGEM DE ARQUIVOS ANTES DA LIMPEZA:")
    total_files_before = 0
    for item in root.rglob('*'):
        if item.is_file():
            total_files_before += 1
    print(f"   📁 Total de arquivos: {total_files_before}")
    
    # Validação prévia
    print("\n📋 VALIDAÇÃO PRÉVIA:")
    if not validate_essential_files():
        print("❌ Abortando limpeza - arquivos essenciais não encontrados")
        sys.exit(1)
    
    # Confirmação
    print(f"\n🎯 ARQUIVOS/PASTAS PARA REMOÇÃO: {len(files_to_remove)}")
    for file_path in files_to_remove:
        full_path = root / file_path
        if full_path.exists():
            if full_path.is_dir():
                file_count = count_files_in_directory(full_path)
                print(f"   📁 {file_path} ({file_count} arquivos)")
            else:
                print(f"   📄 {file_path}")
        else:
            print(f"   ⚠️  {file_path} (não encontrado)")
    
    response = input("\n❓ Continuar com a limpeza interna profunda? (s/N): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Limpeza cancelada pelo usuário")
        sys.exit(0)
    
    # Execução da limpeza
    print("\n🧹 EXECUTANDO LIMPEZA INTERNA PROFUNDA:")
    removed_count = 0
    failed_count = 0
    files_removed = 0
    
    for file_path in files_to_remove:
        full_path = root / file_path
        if full_path.exists():
            if full_path.is_dir():
                file_count = count_files_in_directory(full_path)
                files_removed += file_count
            
            if remove_file_or_dir(full_path):
                removed_count += 1
            else:
                failed_count += 1
        else:
            print(f"⚠️  Arquivo não encontrado: {file_path}")
    
    # Contagem de arquivos após a limpeza
    print("\n📊 CONTAGEM DE ARQUIVOS APÓS A LIMPEZA:")
    total_files_after = 0
    for item in root.rglob('*'):
        if item.is_file():
            total_files_after += 1
    print(f"   📁 Total de arquivos: {total_files_after}")
    print(f"   📉 Arquivos removidos: {total_files_before - total_files_after}")
    
    # Validação pós-limpeza
    print("\n📋 VALIDAÇÃO PÓS-LIMPEZA:")
    if not validate_essential_files():
        print("❌ ERRO: Arquivos essenciais foram removidos!")
        print("   Execute 'git checkout' para restaurar se necessário")
        sys.exit(1)
    
    # Relatório final
    print("\n🎉 LIMPEZA INTERNA PROFUNDA CONCLUÍDA:")
    print(f"   ✅ Diretórios/arquivos removidos: {removed_count}")
    print(f"   ❌ Falhas: {failed_count}")
    print(f"   📁 Total processado: {len(files_to_remove)}")
    print(f"   📄 Arquivos individuais removidos: {files_removed}")
    print(f"   📊 Redução total: {total_files_before - total_files_after} arquivos")
    
    print("\n📋 ESTRUTURA FINAL ULTRA-LIMPA:")
    essential_structure = [
        "backend/ - Código do backend (sem docs de desenvolvimento)",
        "frontend/ - Código do frontend (sem testes excessivos)", 
        "config/ - Configurações essenciais (sem setup scripts)",
        "docs/ - Documentação técnica da API apenas",
        "scripts/ - Scripts de manutenção essenciais",
        "monitoring/ - Configuração de monitoramento",
        "docker-compose.yml - Orquestração",
        "requirements.txt - Dependências",
    ]
    
    for item in essential_structure:
        print(f"   ✅ {item}")
    
    print("\n🚀 PROJETO ULTRA-LIMPO E FUNCIONAL!")

if __name__ == "__main__":
    main()
