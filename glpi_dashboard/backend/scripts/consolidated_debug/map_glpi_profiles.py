#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mapear e analisar todos os perfis de usuário configurados no GLPI

Este script:
1. Lista todos os perfis do GLPI
2. Analisa permissões e configurações
3. Identifica perfis técnicos e administrativos
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

from services.glpi_service import GLPIService

def analyze_profile_permissions(profile):
    """
    Analisa as permissões de um perfil
    """
    # Permissões relacionadas a tickets
    ticket_permissions = {
        'ticket': profile.get('ticket', 0),
        'followup': profile.get('followup', 0),
        'task': profile.get('task', 0),
        'ticketvalidation': profile.get('ticketvalidation', 0),
        'planning': profile.get('planning', 0)
    }
    
    # Permissões administrativas
    admin_permissions = {
        'user': profile.get('user', 0),
        'group': profile.get('group', 0),
        'entity': profile.get('entity', 0),
        'config': profile.get('config', 0),
        'dropdown': profile.get('dropdown', 0)
    }
    
    # Permissões de inventário
    inventory_permissions = {
        'computer': profile.get('computer', 0),
        'monitor': profile.get('monitor', 0),
        'networking': profile.get('networking', 0),
        'phone': profile.get('phone', 0),
        'printer': profile.get('printer', 0)
    }
    
    # Outras permissões importantes
    other_permissions = {
        'knowbase': profile.get('knowbase', 0),
        'document': profile.get('document', 0),
        'backup': profile.get('backup', 0),
        'logs': profile.get('logs', 0)
    }
    
    return {
        'ticket_permissions': ticket_permissions,
        'admin_permissions': admin_permissions,
        'inventory_permissions': inventory_permissions,
        'other_permissions': other_permissions
    }

def classify_profile_type(profile, permissions):
    """
    Classifica o tipo de perfil baseado nas permissões
    """
    profile_types = []
    
    # Verificar se é perfil técnico
    ticket_perms = permissions['ticket_permissions']
    if (ticket_perms['ticket'] > 0 and 
        ticket_perms['followup'] > 0 and 
        ticket_perms['task'] > 0):
        profile_types.append('technical')
    
    # Verificar se é perfil administrativo
    admin_perms = permissions['admin_permissions']
    if (admin_perms['user'] > 0 or 
        admin_perms['config'] > 0 or 
        admin_perms['dropdown'] > 0):
        profile_types.append('administrative')
    
    # Verificar se é perfil de inventário
    inv_perms = permissions['inventory_permissions']
    if (inv_perms['computer'] > 0 and 
        inv_perms['networking'] > 0):
        profile_types.append('inventory')
    
    # Verificar se é perfil de helpdesk
    if profile.get('interface') == 'helpdesk':
        profile_types.append('helpdesk')
    elif profile.get('interface') == 'central':
        profile_types.append('central')
    
    # Verificar se é perfil de leitura apenas
    all_perms = []
    for perm_group in permissions.values():
        if isinstance(perm_group, dict):
            all_perms.extend(perm_group.values())
    
    if all(perm in [0, 1] for perm in all_perms if isinstance(perm, int)):
        profile_types.append('read_only')
    
    return profile_types if profile_types else ['unknown']

def get_permission_level_description(level):
    """
    Retorna descrição do nível de permissão
    """
    descriptions = {
        0: 'Sem acesso',
        1: 'Leitura',
        2: 'Escrita',
        3: 'Leitura/Escrita',
        4: 'Criação',
        7: 'Leitura/Escrita/Criação',
        15: 'Leitura/Escrita/Criação/Exclusão',
        31: 'Acesso total (com purge)',
        127: 'Acesso completo',
        1023: 'Administrador',
        1024: 'Validação',
        2048: 'Aprovação',
        4096: 'Supervisão'
    }
    
    return descriptions.get(level, f'Nível {level}')

def main():
    print("👤 Mapeamento de Perfis GLPI")
    print("=" * 50)
    
    try:
        # Configurar serviço GLPI
        glpi_service = GLPIService()
        
        print("\n1️⃣ Buscando todos os perfis...")
        
        # Buscar todos os perfis
        profiles_response = glpi_service._make_authenticated_request(
            "GET", f"{glpi_service.glpi_url}/Profile",
            params={"range": "0-999", "expand_dropdowns": "true"}
        )
        
        if not profiles_response or not profiles_response.ok:
            print("❌ Erro ao buscar perfis")
            return
        
        profiles_data = profiles_response.json()
        profiles = profiles_data if isinstance(profiles_data, list) else []
        
        print(f"   📊 Total de perfis encontrados: {len(profiles)}")
        
        # Analisar cada perfil
        print("\n2️⃣ Analisando permissões por perfil...")
        
        detailed_analysis = []
        profile_types_summary = {}
        
        for profile in profiles:
            profile_id = profile.get('id')
            profile_name = profile.get('name')
            
            print(f"   👤 Analisando perfil: {profile_name} (ID: {profile_id})")
            
            # Analisar permissões
            permissions = analyze_profile_permissions(profile)
            profile_types = classify_profile_type(profile, permissions)
            
            # Contar tipos de perfil
            for ptype in profile_types:
                profile_types_summary[ptype] = profile_types_summary.get(ptype, 0) + 1
            
            # Buscar usuários com este perfil
            users_response = glpi_service._make_authenticated_request(
                "GET", f"{glpi_service.glpi_url}/search/User",
                params={
                    "criteria[0][field]": "20",  # profiles_id
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": profile_id,
                    "range": "0-999"
                }
            )
            
            users_count = 0
            if users_response and users_response.ok:
                users_data = users_response.json()
                if 'data' in users_data:
                    users_count = len(users_data['data'])
            
            # Análise detalhada do perfil
            profile_analysis = {
                'id': profile_id,
                'name': profile_name,
                'interface': profile.get('interface'),
                'is_default': profile.get('is_default'),
                'comment': profile.get('comment'),
                'users_count': users_count,
                'profile_types': profile_types,
                'permissions': permissions,
                'key_permissions': {
                    'ticket_management': get_permission_level_description(profile.get('ticket', 0)),
                    'user_management': get_permission_level_description(profile.get('user', 0)),
                    'config_access': get_permission_level_description(profile.get('config', 0)),
                    'inventory_access': get_permission_level_description(profile.get('computer', 0)),
                    'knowbase_access': get_permission_level_description(profile.get('knowbase', 0))
                },
                'dates': {
                    'creation': profile.get('date_creation'),
                    'modification': profile.get('date_mod')
                },
                'templates': {
                    'ticket_template': profile.get('tickettemplates_id'),
                    'change_template': profile.get('changetemplates_id'),
                    'problem_template': profile.get('problemtemplates_id')
                }
            }
            
            detailed_analysis.append(profile_analysis)
        
        # Identificar perfis técnicos
        print("\n3️⃣ Identificando perfis técnicos...")
        
        technical_profiles = [
            p for p in detailed_analysis 
            if 'technical' in p['profile_types']
        ]
        
        print(f"   🔧 Perfis técnicos encontrados: {len(technical_profiles)}")
        for tp in technical_profiles:
            print(f"      • {tp['name']} (ID: {tp['id']}) - {tp['users_count']} usuários")
        
        # Identificar perfis administrativos
        print("\n4️⃣ Identificando perfis administrativos...")
        
        admin_profiles = [
            p for p in detailed_analysis 
            if 'administrative' in p['profile_types']
        ]
        
        print(f"   ⚙️ Perfis administrativos encontrados: {len(admin_profiles)}")
        for ap in admin_profiles:
            print(f"      • {ap['name']} (ID: {ap['id']}) - {ap['users_count']} usuários")
        
        # Análise de uso
        print("\n5️⃣ Analisando uso dos perfis...")
        
        total_users = sum(p['users_count'] for p in detailed_analysis)
        unused_profiles = [p for p in detailed_analysis if p['users_count'] == 0]
        most_used_profiles = sorted(detailed_analysis, key=lambda x: x['users_count'], reverse=True)[:5]
        
        print(f"   👥 Total de usuários: {total_users}")
        print(f"   🚫 Perfis não utilizados: {len(unused_profiles)}")
        print(f"   📈 Perfis mais utilizados:")
        for i, p in enumerate(most_used_profiles, 1):
            print(f"      {i}. {p['name']}: {p['users_count']} usuários")
        
        # Preparar relatório final
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_profiles': len(profiles),
            'total_users': total_users,
            'profile_types_summary': profile_types_summary,
            'technical_profiles_count': len(technical_profiles),
            'admin_profiles_count': len(admin_profiles),
            'unused_profiles_count': len(unused_profiles),
            'profiles_summary': {
                'by_interface': {
                    'central': len([p for p in detailed_analysis if p['interface'] == 'central']),
                    'helpdesk': len([p for p in detailed_analysis if p['interface'] == 'helpdesk']),
                    'other': len([p for p in detailed_analysis if p['interface'] not in ['central', 'helpdesk']])
                },
                'default_profiles': len([p for p in detailed_analysis if p['is_default']]),
                'with_templates': len([p for p in detailed_analysis if p['templates']['ticket_template']])
            },
            'technical_profiles': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'users_count': p['users_count'],
                    'interface': p['interface']
                } for p in technical_profiles
            ],
            'admin_profiles': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'users_count': p['users_count'],
                    'interface': p['interface']
                } for p in admin_profiles
            ],
            'most_used_profiles': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'users_count': p['users_count'],
                    'types': p['profile_types']
                } for p in most_used_profiles
            ],
            'unused_profiles': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'interface': p['interface']
                } for p in unused_profiles
            ],
            'detailed_profiles': detailed_analysis,
            'issues_identified': [],
            'recommendations': []
        }
        
        # Identificar problemas
        print("\n6️⃣ Identificando problemas...")
        
        # Perfis não utilizados
        if unused_profiles:
            report['issues_identified'].append({
                'type': 'unused_profiles',
                'description': f'{len(unused_profiles)} perfis não estão sendo utilizados',
                'profiles': [p['name'] for p in unused_profiles]
            })
        
        # Perfis sem comentários
        profiles_without_comments = [p for p in detailed_analysis if not p['comment']]
        if profiles_without_comments:
            report['issues_identified'].append({
                'type': 'missing_documentation',
                'description': f'{len(profiles_without_comments)} perfis sem documentação (comentários)',
                'profiles': [p['name'] for p in profiles_without_comments[:10]]  # Primeiros 10
            })
        
        # Perfis com muitos usuários (possível problema de granularidade)
        high_usage_profiles = [p for p in detailed_analysis if p['users_count'] > 50]
        if high_usage_profiles:
            report['issues_identified'].append({
                'type': 'high_usage_profiles',
                'description': f'{len(high_usage_profiles)} perfis com mais de 50 usuários (revisar granularidade)',
                'profiles': [f"{p['name']} ({p['users_count']} usuários)" for p in high_usage_profiles]
            })
        
        # Gerar recomendações
        print("\n7️⃣ Gerando recomendações...")
        
        if unused_profiles:
            report['recommendations'].append(
                "Revisar e remover perfis não utilizados ou documentar seu propósito"
            )
        
        if profiles_without_comments:
            report['recommendations'].append(
                "Adicionar documentação (comentários) para todos os perfis"
            )
        
        if high_usage_profiles:
            report['recommendations'].append(
                "Considerar criar perfis mais específicos para reduzir concentração de usuários"
            )
        
        report['recommendations'].extend([
            "Implementar revisão periódica de permissões de perfis",
            "Criar matriz de responsabilidades por perfil",
            "Estabelecer processo de aprovação para criação de novos perfis",
            "Implementar auditoria de uso de perfis"
        ])
        
        # Salvar relatório
        analysis_dir = backend_dir / 'glpi_data' / 'analysis'
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = analysis_dir / f'profiles_mapping_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {report_file}")
        
        # Resumo final
        print("\n📋 RESUMO DO MAPEAMENTO DE PERFIS")
        print("=" * 40)
        print(f"📊 Total de perfis: {len(profiles)}")
        print(f"👥 Total de usuários: {total_users}")
        print(f"🔧 Perfis técnicos: {len(technical_profiles)}")
        print(f"⚙️ Perfis administrativos: {len(admin_profiles)}")
        print(f"🚫 Perfis não utilizados: {len(unused_profiles)}")
        print(f"⚠️  Problemas identificados: {len(report['issues_identified'])}")
        print(f"💡 Recomendações: {len(report['recommendations'])}")
        
        if report['issues_identified']:
            print("\n⚠️  PROBLEMAS ENCONTRADOS:")
            for issue in report['issues_identified']:
                print(f"   • {issue['description']}")
        
        print("\n✅ Mapeamento de perfis concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o mapeamento: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()