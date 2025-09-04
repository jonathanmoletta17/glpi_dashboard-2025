#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação - GLPI Metrics Collector

Este script valida se todas as implementações estão funcionando corretamente
e se a documentação está alinhada com o código real.

Autor: Sistema de Engenharia
Data: 2025-01-22
Versão: 1.0
"""

import json
import os
import subprocess
import sys

import requests


def validate_environment() -> bool:
    """Valida se as variáveis de ambiente estão configuradas"""
    print("🔍 Validando configuração do ambiente...")

    required_vars = ["GLPI_BASE_URL", "GLPI_APP_TOKEN", "GLPI_USER_TOKEN"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Variáveis não configuradas: {', '.join(missing_vars)}")
        return False

    print("✅ Variáveis de ambiente configuradas")
    return True


def validate_connectivity() -> bool:
    """Valida conectividade com GLPI"""
    print("🔍 Validando conectividade com GLPI...")

    base_url = os.getenv("GLPI_BASE_URL")
    app_token = os.getenv("GLPI_APP_TOKEN")
    user_token = os.getenv("GLPI_USER_TOKEN")

    try:
        headers = {
            "Content-Type": "application/json",
            "App-Token": app_token,
            "Authorization": f"user_token {user_token}",
        }

        response = requests.get(f"{base_url}/apirest.php/initSession", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "session_token" in data:
                print("✅ Conectividade com GLPI OK")
                return True
            else:
                print("❌ Session token não recebido")
                return False
        else:
            print(f"❌ Erro de conectividade: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False


def validate_technician_mapping() -> bool:
    """Valida mapeamento de técnicos"""
    print("🔍 Validando mapeamento de técnicos...")

    # IDs dos 19 técnicos válidos
    technician_ids = [
        "696",
        "32",
        "141",
        "60",
        "69",
        "1032",
        "252",
        "721",
        "926",
        "1291",
        "185",
        "1331",
        "1404",
        "1088",
        "1263",
        "10",
        "53",
        "250",
        "1471",
    ]

    base_url = os.getenv("GLPI_BASE_URL")
    app_token = os.getenv("GLPI_APP_TOKEN")
    user_token = os.getenv("GLPI_USER_TOKEN")

    # Autenticar
    headers = {
        "Content-Type": "application/json",
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
    }

    response = requests.get(f"{base_url}/apirest.php/initSession", headers=headers)
    if response.status_code != 200:
        print("❌ Falha na autenticação para validação")
        return False

    session_token = response.json().get("session_token")
    headers["Session-Token"] = session_token

    # Mapeamento esperado de níveis
    expected_mapping = {
        "1404": "N1",  # Gabriel Andrade da Conceicao
        "1263": "N1",  # Nicolas Fernando Muniz Nunez
        "1032": "N2",  # Jonathan Nascimento Moletta
        "252": "N2",  # Alessandro Carbonera Vieira
        "721": "N2",  # Thales Vinicius Paz Leite
        "696": "N3",  # Anderson da Silva Morim de Oliveira
        "32": "N3",  # Silvio Godinho Valim
        "141": "N3",  # Jorge Antonio Vicente Júnior
        "1291": "N4",  # Gabriel Silva Machado
        "1088": "N4",  # Luciano de Araujo Silva
    }

    valid_technicians = 0
    correct_mappings = 0

    for tech_id in technician_ids:
        try:
            # Buscar detalhes do usuário
            user_response = requests.get(f"{base_url}/apirest.php/User/{tech_id}", headers=headers)

            if user_response.status_code == 200:
                user_data = user_response.json()
                is_active = str(user_data.get("is_active", "0")).strip()
                is_deleted = str(user_data.get("is_deleted", "0")).strip()

                if str(is_active) == "1" and str(is_deleted) == "0":
                    valid_technicians += 1

                    # Verificar mapeamento de nível se esperado
                    if tech_id in expected_mapping:
                        firstname = user_data.get("firstname", "").lower()
                        realname = user_data.get("realname", "").lower()
                        full_name = f"{firstname} {realname}".strip()

                        # Mapeamento hardcoded do script
                        n1_names = ["gabriel andrade da conceicao", "nicolas fernando muniz nunez"]
                        n2_names = [
                            "alessandro carbonera vieira",
                            "jonathan nascimento moletta",
                            "thales vinicius paz leite",
                            "leonardo trojan repiso riela",
                            "edson joel dos santos silva",
                            "luciano marcelino da silva",
                        ]
                        n3_names = [
                            "anderson da silva morim de oliveira",
                            "silvio godinho valim",
                            "jorge antonio vicente júnior",
                            "pablo hebling guimaraes",
                            "miguelangelo ferreira",
                        ]
                        n4_names = [
                            "gabriel silva machado",
                            "luciano de araujo silva",
                            "wagner mengue",
                            "paulo césar pedó nunes",
                            "alexandre rovinski almoarqueg",
                        ]

                        detected_level = "N1"  # Padrão
                        if full_name in n4_names:
                            detected_level = "N4"
                        elif full_name in n3_names:
                            detected_level = "N3"
                        elif full_name in n2_names:
                            detected_level = "N2"
                        elif full_name in n1_names:
                            detected_level = "N1"

                        expected_level = expected_mapping[tech_id]
                        if detected_level == expected_level:
                            correct_mappings += 1
                            print(f"✅ {tech_id}: {full_name} -> {detected_level}")
                        else:
                            print(
                                f"❌ {tech_id}: {full_name} -> "
                                f"Esperado {expected_level}, Detectado {detected_level}"
                            )

        except Exception as e:
            print(f"❌ Erro ao validar técnico {tech_id}: {e}")

    print(f"✅ Técnicos válidos: {valid_technicians}/19")
    print(f"✅ Mapeamentos corretos: {correct_mappings}/{len(expected_mapping)}")

    return valid_technicians == 19 and correct_mappings == len(expected_mapping)


def validate_script_execution() -> bool:
    """Valida execução do script principal"""
    print("🔍 Validando execução do script principal...")

    try:
        # Importar e executar o script
        import sys

        # Executar o script (versão simplificada sem emojis)
        result = subprocess.run(
            [sys.executable, "glpi_metrics_collector_simple.py"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            print("✅ Script executado com sucesso")

            # Verificar se arquivo JSON foi gerado
            json_files = [
                f for f in os.listdir(".") if f.startswith("glpi_metrics_") and f.endswith(".json")
            ]
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                print(f"✅ Arquivo JSON gerado: {latest_file}")

                # Validar estrutura do JSON
                with open(latest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                required_keys = ["timestamp", "success", "metrics"]
                if all(key in data for key in required_keys):
                    print("✅ Estrutura JSON válida")

                    # Verificar métricas
                    metrics = data.get("metrics", {})
                    if "ranking_tecnicos" in metrics and "status_por_nivel" in metrics:
                        print("✅ Métricas coletadas corretamente")
                        return True
                    else:
                        print("❌ Métricas incompletas")
                        return False
                else:
                    print("❌ Estrutura JSON inválida")
                    return False
            else:
                print("❌ Arquivo JSON não gerado")
                return False
        else:
            print(f"❌ Script falhou: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Script timeout (mais de 60 segundos)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar script: {e}")
        return False


def validate_documentation() -> bool:
    """Valida se a documentação está presente"""
    print("🔍 Validando documentação...")

    required_docs = [
        "GLPI_API_DOCUMENTATION.md",
        "GLPI_API_EXAMPLES.md",
        "GLPI_SETUP_GUIDE.md",
        "GLPI_QUICK_REFERENCE.md",
        "README_GLPI_DOCUMENTATION.md",
    ]

    missing_docs = []
    for doc in required_docs:
        if not os.path.exists(doc):
            missing_docs.append(doc)

    if missing_docs:
        print(f"❌ Documentação faltando: {', '.join(missing_docs)}")
        return False

    print("✅ Toda documentação presente")
    return True


def main():
    """Função principal de validação"""
    print("🚀 INICIANDO VALIDAÇÃO COMPLETA DO GLPI METRICS COLLECTOR")
    print("=" * 60)

    validations = [
        ("Configuração do Ambiente", validate_environment),
        ("Conectividade com GLPI", validate_connectivity),
        ("Mapeamento de Técnicos", validate_technician_mapping),
        ("Execução do Script", validate_script_execution),
        ("Documentação", validate_documentation),
    ]

    results = []

    for name, validation_func in validations:
        print(f"\n📋 {name}")
        print("-" * 40)
        try:
            result = validation_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            results.append((name, False))

    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 60)

    passed = 0
    total = len(results)

    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
        if result:
            passed += 1

    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} validações passaram")

    if passed == total:
        print("🎉 TODAS AS VALIDAÇÕES PASSARAM! Sistema está funcionando corretamente.")
        return True
    else:
        print("⚠️ ALGUMAS VALIDAÇÕES FALHARAM. Verifique os erros acima.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
