# Diretrizes de Interação e Estilo de Código - GLPI Dashboard

## Filosofia de Desenvolvimento

### Princípios Fundamentais
- **Clareza sobre Cleverness**: Código claro e legível é preferível a soluções "inteligentes" mas obscuras
- **Consistência**: Manter padrões consistentes em todo o projeto
- **Segurança por Design**: Considerar segurança em cada decisão de implementação
- **Performance Consciente**: Otimizar quando necessário, medir antes de otimizar
- **Acessibilidade**: Garantir que a aplicação seja acessível a todos os usuários

## Estilo de Comunicação

### Interação com o Desenvolvedor
- **Tom**: Colaborativo e educativo
- **Explicações**: Sempre incluir o "porquê" das decisões técnicas
- **Alternativas**: Apresentar opções quando aplicável
- **Contexto**: Considerar o impacto das mudanças no sistema como um todo

### Documentação de Código
- **Comentários**: Explicar o "porquê", não o "o que"
- **JSDoc/Docstrings**: Obrigatório para funções públicas
- **README**: Manter atualizado com mudanças significativas
- **Changelog**: Documentar mudanças importantes

## Padrões de Código Frontend (React + TypeScript)

### Estrutura de Componentes
```typescript
// ✅ Bom: Componente funcional com tipagem clara
interface DashboardCardProps {
  title: string;
  data: MetricData;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  data,
  isLoading = false,
  onRefresh
}) => {
  // Implementação
};
```

### Hooks Customizados
```typescript
// ✅ Bom: Hook com tipagem e tratamento de erro
export const useGLPIData = <T>(endpoint: string) => {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Implementação com tratamento de erro
};
```

### Gerenciamento de Estado
```typescript
// ✅ Bom: Uso do TanStack Query para cache inteligente
const { data, error, isLoading, refetch } = useQuery({
  queryKey: ['glpi-tickets', filters],
  queryFn: () => fetchGLPITickets(filters),
  staleTime: 5 * 60 * 1000, // 5 minutos
  cacheTime: 10 * 60 * 1000, // 10 minutos
});
```

### Estilização com Tailwind
```typescript
// ✅ Bom: Classes organizadas e responsivas
const cardClasses = cn(
  'bg-white dark:bg-gray-800',
  'rounded-lg shadow-md',
  'p-6 transition-all duration-200',
  'hover:shadow-lg hover:scale-[1.02]',
  'md:p-8 lg:p-10'
);
```

## Padrões de Código Backend (Flask + Python)

### Estrutura de APIs
```python
# ✅ Bom: Endpoint com validação e tratamento de erro
@bp.route('/api/tickets', methods=['GET'])
@require_auth
@validate_json(TicketQuerySchema)
def get_tickets():
    """Retrieve GLPI tickets with filtering and pagination.

    Returns:
        JSON response with tickets data and metadata
    """
    try:
        # Implementação
        return jsonify({
            'data': tickets,
            'meta': pagination_info
        })
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

### Modelos de Dados
```python
# ✅ Bom: Modelo Pydantic com validação
class TicketModel(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Tratamento de Erros
```python
# ✅ Bom: Exceções estruturadas
class GLPIAPIError(Exception):
    """Base exception for GLPI API errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class GLPIConnectionError(GLPIAPIError):
    """Raised when connection to GLPI fails."""
    pass
```

## Segurança

### Autenticação e Autorização
```python
# ✅ Bom: Decorador de autenticação
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not validate_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

### Validação de Entrada
```python
# ✅ Bom: Sanitização de dados
def sanitize_input(data: dict) -> dict:
    """Sanitize user input to prevent injection attacks."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = html.escape(value.strip())
        else:
            sanitized[key] = value
    return sanitized
```

## Performance

### Cache Inteligente
```python
# ✅ Bom: Cache com TTL apropriado
@cache.memoize(timeout=300)  # 5 minutos
def get_dashboard_metrics(user_id: int) -> dict:
    """Get cached dashboard metrics for user."""
    return calculate_metrics(user_id)
```

### Paginação Eficiente
```python
# ✅ Bom: Paginação com cursor
def paginate_tickets(cursor: Optional[str] = None, limit: int = 20):
    query = Ticket.query.order_by(Ticket.created_at.desc())

    if cursor:
        cursor_date = decode_cursor(cursor)
        query = query.filter(Ticket.created_at < cursor_date)

    tickets = query.limit(limit + 1).all()

    has_next = len(tickets) > limit
    if has_next:
        tickets = tickets[:-1]

    next_cursor = encode_cursor(tickets[-1].created_at) if has_next else None

    return tickets, next_cursor
```

## Testes

### Testes Frontend
```typescript
// ✅ Bom: Teste de componente com mocks
describe('DashboardCard', () => {
  it('should display loading state correctly', () => {
    render(
      <DashboardCard
        title="Test Card"
        data={mockData}
        isLoading={true}
      />
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});
```

### Testes Backend
```python
# ✅ Bom: Teste de API com fixtures
def test_get_tickets_success(client, auth_headers, sample_tickets):
    """Test successful ticket retrieval."""
    response = client.get('/api/tickets', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert len(data['data']) == len(sample_tickets)
```

## Monitoramento e Logging

### Logging Estruturado
```python
# ✅ Bom: Log estruturado com contexto
logger.info(
    "Ticket created successfully",
    extra={
        "ticket_id": ticket.id,
        "user_id": current_user.id,
        "action": "create_ticket",
        "duration_ms": duration
    }
)
```

### Métricas de Performance
```python
# ✅ Bom: Instrumentação de performance
@monitor_performance
def process_glpi_sync():
    """Process GLPI synchronization with monitoring."""
    start_time = time.time()

    try:
        # Processamento
        result = sync_glpi_data()

        metrics.increment('glpi.sync.success')
        metrics.timing('glpi.sync.duration', time.time() - start_time)

        return result
    except Exception as e:
        metrics.increment('glpi.sync.error')
        raise
```

## Acessibilidade

### Componentes Acessíveis
```typescript
// ✅ Bom: Componente com acessibilidade
const AccessibleButton: React.FC<ButtonProps> = ({
  children,
  onClick,
  disabled = false,
  ariaLabel
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      className="focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {children}
    </button>
  );
};
```

## Documentação

### API Documentation
```python
# ✅ Bom: Documentação OpenAPI
@bp.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id: int):
    """
    Get ticket by ID
    ---
    parameters:
      - name: ticket_id
        in: path
        type: integer
        required: true
        description: The ticket ID
    responses:
      200:
        description: Ticket details
        schema:
          $ref: '#/definitions/Ticket'
      404:
        description: Ticket not found
    """
    # Implementação
```

Essas diretrizes devem ser seguidas consistentemente em todo o projeto para manter a qualidade, segurança e manutenibilidade do código.
