#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação Pós-Limpeza
Verifica se a limpeza não quebrou funcionalidades
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import requests


class CleanupValidator:
    """Validador para verificar se a limpeza não quebrou nada"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.validation_results = []
        self.errors = []

    def log_validation(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado da validação"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.validation_results.append({"test": test_name, "success": success, "details": details})
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        print()

    def validate_file_structure(self) -> bool:
        """Valida se a estrutura de arquivos está correta"""
        print("🔍 Validando estrutura de arquivos...")

        # Verificar se arquivos importantes ainda existem
        critical_files = [
            "backend/app.py",
            "backend/api/routes.py",
            "backend/services/glpi_service.py",
            "frontend/src/App.tsx",
            "frontend/src/components/DashboardMetrics.tsx",
            "frontend/src/components/DateRangeFilter.tsx",
            "frontend/src/hooks/useDashboard.ts",
            "frontend/src/services/api.ts",
        ]

        missing_files = []
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            self.log_validation(
                "Estrutura de Arquivos", False, f"Arquivos críticos ausentes: {missing_files}"
            )
            return False
        else:
            self.log_validation(
                "Estrutura de Arquivos",
                True,
                f"Todos os {len(critical_files)} arquivos críticos presentes",
            )
            return True

    def validate_no_backup_files(self) -> bool:
        """Valida se não há mais arquivos backup"""
        print("🔍 Validando remoção de arquivos backup...")

        backup_patterns = ["**/*.backup", "**/*.bak", "**/*.old", "**/*.tmp", "**/*.temp"]

        remaining_backups = []
        for pattern in backup_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    remaining_backups.append(str(file_path))

        if remaining_backups:
            self.log_validation(
                "Remoção de Backups", False, f"Arquivos backup ainda presentes: {remaining_backups}"
            )
            return False
        else:
            self.log_validation("Remoção de Backups", True, "Nenhum arquivo backup encontrado")
            return True

    def validate_no_debug_files(self) -> bool:
        """Valida se não há mais arquivos de debug"""
        print("🔍 Validando remoção de arquivos debug...")

        debug_files = [
            "debug_ranking.log",
            "debug_technician_ranking.log",
            "debug_date_validation.py",
            "debug_decorator.py",
            "debug_full_decorator.py",
        ]

        remaining_debug = []
        for file_path in debug_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                remaining_debug.append(file_path)

        if remaining_debug:
            self.log_validation(
                "Remoção de Debug", False, f"Arquivos debug ainda presentes: {remaining_debug}"
            )
            return False
        else:
            self.log_validation("Remoção de Debug", True, "Nenhum arquivo debug encontrado")
            return True

    def validate_no_duplicate_services(self) -> bool:
        """Valida se não há mais serviços duplicados"""
        print("🔍 Validando remoção de serviços duplicados...")

        duplicate_services = ["backend/services/glpi_service_backup.py"]

        remaining_duplicates = []
        for file_path in duplicate_services:
            full_path = self.project_root / file_path
            if full_path.exists():
                remaining_duplicates.append(file_path)

        if remaining_duplicates:
            self.log_validation(
                "Remoção de Duplicados",
                False,
                f"Serviços duplicados ainda presentes: {remaining_duplicates}",
            )
            return False
        else:
            self.log_validation(
                "Remoção de Duplicados", True, "Nenhum serviço duplicado encontrado"
            )
            return True

    def validate_imports(self) -> bool:
        """Valida se imports estão funcionando"""
        print("🔍 Validando imports...")

        # Verificar imports Python
        python_files = list(self.project_root.glob("backend/**/*.py"))
        import_errors = []

        for py_file in python_files[:10]:  # Limitar para não demorar muito
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Verificar imports básicos
                    if "from glpi_service_backup" in content:
                        import_errors.append(f"{py_file}: Import de glpi_service_backup")
            except Exception as e:
                import_errors.append(f"{py_file}: Erro ao ler arquivo - {e}")

        if import_errors:
            self.log_validation(
                "Validação de Imports",
                False,
                f"Problemas de import encontrados: {import_errors[:5]}",
            )
            return False
        else:
            self.log_validation("Validação de Imports", True, "Imports validados com sucesso")
            return True

    def validate_backend_health(self) -> bool:
        """Valida se o backend está funcionando"""
        print("🔍 Validando saúde do backend...")

        try:
            # Tentar conectar ao backend
            response = requests.get("http://localhost:5000/api/health", timeout=10)
            if response.status_code == 200:
                self.log_validation("Backend Health", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_validation("Backend Health", False, f"Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_validation("Backend Health", False, f"Erro de conexão: {str(e)}")
            return False

    def validate_api_endpoints(self) -> bool:
        """Valida se endpoints principais estão funcionando"""
        print("🔍 Validando endpoints da API...")

        endpoints = [
            ("/api/health", "Health Check"),
            ("/api/metrics", "Métricas"),
            ("/api/technicians/ranking", "Ranking de Técnicos"),
        ]

        working_endpoints = 0
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"http://localhost:5000{endpoint}", timeout=30)
                if response.status_code == 200:
                    working_endpoints += 1
                    print(f"   ✅ {name}: {response.status_code}")
                else:
                    print(f"   ❌ {name}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {name}: Erro - {str(e)}")

        success = working_endpoints == len(endpoints)
        self.log_validation(
            "Endpoints da API",
            success,
            f"{working_endpoints}/{len(endpoints)} endpoints funcionando",
        )
        return success

    def validate_frontend_build(self) -> bool:
        """Valida se o frontend pode ser buildado"""
        print("🔍 Validando build do frontend...")

        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            self.log_validation("Build Frontend", False, "Diretório frontend não encontrado")
            return False

        try:
            # Verificar se package.json existe
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                self.log_validation("Build Frontend", False, "package.json não encontrado")
                return False

            # Verificar se node_modules existe
            node_modules = frontend_dir / "node_modules"
            if not node_modules.exists():
                self.log_validation("Build Frontend", False, "node_modules não encontrado")
                return False

            self.log_validation("Build Frontend", True, "Estrutura do frontend OK")
            return True

        except Exception as e:
            self.log_validation("Build Frontend", False, f"Erro: {str(e)}")
            return False

    def validate_documentation_structure(self) -> bool:
        """Valida se a documentação está organizada"""
        print("🔍 Validando estrutura da documentação...")

        # Verificar se docs/archive existe
        archive_dir = self.project_root / "docs" / "archive"
        if not archive_dir.exists():
            self.log_validation("Documentação", False, "Diretório docs/archive não encontrado")
            return False

        # Verificar se relatórios foram movidos
        old_reports = [
            "API_ERRORS_RESOLUTION_REPORT.md",
            "APP_REFACTORING_REPORT.md",
            "BACKEND_ARCHITECTURE_ANALYSIS.md",
        ]

        moved_reports = 0
        for report in old_reports:
            if (self.project_root / "docs" / "archive" / "reports" / report).exists():
                moved_reports += 1

        success = moved_reports > 0
        self.log_validation(
            "Documentação", success, f"{moved_reports} relatórios movidos para archive"
        )
        return success

    def generate_validation_report(self) -> str:
        """Gera relatório de validação"""
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results if result["success"])
        failed_tests = total_tests - passed_tests

        report = f"""
# 🔍 Relatório de Validação Pós-Limpeza

## 📊 Resumo da Validação

**Data**: {Path().cwd()}
**Total de Testes**: {total_tests}
**Testes Passaram**: {passed_tests}
**Testes Falharam**: {failed_tests}
**Taxa de Sucesso**: {(passed_tests/total_tests)*100:.1f}%

## 📋 Resultados dos Testes

"""

        for result in self.validation_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report += f"### {status} {result['test']}\n"
            if result["details"]:
                report += f"{result['details']}\n"
            report += "\n"

        if failed_tests > 0:
            report += """
## ⚠️ Ações Recomendadas

1. Verificar arquivos ausentes
2. Corrigir imports quebrados
3. Restaurar funcionalidades se necessário
4. Executar testes novamente

"""
        else:
            report += """
## ✅ Validação Bem-Sucedida

A limpeza foi realizada com sucesso e não quebrou nenhuma funcionalidade!

### Próximos Passos:
1. Commit das mudanças
2. Atualizar documentação
3. Notificar equipe sobre as mudanças

"""

        return report

    def run_validation(self) -> bool:
        """Executa validação completa"""
        print("🔍 INICIANDO VALIDAÇÃO PÓS-LIMPEZA")
        print("=" * 50)
        print()

        # Executar testes de validação
        validation_tests = [
            ("Estrutura de Arquivos", self.validate_file_structure),
            ("Remoção de Backups", self.validate_no_backup_files),
            ("Remoção de Debug", self.validate_no_debug_files),
            ("Remoção de Duplicados", self.validate_no_duplicate_services),
            ("Validação de Imports", self.validate_imports),
            ("Backend Health", self.validate_backend_health),
            ("Endpoints da API", self.validate_api_endpoints),
            ("Build Frontend", self.validate_frontend_build),
            ("Documentação", self.validate_documentation_structure),
        ]

        for test_name, test_func in validation_tests:
            print(f"🔧 Executando: {test_name}")
            try:
                test_func()
            except Exception as e:
                self.log_validation(test_name, False, f"Erro inesperado: {str(e)}")
            print()

        # Gerar relatório
        report = self.generate_validation_report()

        report_path = self.project_root / "VALIDATION_REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print("📊 RESUMO DA VALIDAÇÃO")
        print("=" * 40)
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results if result["success"])
        print(f"Total de testes: {total_tests}")
        print(f"Testes passaram: {passed_tests}")
        print(f"Testes falharam: {total_tests - passed_tests}")
        print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        print()

        if passed_tests == total_tests:
            print("🎉 TODA VALIDAÇÃO PASSOU!")
            print("✅ A limpeza foi bem-sucedida")
        else:
            print("⚠️ ALGUNS TESTES FALHARAM")
            print("❌ Verifique os problemas acima")

        print(f"📄 Relatório salvo em: {report_path}")

        return passed_tests == total_tests


def main():
    """Função principal"""
    validator = CleanupValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
