#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Métricas GLPI
Gera relatórios detalhados sobre técnicos e tickets baseado nos dados otimizados
"""

import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import os
from collections import Counter, defaultdict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metrics_analysis.log'),
        logging.StreamHandler()
    ]
)

class GLPIMetricsAnalyzer:
    def __init__(self):
        self.tickets_df = None
        self.users_df = None
        self.technicians_df = None
        self.metrics = {}

    def load_data(self):
        """Carrega os dados otimizados para análise"""
        try:
            logging.info("Carregando dados otimizados...")

            # Carregar dados principais
            if os.path.exists('tickets_copilot_optimized.csv'):
                self.tickets_df = pd.read_csv('tickets_copilot_optimized.csv')
                logging.info(f"Tickets carregados: {len(self.tickets_df)}")

            if os.path.exists('users_copilot_optimized.csv'):
                self.users_df = pd.read_csv('users_copilot_optimized.csv')
                logging.info(f"Usuários carregados: {len(self.users_df)}")

            if os.path.exists('tecnicos_formatted.csv'):
                self.technicians_df = pd.read_csv('tecnicos_formatted.csv')
                logging.info(f"Técnicos carregados: {len(self.technicians_df)}")

            return True

        except Exception as e:
            logging.error(f"Erro ao carregar dados: {e}")
            return False

    def analyze_technicians(self):
        """Analisa métricas dos técnicos"""
        try:
            logging.info("Analisando métricas de técnicos...")

            if self.technicians_df is None:
                return {}

            # Técnicos ativos
            active_technicians = self.technicians_df[self.technicians_df['is_active'] == 1]

            # Distribuição por grupos
            group_distribution = active_technicians['grupo_principal'].value_counts().to_dict()

            # Últimos logins
            recent_logins = 0
            if 'last_login' in active_technicians.columns:
                active_technicians['last_login'] = pd.to_datetime(active_technicians['last_login'], errors='coerce')
                cutoff_date = datetime.now() - timedelta(days=30)
                recent_logins = len(active_technicians[active_technicians['last_login'] > cutoff_date])

            # Lista detalhada de técnicos
            technicians_list = []
            for _, tech in active_technicians.iterrows():
                technicians_list.append({
                    'id': tech['id'],
                    'nome_completo': tech.get('nome_completo', ''),
                    'grupo_principal': tech.get('grupo_principal', ''),
                    'last_login': str(tech.get('last_login', '')),
                    'is_active': tech.get('is_active', 0)
                })

            technician_metrics = {
                'total_ativos': len(active_technicians),
                'total_geral': len(self.technicians_df),
                'distribuicao_grupos': group_distribution,
                'logins_recentes_30d': recent_logins,
                'lista_tecnicos': technicians_list
            }

            return technician_metrics

        except Exception as e:
            logging.error(f"Erro ao analisar técnicos: {e}")
            return {}

    def analyze_tickets(self):
        """Analisa métricas dos tickets"""
        try:
            logging.info("Analisando métricas de tickets...")

            if self.tickets_df is None:
                return {}

            # Métricas básicas
            total_tickets = len(self.tickets_df)

            # Tickets solucionados (status 5 = Solucionado, 6 = Fechado)
            solved_tickets = len(self.tickets_df[self.tickets_df['status'].isin([5, 6])])

            # Distribuição por categoria automática
            category_distribution = self.tickets_df['categoria_automatica'].value_counts().to_dict()

            # Distribuição por status
            status_distribution = self.tickets_df['status_desc'].value_counts().to_dict()

            # Distribuição por prioridade
            priority_distribution = self.tickets_df['priority_desc'].value_counts().to_dict()

            # Tempo médio de resolução
            avg_resolution_time = 0
            if 'tempo_resolucao_dias' in self.tickets_df.columns:
                resolved_tickets = self.tickets_df[self.tickets_df['tempo_resolucao_dias'].notna()]
                if len(resolved_tickets) > 0:
                    avg_resolution_time = resolved_tickets['tempo_resolucao_dias'].mean()

            # Tickets por entidade
            entity_distribution = self.tickets_df['entities_id'].value_counts().head(10).to_dict()

            # Exemplos de tickets por categoria
            examples_by_category = {}
            for category in category_distribution.keys():
                category_tickets = self.tickets_df[self.tickets_df['categoria_automatica'] == category].head(3)
                examples_by_category[category] = [
                    {
                        'id': int(row['id']),
                        'name': str(row.get('name', '')),
                        'status': str(row.get('status_desc', '')),
                        'priority': str(row.get('priority_desc', ''))
                    }
                    for _, row in category_tickets.iterrows()
                ]

            ticket_metrics = {
                'total_tickets': total_tickets,
                'tickets_solucionados': solved_tickets,
                'taxa_resolucao': round((solved_tickets / total_tickets) * 100, 2) if total_tickets > 0 else 0,
                'tempo_medio_resolucao_dias': round(avg_resolution_time, 2),
                'distribuicao_categorias': category_distribution,
                'distribuicao_status': status_distribution,
                'distribuicao_prioridades': priority_distribution,
                'distribuicao_entidades': entity_distribution,
                'exemplos_por_categoria': examples_by_category
            }

            return ticket_metrics

        except Exception as e:
            logging.error(f"Erro ao analisar tickets: {e}")
            return {}

    def analyze_correlations(self):
        """Analisa correlações entre técnicos e tickets"""
        try:
            logging.info("Analisando correlações...")

            correlations = {}

            if self.tickets_df is not None and self.technicians_df is not None:
                # Tickets por técnico (último atualizador)
                if 'users_id_lastupdater' in self.tickets_df.columns:
                    tickets_by_tech = self.tickets_df['users_id_lastupdater'].value_counts().to_dict()

                    # Mapear IDs para nomes
                    tech_performance = {}
                    for tech_id, ticket_count in tickets_by_tech.items():
                        tech_info = self.technicians_df[self.technicians_df['name'] == tech_id]
                        if not tech_info.empty:
                            tech_name = tech_info.iloc[0].get('nome_completo', tech_id)
                            tech_group = tech_info.iloc[0].get('grupo_principal', '')
                            tech_performance[tech_name] = {
                                'tickets_atualizados': ticket_count,
                                'grupo': tech_group
                            }

                    correlations['performance_tecnicos'] = tech_performance

                # Categorias mais comuns por grupo
                group_categories = defaultdict(lambda: defaultdict(int))
                if 'users_id_lastupdater' in self.tickets_df.columns:
                    for _, ticket in self.tickets_df.iterrows():
                        tech_id = ticket.get('users_id_lastupdater')
                        category = ticket.get('categoria_automatica', 'Outros')

                        tech_info = self.technicians_df[self.technicians_df['name'] == tech_id]
                        if not tech_info.empty:
                            group = tech_info.iloc[0].get('grupo_principal', 'Sem Grupo')
                            group_categories[group][category] += 1

                correlations['categorias_por_grupo'] = dict(group_categories)

            return correlations

        except Exception as e:
            logging.error(f"Erro ao analisar correlações: {e}")
            return {}

    def generate_insights(self):
        """Gera insights inteligentes baseados nos dados"""
        try:
            logging.info("Gerando insights...")

            insights = []

            # Insights sobre técnicos
            if 'tecnicos' in self.metrics:
                tech_metrics = self.metrics['tecnicos']
                insights.append(f"Sistema possui {tech_metrics['total_ativos']} técnicos ativos de {tech_metrics['total_geral']} cadastrados")

                if tech_metrics['logins_recentes_30d'] > 0:
                    insights.append(f"{tech_metrics['logins_recentes_30d']} técnicos fizeram login nos últimos 30 dias")

                # Grupo mais ativo
                if tech_metrics['distribuicao_grupos']:
                    top_group = max(tech_metrics['distribuicao_grupos'], key=tech_metrics['distribuicao_grupos'].get)
                    insights.append(f"Grupo com mais técnicos: {top_group} ({tech_metrics['distribuicao_grupos'][top_group]} técnicos)")

            # Insights sobre tickets
            if 'tickets' in self.metrics:
                ticket_metrics = self.metrics['tickets']
                insights.append(f"Taxa de resolução de tickets: {ticket_metrics['taxa_resolucao']}%")
                insights.append(f"Tempo médio de resolução: {ticket_metrics['tempo_medio_resolucao_dias']} dias")

                # Categoria mais comum
                if ticket_metrics['distribuicao_categorias']:
                    top_category = max(ticket_metrics['distribuicao_categorias'], key=ticket_metrics['distribuicao_categorias'].get)
                    insights.append(f"Categoria mais comum: {top_category} ({ticket_metrics['distribuicao_categorias'][top_category]} tickets)")

                # Status mais comum
                if ticket_metrics['distribuicao_status']:
                    top_status = max(ticket_metrics['distribuicao_status'], key=ticket_metrics['distribuicao_status'].get)
                    insights.append(f"Status mais comum: {top_status} ({ticket_metrics['distribuicao_status'][top_status]} tickets)")

            return insights

        except Exception as e:
            logging.error(f"Erro ao gerar insights: {e}")
            return []

    def run_analysis(self):
        """Executa análise completa"""
        try:
            logging.info("Iniciando análise completa de métricas...")

            # Carregar dados
            if not self.load_data():
                return False

            # Executar análises
            self.metrics['tecnicos'] = self.analyze_technicians()
            self.metrics['tickets'] = self.analyze_tickets()
            self.metrics['correlacoes'] = self.analyze_correlations()
            self.metrics['insights'] = self.generate_insights()

            # Adicionar metadados
            self.metrics['metadata'] = {
                'data_analise': datetime.now().isoformat(),
                'versao': '1.0',
                'fonte_dados': 'GLPI API Extraction - Copilot Optimized'
            }

            return True

        except Exception as e:
            logging.error(f"Erro na análise: {e}")
            return False

    def save_results(self):
        """Salva resultados da análise"""
        try:
            # Salvar JSON completo
            with open('glpi_metrics_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2, default=str)

            # Criar relatório em texto
            self.create_text_report()

            logging.info("Resultados salvos com sucesso")
            return True

        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {e}")
            return False

    def create_text_report(self):
        """Cria relatório em texto legível"""
        report = []
        report.append("="*80)
        report.append("RELATÓRIO DE MÉTRICAS GLPI")
        report.append("="*80)
        report.append(f"Data da Análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append("")

        # Seção Técnicos
        if 'tecnicos' in self.metrics:
            tech = self.metrics['tecnicos']
            report.append("📋 MÉTRICAS DE TÉCNICOS")
            report.append("-" * 40)
            report.append(f"• Total de Técnicos Ativos: {tech.get('total_ativos', 0)}")
            report.append(f"• Total Geral Cadastrados: {tech.get('total_geral', 0)}")
            report.append(f"• Logins Recentes (30 dias): {tech.get('logins_recentes_30d', 0)}")
            report.append("")

            if tech.get('distribuicao_grupos'):
                report.append("Distribuição por Grupos:")
                for grupo, count in tech['distribuicao_grupos'].items():
                    report.append(f"  - {grupo}: {count} técnicos")
            report.append("")

        # Seção Tickets
        if 'tickets' in self.metrics:
            tickets = self.metrics['tickets']
            report.append("🎫 MÉTRICAS DE TICKETS")
            report.append("-" * 40)
            report.append(f"• Total de Tickets: {tickets.get('total_tickets', 0):,}")
            report.append(f"• Tickets Solucionados: {tickets.get('tickets_solucionados', 0):,}")
            report.append(f"• Taxa de Resolução: {tickets.get('taxa_resolucao', 0)}%")
            report.append(f"• Tempo Médio de Resolução: {tickets.get('tempo_medio_resolucao_dias', 0)} dias")
            report.append("")

            if tickets.get('distribuicao_categorias'):
                report.append("Top 5 Categorias:")
                sorted_categories = sorted(tickets['distribuicao_categorias'].items(), key=lambda x: x[1], reverse=True)[:5]
                for categoria, count in sorted_categories:
                    report.append(f"  - {categoria}: {count:,} tickets")
            report.append("")

        # Seção Insights
        if 'insights' in self.metrics and self.metrics['insights']:
            report.append("💡 INSIGHTS PRINCIPAIS")
            report.append("-" * 40)
            for insight in self.metrics['insights']:
                report.append(f"• {insight}")
            report.append("")

        report.append("="*80)

        # Salvar relatório
        with open('glpi_metrics_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

def main():
    """Função principal"""
    start_time = datetime.now()

    print("\n" + "="*70)
    print("ANALISADOR DE MÉTRICAS GLPI")
    print("="*70)

    analyzer = GLPIMetricsAnalyzer()

    # Executar análise
    if analyzer.run_analysis():
        # Salvar resultados
        if analyzer.save_results():
            end_time = datetime.now()
            duration = end_time - start_time

            print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
            print(f"⏱️  Tempo de execução: {duration}")
            print("\n📊 ARQUIVOS GERADOS:")
            print("  • glpi_metrics_analysis.json - Dados completos em JSON")
            print("  • glpi_metrics_report.txt - Relatório legível")
            print("  • metrics_analysis.log - Log da execução")

            # Mostrar resumo rápido
            if 'tecnicos' in analyzer.metrics and 'tickets' in analyzer.metrics:
                tech_count = analyzer.metrics['tecnicos'].get('total_ativos', 0)
                ticket_count = analyzer.metrics['tickets'].get('total_tickets', 0)
                resolution_rate = analyzer.metrics['tickets'].get('taxa_resolucao', 0)

                print("\n📈 RESUMO EXECUTIVO:")
                print(f"  • {tech_count} técnicos ativos")
                print(f"  • {ticket_count:,} tickets analisados")
                print(f"  • {resolution_rate}% taxa de resolução")

            print("\n🎯 Dados prontos para análise e dashboard!")
            print("="*70)
        else:
            print("❌ Erro ao salvar resultados")
    else:
        print("❌ Erro na análise")

if __name__ == "__main__":
    main()
