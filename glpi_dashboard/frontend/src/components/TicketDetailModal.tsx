import React from 'react';
import { Ticket } from '../types/ticket';
import { X, ExternalLink, Clock, User, Tag, Paperclip, MessageSquare } from 'lucide-react';
import { formatDate } from '../lib/utils';

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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgente': return 'bg-red-500 text-white';
      case 'alta': return 'bg-orange-500 text-white';
      case 'normal': return 'bg-blue-500 text-white';
      case 'baixa': return 'bg-gray-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'novo': return 'bg-green-100 text-green-800 border-green-200';
      case 'pendente': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'progresso': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'resolvido': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'fechado': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
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
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 flex justify-between items-start">
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-2 pr-4">{ticket.title}</h2>
            <p className="text-blue-100 text-sm">Ticket #{ticket.id}</p>
          </div>
          <div className="flex items-center gap-3">
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
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Description */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <MessageSquare size={18} />
                  Descrição
                </h3>
                <p className="text-gray-700 leading-relaxed">{ticket.description}</p>
              </div>

              {/* Comments */}
              {ticket.comments && ticket.comments.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <MessageSquare size={18} />
                    Comentários ({ticket.comments.length})
                  </h3>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {ticket.comments.map((comment) => (
                      <div key={comment.id} className="bg-white rounded-lg p-3 border border-gray-200">
                        <div className="flex items-center gap-2 mb-2">
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
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Paperclip size={18} />
                    Anexos ({ticket.attachments.length})
                  </h3>
                  <div className="space-y-2">
                    {ticket.attachments.map((attachment) => (
                      <a
                        key={attachment.id}
                        href={attachment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
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
            <div className="space-y-4">
              {/* Status and Priority Section */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-4">Status e Prioridade</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-600 block mb-1">Status</label>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(ticket.status)}`}>
                      {ticket.status.charAt(0).toUpperCase() + ticket.status.slice(1)}
                    </span>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600 block mb-1">Prioridade</label>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(ticket.priority)}`}>
                      {ticket.priority.charAt(0).toUpperCase() + ticket.priority.slice(1)}
                    </span>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600 block mb-1">Categoria</label>
                    <p className="text-sm text-gray-900">{ticket.category}</p>
                  </div>
                </div>
              </div>

              {/* People Involved Section */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <User size={18} />
                  Pessoas Envolvidas
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600 block mb-2">Solicitante</label>
                    <div className="flex items-center gap-3">
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
                      <label className="text-sm font-medium text-gray-600 block mb-2">Técnico Responsável</label>
                      <div className="flex items-center gap-3">
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
                      <label className="text-sm font-medium text-gray-600 block mb-1">Grupo</label>
                      <p className="text-sm text-gray-900">{ticket.group.name}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Time Information */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Clock size={18} />
                  Informações de Tempo
                </h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-600 block mb-1">Criado em</label>
                    <p className="text-sm text-gray-900">
                      {formatDate(ticket.createdAt, 'time')}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600 block mb-1">Última atualização</label>
                    <p className="text-sm text-gray-900">
                      {formatDate(ticket.updatedAt, 'time')}
                    </p>
                  </div>
                  {ticket.dueDate && (
                    <div>
                      <label className="text-sm font-medium text-gray-600 block mb-1">Prazo</label>
                      <p className="text-sm text-gray-900">
                        {formatDate(ticket.dueDate, 'time')}
                      </p>
                    </div>
                  )}
                  {ticket.timeTracking && (
                    <div>
                      <label className="text-sm font-medium text-gray-600 block mb-1">Tempo Total</label>
                      <p className="text-sm text-gray-900">
                        {Math.floor(ticket.timeTracking.totalTime / 60)}h {ticket.timeTracking.totalTime % 60}m
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Tags */}
              {ticket.tags && ticket.tags.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Tag size={18} />
                    Tags
                  </h3>
                  <div className="flex flex-wrap gap-2">
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
