import React from 'react';
import { Ticket } from '../types/ticket';
import { X, ExternalLink, Clock, User, Tag, Paperclip, MessageSquare, Phone } from 'lucide-react';
import { formatDate, getStatusColor } from '../lib/utils';
import { createCardClasses, createFlexClasses, TAILWIND_CLASSES } from '../design-system/utils';
import { cn } from '../lib/utils';
import { TicketDescriptionFormatter } from './TicketDescriptionFormatter';

// Função para formatar a descrição estruturada (mantida para compatibilidade)
const formatDescription = (description: string): JSX.Element => {
  return <TicketDescriptionFormatter description={description} />;
};

interface TicketDetailModalProps {
  ticket: Ticket | null;
  isOpen: boolean;
  onClose: () => void;
}


export const TicketDetailModal: React.FC<TicketDetailModalProps> = ({
  ticket,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !ticket) return null;

  // Ajuste para classes semânticas de prioridade (definidas em App.css)
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgente': return 'priority-urgente';
      case 'alta': return 'priority-alta';
      case 'normal': return 'priority-normal';
      case 'baixa': return 'priority-baixa';
      default: return 'priority-normal';
    }
  };

  const handleOpenInGLPI = () => {
    // Implementar abertura no GLPI
    window.open(`/glpi/front/ticket.form.php?id=${ticket.id}`, '_blank');
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col border border-gray-200 dark:border-gray-700">
        {/* Header Profissional */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700">
                  <MessageSquare className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white truncate">
                    {ticket.title}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Ticket #{ticket.id}</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 ml-4">
              <button
                onClick={handleOpenInGLPI}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 hover:border-gray-400 dark:hover:border-gray-500 transition-colors duration-150"
              >
                <ExternalLink className="h-4 w-4" />
                Abrir no GLPI
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-200 transition-colors p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 border border-transparent hover:border-gray-200 dark:hover:border-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-4">
              {/* Phone/Ramal */}
              {ticket.phone && (
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Phone className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Ramal/Telefone</h3>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 font-medium">{ticket.phone}</p>
                </div>
              )}

              {/* Description */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Descrição</h3>
                </div>
                <div className="text-gray-700 dark:text-gray-300">
                  {formatDescription(ticket.description)}
                </div>
              </div>

              {/* Comments */}
              {ticket.comments && ticket.comments.length > 0 && (
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <MessageSquare className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Comentários ({ticket.comments.length})</h3>
                  </div>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {ticket.comments.map((comment) => (
                      <div key={comment.id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          {comment.author.avatar && (
                            <img
                              src={comment.author.avatar}
                              alt={comment.author.name}
                              className="w-6 h-6 rounded-full"
                            />
                          )}
                          <span className="font-medium text-sm text-gray-900 dark:text-white">{comment.author.name}</span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {formatDate(comment.createdAt, 'time')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300">{comment.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Attachments */}
              {ticket.attachments && ticket.attachments.length > 0 && (
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Paperclip className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Anexos ({ticket.attachments.length})</h3>
                  </div>
                  <div className="space-y-2">
                    {ticket.attachments.map((attachment) => (
                      <a
                        key={attachment.id}
                        href={attachment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-150"
                      >
                        <Paperclip className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm text-gray-900 dark:text-white truncate">{attachment.name}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {(attachment.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                        <ExternalLink className="h-4 w-4 text-gray-400 dark:text-gray-500" />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-4">
              {/* Status and Priority Section */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-3">Status e Prioridade</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Status</label>
                    <span className={cn("inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border", getStatusColor(ticket.status))}>
                      {ticket.status.charAt(0).toUpperCase() + ticket.status.slice(1)}
                    </span>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Prioridade</label>
                    <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${getPriorityColor(ticket.priority)}`}>
                      {ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}
                    </span>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Categoria</label>
                    <p className="text-sm text-gray-900 dark:text-white">{ticket.category}</p>
                  </div>
                </div>
              </div>

              {/* People Involved Section */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <User className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Pessoas Envolvidas</h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-2">Solicitante</label>
                    <div className="flex items-center gap-3">
                      {ticket.requester.avatar && (
                        <img
                          src={ticket.requester.avatar}
                          alt={ticket.requester.name}
                          className="w-8 h-8 rounded-full"
                        />
                      )}
                      <div>
                        <p className="font-medium text-sm text-gray-900 dark:text-white">{ticket.requester.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{ticket.requester.email}</p>
                      </div>
                    </div>
                  </div>

                  {ticket.technician && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-2">Técnico Responsável</label>
                      <div className="flex items-center gap-3">
                        {ticket.technician.avatar && (
                          <img
                            src={ticket.technician.avatar}
                            alt={ticket.technician.name}
                            className="w-8 h-8 rounded-full"
                          />
                        )}
                        <div>
                        <p className="font-medium text-sm text-gray-900 dark:text-white">{ticket.technician.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{ticket.technician.email}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Grupo</label>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {ticket.group?.name || "Não atribuído"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Time Information */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Clock className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Informações de Tempo</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Criado em</label>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {formatDate(ticket.createdAt, 'time')}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Última atualização</label>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {formatDate(ticket.updatedAt, 'time')}
                    </p>
                  </div>
                  {ticket.dueDate && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Prazo</label>
                      <p className="text-sm text-gray-900 dark:text-white">
                        {formatDate(ticket.dueDate, 'time')}
                      </p>
                    </div>
                  )}
                  {ticket.timeTracking && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide block mb-1">Tempo Total</label>
                      <p className="text-sm text-gray-900 dark:text-white">
                        {Math.floor(ticket.timeTracking.totalTime / 60)}h {ticket.timeTracking.totalTime % 60}m
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Tags */}
              {ticket.tags && ticket.tags.length > 0 && (
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Tag className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Tags</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {ticket.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
