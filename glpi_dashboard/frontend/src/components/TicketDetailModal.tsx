import React from 'react';
import { Ticket } from '../types/ticket';
import { X, ExternalLink, Clock, User, Tag, Paperclip, MessageSquare } from 'lucide-react';
import { formatDate, getStatusColor } from '../lib/utils';
import { createCardClasses, createFlexClasses, TAILWIND_CLASSES } from '../design-system/utils';
import { cn } from '../lib/utils';

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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className={cn("bg-gradient-to-r from-blue-600 to-blue-700 text-white", TAILWIND_CLASSES.padding.section, createFlexClasses('row', 'start', 'between'))}>
          <div className="flex-1">
            <h2 className={cn("text-2xl font-bold pr-4", TAILWIND_CLASSES.margin.small)}>{ticket.title}</h2>
            <p className="text-blue-100 text-sm">Ticket #{ticket.id}</p>
          </div>
          <div className={createFlexClasses('row', 'center', 'start', 'normal')}>
            <button
              onClick={handleOpenInGLPI}
              className="flex items-center gap-2 bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all duration-200"
            >
              <ExternalLink size={16} />
              <span className="text-sm font-medium">Abrir no GLPI</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-all duration-200"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className={cn(TAILWIND_CLASSES.padding.section, "overflow-y-auto max-h-[calc(90vh-120px)]")}>
          <div className={cn("grid grid-cols-1 lg:grid-cols-3", TAILWIND_CLASSES.gap.section)}>
            {/* Main Content */}
            <div className={cn("lg:col-span-2", TAILWIND_CLASSES.spaceY.section)}>
              {/* Description */}
              <div className={createCardClasses()}>
                <h3 className={cn("font-semibold text-gray-900", TAILWIND_CLASSES.margin.small, createFlexClasses('row', 'center', 'start', 'small'))}>
                  <MessageSquare size={18} />
                  Descrição
                </h3>
                <p className="text-gray-700 leading-relaxed">{ticket.description}</p>
              </div>

              {/* Comments */}
              {ticket.comments && ticket.comments.length > 0 && (
                <div className={createCardClasses()}>
                  <h3 className={cn("font-semibold text-gray-900", TAILWIND_CLASSES.margin.element, createFlexClasses('row', 'center', 'start', 'small'))}>
                    <MessageSquare size={18} />
                    Comentários ({ticket.comments.length})
                  </h3>
                  <div className={cn(TAILWIND_CLASSES.spaceY.normal, "max-h-64 overflow-y-auto")}>
                    {ticket.comments.map((comment) => (
                      <div key={comment.id} className={cn("bg-white rounded-lg border border-gray-200", TAILWIND_CLASSES.padding.normal)}>
                        <div className={cn(createFlexClasses('row', 'center', 'start', 'small'), TAILWIND_CLASSES.margin.small)}>
                          {comment.author.avatar && (
                            <img
                              src={comment.author.avatar}
                              alt={comment.author.name}
                              className="w-6 h-6 rounded-full"
                            />
                          )}
                          <span className="font-medium text-sm text-gray-900">{comment.author.name}</span>
                          <span className="text-xs text-gray-500">
                            {formatDate(comment.createdAt, 'time')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">{comment.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Attachments */}
              {ticket.attachments && ticket.attachments.length > 0 && (
                <div className={createCardClasses()}>
                  <h3 className={cn("font-semibold text-gray-900", TAILWIND_CLASSES.margin.small, createFlexClasses('row', 'center', 'start', 'small'))}>
                    <Paperclip size={18} />
                    Anexos ({ticket.attachments.length})
                  </h3>
                  <div className={TAILWIND_CLASSES.spaceY.list}>
                    {ticket.attachments.map((attachment) => (
                      <a
                        key={attachment.id}
                        href={attachment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={cn(createFlexClasses('row', 'center', 'start', 'normal'), TAILWIND_CLASSES.padding.normal, "bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200")}
                      >
                        <Paperclip size={16} className="text-gray-500" />
                        <div className="flex-1">
                          <p className="font-medium text-sm text-gray-900">{attachment.name}</p>
                          <p className="text-xs text-gray-500">
                            {(attachment.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                        <ExternalLink size={14} className="text-gray-400" />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className={TAILWIND_CLASSES.spaceY.md}>
              {/* Status and Priority Section */}
              <div className={cn("bg-white border border-gray-200 rounded-lg", TAILWIND_CLASSES.padding.card)}>
                <h3 className={cn("font-semibold text-gray-900", TAILWIND_CLASSES.margin.element)}>Status e Prioridade</h3>
                <div className={TAILWIND_CLASSES.spaceY.normal}>
                  <div>
                    <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Status</label>
                    <span className={cn("inline-flex items-center text-sm font-medium", getStatusColor(ticket.status))}>
                      {ticket.status.charAt(0).toUpperCase() + ticket.status.slice(1)}
                    </span>
                  </div>
                  <div>
                    <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Prioridade</label>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(ticket.priority)}`}>
                      {ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}
                    </span>
                  </div>
                  <div>
                    <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Categoria</label>
                    <p className="text-sm text-gray-900">{ticket.category}</p>
                  </div>
                </div>
              </div>

              {/* People Involved Section */}
              <div className={cn("bg-white border border-gray-200 rounded-lg", TAILWIND_CLASSES.padding.card)}>
                <h3 className={cn("font-semibold text-gray-900", TAILWIND_CLASSES.margin.element, createFlexClasses('row', 'center', 'start', 'small'))}>
                  <User size={18} />
                  Pessoas Envolvidas
                </h3>
                <div className={TAILWIND_CLASSES.spaceY.card}>
                  <div>
                    <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.small)}>Solicitante</label>
                    <div className={createFlexClasses('row', 'center', 'start', 'normal')}>
                      {ticket.requester.avatar && (
                        <img
                          src={ticket.requester.avatar}
                          alt={ticket.requester.name}
                          className="w-8 h-8 rounded-full"
                        />
                      )}
                      <div>
                        <p className="font-medium text-sm text-gray-900">{ticket.requester.name}</p>
                        <p className="text-xs text-gray-500">{ticket.requester.email}</p>
                      </div>
                    </div>
                  </div>

                  {ticket.technician && (
                    <div>
                      <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.small)}>Técnico Responsável</label>
                      <div className={createFlexClasses('row', 'center', 'start', 'normal')}>
                        {ticket.technician.avatar && (
                          <img
                            src={ticket.technician.avatar}
                            alt={ticket.technician.name}
                            className="w-8 h-8 rounded-full"
                          />
                        )}
                        <div>
                          <p className="font-medium text-sm text-gray-900">{ticket.technician.name}</p>
                          <p className="text-xs text-gray-500">{ticket.technician.email}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {ticket.group && (
                    <div>
                      <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Grupo</label>
                      <p className="text-sm text-gray-900">{ticket.group.name}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Time Information */}
              <div className={cn("bg-white border border-gray-200 rounded-lg", TAILWIND_CLASSES.padding.card)}>
                <h3 className={cn("font-semibold text-gray-900", TAILWIND_CLASSES.margin.md, createFlexClasses('row', 'center', 'start', 'small'))}>
                  <Clock size={18} />
                  Informações de Tempo
                </h3>
                <div className={TAILWIND_CLASSES.spaceY.normal}>
                  <div>
                    <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Criado em</label>
                    <p className="text-sm text-gray-900">
                      {formatDate(ticket.createdAt, 'time')}
                    </p>
                  </div>
                  <div>
                    <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Última atualização</label>
                    <p className="text-sm text-gray-900">
                      {formatDate(ticket.updatedAt, 'time')}
                    </p>
                  </div>
                  {ticket.dueDate && (
                    <div>
                      <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Prazo</label>
                      <p className="text-sm text-gray-900">
                        {formatDate(ticket.dueDate, 'time')}
                      </p>
                    </div>
                  )}
                  {ticket.timeTracking && (
                    <div>
                      <label className={cn("text-sm font-medium text-gray-600 block", TAILWIND_CLASSES.margin.xs)}>Tempo Total</label>
                      <p className="text-sm text-gray-900">
                        {Math.floor(ticket.timeTracking.totalTime / 60)}h {ticket.timeTracking.totalTime % 60}m
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Tags */}
              {ticket.tags && ticket.tags.length > 0 && (
                <div className={cn("bg-white border border-gray-200 rounded-lg", TAILWIND_CLASSES.padding.card)}>
                  <h3 className={cn("font-semibold text-gray-900", TAILWIND_CLASSES.margin.small, createFlexClasses('row', 'center', 'start', 'small'))}>
                    <Tag size={18} />
                    Tags
                  </h3>
                  <div className={cn("flex flex-wrap", TAILWIND_CLASSES.gap.items)}>
                    {ticket.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
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
