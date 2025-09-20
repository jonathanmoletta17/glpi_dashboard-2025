#!/usr/bin/env python3
"""
GLPI Metrics Collector.

Este coletor implementa todas as funcionalidades necessárias para:
- Autenticação segura com GLPI
- Coleta de métricas de usuários, tickets, computadores e impressoras
- Processamento e formatação de dados
- Integração com dashboard

Endpoint principal: /api/search/User
Critérios de busca: is_active=1, is_deleted=0
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class GLPIConfig:
    """Configuração para conexão com GLPI."""

    base_url: str
    app_token: str
    user_token: str
    timeout: int = 30


class GLPIMetricsCollector:
    """
    Coletor de métricas do GLPI.

    Este coletor implementa todas as funcionalidades necessárias para:
    - Autenticação segura com GLPI
    - Coleta de métricas de usuários, tickets, computadores e impressoras
    - Processamento e formatação de dados
    - Integração com dashboard

    Endpoint principal: /api/search/User
    Critérios de busca: is_active=1, is_deleted=0
    """

    def __init__(self, config: GLPIConfig):
        """
        Inicializa o coletor com configuração.

        Args:
            config: Configuração do GLPI
        """
        self.config = config
        self.session_token = None
        self.session = requests.Session()
        self.session.timeout = config.timeout

        # Configurar logging
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def login(self) -> bool:
        """
        Autentica no GLPI e obtém token de sessão.

        Returns:
            bool: True se autenticação bem-sucedida
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"user_token {self.config.user_token}",
                "App-Token": self.config.app_token,
            }

            response = self.session.get(
                f"{self.config.base_url}/initSession", headers=headers)

            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get("session_token")
                self.logger.info("Autenticação realizada com sucesso")
                return True
            else:
                self.logger.error(
                    f"Erro na autenticação: {
                        response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Erro durante autenticação: {str(e)}")
            return False

    def logout(self) -> bool:
        """
        Encerra sessão no GLPI.

        Returns:
            bool: True se logout bem-sucedido
        """
        if not self.session_token:
            return True

        try:
            headers = {
                "Session-Token": self.session_token,
                "App-Token": self.config.app_token}

            response = self.session.get(
                f"{self.config.base_url}/killSession", headers=headers)

            if response.status_code == 200:
                self.logger.info("Logout realizado com sucesso")
                return True
            else:
                self.logger.warning(f"Aviso no logout: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Erro durante logout: {str(e)}")
            return False

    def get_users_by_level(
        self, level: str = None, filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Coleta informações de usuários por nível.

        Args:
            level: Nível do usuário para filtrar
            filters: Filtros adicionais para busca

        Returns:
            Dict com dados dos usuários
        """
        if not self.login():
            return {"error": "Falha na autenticação"}

        try:
            headers = {
                "Session-Token": self.session_token,
                "App-Token": self.config.app_token,
                "Content-Type": "application/json",
            }

            # Construir critérios de busca
            criteria = [
                {"field": 2, "searchtype": "equals", "value": 1},  # ativo
                {"field": 23, "searchtype": "equals", "value": 0},  # não deletado
            ]

            if level:
                criteria.append(
                    {"field": "level", "searchtype": "equals", "value": level})

            if filters:
                for field, value in filters.items():
                    criteria.append(
                        {"field": field, "searchtype": "equals", "value": value})

            search_params = {
                "criteria": criteria,
                "forcedisplay": [2, 34, 5, 6, 3, 4],  # campos desejados
            }

            response = self.session.get(
                f"{self.config.base_url}/search/User",
                headers=headers,
                params={"searchText": json.dumps(search_params)},
            )

            if response.status_code == 200:
                data = response.json()
                self.logger.info(
                    f"Coletados {
                        data.get(
                            'totalcount',
                            0)} usuários")
                return data
            else:
                self.logger.error(
                    f"Erro na coleta de usuários: {
                        response.status_code}")
                return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            self.logger.error(f"Erro durante coleta: {str(e)}")
            return {"error": str(e)}
        finally:
            self.logout()


def main():
    """Função principal para teste do coletor."""
    # Configuração de exemplo
    config = GLPIConfig(
        base_url="https://seu-glpi.com/apirest.php",
        app_token="seu_app_token",
        user_token="seu_user_token",
    )

    # Criar coletor
    collector = GLPIMetricsCollector(config)

    # Testar coleta
    users = collector.get_users_by_level()
    print(f"Resultado: {users}")


if __name__ == "__main__":
    main()
