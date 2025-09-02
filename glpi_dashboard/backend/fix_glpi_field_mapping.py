#!/usr/bin/env python3
"""
Script para corrigir o mapeamento de campos GLPI

Problema identificado:
- A API GLPI retorna dados com chaves numéricas ("2", "12", "8", etc.)
- O GLPIDataValidator espera campos com nomes ("id", "status", etc.)
- Precisa criar um mapeamento entre números e nomes de campos

Solução:
1. Criar mapeamento de campos GLPI
2. Implementar função de conversão de dados
3. Atualizar GLPIDataValidator para usar o mapeamento
4. Testar a correção
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Adicionar o caminho do backend ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from services.glpi_service import GLPIService
from utils.glpi_data_validator import GLPIDataValidator

# Mapeamento de campos GLPI baseado na documentação e testes
GLPI_FIELD_MAPPING = {
    # Campos básicos de ticket
    "2": "id",                    # ID do ticket
    "1": "name",                  # Nome/Título do ticket
    "12": "status",               # Status do ticket
    "80": "entities_id",          # ID da entidade
    "15": "date",                 # Data de criação
    "19": "date_mod",             # Data de modificação
    "16": "closedate",            # Data de fechamento
    "17": "solvedate",            # Data de resolução
    "5": "users_id_assign",       # Técnico atribuído
    "8": "groups_id_assign",      # Grupo atribuído (hierarquia)
    "71": "groups_id",            # Grupo (campo alternativo)
    "7": "itilcategories_id",     # Categoria do ticket
    "3": "priority",              # Prioridade
    "21": "content",              # Conteúdo/Descrição
    "6": "users_id_recipient",    # Usuário solicitante
    "22": "users_id_lastupdater", # Último usuário que atualizou
    "18": "due_date",             # Data de vencimento
    "14": "type",                 # Tipo do ticket
    "13": "urgency",              # Urgência
    "11": "impact",               # Impacto
    "37": "locations_id",         # Localização
    "131": "validation",          # Validação
    "142": "global_validation",   # Validação global
}

# Mapeamento reverso (nome -> número)
GLPI_REVERSE_FIELD_MAPPING = {v: k for k, v in GLPI_FIELD_MAPPING.items()}

def convert_glpi_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte dados da API GLPI de formato numérico para nomes de campos.
    
    Args:
        raw_data: Dados brutos da API GLPI com chaves numéricas
        
    Returns:
        Dict com chaves convertidas para nomes de campos
    """
    converted_data = {}
    
    for field_num, value in raw_data.items():
        # Converter chave numérica para nome do campo
        field_name = GLPI_FIELD_MAPPING.get(str(field_num), f"field_{field_num}")
        converted_data[field_name] = value
    
    return converted_data

def convert_glpi_tickets_list(raw_tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converte uma lista de tickets da API GLPI.
    
    Args:
        raw_tickets: Lista de tickets com chaves numéricas
        
    Returns:
        Lista de tickets com chaves convertidas
    """
    return [convert_glpi_data(ticket) for ticket in raw_tickets]

def test_field_mapping():
    """
    Testa o mapeamento de campos com dados reais da API GLPI.
    """
    print("🧪 TESTANDO MAPEAMENTO DE CAMPOS GLPI")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "field_mapping_test": {},
        "validation_test": {},
        "sample_conversions": []
    }
    
    try:
        # Inicializar serviços
        glpi_service = GLPIService()
        validator = GLPIDataValidator()
        
        if not glpi_service._ensure_authenticated():
            print("❌ Falha na autenticação com GLPI")
            return
        
        # Buscar alguns tickets para teste
        print("\n🔍 BUSCANDO TICKETS PARA TESTE")
        print("-" * 30)
        
        params = {
            "range": "0-4",  # Apenas 5 tickets para teste
            "forcedisplay[0]": "2",   # ID
            "forcedisplay[1]": "1",   # Nome
            "forcedisplay[2]": "12",  # Status
            "forcedisplay[3]": "15",  # Data criação
            "forcedisplay[4]": "5",   # Técnico
            "forcedisplay[5]": "8",   # Grupo hierarquia
        }
        
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/search/Ticket",
            params=params
        )
        
        if response and response.ok:
            data = response.json()
            
            if 'data' in data and data['data']:
                raw_tickets = data['data']
                print(f"✅ {len(raw_tickets)} tickets encontrados")
                
                # Testar conversão de cada ticket
                print("\n🔄 CONVERTENDO TICKETS")
                print("-" * 25)
                
                converted_tickets = []
                validation_results = []
                
                for i, raw_ticket in enumerate(raw_tickets):
                    print(f"\n   Ticket {i+1}:")
                    print(f"     Raw: {raw_ticket}")
                    
                    # Converter dados
                    converted_ticket = convert_glpi_data(raw_ticket)
                    print(f"     Convertido: {converted_ticket}")
                    
                    converted_tickets.append(converted_ticket)
                    
                    # Testar validação
                    is_valid = validator.validate_ticket_data(converted_ticket)
                    print(f"     Validação: {'✅ Válido' if is_valid else '❌ Inválido'}")
                    
                    validation_results.append({
                        "ticket_index": i,
                        "raw_data": raw_ticket,
                        "converted_data": converted_ticket,
                        "is_valid": is_valid
                    })
                    
                    # Salvar amostra para análise
                    if i < 3:  # Primeiros 3 tickets
                        results["sample_conversions"].append({
                            "raw": raw_ticket,
                            "converted": converted_ticket,
                            "valid": is_valid
                        })
                
                # Estatísticas de validação
                valid_count = sum(1 for r in validation_results if r["is_valid"])
                total_count = len(validation_results)
                
                print(f"\n📊 RESULTADOS DA VALIDAÇÃO")
                print("-" * 30)
                print(f"   Total de tickets: {total_count}")
                print(f"   Tickets válidos: {valid_count}")
                print(f"   Taxa de sucesso: {(valid_count/total_count)*100:.1f}%")
                
                results["validation_test"] = {
                    "total_tickets": total_count,
                    "valid_tickets": valid_count,
                    "success_rate": (valid_count/total_count)*100,
                    "detailed_results": validation_results
                }
                
                # Verificar campos mais comuns
                print(f"\n🔍 ANÁLISE DE CAMPOS")
                print("-" * 20)
                
                field_usage = {}
                for ticket in raw_tickets:
                    for field_num in ticket.keys():
                        field_name = GLPI_FIELD_MAPPING.get(str(field_num), f"unknown_{field_num}")
                        if field_name not in field_usage:
                            field_usage[field_name] = 0
                        field_usage[field_name] += 1
                
                print("   Campos encontrados:")
                for field_name, count in sorted(field_usage.items()):
                    print(f"     {field_name}: {count} tickets")
                
                results["field_mapping_test"] = {
                    "field_usage": field_usage,
                    "mapping_coverage": len([f for f in field_usage.keys() if not f.startswith("unknown_")]),
                    "unknown_fields": [f for f in field_usage.keys() if f.startswith("unknown_")]
                }
                
            else:
                print("❌ Nenhum ticket encontrado na resposta")
                results["validation_test"]["error"] = "No tickets found in response"
        
        else:
            print(f"❌ Erro na busca de tickets: {response.status_code if response else 'None'}")
            results["validation_test"]["error"] = f"API request failed: {response.status_code if response else 'None'}"
    
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        results["validation_test"]["error"] = str(e)
    
    # Salvar resultados
    output_file = f"glpi_field_mapping_test_{results['timestamp']}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    return results

def create_enhanced_validator():
    """
    Cria uma versão melhorada do GLPIDataValidator que suporta mapeamento de campos.
    """
    print("\n🔧 CRIANDO VALIDATOR MELHORADO")
    print("-" * 35)
    
    enhanced_validator_code = '''
# -*- coding: utf-8 -*-
"""
GLPI Data Validator Enhanced

Versão melhorada que suporta mapeamento de campos numéricos da API GLPI.

Autor: Sistema de Auditoria
Data: 30 de Agosto de 2025
Versão: 2.0
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re

# Mapeamento de campos GLPI
GLPI_FIELD_MAPPING = {
    "2": "id",
    "1": "name",
    "12": "status",
    "80": "entities_id",
    "15": "date",
    "19": "date_mod",
    "16": "closedate",
    "17": "solvedate",
    "5": "users_id_assign",
    "8": "groups_id_assign",
    "71": "groups_id",
    "7": "itilcategories_id",
    "3": "priority",
    "21": "content",
    "6": "users_id_recipient",
    "22": "users_id_lastupdater",
    "18": "due_date",
    "14": "type",
    "13": "urgency",
    "11": "impact",
    "37": "locations_id",
}

class GLPIDataValidatorEnhanced:
    """
    Validador melhorado para dados da API GLPI com suporte a mapeamento de campos.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.field_mapping = GLPI_FIELD_MAPPING
        
        # Padrões de validação
        self.email_pattern = re.compile(r\''^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\')
        self.name_pattern = re.compile(r\''^[a-zA-ZÀ-ÿ\\s\\-\\.]{2,100}$\')
    
    def convert_glpi_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte dados da API GLPI de formato numérico para nomes de campos.
        """
        converted_data = {}
        
        for field_num, value in raw_data.items():
            field_name = self.field_mapping.get(str(field_num), f"field_{field_num}")
            converted_data[field_name] = value
        
        return converted_data
    
    def validate_ticket_data(self, ticket: Dict[str, Any], auto_convert: bool = True) -> bool:
        """
        Valida dados de um ticket GLPI com suporte a conversão automática.
        
        Args:
            ticket: Dicionário com dados do ticket
            auto_convert: Se True, tenta converter campos numéricos automaticamente
            
        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            # Verificar se precisa converter campos numéricos
            if auto_convert and self._has_numeric_fields(ticket):
                ticket = self.convert_glpi_data(ticket)
            
            # Campos obrigatórios
            required_fields = [\'id\', \'status\']
            
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in ticket or ticket[field] is None:
                    self.logger.warning(f"Campo obrigatório \'{field}\' ausente ou nulo no ticket")
                    return False
            
            # Validar ID do ticket
            if not self._validate_id(ticket[\'id\']):
                self.logger.warning(f"ID de ticket inválido: {ticket.get(\'id\')}")
                return False
            
            # Validar status
            if not self._validate_status(ticket[\'status\']):
                self.logger.warning(f"Status de ticket inválido: {ticket.get(\'status\')}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar dados do ticket: {e}")
            return False
    
    def _has_numeric_fields(self, data: Dict[str, Any]) -> bool:
        """
        Verifica se os dados contêm campos numéricos (formato da API GLPI).
        """
        return any(key.isdigit() for key in data.keys())
    
    def _validate_id(self, value: Any) -> bool:
        """
        Valida se um valor é um ID válido.
        """
        try:
            return isinstance(value, (int, str)) and int(value) > 0
        except (ValueError, TypeError):
            return False
    
    def _validate_status(self, value: Any) -> bool:
        """
        Valida se um valor é um status válido.
        """
        try:
            status_int = int(value)
            return 1 <= status_int <= 6  # Status válidos do GLPI
        except (ValueError, TypeError):
            return False
'''
    
    # Salvar o validator melhorado
    enhanced_file = "utils/glpi_data_validator_enhanced.py"
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_validator_code)
    
    print(f"✅ Validator melhorado criado: {enhanced_file}")
    return enhanced_file

def main():
    """
    Função principal que executa todos os testes e correções.
    """
    print("🚀 CORREÇÃO DE MAPEAMENTO DE CAMPOS GLPI")
    print("=" * 45)
    
    # Teste 1: Testar mapeamento de campos
    test_results = test_field_mapping()
    
    # Teste 2: Criar validator melhorado
    enhanced_validator_file = create_enhanced_validator()
    
    # Resumo final
    print("\n🎯 RESUMO DA CORREÇÃO")
    print("-" * 25)
    
    if test_results.get("validation_test", {}).get("success_rate", 0) > 0:
        success_rate = test_results["validation_test"]["success_rate"]
        print(f"✅ Taxa de sucesso da validação: {success_rate:.1f}%")
    else:
        print("❌ Falha nos testes de validação")
    
    print(f"✅ Validator melhorado criado: {enhanced_validator_file}")
    print(f"✅ Mapeamento de {len(GLPI_FIELD_MAPPING)} campos implementado")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Atualizar GLPIMetricsAdapter para usar o novo validator")
    print("2. Implementar conversão automática nos métodos de busca")
    print("3. Testar integração completa")
    print("4. Atualizar documentação")

if __name__ == "__main__":
    main()