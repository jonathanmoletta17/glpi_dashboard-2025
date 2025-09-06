import React from 'react';

interface TicketDescriptionFormatterProps {
  description: string;
  className?: string;
}

export const TicketDescriptionFormatter: React.FC<TicketDescriptionFormatterProps> = ({
  description,
  className = ''
}) => {
  // Verificação básica de entrada
  
  if (!description) {
    return (
      <div className={`text-gray-500 italic ${className}`}>
        Nenhuma descrição disponível
      </div>
    );
  }

  // Remove HTML tags e entidades HTML
  const cleanDescription = description
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim();

  // Verifica se é uma descrição estruturada - mais permissivo
  const hasStructuredFields = /(LOCALIZAÇÃO|RAMAL|DESCRIÇÃO|DESCR|Dados do formulário|Dados Gerais|ARQUIVO)/i.test(cleanDescription);

  if (hasStructuredFields) {
    return <StructuredDescription description={cleanDescription} className={className} />;
  }

  // Descrição não estruturada - sempre mostrar o texto
  return (
    <div className={`whitespace-pre-wrap text-gray-700 leading-relaxed p-4 bg-gray-50 rounded-lg border border-gray-200 ${className}`}>
      {cleanDescription}
    </div>
  );
};

const StructuredDescription: React.FC<{ description: string; className: string }> = ({
  description,
  className
}) => {
  const processField = (fieldName: string, content: string) => {
    if (!fieldName || !content.trim()) return null;

    const getFieldIcon = (field: string) => {
      switch (field.toUpperCase()) {
        case 'LOCALIZAÇÃO': return '📍';
        case 'RAMAL': return '📞';
        case 'DESCRIÇÃO':
        case 'DESCR': return '📝';
        case 'ARQUIVO': return '📎';
        default: return '📋';
      }
    };

    const getFieldColor = (field: string) => {
      switch (field.toUpperCase()) {
        case 'LOCALIZAÇÃO': return 'border-blue-500 bg-blue-50';
        case 'RAMAL': return 'border-green-500 bg-green-50';
        case 'DESCRIÇÃO':
        case 'DESCR': return 'border-purple-500 bg-purple-50';
        case 'ARQUIVO': return 'border-orange-500 bg-orange-50';
        default: return 'border-gray-500 bg-gray-50';
      }
    };

    return (
      <div 
        key={`field-${fieldName}`}
        className={`mb-4 p-4 rounded-lg border-l-4 ${getFieldColor(fieldName)}`}
      >
        <div className="flex items-center mb-3">
          <span className="text-lg mr-3">{getFieldIcon(fieldName)}</span>
          <span className="font-semibold text-gray-800 text-sm uppercase tracking-wide">
            {fieldName}:
          </span>
        </div>
        <div className="text-gray-700 ml-8 leading-relaxed text-sm">
          {content.trim()}
        </div>
      </div>
    );
  };

  // Tentar extrair campos usando regex mais simples e robusto
  const fields: { [key: string]: string } = {};
  
  // Padrões específicos para o formato encontrado
  const patterns = [
    { name: 'LOCALIZAÇÃO', regex: /1\)\s*LOCALIZAÇÃO\s*:?\s*([^2-9]+?)(?=2\)|$)/i },
    { name: 'RAMAL', regex: /2\)\s*RAMAL\s*:?\s*:?\s*([^3-9]+?)(?=3\)|$)/i },
    { name: 'DESCRIÇÃO', regex: /3\)\s*DESCR[IÇ]?[ÃA]?O?\s*DO\s*PEDIDO\s*:?\s*([^4-9]+?)(?=4\)|$)/i },
    { name: 'ARQUIVO', regex: /4\)\s*ARQUIVO\s*:?\s*:?\s*([^1-9]+?)(?=$)/i }
  ];

  // Tentar extrair cada campo
  patterns.forEach(({ name, regex }) => {
    const match = description.match(regex);
    if (match && match[1]) {
      let content = match[1].trim();
      content = content.replace(/\s+/g, ' ').trim();
      if (content && content !== '') {
        fields[name] = content;
      }
    }
  });

  // Se não encontrou com padrões numerados, tentar padrões sem números
  if (Object.keys(fields).length === 0) {
    const fallbackPatterns = [
      { name: 'LOCALIZAÇÃO', regex: /LOCALIZAÇÃO\s*:?\s*([^2-9]+?)(?=\d+\)|RAMAL|DESCR|ARQUIVO|$)/i },
      { name: 'RAMAL', regex: /RAMAL\s*:?\s*:?\s*([^3-9]+?)(?=\d+\)|DESCR|ARQUIVO|$)/i },
      { name: 'DESCRIÇÃO', regex: /DESCR[IÇ]?[ÃA]?O?\s*DO\s*PEDIDO\s*:?\s*([^4-9]+?)(?=\d+\)|ARQUIVO|$)/i },
      { name: 'ARQUIVO', regex: /ARQUIVO\s*:?\s*:?\s*([^1-9]+?)(?=\d+\)|$)/i }
    ];

    fallbackPatterns.forEach(({ name, regex }) => {
      const match = description.match(regex);
      if (match && match[1]) {
        let content = match[1].trim();
        content = content.replace(/\s+/g, ' ').trim();
        if (content && content !== '') {
          fields[name] = content;
        }
      }
    });
  }

  // Se encontrou pelo menos um campo estruturado, mostrar formatado
  if (Object.keys(fields).length > 0) {
    return (
      <div className={`space-y-3 ${className}`}>
        {Object.entries(fields).map(([fieldName, content]) => 
          processField(fieldName, content)
        )}
      </div>
    );
  }

  // Se não encontrou campos estruturados, mostrar como texto normal
  return (
    <div className={`whitespace-pre-wrap text-gray-700 leading-relaxed p-4 bg-gray-50 rounded-lg border border-gray-200 ${className}`}>
      {description}
    </div>
  );
};
