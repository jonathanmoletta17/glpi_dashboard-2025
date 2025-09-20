#!/usr/bin/env python3
"""
Script para limpeza da raiz do projeto GLPI Dashboard
Remove apenas documentação de desenvolvimento e arquivos obsoletos
Mantém toda a funcionalidade e conhecimento técnico essencial
."""

import shutil
import sys
from pathlib import Path


def get_project_root():
    """Retorna o diretório raiz do projeto."""
    return Path(__file__).parent.parent


def get_files_to_remove():
    """Lista de arquivos e pastas para remoção."""
    return [
        # Documentação de Desenvolvimento
        "RELATORIO_AUDITORIA_COMPLETA_PROJETO.md",
        "RESUMO_EXECUTIVO_AUDITORIA.md",
        "STATUS_CORRECOES_APLICADAS.md",
        "STATUS_FINAL_SISTEMA.md",
        "CORRECOES_FINAL_APLICADAS.md",
        "CORRECAO_ERRO_404_RANKING.md",
        "VALIDACAO_CRITICA_PLANO_LIMPEZA.md",
        "RESUMO_VALIDACAO_CRITICA.md",
        "PLANO_IMPLEMENTACAO_FILTROS_DATA.md",
        "PROPOSTA_REFATORACAO_ARQUITETURAL.md",
        "REFACTORING_PROMPTS.md",
        "GUIA_IMPLEMENTACAO_REFATORACAO.md",
        "TRAE_AI_INSTRUCTIONS.md",
        "FILTROS_DATA_IMPLEMENTACAO_COMPLETA.md",
        "RESUMO_FINAL_FILTROS_DATA.md",
        "METRICS_SOLUTION_DOCUMENTATION.md",
        "DIAGNOSTICO_CARDS_STATUS.md",
        "GARANTIA_FUNCIONAMENTO_INTERFACE.md",
        "REFATORACAO_CSS_RANKING_CARD.md",
        "TESTE_REFATORACAO_CSS.md",
        "README_CLEAN_STRUCTURE.md",
        # Configurações de Teste
        "TESTING_PROTOCOL.md",
        "TESTING_README.md",
        "VALIDATION_REPORT.md",
        "VALIDATION_REPORT.json",
        "validacao_filtros_data.json",
        "CLEANUP_REPORT.md",
        "test_config.py",
        "coverage.json",
        # Configurações de CI/CD
        "codecov.yml",
        "sonar-project.properties",
        "uv.lock",
        # Contexto e Análise
        "CONTEXT_ANALYSIS.md",
        "CONTRIBUTING.md",
        "CI_SETUP.md",
        "KNOWLEDGE_BASE.md",
        # Logs de Debug
        "backend/debug_ranking.log",
        "backend/debug_technician_ranking.log",
        "backend/logs/ai_integration_test.log",
        # Configurações de IA
        "config/ai_agent_system.yaml",
        "config/sandbox.json",
        "trae-context.yml",
        # Pastas completas
        "docs/ai/",
    ]


def get_files_to_keep():
    """Lista de arquivos essenciais que devem ser mantidos."""
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
        "docs/GLPI_KNOWLEDGE_BASE.md",
        "docs/AI_ASSISTANT_CONTEXT.md",
        "docs/SISTEMA_TRATAMENTO_ERROS.md",
        # Scripts de Validação
        "validar_filtros_data.py",
        "scripts/cleanup_project.py",
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
    """Remove arquivo ou diretório de forma segura."""
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
    """Valida se arquivos essenciais ainda existem."""
    root = get_project_root()
    essential_files = [
        "backend/app.py",
        "frontend/package.json",
        "config/system.yaml",
        "requirements.txt",
        "docker-compose.yml",
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


def main():
    """Função principal de limpeza."""
    print("🧹 INICIANDO LIMPEZA DA RAIZ DO PROJETO GLPI DASHBOARD")
    print("=" * 60)

    root = get_project_root()
    files_to_remove = get_files_to_remove()

    # Validação prévia
    print("\n📋 VALIDAÇÃO PRÉVIA:")
    if not validate_essential_files():
        print("❌ Abortando limpeza - arquivos essenciais não encontrados")
        sys.exit(1)

    # Confirmação
    print(f"\n🎯 ARQUIVOS PARA REMOÇÃO: {len(files_to_remove)}")
    for file_path in files_to_remove:
        print(f"   - {file_path}")

    response = input("\n❓ Continuar com a limpeza? (s/N): ").strip().lower()
    if response not in ["s", "sim", "y", "yes"]:
        print("❌ Limpeza cancelada pelo usuário")
        sys.exit(0)

    # Execução da limpeza
    print("\n🧹 EXECUTANDO LIMPEZA:")
    removed_count = 0
    failed_count = 0

    for file_path in files_to_remove:
        full_path = root / file_path
        if full_path.exists():
            if remove_file_or_dir(full_path):
                removed_count += 1
            else:
                failed_count += 1
        else:
            print(f"⚠️  Arquivo não encontrado: {file_path}")

    # Validação pós-limpeza
    print("\n📋 VALIDAÇÃO PÓS-LIMPEZA:")
    if not validate_essential_files():
        print("❌ ERRO: Arquivos essenciais foram removidos!")
        print("   Execute 'git checkout' para restaurar se necessário")
        sys.exit(1)

    # Relatório final
    print("\n🎉 LIMPEZA CONCLUÍDA:")
    print(f"   ✅ Arquivos removidos: {removed_count}")
    print(f"   ❌ Falhas: {failed_count}")
    print(f"   📁 Total processado: {len(files_to_remove)}")

    print("\n📋 ESTRUTURA FINAL MANTIDA:")
    essential_structure = [
        "backend/ - Código do backend",
        "frontend/ - Código do frontend",
        "config/ - Configurações do sistema",
        "docs/ - Documentação técnica",
        "scripts/ - Scripts de validação",
        "monitoring/ - Configuração de monitoramento",
        "docker-compose.yml - Orquestração",
        "requirements.txt - Dependências",
    ]

    for item in essential_structure:
        print(f"   ✅ {item}")

    print("\n🚀 PROJETO LIMPO E FUNCIONAL!")


if __name__ == "__main__":
    main()
