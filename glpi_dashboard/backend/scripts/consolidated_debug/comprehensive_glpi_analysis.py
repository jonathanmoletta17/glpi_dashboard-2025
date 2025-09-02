#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Abrangente do GLPI
Investiga João Pedro Dias e mapeia completamente a estrutura do GLPI

Autor: AI Assistant
Data: 2025-01-28
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Adicionar o diretório backend ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
backend_dir = os.path.join(project_dir, 'glpi_dashboard', 'backend')
sys.path.insert(0, backend_dir)

from services.glpi_service import GLPIService
from config.settings import Config

class GLPIComprehensiveAnalyzer:
    """Analisador abrangente da estrutura do GLPI"""
    
    def __init__(self):
        self.glpi_service = GLPIService()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'joao_investigation': {},
            'entities': {},
            'profiles': {},
            'groups': {},
            'categories': {},
            'structure_analysis': {},
            'recommendations': []
        }
    
    def investigate_joao_pedro_dias(self) -> Dict[str, Any]:
        """Investigação específica do João Pedro Dias"""
        print("\n=== INVESTIGAÇÃO JOÃO PEDRO DIAS (ID: 1471) ===")
        
        joao_data = {
            'user_id': 1471,
            'username': 'joao-dias',
            'user_exists': False,
            'user_details': {},
            'tickets_assigned': [],
            'tickets_in_lists': [],
            'profile_analysis': {},
            'group_analysis': {},
            'entity_analysis': {},
            'ranking_eligibility': False,
            'issues_found': []
        }
        
        try:
            # 1. Verificar se o usuário existe
            print("1. Verificando existência do usuário...")
            user_response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/User/1471"
            )
            
            if user_response and user_response.status_code == 200:
                user_data = user_response.json()
                joao_data['user_exists'] = True
                joao_data['user_details'] = user_data
                print(f"   ✓ Usuário encontrado: {user_data.get('name', 'N/A')}")
                print(f"   - Nome completo: {user_data.get('firstname', '')} {user_data.get('realname', '')}")
                print(f"   - Ativo: {user_data.get('is_active')}")
                print(f"   - Deletado: {user_data.get('is_deleted')}")
                print(f"   - Perfil: {user_data.get('profiles_id')}")
                print(f"   - Entidade: {user_data.get('entities_id')}")
                print(f"   - Último login: {user_data.get('last_login')}")
            else:
                joao_data['issues_found'].append("Usuário não encontrado no GLPI")
                print("   ✗ Usuário não encontrado")
                return joao_data
            
            # 2. Buscar tickets atribuídos diretamente
            print("\n2. Buscando tickets atribuídos diretamente...")
            tickets = self._search_tickets_for_technician(1471)
            joao_data['tickets_assigned'] = tickets
            print(f"   - Tickets encontrados: {len(tickets)}")
            
            # 3. Buscar tickets onde pode aparecer em listas
            print("\n3. Buscando tickets em listas de técnicos...")
            list_tickets = self._search_tickets_in_lists(1471)
            joao_data['tickets_in_lists'] = list_tickets
            print(f"   - Tickets em listas: {len(list_tickets)}")
            
            # 4. Analisar perfil do usuário
            print("\n4. Analisando perfil do usuário...")
            profile_analysis = self._analyze_user_profile(user_data)
            joao_data['profile_analysis'] = profile_analysis
            
            # 5. Analisar grupo do usuário
            print("\n5. Analisando grupo do usuário...")
            group_analysis = self._analyze_user_group(user_data)
            joao_data['group_analysis'] = group_analysis
            
            # 6. Analisar entidade do usuário
            print("\n6. Analisando entidade do usuário...")
            entity_analysis = self._analyze_user_entity(user_data)
            joao_data['entity_analysis'] = entity_analysis
            
            # 7. Verificar elegibilidade para ranking
            print("\n7. Verificando elegibilidade para ranking...")
            joao_data['ranking_eligibility'] = self._check_ranking_eligibility(joao_data)
            
        except Exception as e:
            joao_data['issues_found'].append(f"Erro durante investigação: {str(e)}")
            print(f"   ✗ Erro: {e}")
        
        return joao_data
    
    def map_glpi_entities(self) -> Dict[str, Any]:
        """Mapeia todas as entidades do GLPI"""
        print("\n=== MAPEAMENTO DE ENTIDADES ===")
        
        entities_data = {
            'total_count': 0,
            'entities': [],
            'hierarchy': {},
            'issues_found': []
        }
        
        try:
            # Buscar todas as entidades
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/Entity",
                params={"range": "0-999", "expand_dropdowns": "true"}
            )
            
            if response and response.status_code in [200, 206]:
                entities = response.json()
                entities_data['total_count'] = len(entities)
                entities_data['entities'] = entities
                
                print(f"   ✓ {len(entities)} entidades encontradas")
                
                # Analisar hierarquia
                hierarchy = self._build_entity_hierarchy(entities)
                entities_data['hierarchy'] = hierarchy
                
                # Identificar problemas
                issues = self._analyze_entity_issues(entities)
                entities_data['issues_found'] = issues
                
            else:
                entities_data['issues_found'].append("Erro ao buscar entidades")
                print("   ✗ Erro ao buscar entidades")
                
        except Exception as e:
            entities_data['issues_found'].append(f"Erro: {str(e)}")
            print(f"   ✗ Erro: {e}")
        
        return entities_data
    
    def map_glpi_profiles(self) -> Dict[str, Any]:
        """Mapeia todos os perfis do GLPI"""
        print("\n=== MAPEAMENTO DE PERFIS ===")
        
        profiles_data = {
            'total_count': 0,
            'profiles': [],
            'permissions_matrix': {},
            'issues_found': []
        }
        
        try:
            # Buscar todos os perfis
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/Profile",
                params={"range": "0-999", "expand_dropdowns": "true"}
            )
            
            if response and response.status_code in [200, 206]:
                profiles = response.json()
                profiles_data['total_count'] = len(profiles)
                profiles_data['profiles'] = profiles
                
                print(f"   ✓ {len(profiles)} perfis encontrados")
                
                # Analisar matriz de permissões
                permissions = self._analyze_profile_permissions(profiles)
                profiles_data['permissions_matrix'] = permissions
                
                # Identificar problemas
                issues = self._analyze_profile_issues(profiles)
                profiles_data['issues_found'] = issues
                
            else:
                profiles_data['issues_found'].append("Erro ao buscar perfis")
                print("   ✗ Erro ao buscar perfis")
                
        except Exception as e:
            profiles_data['issues_found'].append(f"Erro: {str(e)}")
            print(f"   ✗ Erro: {e}")
        
        return profiles_data
    
    def map_glpi_groups(self) -> Dict[str, Any]:
        """Mapeia todos os grupos do GLPI"""
        print("\n=== MAPEAMENTO DE GRUPOS ===")
        
        groups_data = {
            'total_count': 0,
            'groups': [],
            'hierarchy': {},
            'user_distribution': {},
            'issues_found': []
        }
        
        try:
            # Buscar todos os grupos
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/Group",
                params={"range": "0-999", "expand_dropdowns": "true"}
            )
            
            if response and response.status_code in [200, 206]:
                groups = response.json()
                groups_data['total_count'] = len(groups)
                groups_data['groups'] = groups
                
                print(f"   ✓ {len(groups)} grupos encontrados")
                
                # Analisar hierarquia de grupos
                hierarchy = self._build_group_hierarchy(groups)
                groups_data['hierarchy'] = hierarchy
                
                # Analisar distribuição de usuários
                distribution = self._analyze_group_user_distribution(groups)
                groups_data['user_distribution'] = distribution
                
                # Identificar problemas
                issues = self._analyze_group_issues(groups)
                groups_data['issues_found'] = issues
                
            else:
                groups_data['issues_found'].append("Erro ao buscar grupos")
                print("   ✗ Erro ao buscar grupos")
                
        except Exception as e:
            groups_data['issues_found'].append(f"Erro: {str(e)}")
            print(f"   ✗ Erro: {e}")
        
        return groups_data
    
    def map_glpi_categories(self) -> Dict[str, Any]:
        """Mapeia categorias de problemas do GLPI"""
        print("\n=== MAPEAMENTO DE CATEGORIAS ===")
        
        categories_data = {
            'total_count': 0,
            'categories': [],
            'hierarchy': {},
            'assignment_rules': {},
            'issues_found': []
        }
        
        try:
            # Buscar categorias de tickets
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/ITILCategory",
                params={"range": "0-999", "expand_dropdowns": "true"}
            )
            
            if response and response.status_code in [200, 206]:
                categories = response.json()
                categories_data['total_count'] = len(categories)
                categories_data['categories'] = categories
                
                print(f"   ✓ {len(categories)} categorias encontradas")
                
                # Analisar hierarquia
                hierarchy = self._build_category_hierarchy(categories)
                categories_data['hierarchy'] = hierarchy
                
                # Analisar regras de atribuição
                assignment_rules = self._analyze_category_assignment_rules(categories)
                categories_data['assignment_rules'] = assignment_rules
                
                # Identificar problemas
                issues = self._analyze_category_issues(categories)
                categories_data['issues_found'] = issues
                
            else:
                categories_data['issues_found'].append("Erro ao buscar categorias")
                print("   ✗ Erro ao buscar categorias")
                
        except Exception as e:
            categories_data['issues_found'].append(f"Erro: {str(e)}")
            print(f"   ✗ Erro: {e}")
        
        return categories_data
    
    def _search_tickets_for_technician(self, tech_id: int, days: int = 90) -> List[Dict]:
        """Busca tickets atribuídos a um técnico específico"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "range": "0-999",
            "criteria[0][field]": "15",  # date
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": start_date.strftime("%Y-%m-%d"),
            "criteria[1][field]": "5",  # users_id_tech
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": str(tech_id),
            "criteria[1][link]": "AND",
            "forcedisplay[0]": "2",  # id
            "forcedisplay[1]": "5",  # users_id_tech
            "forcedisplay[2]": "15",  # date
            "forcedisplay[3]": "1",  # name
            "forcedisplay[4]": "12",  # status
        }
        
        try:
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/search/Ticket", params=params
            )
            
            if response and response.status_code in [200, 206]:
                return response.json().get("data", [])
        except Exception as e:
            print(f"Erro ao buscar tickets: {e}")
        
        return []
    
    def _search_tickets_in_lists(self, tech_id: int, days: int = 90) -> List[Dict]:
        """Busca tickets onde o técnico pode aparecer em listas"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "range": "0-999",
            "criteria[0][field]": "15",  # date
            "criteria[0][searchtype]": "morethan",
            "criteria[0][value]": start_date.strftime("%Y-%m-%d"),
            "forcedisplay[0]": "2",  # id
            "forcedisplay[1]": "5",  # users_id_tech
            "forcedisplay[2]": "15",  # date
            "forcedisplay[3]": "1",  # name
        }
        
        try:
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/search/Ticket", params=params
            )
            
            if response and response.status_code in [200, 206]:
                tickets = response.json().get("data", [])
                # Filtrar tickets onde o técnico aparece em listas
                filtered_tickets = []
                for ticket in tickets:
                    tech_field = ticket.get('5', '')
                    if isinstance(tech_field, str) and str(tech_id) in tech_field:
                        filtered_tickets.append(ticket)
                    elif isinstance(tech_field, list) and str(tech_id) in [str(t) for t in tech_field]:
                        filtered_tickets.append(ticket)
                return filtered_tickets
        except Exception as e:
            print(f"Erro ao buscar tickets em listas: {e}")
        
        return []
    
    def _analyze_user_profile(self, user_data: Dict) -> Dict:
        """Analisa o perfil do usuário"""
        profile_id = user_data.get('profiles_id')
        if not profile_id:
            return {'error': 'Perfil não encontrado'}
        
        try:
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/Profile/{profile_id}"
            )
            
            if response and response.status_code == 200:
                return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar perfil: {e}'}
        
        return {}
    
    def _analyze_user_group(self, user_data: Dict) -> Dict:
        """Analisa o grupo do usuário"""
        # Buscar grupos do usuário
        user_id = user_data.get('id')
        if not user_id:
            return {'error': 'ID do usuário não encontrado'}
        
        try:
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/User/{user_id}/Group_User"
            )
            
            if response and response.status_code == 200:
                return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar grupos: {e}'}
        
        return {}
    
    def _analyze_user_entity(self, user_data: Dict) -> Dict:
        """Analisa a entidade do usuário"""
        entity_id = user_data.get('entities_id')
        if not entity_id:
            return {'error': 'Entidade não encontrada'}
        
        try:
            response = self.glpi_service._make_authenticated_request(
                "GET", f"{self.glpi_service.glpi_url}/Entity/{entity_id}"
            )
            
            if response and response.status_code == 200:
                return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar entidade: {e}'}
        
        return {}
    
    def _check_ranking_eligibility(self, joao_data: Dict) -> bool:
        """Verifica se o usuário é elegível para aparecer no ranking"""
        # Critérios para aparecer no ranking:
        # 1. Usuário ativo
        # 2. Não deletado
        # 3. Tem tickets atribuídos nos últimos 90 dias
        # 4. Perfil adequado
        
        user_details = joao_data.get('user_details', {})
        tickets_assigned = joao_data.get('tickets_assigned', [])
        tickets_in_lists = joao_data.get('tickets_in_lists', [])
        
        is_active = user_details.get('is_active') == 1
        is_not_deleted = user_details.get('is_deleted') == 0
        has_tickets = len(tickets_assigned) > 0 or len(tickets_in_lists) > 0
        
        return is_active and is_not_deleted and has_tickets
    
    def _build_entity_hierarchy(self, entities: List[Dict]) -> Dict:
        """Constrói hierarquia de entidades"""
        hierarchy = {}
        for entity in entities:
            parent_id = entity.get('entities_id', 0)
            entity_id = entity.get('id')
            
            if parent_id not in hierarchy:
                hierarchy[parent_id] = []
            hierarchy[parent_id].append({
                'id': entity_id,
                'name': entity.get('name', ''),
                'completename': entity.get('completename', '')
            })
        
        return hierarchy
    
    def _build_group_hierarchy(self, groups: List[Dict]) -> Dict:
        """Constrói hierarquia de grupos"""
        hierarchy = {}
        for group in groups:
            parent_id = group.get('groups_id', 0)
            group_id = group.get('id')
            
            if parent_id not in hierarchy:
                hierarchy[parent_id] = []
            hierarchy[parent_id].append({
                'id': group_id,
                'name': group.get('name', ''),
                'completename': group.get('completename', '')
            })
        
        return hierarchy
    
    def _build_category_hierarchy(self, categories: List[Dict]) -> Dict:
        """Constrói hierarquia de categorias"""
        hierarchy = {}
        for category in categories:
            parent_id = category.get('itilcategories_id', 0)
            category_id = category.get('id')
            
            if parent_id not in hierarchy:
                hierarchy[parent_id] = []
            hierarchy[parent_id].append({
                'id': category_id,
                'name': category.get('name', ''),
                'completename': category.get('completename', '')
            })
        
        return hierarchy
    
    def _analyze_entity_issues(self, entities: List[Dict]) -> List[str]:
        """Analisa problemas nas entidades"""
        issues = []
        
        # Verificar entidades órfãs
        entity_ids = {e.get('id') for e in entities}
        for entity in entities:
            parent_id = entity.get('entities_id')
            if parent_id and parent_id not in entity_ids and parent_id != 0:
                issues.append(f"Entidade órfã: {entity.get('name')} (parent {parent_id} não existe)")
        
        # Verificar nomes duplicados
        names = {}
        for entity in entities:
            name = entity.get('name', '')
            if name in names:
                issues.append(f"Nome duplicado: {name}")
            names[name] = entity.get('id')
        
        return issues
    
    def _analyze_profile_permissions(self, profiles: List[Dict]) -> Dict:
        """Analisa matriz de permissões dos perfis"""
        permissions = {}
        for profile in profiles:
            profile_id = profile.get('id')
            profile_name = profile.get('name', '')
            
            # Extrair permissões relevantes
            permissions[profile_id] = {
                'name': profile_name,
                'ticket_permissions': {
                    'ticket': profile.get('ticket', ''),
                    'followup': profile.get('followup', ''),
                    'task': profile.get('task', '')
                },
                'user_permissions': {
                    'user': profile.get('user', ''),
                    'group': profile.get('group', '')
                }
            }
        
        return permissions
    
    def _analyze_profile_issues(self, profiles: List[Dict]) -> List[str]:
        """Analisa problemas nos perfis"""
        issues = []
        
        # Verificar perfis sem permissões
        for profile in profiles:
            name = profile.get('name', '')
            if not any(profile.get(perm) for perm in ['ticket', 'user', 'group']):
                issues.append(f"Perfil sem permissões: {name}")
        
        return issues
    
    def _analyze_group_user_distribution(self, groups: List[Dict]) -> Dict:
        """Analisa distribuição de usuários nos grupos"""
        distribution = {}
        
        for group in groups:
            group_id = group.get('id')
            group_name = group.get('name', '')
            
            # Buscar usuários do grupo
            try:
                response = self.glpi_service._make_authenticated_request(
                    "GET", f"{self.glpi_service.glpi_url}/Group/{group_id}/Group_User"
                )
                
                if response and response.status_code == 200:
                    users = response.json()
                    distribution[group_id] = {
                        'name': group_name,
                        'user_count': len(users),
                        'users': users
                    }
            except Exception:
                distribution[group_id] = {
                    'name': group_name,
                    'user_count': 0,
                    'error': 'Erro ao buscar usuários'
                }
        
        return distribution
    
    def _analyze_group_issues(self, groups: List[Dict]) -> List[str]:
        """Analisa problemas nos grupos"""
        issues = []
        
        # Verificar grupos vazios
        for group in groups:
            group_id = group.get('id')
            try:
                response = self.glpi_service._make_authenticated_request(
                    "GET", f"{self.glpi_service.glpi_url}/Group/{group_id}/Group_User"
                )
                
                if response and response.status_code == 200:
                    users = response.json()
                    if len(users) == 0:
                        issues.append(f"Grupo vazio: {group.get('name')}")
            except Exception:
                pass
        
        return issues
    
    def _analyze_category_assignment_rules(self, categories: List[Dict]) -> Dict:
        """Analisa regras de atribuição das categorias"""
        assignment_rules = {}
        
        for category in categories:
            category_id = category.get('id')
            category_name = category.get('name', '')
            
            assignment_rules[category_id] = {
                'name': category_name,
                'auto_assign_mode': category.get('auto_assign_mode', ''),
                'groups_id': category.get('groups_id', ''),
                'users_id': category.get('users_id', ''),
                'level': category.get('level', 0)
            }
        
        return assignment_rules
    
    def _analyze_category_issues(self, categories: List[Dict]) -> List[str]:
        """Analisa problemas nas categorias"""
        issues = []
        
        # Verificar categorias sem regras de atribuição
        for category in categories:
            name = category.get('name', '')
            if not category.get('groups_id') and not category.get('users_id'):
                issues.append(f"Categoria sem atribuição automática: {name}")
        
        # Verificar hierarquia confusa
        level_counts = {}
        for category in categories:
            level = category.get('level', 0)
            level_counts[level] = level_counts.get(level, 0) + 1
        
        if len(level_counts) > 5:
            issues.append(f"Hierarquia muito profunda: {len(level_counts)} níveis")
        
        return issues
    
    def generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Recomendações para João Pedro Dias
        joao_data = self.results.get('joao_investigation', {})
        if not joao_data.get('ranking_eligibility', False):
            if len(joao_data.get('tickets_assigned', [])) == 0:
                recommendations.append(
                    "João Pedro Dias: Verificar se deveria ter tickets atribuídos ou "
                    "considerar incluir técnicos recém-contratados no ranking"
                )
        
        # Recomendações para entidades
        entities_issues = self.results.get('entities', {}).get('issues_found', [])
        if entities_issues:
            recommendations.append(
                f"Entidades: Corrigir {len(entities_issues)} problemas estruturais identificados"
            )
        
        # Recomendações para categorias
        categories_issues = self.results.get('categories', {}).get('issues_found', [])
        if categories_issues:
            recommendations.append(
                "Categorias: Implementar regras de atribuição automática e "
                "simplificar hierarquia para melhor UX"
            )
        
        return recommendations
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Executa análise abrangente completa"""
        print("=== ANÁLISE ABRANGENTE DO GLPI ===")
        print(f"Iniciado em: {self.results['timestamp']}")
        
        # 1. Investigar João Pedro Dias
        self.results['joao_investigation'] = self.investigate_joao_pedro_dias()
        
        # 2. Mapear entidades
        self.results['entities'] = self.map_glpi_entities()
        
        # 3. Mapear perfis
        self.results['profiles'] = self.map_glpi_profiles()
        
        # 4. Mapear grupos
        self.results['groups'] = self.map_glpi_groups()
        
        # 5. Mapear categorias
        self.results['categories'] = self.map_glpi_categories()
        
        # 6. Gerar recomendações
        self.results['recommendations'] = self.generate_recommendations()
        
        # 7. Salvar resultados
        self._save_results()
        
        print("\n=== ANÁLISE CONCLUÍDA ===")
        print(f"Resultados salvos em: {self._get_output_filename()}")
        
        return self.results
    
    def _save_results(self):
        """Salva os resultados da análise"""
        output_file = self._get_output_filename()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n✓ Resultados salvos em: {output_file}")
        except Exception as e:
            print(f"\n✗ Erro ao salvar resultados: {e}")
    
    def _get_output_filename(self) -> str:
        """Gera nome do arquivo de saída"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'glpi_dashboard', 'backend', 'glpi_data', 'test_results',
            f'comprehensive_glpi_analysis_{timestamp}.json'
        )

def main():
    """Função principal"""
    try:
        analyzer = GLPIComprehensiveAnalyzer()
        results = analyzer.run_comprehensive_analysis()
        
        # Resumo executivo
        print("\n=== RESUMO EXECUTIVO ===")
        
        joao_data = results.get('joao_investigation', {})
        print(f"João Pedro Dias - Elegível para ranking: {joao_data.get('ranking_eligibility', False)}")
        print(f"Tickets atribuídos: {len(joao_data.get('tickets_assigned', []))}")
        
        entities_data = results.get('entities', {})
        print(f"Entidades mapeadas: {entities_data.get('total_count', 0)}")
        print(f"Problemas encontrados: {len(entities_data.get('issues_found', []))}")
        
        profiles_data = results.get('profiles', {})
        print(f"Perfis mapeados: {profiles_data.get('total_count', 0)}")
        
        groups_data = results.get('groups', {})
        print(f"Grupos mapeados: {groups_data.get('total_count', 0)}")
        
        categories_data = results.get('categories', {})
        print(f"Categorias mapeadas: {categories_data.get('total_count', 0)}")
        print(f"Problemas encontrados: {len(categories_data.get('issues_found', []))}")
        
        recommendations = results.get('recommendations', [])
        print(f"\nRecomendações geradas: {len(recommendations)}")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
    except Exception as e:
        print(f"Erro durante execução: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())