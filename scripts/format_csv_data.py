#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para formatar e limpar dados CSV extraídos do GLPI
Remove campos desnecessários e organiza dados em formato mais legível
."""

import logging
import os
from datetime import datetime

import pandas as pd

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("format_csv.log"), logging.StreamHandler()],
)


def format_tickets_csv():
    """Formata o arquivo tickets.csv com campos essenciais."""
    try:
        logging.info("Formatando tickets.csv...")
        df = pd.read_csv("data/tickets.csv")

        # Campos essenciais para tickets
        essential_fields = [
            "id",
            "name",
            "content",
            "status",
            "priority",
            "urgency",
            "date",
            "date_creation",
            "date_mod",
            "closedate",
            "solvedate",
            "entities_id",
            "itilcategories_id",
            "requesttypes_id",
            "users_id_recipient",
            "users_id_lastupdater",
            "type",
            "actiontime",
            "solve_delay_stat",
            "close_delay_stat",
        ]

        # Filtrar apenas campos que existem no DataFrame
        available_fields = [field for field in essential_fields if field in df.columns]
        df_formatted = df[available_fields].copy()

        # Limpar e formatar dados
        if "content" in df_formatted.columns:
            df_formatted["content"] = (
                df_formatted["content"].astype(str).str.replace("\n", " ").str.replace("\r", " ")
            )
            df_formatted["content"] = df_formatted["content"].str.strip()

        if "name" in df_formatted.columns:
            df_formatted["name"] = df_formatted["name"].astype(str).str.strip()

        # Mapear status
        status_map = {
            1: "Novo",
            2: "Em andamento (atribuído)",
            3: "Em andamento (planejado)",
            4: "Pendente",
            5: "Solucionado",
            6: "Fechado",
        }

        if "status" in df_formatted.columns:
            df_formatted["status_desc"] = df_formatted["status"].map(status_map)

        # Mapear prioridade
        priority_map = {
            1: "Muito baixa",
            2: "Baixa",
            3: "Média",
            4: "Alta",
            5: "Muito alta",
            6: "Crítica",
        }

        if "priority" in df_formatted.columns:
            df_formatted["priority_desc"] = df_formatted["priority"].map(priority_map)

        # Salvar arquivo formatado
        df_formatted.to_csv("data/tickets_formatted.csv", index=False, encoding="utf-8")
        logging.info(f"Tickets formatados salvos: {len(df_formatted)} registros")

        return len(df_formatted)

    except Exception as e:
        logging.error(f"Erro ao formatar tickets: {e}")
        return 0


def format_users_csv():
    """Formata o arquivo usuarios.csv com campos essenciais."""
    try:
        logging.info("Formatando usuarios.csv...")
        df = pd.read_csv("data/usuarios.csv")

        # Campos essenciais para usuários
        essential_fields = [
            "id",
            "firstname",
            "realname",
            "name",
            "comment",
            "entities_id",
            "is_active",
            "is_deleted",
            "groups_id",
            "date_creation",
            "date_mod",
            "last_login",
            "phone",
            "phone2",
            "mobile",
            "registration_number",
            "user_dn",
            "usercategories_id",
            "authtype",
        ]

        # Filtrar apenas campos que existem no DataFrame
        available_fields = [field for field in essential_fields if field in df.columns]
        df_formatted = df[available_fields].copy()

        # Limpar e formatar dados
        text_fields = ["firstname", "realname", "name", "comment"]
        for field in text_fields:
            if field in df_formatted.columns:
                df_formatted[field] = df_formatted[field].astype(str).str.strip()

        # Criar nome completo
        if "firstname" in df_formatted.columns and "realname" in df_formatted.columns:
            df_formatted["nome_completo"] = (
                df_formatted["firstname"].astype(str) + " " + df_formatted["realname"].astype(str)
            ).str.strip()

        # Mapear status ativo
        if "is_active" in df_formatted.columns:
            df_formatted["status_ativo"] = df_formatted["is_active"].map({1: "Ativo", 0: "Inativo"})

        # Salvar arquivo formatado
        df_formatted.to_csv("data/usuarios_formatted.csv", index=False, encoding="utf-8")
        logging.info(f"Usuários formatados salvos: {len(df_formatted)} registros")

        return len(df_formatted)

    except Exception as e:
        logging.error(f"Erro ao formatar usuários: {e}")
        return 0


def format_technicians_csv():
    """Formata o arquivo tecnicos.csv com campos essenciais."""
    try:
        logging.info("Formatando tecnicos.csv...")
        df = pd.read_csv("data/tecnicos.csv")

        # Campos essenciais para técnicos
        essential_fields = [
            "id",
            "firstname",
            "realname",
            "name",
            "comment",
            "entities_id",
            "groups_id",
            "is_active",
            "date_creation",
            "date_mod",
            "last_login",
            "phone",
            "phone2",
            "mobile",
            "registration_number",
        ]

        # Filtrar apenas campos que existem no DataFrame
        available_fields = [field for field in essential_fields if field in df.columns]
        df_formatted = df[available_fields].copy()

        # Limpar e formatar dados
        text_fields = ["firstname", "realname", "name", "comment"]
        for field in text_fields:
            if field in df_formatted.columns:
                df_formatted[field] = df_formatted[field].astype(str).str.strip()

        # Criar nome completo
        if "firstname" in df_formatted.columns and "realname" in df_formatted.columns:
            df_formatted["nome_completo"] = (
                df_formatted["firstname"].astype(str) + " " + df_formatted["realname"].astype(str)
            ).str.strip()

        # Extrair grupo principal do campo comment
        if "comment" in df_formatted.columns:
            df_formatted["grupo_principal"] = df_formatted["comment"].str.extract(r"(CC-[^,\s]+)")

        # Salvar arquivo formatado
        df_formatted.to_csv("data/tecnicos_formatted.csv", index=False, encoding="utf-8")
        logging.info(f"Técnicos formatados salvos: {len(df_formatted)} registros")

        return len(df_formatted)

    except Exception as e:
        logging.error(f"Erro ao formatar técnicos: {e}")
        return 0


def format_requesters_csv():
    """Formata o arquivo solicitantes.csv com campos essenciais."""
    try:
        logging.info("Formatando solicitantes.csv...")
        df = pd.read_csv("data/solicitantes.csv")

        # Campos essenciais para solicitantes
        essential_fields = [
            "id",
            "firstname",
            "realname",
            "name",
            "comment",
            "entities_id",
            "is_active",
            "date_creation",
            "date_mod",
            "phone",
            "phone2",
            "mobile",
            "registration_number",
        ]

        # Filtrar apenas campos que existem no DataFrame
        available_fields = [field for field in essential_fields if field in df.columns]
        df_formatted = df[available_fields].copy()

        # Limpar e formatar dados
        text_fields = ["firstname", "realname", "name", "comment"]
        for field in text_fields:
            if field in df_formatted.columns:
                df_formatted[field] = df_formatted[field].astype(str).str.strip()

        # Criar nome completo
        if "firstname" in df_formatted.columns and "realname" in df_formatted.columns:
            df_formatted["nome_completo"] = (
                df_formatted["firstname"].astype(str) + " " + df_formatted["realname"].astype(str)
            ).str.strip()

        # Extrair setor do campo comment
        if "comment" in df_formatted.columns:
            df_formatted["setor"] = df_formatted["comment"].str.extract(r"(CC-[^,\s]+)")

        # Salvar arquivo formatado
        df_formatted.to_csv("data/solicitantes_formatted.csv", index=False, encoding="utf-8")
        logging.info(f"Solicitantes formatados salvos: {len(df_formatted)} registros")

        return len(df_formatted)

    except Exception as e:
        logging.error(f"Erro ao formatar solicitantes: {e}")
        return 0


def main():
    """Função principal para formatar todos os arquivos CSV."""
    start_time = datetime.now()
    logging.info("Iniciando formatação de arquivos CSV...")

    # Verificar se os arquivos existem
    required_files = [
        "data/tickets.csv",
        "data/usuarios.csv",
        "data/tecnicos.csv",
        "data/solicitantes.csv",
    ]
    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        logging.error(f"Arquivos não encontrados: {missing_files}")
        return

    # Formatar cada arquivo
    results = {
        "tickets": format_tickets_csv(),
        "usuarios": format_users_csv(),
        "tecnicos": format_technicians_csv(),
        "solicitantes": format_requesters_csv(),
    }

    end_time = datetime.now()
    duration = end_time - start_time

    # Relatório final
    print("\n" + "=" * 60)
    print("FORMATAÇÃO DE DADOS CSV CONCLUÍDA")
    print("=" * 60)
    print(f"Início: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Fim: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duração: {duration}")
    print("\nARQUIVOS FORMATADOS:")
    for file_type, count in results.items():
        if count > 0:
            print(f"  • {file_type}_formatted.csv: {count} registros")
    print("\n✅ Formatação concluída com sucesso!")
    print("📁 Verifique os arquivos *_formatted.csv gerados.")
    print("🤖 Dados organizados e limpos para análise.")
    print("=" * 60)


if __name__ == "__main__":
    main()
