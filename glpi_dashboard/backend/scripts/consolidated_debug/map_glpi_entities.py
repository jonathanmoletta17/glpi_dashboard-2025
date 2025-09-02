#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mapear e analisar todas as entidades configuradas no GLPI

Este script:
1. Lista todas as entidades do GLPI
2. Analisa a estrutura hierárquica
3. Identifica configurações e permissões
4. Gera relatório detalhado

Autor: Sistema de Análise GLPI
Data: 2025-08-28
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent.parent / 'glpi_dashboard' / 'backend'
sys.path.insert(0, str(backend_dir))

from config.settings import get_config
from services.glpi_service import GLPIService

def analyze_entity_hierarchy(entities):
    """
    Analisa a hierarquia das entidades
    """
    hierarchy = {}
    root_entities = []
    
    # Organizar por nível hierárquico
    for entity in entities:
        level = entity.get('level', 0)
        if level not in hierarchy:
            hierarchy[level] = []
        hierarchy[level].append(entity)
        
        # Identificar entidades raiz
        if entity.get('entities_id') == 0 or level == 0:
            root_entities.append(entity)
    
    return hierarchy, root_entities

def analyze_entity_permissions(entity):
    """
    Analisa as permissões e configurações de uma entidade
    """
    permissions = {
        'can_assign_tickets': entity.get('is_assign', 0),
        'can_be_requester': entity.get('is_requester', 0),
        'can_watch_tickets': entity.get('is_watcher', 0),
        'recursive': entity.get('is_recursive', 0)
    }
    
    return permissions

def main():
    print("🏢 Mapeamento de Entidades GLPI")
    print("=" * 50)
    
    try:
        # Configurar serviço GLPI
        glpi_service = GLPIService()
        
        print("\n1️⃣ Buscando todas as entidades...")
        
        # Buscar todas as entidades
        entities_response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/Entity",
            params={"range": "0-9999", "expand_dropdowns": "true"}
        )
        
        if not entities_response or not entities_response.ok:
            print("❌ Erro ao buscar entidades")
            return
        
        entities_data = entities_response.json()
        entities = entities_data if isinstance(entities_data, list) else []
        
        print(f"   📊 Total de entidades encontradas: {len(entities)}")
        
        # Analisar hierarquia
        print("\n2️⃣ Analisando hierarquia...")
        hierarchy, root_entities = analyze_entity_hierarchy(entities)
        
        print(f"   🌳 Níveis hierárquicos: {len(hierarchy)}")
        print(f"   🌱 Entidades raiz: {len(root_entities)}")
        
        # Análise detalhada por entidade
        print("\n3️⃣ Analisando configurações por entidade...")
        
        detailed_analysis = []
        
        for entity in entities:
            entity_analysis = {
                'id': entity.get('id'),
                'name': entity.get('name'),
                'completename': entity.get('completename'),
                'level': entity.get('level'),
                'parent_id': entity.get('entities_id'),
                'is_recursive': entity.get('is_recursive'),
                'comment': entity.get('comment'),
                'contact_info': {
                    'address': entity.get('address'),
                    'phone': entity.get('phonenumber'),
                    'email': entity.get('email'),
                    'website': entity.get('website')
                },
                'notification_config': {
                    'admin_email': entity.get('admin_email'),
                    'from_email': entity.get('from_email'),
                    'noreply_email': entity.get('noreply_email'),
                    'replyto_email': entity.get('replyto_email')
                },
                'dates': {
                    'creation': entity.get('date_creation'),
                    'modification': entity.get('date_mod')
                }
            }
            
            detailed_analysis.append(entity_analysis)
            
            print(f"   📁 {entity.get('name')} (ID: {entity.get('id')}) - Nível {entity.get('level')}")
        
        # Buscar usuários por entidade
        print("\n4️⃣ Mapeando usuários por entidade...")
        
        entity_users = {}
        for entity in entities[:5]:  # Limitar para as primeiras 5 entidades para teste
            entity_id = entity.get('id')
            
            users_response = glpi_service._make_authenticated_request(
                "GET", f"{glpi_service.glpi_url}/search/User",
                params={
                    "criteria[0][field]": "80",  # entities_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": entity_id,
                    "range": "0-999"
                }
            )
            
            users_count = 0
            if users_response and users_response.ok:
                users_data = users_response.json()
                if 'data' in users_data:
                    users_count = len(users_data['data'])
            
            entity_users[entity_id] = users_count
            print(f"   👥 Entidade {entity.get('name')}: {users_count} usuários")
        
        # Preparar relatório final
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_entities': len(entities),
            'hierarchy_levels': len(hierarchy),
            'root_entities_count': len(root_entities),
            'entities_summary': {
                'by_level': {str(level): len(ents) for level, ents in hierarchy.items()},
                'with_recursive': len([e for e in entities if e.get('is_recursive')]),
                'with_email_config': len([e for e in entities if e.get('admin_email')]),
                'with_contact_info': len([e for e in entities if e.get('address') or e.get('phonenumber')])
            },
            'root_entities': [
                {
                    'id': e.get('id'),
                    'name': e.get('name'),
                    'completename': e.get('completename')
                } for e in root_entities
            ],
            'hierarchy': {str(level): [
                {
                    'id': e.get('id'),
                    'name': e.get('name'),
                    'parent_id': e.get('entities_id'),
                    'is_recursive': e.get('is_recursive')
                } for e in ents
            ] for level, ents in hierarchy.items()},
            'detailed_entities': detailed_analysis,
            'entity_users_sample': entity_users,
            'issues_identified': [],
            'recommendations': []
        }
        
        # Identificar problemas
        print("\n5️⃣ Identificando problemas...")
        
        # Entidades sem configuração de email
        entities_without_email = [e for e in entities if not e.get('admin_email')]
        if entities_without_email:
            report['issues_identified'].append({
                'type': 'missing_email_config',
                'description': f'{len(entities_without_email)} entidades sem configuração de email',
                'entities': [e.get('name') for e in entities_without_email[:10]]  # Primeiras 10
            })
        
        # Entidades órfãs (parent_id inválido)
        valid_entity_ids = {e.get('id') for e in entities}
        orphan_entities = [
            e for e in entities 
            if e.get('entities_id') not in valid_entity_ids and e.get('entities_id') != 0
        ]
        if orphan_entities:
            report['issues_identified'].append({
                'type': 'orphan_entities',
                'description': f'{len(orphan_entities)} entidades órfãs encontradas',
                'entities': [e.get('name') for e in orphan_entities]
            })
        
        # Gerar recomendações
        print("\n6️⃣ Gerando recomendações...")
        
        if entities_without_email:
            report['recommendations'].append(
                "Configurar emails administrativos para todas as entidades"
            )
        
        if orphan_entities:
            report['recommendations'].append(
                "Corrigir referências de entidades órfãs"
            )
        
        report['recommendations'].extend([
            "Revisar estrutura hierárquica para otimização",
            "Implementar nomenclatura padronizada para entidades",
            "Configurar informações de contato completas"
        ])
        
        # Salvar relatório
        analysis_dir = backend_dir / 'glpi_data' / 'analysis'
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = analysis_dir / f'entities_mapping_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {report_file}")
        
        # Resumo final
        print("\n📋 RESUMO DO MAPEAMENTO")
        print("=" * 30)
        print(f"📊 Total de entidades: {len(entities)}")
        print(f"🌳 Níveis hierárquicos: {len(hierarchy)}")
        print(f"🌱 Entidades raiz: {len(root_entities)}")
        print(f"⚠️  Problemas identificados: {len(report['issues_identified'])}")
        print(f"💡 Recomendações: {len(report['recommendations'])}")
        
        if report['issues_identified']:
            print("\n⚠️  PROBLEMAS ENCONTRADOS:")
            for issue in report['issues_identified']:
                print(f"   • {issue['description']}")
        
        print("\n✅ Mapeamento de entidades concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o mapeamento: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()