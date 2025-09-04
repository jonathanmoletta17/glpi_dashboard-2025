#!/usr/bin/env python3
"""
Script para validação de dependências circulares.
Este script verifica se há dependências circulares no código Python.
"""

import ast
import os
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set


class DependencyAnalyzer:
    """Analisador de dependências para detectar ciclos."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.modules: Set[str] = set()

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extrai imports de um arquivo Python."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

            return imports
        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")
            return set()

    def build_dependency_graph(self):
        """Constrói o grafo de dependências."""
        python_files = list(self.root_path.rglob("*.py"))

        for file_path in python_files:
            # Converte o caminho do arquivo para nome do módulo
            relative_path = file_path.relative_to(self.root_path)
            module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")

            # Ignora arquivos de teste e __pycache__
            if "test" in module_name.lower() or "__pycache__" in str(file_path):
                continue

            self.modules.add(module_name)
            imports = self.extract_imports(file_path)

            # Filtra apenas imports locais (dentro do projeto)
            local_imports = set()
            for imp in imports:
                # Verifica se é um import local
                for mod in self.modules:
                    if mod.startswith(imp) or imp in mod:
                        local_imports.add(imp)

            self.dependencies[module_name] = local_imports

    def detect_cycles(self) -> List[List[str]]:
        """Detecta ciclos no grafo de dependências usando DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Encontrou um ciclo
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependencies.get(node, set()):
                if neighbor in self.modules:  # Apenas módulos locais
                    dfs(neighbor, path.copy())

            rec_stack.remove(node)
            return False

        for module in self.modules:
            if module not in visited:
                dfs(module, [])

        return cycles


def main():
    """Função principal."""
    # Determina o diretório raiz do projeto
    current_dir = Path.cwd()

    # Procura pelo diretório que contém código Python
    root_dirs = ["api", "services", "utils", "schemas", "database"]
    project_root = None

    for root_dir in root_dirs:
        if (current_dir / root_dir).exists():
            project_root = current_dir
            break

    if not project_root:
        print("❌ Não foi possível encontrar o diretório raiz do projeto")
        return 1

    print(f"🔍 Analisando dependências em: {project_root}")

    analyzer = DependencyAnalyzer(str(project_root))
    analyzer.build_dependency_graph()

    print(f"📦 Encontrados {len(analyzer.modules)} módulos")

    cycles = analyzer.detect_cycles()

    if cycles:
        print(f"❌ Encontradas {len(cycles)} dependências circulares:")
        for i, cycle in enumerate(cycles, 1):
            print(f"  {i}. {' -> '.join(cycle)}")
        return 1
    else:
        print("✅ Nenhuma dependência circular encontrada")
        return 0


if __name__ == "__main__":
    sys.exit(main())
