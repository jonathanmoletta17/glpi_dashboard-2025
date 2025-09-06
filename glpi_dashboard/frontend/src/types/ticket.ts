export interface Ticket {
  id: string;
  title: string;
  description: string;
  phone?: string;  // Campo para ramal/telefone
  status: 'novo' | 'pendente' | 'progresso' | 'resolvido' | 'fechado';
  priority: 'baixa' | 'normal' | 'alta' | 'urgente';
  category: string;
  requester: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  technician?: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  group?: {
    id: string;
    name: string;
  };
  createdAt: string;
  updatedAt: string;
  dueDate?: string;
  location?: string;
  urgency: number;
  impact: number;
  tags?: string[];
  attachments?: {
    id: string;
    name: string;
    url: string;
    size: number;
  }[];
  comments?: {
    id: string;
    content: string;
    author: {
      id: string;
      name: string;
      avatar?: string;
    };
    createdAt: string;
  }[];
  timeTracking?: {
    totalTime: number;
    entries: {
      id: string;
      duration: number;
      description: string;
      date: string;
      technician: string;
    }[];
  };
}

export interface TicketFilters {
  status?: string[];
  priority?: string[];
  category?: string[];
  technician?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface TicketMetrics {
  total: number;
  novos: number;
  pendentes: number;
  progresso: number;
  resolvidos: number;
  fechados: number;
}
