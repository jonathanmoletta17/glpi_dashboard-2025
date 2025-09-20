#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para detectar dependências circulares no projeto
."""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set


class DependencyAnalyzer:
    """Analisador de dependências do projeto."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.dependencies: Dict[str, Set[str]] = {}

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extrai imports de um arquivo Python."""
        imports = set()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")

        return imports

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Constrói grafo de dependências do projeto."""

        # Encontrar todos os arquivos Python
        python_files = list(self.project_root.rglob("*.py"))

        # Extrair módulos do projeto
        project_modules = set()
        for py_file in python_files:
            relative_path = py_file.relative_to(self.project_root)
            module_path = str(relative_path.with_suffix(""))
            module_name = module_path.replace(os.sep, ".")

            # Filtrar apenas módulos do projeto (não bibliotecas externas)
            if not any(part.startswith(".") for part in module_name.split(".")):
                project_modules.add(module_name.split(".")[0])

        # Analisar dependências
        for py_file in python_files:
            relative_path = py_file.relative_to(self.project_root)
            module_path = str(relative_path.with_suffix(""))
            module_name = module_path.replace(os.sep, ".")

            imports = self.extract_imports(py_file)

            # Filtrar apenas imports de módulos do projeto
            project_imports = imports.intersection(project_modules)

            if project_imports:
                self.dependencies[module_name] = project_imports

        return self.dependencies

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detecta dependências circulares usando DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Encontrou ciclo
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            # Visitar dependências
            for dependency in self.dependencies.get(node, set()):
                if dfs(dependency, path + [node]):
                    return True

            rec_stack.remove(node)
            return False

        # Executar DFS para todos os nós
        for module in self.dependencies:
            if module not in visited:
                dfs(module, [])

        return cycles


def find_project_root() -> Path:
    """Encontra a raiz do projeto."""
    current = Path.cwd()

    # Procurar por indicadores de raiz do projeto
    indicators = [".git", "pyproject.toml", "setup.py", "requirements.txt"]

    while current != current.parent:
        if any((current / indicator).exists() for indicator in indicators):
            return current
        current = current.parent

    return Path.cwd()


def main() -> int:
    """Função principal."""
    try:
        project_root = find_project_root()

        if not project_root:
            print("X Nao foi possivel encontrar o diretorio raiz do projeto")
            return 1

        print(f"Analisando dependencias em: {project_root}")

        analyzer = DependencyAnalyzer(str(project_root))
        dependencies = analyzer.build_dependency_graph()

        if not dependencies:
            print("Nenhuma dependencia interna encontrada")
            return 0

        cycles = analyzer.detect_circular_dependencies()

        if cycles:
            print("X Dependencias circulares detectadas:")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Ciclo {i}: {' -> '.join(cycle)}")
            return 1
        else:
            print("V Nenhuma dependencia circular detectada")
            return 0

    except Exception as e:
        print(f"Erro durante analise: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
