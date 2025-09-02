#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mapear e analisar todos os grupos configurados no GLPI

Este script:
1. Lista todos os grupos do GLPI
2. Analisa hierarquia e configurações
3. Identifica grupos técnicos e administrativos
4. Mapeia usuários por grupo
5. Gera relatório detalhado

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

from services.glpi_service import GLPIService

def analyze_group_configuration(group):
    """
    Analisa a configuração de um grupo
    """
    config = {
        'is_technical': bool(group.get('is_tech', 0)),
        'is_manager': bool(group.get('is_manager', 0)),
        'is_assign': bool(group.get('is_assign', 0)),
        'is_notify': bool(group.get('is_notify', 0)),
        'is_itemgroup': bool(group.get('is_itemgroup', 0)),
        'is_usergroup': bool(group.get('is_usergroup', 0)),
        'is_task': bool(group.get('is_task', 0)),
        'is_request': bool(group.get('is_request', 0)),
        'is_incident': bool(group.get('is_incident', 0)),
        'is_problem': bool(group.get('is_problem', 0)),
        'is_change': bool(group.get('is_change', 0))
    }
    
    return config

def classify_group_type(group, config):
    """
    Classifica o tipo de grupo baseado na configuração
    """
    group_types = []
    
    # Grupo técnico
    if config['is_technical']:
        group_types.append('technical')
    
    # Grupo de gestão
    if config['is_manager']:
        group_types.append('management')
    
    # Grupo de atribuição
    if config['is_assign']:
        group_types.append('assignment')
    
    # Grupo de notificação
    if config['is_notify']:
        group_types.append('notification')
    
    # Grupo de itens
    if config['is_itemgroup']:
        group_types.append('item_group')
    
    # Grupo de usuários
    if config['is_usergroup']:
        group_types.append('user_group')
    
    # Grupos por tipo de ticket
    if config['is_request']:
        group_types.append('request_handler')
    
    if config['is_incident']:
        group_types.append('incident_handler')
    
    if config['is_problem']:
        group_types.append('problem_handler')
    
    if config['is_change']:
        group_types.append('change_handler')
    
    if config['is_task']:
        group_types.append('task_handler')
    
    # Se não tem nenhuma configuração específica
    if not group_types:
        group_types.append('basic')
    
    return group_types

def get_group_hierarchy(groups):
    """
    Constrói a hierarquia de grupos
    """
    hierarchy = {}
    root_groups = []
    
    # Criar mapa de grupos por ID
    groups_map = {group['id']: group for group in groups}
    
    # Identificar grupos raiz e construir hierarquia
    for group in groups:
        group_id = group['id']
        parent_id = group.get('groups_id')
        
        if not parent_id or parent_id == 0:
            # Grupo raiz
            root_groups.append(group_id)
            hierarchy[group_id] = {
                'group': group,
                'children': [],
                'level': 0
            }
        else:
            # Grupo filho
            if parent_id not in hierarchy:
                hierarchy[parent_id] = {
                    'group': groups_map.get(parent_id, {}),
                    'children': [],
                    'level': 0
                }
            
            hierarchy[group_id] = {
                'group': group,
                'children': [],
                'level': hierarchy[parent_id]['level'] + 1
            }
            
            hierarchy[parent_id]['children'].append(group_id)
    
    return hierarchy, root_groups

def get_group_users(glpi_service, group_id):
    """
    Busca usuários de um grupo
    """
    try:
        users_response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/User",
            params={
                "criteria[0][field]": "13",  # groups_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": group_id,
                "range": "0-999"
            }
        )
        
        if users_response and users_response.ok:
            users_data = users_response.json()
            if 'data' in users_data:
                return users_data['data']
        
        return []
    except Exception as e:
        print(f"   ⚠️ Erro ao buscar usuários do grupo {group_id}: {e}")
        return []

def get_group_tickets_stats(glpi_service, group_id):
    """
    Busca estatísticas de tickets do grupo
    """
    try:
        # Tickets atribuídos ao grupo
        tickets_response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/Ticket",
            params={
                "criteria[0][field]": "8",  # groups_id_assign
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": group_id,
                "range": "0-999"
            }
        )
        
        assigned_tickets = 0
        if tickets_response and tickets_response.ok:
            tickets_data = tickets_response.json()
            if 'data' in tickets_data:
                assigned_tickets = len(tickets_data['data'])
        
        # Tickets solicitados pelo grupo
        requester_response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/search/Ticket",
            params={
                "criteria[0][field]": "71",  # groups_id
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": group_id,
                "range": "0-999"
            }
        )
        
        requested_tickets = 0
        if requester_response and requester_response.ok:
            requester_data = requester_response.json()
            if 'data' in requester_data:
                requested_tickets = len(requester_data['data'])
        
        return {
            'assigned_tickets': assigned_tickets,
            'requested_tickets': requested_tickets,
            'total_tickets': assigned_tickets + requested_tickets
        }
    
    except Exception as e:
        print(f"   ⚠️ Erro ao buscar estatísticas de tickets do grupo {group_id}: {e}")
        return {
            'assigned_tickets': 0,
            'requested_tickets': 0,
            'total_tickets': 0
        }

def main():
    print("👥 Mapeamento de Grupos GLPI")
    print("=" * 50)
    
    try:
        # Configurar serviço GLPI
        glpi_service = GLPIService()
        
        print("\n1️⃣ Buscando todos os grupos...")
        
        # Buscar todos os grupos
        groups_response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/Group",
            params={"range": "0-999", "expand_dropdowns": "true"}
        )
        
        if not groups_response or not groups_response.ok:
            print("❌ Erro ao buscar grupos")
            return
        
        groups_data = groups_response.json()
        groups = groups_data if isinstance(groups_data, list) else []
        
        print(f"   📊 Total de grupos encontrados: {len(groups)}")
        
        # Construir hierarquia
        print("\n2️⃣ Analisando hierarquia de grupos...")
        
        hierarchy, root_groups = get_group_hierarchy(groups)
        max_level = max([h['level'] for h in hierarchy.values()]) if hierarchy else 0
        
        print(f"   🌳 Níveis hierárquicos: {max_level + 1}")
        print(f"   🌱 Grupos raiz: {len(root_groups)}")
        
        # Analisar cada grupo
        print("\n3️⃣ Analisando configuração dos grupos...")
        
        detailed_analysis = []
        group_types_summary = {}
        technical_groups = []
        management_groups = []
        
        for group in groups:
            group_id = group.get('id')
            group_name = group.get('name')
            
            print(f"   👥 Analisando grupo: {group_name} (ID: {group_id})")
            
            # Analisar configuração
            config = analyze_group_configuration(group)
            group_types = classify_group_type(group, config)
            
            # Contar tipos de grupo
            for gtype in group_types:
                group_types_summary[gtype] = group_types_summary.get(gtype, 0) + 1
            
            # Buscar usuários do grupo
            users = get_group_users(glpi_service, group_id)
            users_count = len(users)
            
            # Buscar estatísticas de tickets
            ticket_stats = get_group_tickets_stats(glpi_service, group_id)
            
            # Análise detalhada do grupo
            group_analysis = {
                'id': group_id,
                'name': group_name,
                'comment': group.get('comment'),
                'parent_id': group.get('groups_id'),
                'entity_id': group.get('entities_id'),
                'level': hierarchy.get(group_id, {}).get('level', 0),
                'users_count': users_count,
                'group_types': group_types,
                'configuration': config,
                'ticket_stats': ticket_stats,
                'users': [
                    {
                        'id': user.get('2'),  # ID do usuário
                        'name': user.get('1'),  # Nome do usuário
                        'login': user.get('1')  # Login (mesmo campo)
                    } for user in users[:10]  # Primeiros 10 usuários
                ],
                'dates': {
                    'creation': group.get('date_creation'),
                    'modification': group.get('date_mod')
                },
                'visibility': {
                    'is_recursive': bool(group.get('is_recursive', 0)),
                    'visibility': group.get('visibility')
                }
            }
            
            detailed_analysis.append(group_analysis)
            
            # Coletar grupos técnicos e de gestão
            if 'technical' in group_types:
                technical_groups.append(group_analysis)
            
            if 'management' in group_types:
                management_groups.append(group_analysis)
        
        # Identificar grupos técnicos
        print("\n4️⃣ Identificando grupos técnicos...")
        
        print(f"   🔧 Grupos técnicos encontrados: {len(technical_groups)}")
        for tg in technical_groups:
            print(f"      • {tg['name']} (ID: {tg['id']}) - {tg['users_count']} usuários")
        
        # Identificar grupos de gestão
        print("\n5️⃣ Identificando grupos de gestão...")
        
        print(f"   👔 Grupos de gestão encontrados: {len(management_groups)}")
        for mg in management_groups:
            print(f"      • {mg['name']} (ID: {mg['id']}) - {mg['users_count']} usuários")
        
        # Análise de uso
        print("\n6️⃣ Analisando uso dos grupos...")
        
        total_users = sum(g['users_count'] for g in detailed_analysis)
        empty_groups = [g for g in detailed_analysis if g['users_count'] == 0]
        most_used_groups = sorted(detailed_analysis, key=lambda x: x['users_count'], reverse=True)[:5]
        
        print(f"   👥 Total de usuários em grupos: {total_users}")
        print(f"   🚫 Grupos vazios: {len(empty_groups)}")
        print(f"   📈 Grupos mais utilizados:")
        for i, g in enumerate(most_used_groups, 1):
            print(f"      {i}. {g['name']}: {g['users_count']} usuários")
        
        # Análise de tickets
        print("\n7️⃣ Analisando atividade de tickets...")
        
        total_assigned = sum(g['ticket_stats']['assigned_tickets'] for g in detailed_analysis)
        total_requested = sum(g['ticket_stats']['requested_tickets'] for g in detailed_analysis)
        
        active_groups = [g for g in detailed_analysis if g['ticket_stats']['total_tickets'] > 0]
        most_active_groups = sorted(detailed_analysis, key=lambda x: x['ticket_stats']['total_tickets'], reverse=True)[:5]
        
        print(f"   🎫 Total de tickets atribuídos: {total_assigned}")
        print(f"   📝 Total de tickets solicitados: {total_requested}")
        print(f"   🔄 Grupos ativos: {len(active_groups)}")
        print(f"   📊 Grupos mais ativos:")
        for i, g in enumerate(most_active_groups, 1):
            if g['ticket_stats']['total_tickets'] > 0:
                print(f"      {i}. {g['name']}: {g['ticket_stats']['total_tickets']} tickets")
        
        # Preparar relatório final
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_groups': len(groups),
            'total_users_in_groups': total_users,
            'hierarchy_levels': max_level + 1,
            'root_groups_count': len(root_groups),
            'group_types_summary': group_types_summary,
            'technical_groups_count': len(technical_groups),
            'management_groups_count': len(management_groups),
            'empty_groups_count': len(empty_groups),
            'active_groups_count': len(active_groups),
            'ticket_stats': {
                'total_assigned': total_assigned,
                'total_requested': total_requested,
                'total_tickets': total_assigned + total_requested
            },
            'hierarchy': {
                'root_groups': [
                    {
                        'id': gid,
                        'name': hierarchy[gid]['group'].get('name'),
                        'children_count': len(hierarchy[gid]['children'])
                    } for gid in root_groups
                ],
                'max_depth': max_level
            },
            'technical_groups': [
                {
                    'id': g['id'],
                    'name': g['name'],
                    'users_count': g['users_count'],
                    'assigned_tickets': g['ticket_stats']['assigned_tickets']
                } for g in technical_groups
            ],
            'management_groups': [
                {
                    'id': g['id'],
                    'name': g['name'],
                    'users_count': g['users_count']
                } for g in management_groups
            ],
            'most_used_groups': [
                {
                    'id': g['id'],
                    'name': g['name'],
                    'users_count': g['users_count'],
                    'types': g['group_types']
                } for g in most_used_groups
            ],
            'most_active_groups': [
                {
                    'id': g['id'],
                    'name': g['name'],
                    'total_tickets': g['ticket_stats']['total_tickets'],
                    'assigned_tickets': g['ticket_stats']['assigned_tickets'],
                    'requested_tickets': g['ticket_stats']['requested_tickets']
                } for g in most_active_groups if g['ticket_stats']['total_tickets'] > 0
            ],
            'empty_groups': [
                {
                    'id': g['id'],
                    'name': g['name'],
                    'types': g['group_types']
                } for g in empty_groups
            ],
            'detailed_groups': detailed_analysis,
            'issues_identified': [],
            'recommendations': []
        }
        
        # Identificar problemas
        print("\n8️⃣ Identificando problemas...")
        
        # Grupos vazios
        if empty_groups:
            report['issues_identified'].append({
                'type': 'empty_groups',
                'description': f'{len(empty_groups)} grupos não possuem usuários',
                'groups': [g['name'] for g in empty_groups]
            })
        
        # Grupos sem documentação
        groups_without_comments = [g for g in detailed_analysis if not g['comment']]
        if groups_without_comments:
            report['issues_identified'].append({
                'type': 'missing_documentation',
                'description': f'{len(groups_without_comments)} grupos sem documentação (comentários)',
                'groups': [g['name'] for g in groups_without_comments[:10]]  # Primeiros 10
            })
        
        # Grupos técnicos sem usuários
        empty_tech_groups = [g for g in technical_groups if g['users_count'] == 0]
        if empty_tech_groups:
            report['issues_identified'].append({
                'type': 'empty_technical_groups',
                'description': f'{len(empty_tech_groups)} grupos técnicos sem usuários',
                'groups': [g['name'] for g in empty_tech_groups]
            })
        
        # Grupos com muitos usuários
        large_groups = [g for g in detailed_analysis if g['users_count'] > 100]
        if large_groups:
            report['issues_identified'].append({
                'type': 'oversized_groups',
                'description': f'{len(large_groups)} grupos com mais de 100 usuários',
                'groups': [f"{g['name']} ({g['users_count']} usuários)" for g in large_groups]
            })
        
        # Gerar recomendações
        print("\n9️⃣ Gerando recomendações...")
        
        if empty_groups:
            report['recommendations'].append(
                "Revisar grupos vazios e considerar remoção ou redistribuição"
            )
        
        if groups_without_comments:
            report['recommendations'].append(
                "Adicionar documentação (comentários) para todos os grupos"
            )
        
        if empty_tech_groups:
            report['recommendations'].append(
                "Atribuir técnicos aos grupos técnicos ou revisar configuração"
            )
        
        if large_groups:
            report['recommendations'].append(
                "Considerar subdivisão de grupos com muitos usuários"
            )
        
        report['recommendations'].extend([
            "Implementar revisão periódica da estrutura de grupos",
            "Criar processo de aprovação para criação de novos grupos",
            "Estabelecer nomenclatura padronizada para grupos",
            "Implementar auditoria de permissões de grupos",
            "Criar matriz de responsabilidades por grupo técnico"
        ])
        
        # Salvar relatório
        analysis_dir = backend_dir / 'glpi_data' / 'analysis'
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = analysis_dir / f'groups_mapping_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {report_file}")
        
        # Resumo final
        print("\n📋 RESUMO DO MAPEAMENTO DE GRUPOS")
        print("=" * 40)
        print(f"📊 Total de grupos: {len(groups)}")
        print(f"👥 Total de usuários em grupos: {total_users}")
        print(f"🌳 Níveis hierárquicos: {max_level + 1}")
        print(f"🔧 Grupos técnicos: {len(technical_groups)}")
        print(f"👔 Grupos de gestão: {len(management_groups)}")
        print(f"🚫 Grupos vazios: {len(empty_groups)}")
        print(f"🔄 Grupos ativos: {len(active_groups)}")
        print(f"🎫 Total de tickets: {total_assigned + total_requested}")
        print(f"⚠️  Problemas identificados: {len(report['issues_identified'])}")
        print(f"💡 Recomendações: {len(report['recommendations'])}")
        
        if report['issues_identified']:
            print("\n⚠️  PROBLEMAS ENCONTRADOS:")
            for issue in report['issues_identified']:
                print(f"   • {issue['description']}")
        
        print("\n✅ Mapeamento de grupos concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o mapeamento: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()