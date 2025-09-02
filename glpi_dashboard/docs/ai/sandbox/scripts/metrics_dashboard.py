import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys

# Adicionar o diretório backend ao path para importar os serviços
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'backend'))

try:
    from services.glpi_service import GLPIService
except ImportError:
    GLPIService = None

def load_test_results():
    """Carrega resultados de testes ou dados mock"""
    return {
        'accuracy': 0.95,
        'avg_time': 2.3,
        'code_quality': 0.88,
        'success_rate': 0.92,
        'by_type': pd.DataFrame({
            'test_type': ['API', 'Frontend', 'Backend', 'Integration'],
            'performance': [0.95, 0.88, 0.92, 0.85]
        }),
        'timeline': pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'accuracy': [0.85 + 0.1 * (i % 10) / 10 for i in range(30)]
        })
    }

def load_glpi_metrics():
    """Carrega métricas reais do GLPI se disponível"""
    if GLPIService is None:
        return None

    try:
        glpi = GLPIService()
        if not glpi.authenticate():
            return None

        # Buscar métricas básicas
        total_tickets = glpi.get_ticket_count()
        n1_tickets = glpi.get_ticket_count(group_id=89)  # N1 group

        return {
            'total_tickets': total_tickets,
            'n1_tickets': n1_tickets,
            'connection_status': 'Connected',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'connection_status': 'Error',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def create_dashboard():
    st.set_page_config(
        page_title="GLPI Dashboard - Sandbox",
        page_icon="🧪",
        layout="wide"
    )

    st.title('🧪 GLPI Dashboard - Sandbox de Métricas')
    st.markdown('---')

    # Sidebar para configurações
    with st.sidebar:
        st.header('⚙️ Configurações')
        show_mock_data = st.checkbox('Mostrar dados mock', value=True)
        show_real_data = st.checkbox('Tentar conectar GLPI', value=False)

        if st.button('🔄 Atualizar Dados'):
            st.rerun()

    # Dados mock
    if show_mock_data:
        st.header('📊 Métricas de Teste (Mock Data)')
        results = load_test_results()

        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric('Precisão Média', f"{results['accuracy']:.2%}")

        with col2:
            st.metric('Tempo Médio', f"{results['avg_time']:.2f}s")

        with col3:
            st.metric('Qualidade Código', f"{results['code_quality']:.2%}")

        with col4:
            st.metric('Taxa Sucesso', f"{results['success_rate']:.2%}")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Performance por Tipo de Teste')
            fig = px.bar(
                results['by_type'],
                x='test_type',
                y='performance',
                title='Performance por Categoria'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader('Histórico de Testes')
            fig_timeline = px.line(
                results['timeline'],
                x='date',
                y='accuracy',
                title='Evolução da Precisão'
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

    # Dados reais do GLPI
    if show_real_data:
        st.header('🔗 Métricas GLPI (Dados Reais)')

        with st.spinner('Conectando ao GLPI...'):
            glpi_metrics = load_glpi_metrics()

        if glpi_metrics:
            if 'error' in glpi_metrics:
                st.error(f"Erro ao conectar: {glpi_metrics['error']}")
                st.info(f"Status: {glpi_metrics['connection_status']}")
            else:
                # Métricas GLPI
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric('Total de Tickets', glpi_metrics['total_tickets'])

                with col2:
                    st.metric('Tickets N1', glpi_metrics['n1_tickets'])

                with col3:
                    st.metric('Status', glpi_metrics['connection_status'])

                st.success(f"Última atualização: {glpi_metrics['last_update']}")

                # Gráfico de distribuição
                if glpi_metrics['total_tickets'] > 0:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['N1', 'Outros'],
                            values=[
                                glpi_metrics['n1_tickets'],
                                glpi_metrics['total_tickets'] - glpi_metrics['n1_tickets']
                            ]
                        )
                    ])
                    fig.update_layout(title='Distribuição de Tickets')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning('Não foi possível conectar ao GLPI')

    # Informações do sistema
    with st.expander('ℹ️ Informações do Sistema'):
        st.write(f"**Python Version:** {sys.version}")
        st.write(f"**Streamlit Version:** {st.__version__}")
        st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if GLPIService:
            st.success('✅ GLPIService disponível')
        else:
            st.warning('⚠️ GLPIService não disponível')

if __name__ == '__main__':
    create_dashboard()
