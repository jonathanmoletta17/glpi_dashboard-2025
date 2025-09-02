import React, { useState, useEffect } from 'react';
import { Ticket } from '../types/ticket';
import { Clock, User, AlertCircle, CheckCircle, Circle, Play } from 'lucide-react';

interface TicketListProps {
  onTicketClick: (ticket: Ticket) => void;
}

export const TicketList: React.FC<TicketListProps> = ({ onTicketClick }) => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  // Mock data para demonstração
  useEffect(() => {
    const mockTickets: Ticket[] = [
      {
        id: '001',
        title: 'Problema com impressora do setor financeiro',
        description: 'A impressora HP LaserJet do setor financeiro não está funcionando. Apresenta erro de papel atolado, mas não há papel atolado visível.',
        status: 'novo',
        priority: 'alta',
        category: 'Hardware',
        requester: {
          id: '1',
          name: 'Maria Silva',
          email: 'maria.silva@empresa.com',
          avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=32&h=32&fit=crop&crop=face'
        },
        technician: {
          id: '2',
          name: 'João Santos',
          email: 'joao.santos@empresa.com',
          avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'
        },
        group: {
          id: '1',
          name: 'Suporte Técnico'
        },
        createdAt: '2024-01-15T09:30:00Z',
        updatedAt: '2024-01-15T10:15:00Z',
        dueDate: '2024-01-16T17:00:00Z',
        location: 'Andar 2 - Sala 205',
        urgency: 3,
        impact: 2,
        tags: ['impressora', 'hardware', 'financeiro'],
        comments: [
          {
            id: '1',
            content: 'Verificando o problema. Parece ser um sensor defeituoso.',
            author: {
              id: '2',
              name: 'João Santos',
              avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'
            },
            createdAt: '2024-01-15T10:15:00Z'
          }
        ]
      },
      {
        id: '002',
        title: 'Solicitação de acesso ao sistema ERP',
        description: 'Novo funcionário precisa de acesso ao sistema ERP com perfil de consulta para o módulo financeiro.',
        status: 'pendente',
        priority: 'normal',
        category: 'Acesso',
        requester: {
          id: '3',
          name: 'Carlos Oliveira',
          email: 'carlos.oliveira@empresa.com'
        },
        createdAt: '2024-01-14T14:20:00Z',
        updatedAt: '2024-01-15T08:45:00Z',
        urgency: 2,
        impact: 1,
        tags: ['acesso', 'erp', 'novo-funcionario']
      },
      {
        id: '003',
        title: 'Computador lento no departamento de vendas',
        description: 'O computador da estação 15 está muito lento, travando constantemente e dificultando o trabalho da equipe.',
        status: 'progresso',
        priority: 'alta',
        category: 'Performance',
        requester: {
          id: '4',
          name: 'Ana Costa',
          email: 'ana.costa@empresa.com'
        },
        technician: {
          id: '5',
          name: 'Pedro Lima',
          email: 'pedro.lima@empresa.com'
        },
        createdAt: '2024-01-13T11:10:00Z',
        updatedAt: '2024-01-15T09:20:00Z',
        urgency: 3,
        impact: 3,
        tags: ['performance', 'hardware', 'vendas'],
        timeTracking: {
          totalTime: 120,
          entries: [
            {
              id: '1',
              duration: 60,
              description: 'Diagnóstico inicial',
              date: '2024-01-14T09:00:00Z',
              technician: 'Pedro Lima'
            },
            {
              id: '2',
              duration: 60,
              description: 'Limpeza e otimização',
              date: '2024-01-15T09:00:00Z',
              technician: 'Pedro Lima'
            }
          ]
        }
      },
      {
        id: '004',
        title: 'Backup do servidor de arquivos',
        description: 'Realizar backup completo do servidor de arquivos conforme procedimento mensal.',
        status: 'resolvido',
        priority: 'normal',
        category: 'Manutenção',
        requester: {
          id: '6',
          name: 'Sistema Automático',
          email: 'sistema@empresa.com'
        },
        technician: {
          id: '7',
          name: 'Roberto Silva',
          email: 'roberto.silva@empresa.com'
        },
        createdAt: '2024-01-12T02:00:00Z',
        updatedAt: '2024-01-12T06:30:00Z',
        urgency: 2,
        impact: 2,
        tags: ['backup', 'servidor', 'manutenção']
      }
    ];

    setTimeout(() => {
      setTickets(mockTickets);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'novo': return <Circle className="w-4 h-4 text-green-500" />;
      case 'pendente': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'progresso': return <Play className="w-4 h-4 text-blue-500" />;
      case 'resolvido': return <CheckCircle className="w-4 h-4 text-purple-500" />;
      case 'fechado': return <CheckCircle className="w-4 h-4 text-gray-500" />;
      default: return <Circle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgente': return 'border-l-red-500 bg-red-50';
      case 'alta': return 'border-l-orange-500 bg-orange-50';
      case 'normal': return 'border-l-blue-500 bg-blue-50';
      case 'baixa': return 'border-l-gray-500 bg-gray-50';
      default: return 'border-l-gray-500 bg-gray-50';
    }
  };

  const filteredTickets = tickets.filter(ticket => {
    if (filter === 'all') return true;
    return ticket.status === filter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Carregando tickets...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Todos ({tickets.length})
        </button>
        <button
          onClick={() => setFilter('novo')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'novo'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Novos ({tickets.filter(t => t.status === 'novo').length})
        </button>
        <button
          onClick={() => setFilter('pendente')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'pendente'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Pendentes ({tickets.filter(t => t.status === 'pendente').length})
        </button>
        <button
          onClick={() => setFilter('progresso')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'progresso'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Em Progresso ({tickets.filter(t => t.status === 'progresso').length})
        </button>
        <button
          onClick={() => setFilter('resolvido')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'resolvido'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Resolvidos ({tickets.filter(t => t.status === 'resolvido').length})
        </button>
      </div>

      {/* Ticket List */}
      <div className="space-y-4">
        {filteredTickets.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Nenhum ticket encontrado para o filtro selecionado.</p>
          </div>
        ) : (
          filteredTickets.map((ticket) => (
            <div
              key={ticket.id}
              onClick={() => onTicketClick(ticket)}
              className={`border-l-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer p-6 ${getPriorityColor(ticket.priority)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(ticket.status)}
                    <h3 className="font-semibold text-gray-900 text-lg">{ticket.title}</h3>
                    <span className="text-sm text-gray-500">#{ticket.id}</span>
                  </div>
                  
                  <p className="text-gray-600 mb-4 line-clamp-2">{ticket.description}</p>
                  
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      <span>{ticket.requester.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>{new Date(ticket.createdAt).toLocaleDateString('pt-BR')}</span>
                    </div>
                    <div className="bg-gray-100 px-2 py-1 rounded text-xs">
                      {ticket.category}
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    ticket.priority === 'urgente' ? 'bg-red-100 text-red-800' :
                    ticket.priority === 'alta' ? 'bg-orange-100 text-orange-800' :
                    ticket.priority === 'normal' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}
                  </span>
                  
                  {ticket.technician && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      {ticket.technician.avatar && (
                        <img
                          src={ticket.technician.avatar}
                          alt={ticket.technician.name}
                          className="w-6 h-6 rounded-full"
                        />
                      )}
                      <span>{ticket.technician.name}</span>
                    </div>
                  )}
                </div>
              </div>
              
              {ticket.tags && ticket.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {ticket.tags.slice(0, 3).map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {tag}
                    </span>
                  ))}
                  {ticket.tags.length > 3 && (
                    <span className="text-xs text-gray-500">+{ticket.tags.length - 3} mais</span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};