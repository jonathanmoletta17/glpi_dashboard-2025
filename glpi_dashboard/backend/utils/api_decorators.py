"""Decoradores para padronização de APIs.

Este módulo fornece decoradores para automatizar a conversão de nomenclatura
e padronizar respostas entre backend e frontend.
"""

import functools
import logging
from typing import Any, Callable, Dict, Union
from flask import jsonify, request
from .naming_converter import NamingConverter

logger = logging.getLogger(__name__)


def standardize_response(func: Callable) -> Callable:
    """Decorador que padroniza respostas da API convertendo snake_case para camelCase.
    
    Este decorador automaticamente converte todas as chaves de resposta
    do formato snake_case (usado no backend) para camelCase (esperado pelo frontend).
    
    Args:
        func: Função da API a ser decorada
        
    Returns:
        Função decorada que retorna resposta padronizada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Executa a função original
            result = func(*args, **kwargs)
            
            # Se o resultado já é uma Response do Flask, retorna como está
            if hasattr(result, 'status_code'):
                return result
            
            # Se é uma tupla (data, status_code), processa apenas os dados
            if isinstance(result, tuple) and len(result) == 2:
                data, status_code = result
                if isinstance(data, dict):
                    normalized_data = NamingConverter.normalize_api_response(data)
                    return jsonify(normalized_data), status_code
                return result
            
            # Se é um dicionário, converte as chaves
            if isinstance(result, dict):
                normalized_result = NamingConverter.normalize_api_response(result)
                return jsonify(normalized_result)
            
            # Para outros tipos, retorna como está
            return result
            
        except Exception as e:
            logger.error(f"Erro ao padronizar resposta da API: {e}")
            # Em caso de erro, retorna o resultado original
            return func(*args, **kwargs)
    
    return wrapper


def normalize_request_params(func: Callable) -> Callable:
    """Decorador que normaliza parâmetros de requisição convertendo camelCase para snake_case.
    
    Este decorador automaticamente converte parâmetros vindos do frontend
    (camelCase) para o formato esperado pelo backend (snake_case).
    
    Args:
        func: Função da API a ser decorada
        
    Returns:
        Função decorada que recebe parâmetros normalizados
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Normaliza parâmetros de query string
            normalized_args = {}
            for key, value in request.args.items():
                snake_key = NamingConverter.camel_to_snake(key)
                normalized_args[snake_key] = value
            
            # Atualiza request.args temporariamente
            original_args = request.args
            request.args = type(original_args)(normalized_args)
            
            # Normaliza parâmetros JSON se existirem
            if request.is_json and request.json:
                normalized_json = NamingConverter.normalize_api_params(request.json)
                # Adiciona os parâmetros normalizados aos kwargs
                kwargs.update(normalized_json)
            
            result = func(*args, **kwargs)
            
            # Restaura request.args original
            request.args = original_args
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao normalizar parâmetros da requisição: {e}")
            # Em caso de erro, executa função original
            return func(*args, **kwargs)
    
    return wrapper


def api_standardization(func: Callable) -> Callable:
    """Decorador combinado que normaliza parâmetros de entrada e padroniza resposta.
    
    Este decorador combina normalize_request_params e standardize_response
    para fornecer padronização completa da API.
    
    Args:
        func: Função da API a ser decorada
        
    Returns:
        Função decorada com padronização completa
    """
    return standardize_response(normalize_request_params(func))


def legacy_compatibility(func: Callable) -> Callable:
    """Decorador para manter compatibilidade com estruturas de dados legadas.
    
    Este decorador garante que respostas incluam tanto a estrutura nova
    quanto a legada para transição gradual.
    
    Args:
        func: Função da API a ser decorada
        
    Returns:
        Função decorada com compatibilidade legada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # Se o resultado é um dicionário com dados de métricas
            if isinstance(result, dict) and 'niveis' in result:
                # Adiciona estrutura legada 'by_level' se não existir
                if 'by_level' not in result:
                    result['by_level'] = result['niveis']
                
                # Adiciona estrutura 'general' se necessário (para compatibilidade)
                if 'general' not in result and 'geral' in result:
                    result['general'] = result['geral']
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao aplicar compatibilidade legada: {e}")
            return func(*args, **kwargs)
    
    return wrapper


def validate_required_params(*required_params: str):
    """Decorador para validar parâmetros obrigatórios.
    
    Args:
        *required_params: Lista de parâmetros obrigatórios
        
    Returns:
        Decorador que valida os parâmetros
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            missing_params = []
            
            # Verifica parâmetros de query string
            for param in required_params:
                # Verifica tanto snake_case quanto camelCase
                snake_param = NamingConverter.camel_to_snake(param)
                camel_param = NamingConverter.snake_to_camel(param)
                
                if (param not in request.args and 
                    snake_param not in request.args and 
                    camel_param not in request.args):
                    missing_params.append(param)
            
            if missing_params:
                return jsonify({
                    'error': 'Parâmetros obrigatórios ausentes',
                    'missing_params': missing_params
                }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Aliases para facilitar importação
standardize_api = api_standardization
normalize_params = normalize_request_params
standardize_resp = standardize_response