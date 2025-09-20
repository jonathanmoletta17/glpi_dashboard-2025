#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Limpeza do Projeto GLPI Dashboard
Remove arquivos obsoletos, duplicações e organiza estrutura
."""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ProjectCleanup:
    """Classe para limpeza e organização do projeto."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "docs" / "archive"
        self.removed_files = []
        self.moved_files = []
        self.errors = []

    def log_action(self, action: str, file_path: str, status: str = "SUCCESS"):
        """Registra ação realizada."""
        print(f"[{status}] {action}: {file_path}")

    def create_backup_structure(self):
        """Cria estrutura de backup para arquivos importantes."""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            self.log_action("CREATE", f"Diretório de backup: {self.backup_dir}")
            return True
        except Exception as e:
            self.errors.append(f"Erro ao criar backup: {e}")
            return False

    def remove_backup_files(self) -> bool:
        """Remove arquivos .backup."""
        backup_patterns = ["**/*.backup", "**/*.bak", "**/*.old", "**/*.tmp", "**/*.temp"]

        removed_count = 0
        for pattern in backup_patterns:
            for file_path in self.project_root.glob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        self.removed_files.append(str(file_path))
                        self.log_action("REMOVE", str(file_path))
                        removed_count += 1
                except Exception as e:
                    self.errors.append(f"Erro ao remover {file_path}: {e}")

        print(f"✅ Removidos {removed_count} arquivos backup")
        return removed_count > 0

    def remove_debug_files(self) -> bool:
        """Remove arquivos de debug e logs temporários."""
        debug_files = [
            "debug_ranking.log",
            "debug_technician_ranking.log",
            "debug_date_validation.py",
            "debug_decorator.py",
            "debug_full_decorator.py",
            "docs/debug_resultado.txt",
        ]
        # NOTA: validar_filtros_data.py NÃO deve ser removido - é um script funcional importante

        removed_count = 0
        for file_path in debug_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    self.removed_files.append(str(full_path))
                    self.log_action("REMOVE", str(full_path))
                    removed_count += 1
                except Exception as e:
                    self.errors.append(f"Erro ao remover {full_path}: {e}")

        print(f"✅ Removidos {removed_count} arquivos de debug")
        return removed_count > 0

    def remove_refactored_duplicates(self) -> bool:
        """Remove arquivos refatorados duplicados - CUIDADO: Analisar antes de remover."""
        refactored_files = [
            "frontend/src/components/dashboard/MetricsGrid-refactored.tsx",
            "frontend/src/components/dashboard/StatusCard-refactored.tsx",
            "frontend/src/components/dashboard/NewTicketsList-refactored.tsx",
            "frontend/src/components/dashboard/RankingTable-refactored-example.tsx",
            "frontend/src/styles/metrics-grid-refactored.css",
            "frontend/src/styles/status-card-refactored.css",
            "frontend/src/styles/new-tickets-list-refactored.css",
            "frontend/src/styles/ranking-card-refactored.css",
        ]
        # NOTA: Estes arquivos podem conter melhorias não migradas - analisar antes de remover

        removed_count = 0
        for file_path in refactored_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    self.removed_files.append(str(full_path))
                    self.log_action("REMOVE", str(full_path))
                    removed_count += 1
                except Exception as e:
                    self.errors.append(f"Erro ao remover {full_path}: {e}")

        print(f"✅ Removidos {removed_count} arquivos refatorados duplicados")
        return removed_count > 0

    def remove_duplicate_services(self) -> bool:
        """Remove serviços duplicados."""
        duplicate_services = ["backend/services/glpi_service_backup.py"]

        removed_count = 0
        for file_path in duplicate_services:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Mover para backup antes de remover
                    backup_path = self.backup_dir / "services" / full_path.name
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(full_path), str(backup_path))
                    self.moved_files.append(f"{full_path} -> {backup_path}")
                    self.log_action("MOVE", f"{full_path} -> {backup_path}")
                    removed_count += 1
                except Exception as e:
                    self.errors.append(f"Erro ao mover {full_path}: {e}")

        print(f"✅ Movidos {removed_count} serviços duplicados para backup")
        return removed_count > 0

    def archive_old_reports(self) -> bool:
        """Move relatórios antigos para archive."""
        old_reports = [
            "API_ERRORS_RESOLUTION_REPORT.md",
            "APP_REFACTORING_REPORT.md",
            "BACKEND_ARCHITECTURE_ANALYSIS.md",
            "BACKEND_CONSOLIDATION_PRIORITIES.md",
            "BACKEND_CONSOLIDATION_PROMPTS.md",
            "BACKEND_TIMEOUT_FIX_REPORT.md",
            "CONFIG_CONSOLIDATION_REPORT.md",
            "EVIDENCE_REPORT.md",
            "FRONTEND_BACKEND_FIXES_REPORT.md",
            "PHASE1_CLEANUP_REPORT.md",
            "PHASE2_ARCHITECTURAL_REFACTORING_REPORT.md",
            "PHASE3_4_CONSOLIDATION_REPORT.md",
            "ROUTES_CLEANING_REPORT.md",
            "RELATORIO_AUDITORIA_CONSISTENCIA.md",
            "RELATORIO_AUDITORIA_TECNICA_FRONTEND.md",
        ]

        moved_count = 0
        for report in old_reports:
            full_path = self.project_root / report
            if full_path.exists():
                try:
                    archive_path = self.backup_dir / "reports" / full_path.name
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(full_path), str(archive_path))
                    self.moved_files.append(f"{full_path} -> {archive_path}")
                    self.log_action("MOVE", f"{full_path} -> {archive_path}")
                    moved_count += 1
                except Exception as e:
                    self.errors.append(f"Erro ao mover {full_path}: {e}")

        print(f"✅ Movidos {moved_count} relatórios para archive")
        return moved_count > 0

    def organize_root_files(self) -> bool:
        """Organiza arquivos soltos na raiz."""
        root_files = {
            "como_configurar_trae_ai.txt": "docs/",
            "RELATORIO_AUDITORIA_UTILS_FRONTEND.md": "docs/",
        }

        moved_count = 0
        for file_name, target_dir in root_files.items():
            source_path = self.project_root / file_name
            if source_path.exists():
                try:
                    target_path = self.project_root / target_dir / file_name
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source_path), str(target_path))
                    self.moved_files.append(f"{source_path} -> {target_path}")
                    self.log_action("MOVE", f"{source_path} -> {target_path}")
                    moved_count += 1
                except Exception as e:
                    self.errors.append(f"Erro ao mover {source_path}: {e}")

        print(f"✅ Movidos {moved_count} arquivos da raiz")
        return moved_count > 0

    def update_gitignore(self) -> bool:
        """Atualiza .gitignore para evitar arquivos temporários."""
        gitignore_path = self.project_root / ".gitignore"

        new_entries = [
            "",
            "# Arquivos temporários e backup",
            "*.backup",
            "*.bak",
            "*.old",
            "*.tmp",
            "*.temp",
            "debug_*.log",
            "debug_*.py",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "node_modules/",
            ".pytest_cache/",
            ".coverage",
            "htmlcov/",
            ".mypy_cache/",
            ".tox/",
            ".venv/",
            "venv/",
            "ENV/",
            "env/",
            ".env.local",
            ".env.development.local",
            ".env.test.local",
            ".env.production.local",
        ]

        try:
            # Ler .gitignore atual
            existing_entries = []
            if gitignore_path.exists():
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    existing_entries = f.readlines()

            # Adicionar novas entradas se não existirem
            existing_text = "".join(existing_entries)
            new_entries_to_add = []

            for entry in new_entries:
                if entry.strip() and entry.strip() not in existing_text:
                    new_entries_to_add.append(entry + "\n")

            if new_entries_to_add:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.writelines(new_entries_to_add)
                self.log_action("UPDATE", ".gitignore")
                print(f"✅ Adicionadas {len(new_entries_to_add)} entradas ao .gitignore")
                return True
            else:
                print("✅ .gitignore já está atualizado")
                return True

        except Exception as e:
            self.errors.append(f"Erro ao atualizar .gitignore: {e}")
            return False

    def generate_cleanup_report(self) -> str:
        """Gera relatório da limpeza realizada."""
        report = f"""
# 🧹 Relatório de Limpeza do Projeto

## 📊 Resumo da Limpeza

**Data**: {Path().cwd()}
**Arquivos Removidos**: {len(self.removed_files)}
**Arquivos Movidos**: {len(self.moved_files)}
**Erros**: {len(self.errors)}

## 🗑️ Arquivos Removidos

."""

        for file_path in self.removed_files:
            report += f"- {file_path}\n"

        report += "\n## 📁 Arquivos Movidos\n\n"
        for move_info in self.moved_files:
            report += f"- {move_info}\n"

        if self.errors:
            report += "\n## ❌ Erros Encontrados\n\n"
            for error in self.errors:
                report += f"- {error}\n"

        report += f"""
## ✅ Próximos Passos

1. Verificar se a aplicação ainda funciona
2. Executar testes para garantir que nada quebrou
3. Commit das mudanças
4. Atualizar documentação se necessário

## 📋 Checklist Pós-Limpeza

- [ ] Aplicação funcionando
- [ ] Testes passando
- [ ] Imports atualizados
- [ ] Documentação atualizada
- [ ] Commit realizado
."""

        return report

    def run_cleanup(self, dry_run: bool = False) -> bool:
        """Executa limpeza completa do projeto."""
        print("🧹 INICIANDO LIMPEZA DO PROJETO GLPI DASHBOARD")
        print("=" * 60)
        print()

        if dry_run:
            print("🔍 MODO DRY RUN - Nenhuma alteração será feita")
            print()

        try:
            # Criar estrutura de backup
            if not dry_run:
                self.create_backup_structure()

            # Executar limpeza
            steps = [
                ("Removendo arquivos backup", self.remove_backup_files),
                ("Removendo arquivos debug", self.remove_debug_files),
                ("Removendo arquivos refatorados duplicados", self.remove_refactored_duplicates),
                ("Removendo serviços duplicados", self.remove_duplicate_services),
                ("Arquivando relatórios antigos", self.archive_old_reports),
                ("Organizando arquivos da raiz", self.organize_root_files),
                ("Atualizando .gitignore", self.update_gitignore),
            ]

            for step_name, step_func in steps:
                print(f"🔧 {step_name}...")
                if not dry_run:
                    step_func()
                else:
                    print(f"   [DRY RUN] {step_name}")
                print()

            # Gerar relatório
            report = self.generate_cleanup_report()

            if not dry_run:
                report_path = self.project_root / "CLEANUP_REPORT.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(report)
                self.log_action("CREATE", str(report_path))

            print("📊 RESUMO DA LIMPEZA")
            print("=" * 40)
            print(f"Arquivos Removidos: {len(self.removed_files)}")
            print(f"Arquivos Movidos: {len(self.moved_files)}")
            print(f"Erros: {len(self.errors)}")
            print()

            if self.errors:
                print("❌ ERROS ENCONTRADOS:")
                for error in self.errors:
                    print(f"   {error}")
                print()

            if not dry_run:
                print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
                print("📄 Relatório salvo em: CLEANUP_REPORT.md")
            else:
                print("✅ DRY RUN CONCLUÍDO!")
                print("Execute sem --dry-run para aplicar as mudanças")

            return len(self.errors) == 0

        except Exception as e:
            print(f"❌ ERRO CRÍTICO: {e}")
            return False


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Script de limpeza do projeto GLPI Dashboard")
    parser.add_argument("--dry-run", action="store_true", help="Executa sem fazer alterações")
    parser.add_argument("--project-root", default=".", help="Diretório raiz do projeto")

    args = parser.parse_args()

    cleanup = ProjectCleanup(args.project_root)
    success = cleanup.run_cleanup(dry_run=args.dry_run)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
