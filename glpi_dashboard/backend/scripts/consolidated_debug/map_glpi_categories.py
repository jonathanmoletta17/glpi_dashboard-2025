#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mapear e analisar categorias de problemas do GLPI

Este script analisa:
- Estrutura hierárquica das categorias
- Configurações de cada categoria
- Uso das categorias em tickets
- Problemas identificados
- Recomendações de melhoria
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent.parent / 'glpi_dashboard' / 'backend'
sys.path.insert(0, str(backend_path))

from services.glpi_service import GLPIService
from core.database import get_db_connection

class GLPICategoriesMapper:
    def __init__(self):
        self.glpi_service = GLPIService()
        self.db = get_db_connection()
        self.categories = []
        self.tickets_by_category = {}
        self.hierarchy = {}
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'total_categories': 0,
            'hierarchy_levels': 0,
            'root_categories_count': 0,
            'categories_with_tickets': 0,
            'categories_without_tickets': 0,
            'most_used_categories': [],
            'unused_categories': [],
            'categories_without_description': [],
            'hierarchy': {},
            'detailed_categories': [],
            'ticket_stats': {},
            'issues_identified': [],
            'recommendations': []
        }
    
    def fetch_categories(self):
        """Busca todas as categorias do GLPI"""
        print("1️⃣ Buscando categorias do GLPI...")
        
        query = """
        SELECT 
            id,
            name,
            comment,
            itilcategories_id as parent_id,
            level,
            sons_cache,
            ancestors_cache,
            is_helpdeskvisible,
            is_incident,
            is_request,
            is_problem,
            is_change,
            tickettemplates_id_incident,
            tickettemplates_id_demand,
            date_creation,
            date_mod,
            entities_id
        FROM glpi_itilcategories 
        ORDER BY level, name
        """
        
        cursor = self.db.cursor()
        cursor.execute(query)
        self.categories = cursor.fetchall()
        
        print(f"   📋 Total de categorias encontradas: {len(self.categories)}")
        return self.categories
    
    def fetch_ticket_stats(self):
        """Busca estatísticas de uso das categorias em tickets"""
        print("2️⃣ Analisando uso das categorias em tickets...")
        
        query = """
        SELECT 
            itilcategories_id,
            COUNT(*) as ticket_count,
            COUNT(CASE WHEN type = 1 THEN 1 END) as incident_count,
            COUNT(CASE WHEN type = 2 THEN 1 END) as request_count
        FROM glpi_tickets 
        WHERE itilcategories_id IS NOT NULL
        GROUP BY itilcategories_id
        ORDER BY ticket_count DESC
        """
        
        cursor = self.db.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        for row in results:
            category_id = row['itilcategories_id']
            self.tickets_by_category[category_id] = {
                'total_tickets': row['ticket_count'],
                'incidents': row['incident_count'],
                'requests': row['request_count']
            }
        
        print(f"   🎫 Categorias com tickets: {len(self.tickets_by_category)}")
        return self.tickets_by_category
    
    def build_hierarchy(self):
        """Constrói a hierarquia das categorias"""
        print("3️⃣ Construindo hierarquia das categorias...")
        
        # Organizar por nível
        levels = {}
        root_categories = []
        
        for category in self.categories:
            level = category['level']
            if level not in levels:
                levels[level] = []
            levels[level].append(category)
            
            if category['parent_id'] == 0 or category['parent_id'] is None:
                root_categories.append({
                    'id': category['id'],
                    'name': category['name'],
                    'level': level
                })
        
        self.hierarchy = {
            'levels': levels,
            'root_categories': root_categories,
            'max_level': max(levels.keys()) if levels else 0
        }
        
        print(f"   🌳 Níveis hierárquicos: {self.hierarchy['max_level'] + 1}")
        print(f"   📁 Categorias raiz: {len(root_categories)}")
        
        return self.hierarchy
    
    def analyze_categories(self):
        """Analisa as categorias em detalhes"""
        print("4️⃣ Analisando categorias em detalhes...")
        
        detailed_categories = []
        categories_with_tickets = 0
        categories_without_tickets = 0
        categories_without_description = []
        unused_categories = []
        
        for category in self.categories:
            category_id = category['id']
            ticket_stats = self.tickets_by_category.get(category_id, {
                'total_tickets': 0,
                'incidents': 0,
                'requests': 0
            })
            
            # Verificar se tem tickets
            if ticket_stats['total_tickets'] > 0:
                categories_with_tickets += 1
            else:
                categories_without_tickets += 1
                unused_categories.append(category['name'])
            
            # Verificar se tem descrição
            if not category['comment'] or category['comment'].strip() == '':
                categories_without_description.append(category['name'])
            
            # Buscar entidade
            entity_name = "Entidade não encontrada"
            if category['entities_id']:
                entity_query = "SELECT completename FROM glpi_entities WHERE id = %s"
                cursor = self.db.cursor()
                cursor.execute(entity_query, (category['entities_id'],))
                entity_result = cursor.fetchone()
                if entity_result:
                    entity_name = entity_result['completename']
            
            detailed_category = {
                'id': category_id,
                'name': category['name'],
                'comment': category['comment'] or '',
                'parent_id': category['parent_id'],
                'level': category['level'],
                'entity': entity_name,
                'visibility': {
                    'is_helpdeskvisible': bool(category['is_helpdeskvisible']),
                    'is_incident': bool(category['is_incident']),
                    'is_request': bool(category['is_request']),
                    'is_problem': bool(category['is_problem']),
                    'is_change': bool(category['is_change'])
                },
                'templates': {
                    'incident_template_id': category['tickettemplates_id_incident'],
                    'request_template_id': category['tickettemplates_id_demand']
                },
                'ticket_stats': ticket_stats,
                'hierarchy_info': {
                    'sons_cache': category['sons_cache'] or '',
                    'ancestors_cache': category['ancestors_cache'] or ''
                },
                'dates': {
                    'creation': str(category['date_creation']) if category['date_creation'] else None,
                    'modification': str(category['date_mod']) if category['date_mod'] else None
                }
            }
            
            detailed_categories.append(detailed_category)
        
        # Ordenar por uso (mais usadas primeiro)
        detailed_categories.sort(key=lambda x: x['ticket_stats']['total_tickets'], reverse=True)
        
        # Top 10 mais usadas
        most_used = detailed_categories[:10]
        most_used_list = [{
            'name': cat['name'],
            'tickets': cat['ticket_stats']['total_tickets'],
            'incidents': cat['ticket_stats']['incidents'],
            'requests': cat['ticket_stats']['requests']
        } for cat in most_used if cat['ticket_stats']['total_tickets'] > 0]
        
        self.analysis_results.update({
            'detailed_categories': detailed_categories,
            'categories_with_tickets': categories_with_tickets,
            'categories_without_tickets': categories_without_tickets,
            'categories_without_description': categories_without_description,
            'unused_categories': unused_categories,
            'most_used_categories': most_used_list
        })
        
        print(f"   ✅ Categorias com tickets: {categories_with_tickets}")
        print(f"   ❌ Categorias sem tickets: {categories_without_tickets}")
        print(f"   📝 Categorias sem descrição: {len(categories_without_description)}")
        
        return detailed_categories
    
    def identify_issues(self):
        """Identifica problemas na estrutura das categorias"""
        print("5️⃣ Identificando problemas...")
        
        issues = []
        
        # Categorias não utilizadas
        if self.analysis_results['unused_categories']:
            issues.append({
                'type': 'unused_categories',
                'description': f"{len(self.analysis_results['unused_categories'])} categorias não possuem tickets",
                'categories': self.analysis_results['unused_categories'][:10]  # Limitar a 10 para não sobrecarregar
            })
        
        # Categorias sem descrição
        if self.analysis_results['categories_without_description']:
            issues.append({
                'type': 'missing_description',
                'description': f"{len(self.analysis_results['categories_without_description'])} categorias sem descrição",
                'categories': self.analysis_results['categories_without_description'][:10]
            })
        
        # Categorias com muitos tickets (possível necessidade de subdivisão)
        high_usage_categories = []
        for cat in self.analysis_results['detailed_categories']:
            if cat['ticket_stats']['total_tickets'] > 100:
                high_usage_categories.append(f"{cat['name']} ({cat['ticket_stats']['total_tickets']} tickets)")
        
        if high_usage_categories:
            issues.append({
                'type': 'high_usage_categories',
                'description': f"{len(high_usage_categories)} categorias com mais de 100 tickets",
                'categories': high_usage_categories
            })
        
        # Categorias órfãs (parent_id aponta para categoria inexistente)
        existing_ids = {cat['id'] for cat in self.categories}
        orphan_categories = []
        for cat in self.categories:
            if cat['parent_id'] and cat['parent_id'] != 0 and cat['parent_id'] not in existing_ids:
                orphan_categories.append(cat['name'])
        
        if orphan_categories:
            issues.append({
                'type': 'orphan_categories',
                'description': f"{len(orphan_categories)} categorias órfãs (parent_id inválido)",
                'categories': orphan_categories
            })
        
        self.analysis_results['issues_identified'] = issues
        
        print(f"   ⚠️ Problemas identificados: {len(issues)}")
        return issues
    
    def generate_recommendations(self):
        """Gera recomendações de melhoria"""
        print("6️⃣ Gerando recomendações...")
        
        recommendations = [
            "Revisar categorias não utilizadas e considerar remoção ou consolidação",
            "Adicionar descrições claras para todas as categorias",
            "Considerar subdivisão de categorias com alto volume de tickets",
            "Implementar revisão periódica da estrutura de categorias",
            "Criar processo de aprovação para criação de novas categorias",
            "Estabelecer nomenclatura padronizada para categorias",
            "Configurar templates apropriados para cada tipo de categoria",
            "Implementar treinamento sobre uso correto das categorias",
            "Criar matriz de responsabilidades por categoria",
            "Implementar métricas de qualidade da categorização"
        ]
        
        self.analysis_results['recommendations'] = recommendations
        return recommendations
    
    def compile_final_results(self):
        """Compila os resultados finais"""
        print("7️⃣ Compilando resultados finais...")
        
        self.analysis_results.update({
            'total_categories': len(self.categories),
            'hierarchy_levels': self.hierarchy['max_level'] + 1,
            'root_categories_count': len(self.hierarchy['root_categories']),
            'hierarchy': self.hierarchy,
            'ticket_stats': {
                'total_tickets_with_category': sum(stats['total_tickets'] for stats in self.tickets_by_category.values()),
                'total_incidents': sum(stats['incidents'] for stats in self.tickets_by_category.values()),
                'total_requests': sum(stats['requests'] for stats in self.tickets_by_category.values())
            }
        })
        
        return self.analysis_results
    
    def save_report(self):
        """Salva o relatório em arquivo JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'categories_mapping_{timestamp}.json'
        
        # Criar diretório se não existir
        analysis_dir = Path(__file__).parent.parent / 'glpi_dashboard' / 'backend' / 'glpi_data' / 'analysis'
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = analysis_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório salvo em: {filepath}")
        return filepath
    
    def run_analysis(self):
        """Executa a análise completa"""
        print("🔍 INICIANDO MAPEAMENTO DE CATEGORIAS DO GLPI")
        print("=" * 50)
        
        try:
            # Executar análises
            self.fetch_categories()
            self.fetch_ticket_stats()
            self.build_hierarchy()
            self.analyze_categories()
            self.identify_issues()
            self.generate_recommendations()
            self.compile_final_results()
            
            # Salvar relatório
            filepath = self.save_report()
            
            # Exibir resumo
            print("\n📋 RESUMO DO MAPEAMENTO DE CATEGORIAS")
            print("=" * 40)
            print(f"📊 Total de categorias: {self.analysis_results['total_categories']}")
            print(f"🌳 Níveis hierárquicos: {self.analysis_results['hierarchy_levels']}")
            print(f"📁 Categorias raiz: {self.analysis_results['root_categories_count']}")
            print(f"✅ Categorias com tickets: {self.analysis_results['categories_with_tickets']}")
            print(f"❌ Categorias sem tickets: {self.analysis_results['categories_without_tickets']}")
            print(f"🎫 Total de tickets categorizados: {self.analysis_results['ticket_stats']['total_tickets_with_category']}")
            print(f"⚠️  Problemas identificados: {len(self.analysis_results['issues_identified'])}")
            print(f"💡 Recomendações: {len(self.analysis_results['recommendations'])}")
            
            if self.analysis_results['issues_identified']:
                print("\n⚠️  PROBLEMAS ENCONTRADOS:")
                for issue in self.analysis_results['issues_identified']:
                    print(f"   • {issue['description']}")
            
            print("\n✅ Mapeamento de categorias concluído!")
            
        except Exception as e:
            print(f"❌ Erro durante a análise: {str(e)}")
            raise
        finally:
            if hasattr(self, 'db') and self.db:
                self.db.close()

def main():
    """Função principal"""
    mapper = GLPICategoriesMapper()
    mapper.run_analysis()

if __name__ == '__main__':
    main()