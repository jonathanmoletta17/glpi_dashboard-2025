import sys
sys.path.append('.')
from services.glpi_service import GLPIService
from datetime import datetime, timedelta
import json

# Inicializar o serviço GLPI
glpi_service = GLPIService()

# Autenticar
if glpi_service.authenticate():
    print('Autenticação bem-sucedida')
    
    # Buscar tickets criados nas últimas 48 horas
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f'Buscando tickets criados entre {yesterday} e {today}')
    
    # Fazer requisição direta à API de busca de tickets
    search_params = {
        'criteria': [
            {
                'field': 15,  # Campo de data de criação
                'searchtype': 'morethan',
                'value': yesterday
            }
        ],
        'range': '0-20'
    }
    
    response = glpi_service._make_authenticated_request(
        'GET',
        f'{glpi_service.glpi_url}/search/Ticket',
        params=search_params
    )
    
    print(f'Status da resposta: {response.status_code}')
    print(f'Conteúdo da resposta: {response.text[:500]}...')
    
    if response.status_code == 200:
        if response.text.strip():
            try:
                data = response.json()
                print(f'Total de tickets encontrados: {data.get("totalcount", 0)}')
                
                if 'data' in data and data['data']:
                    print('\nPrimeiros 5 tickets:')
                    for i, ticket in enumerate(data['data'][:5]):
                        ticket_id = ticket.get('2')
                        status = ticket.get('12')
                        date_created = ticket.get('15')
                        print(f'Ticket {i+1}: ID={ticket_id}, Status={status}, Data={date_created}')
                        
                    # Verificar se há tickets com status "Novo" (ID 1)
                    new_tickets = [t for t in data['data'] if t.get('12') == '1']
                    print(f'\nTickets com status "Novo" (ID 1): {len(new_tickets)}')
                    
                    # Mostrar distribuição de status
                    status_count = {}
                    for ticket in data['data']:
                        status = ticket.get('12', 'Unknown')
                        status_count[status] = status_count.get(status, 0) + 1
                    
                    print('\nDistribuição de status:')
                    for status, count in status_count.items():
                        print(f'  Status {status}: {count} tickets')
                else:
                    print('Nenhum ticket encontrado nos dados')
            except Exception as e:
                print(f'Erro ao fazer parse JSON: {e}')
        else:
            print('Resposta vazia do servidor')
    else:
        print(f'Erro na requisição: {response.text}')
else:
    print('Falha na autenticação')