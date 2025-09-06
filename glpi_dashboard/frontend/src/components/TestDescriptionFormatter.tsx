import React from 'react';
import { TicketDescriptionFormatter } from './TicketDescriptionFormatter';

export const TestDescriptionFormatter: React.FC = () => {
  const testDescription =
    'Dados do formulárioDados Gerais1) LOCALIZAÇÃO: Departamento de Recuperação - Defesa Civil2) RAMAL:: 519849326913) DESCRIÇÃO DO PEDIDO : Boa tarde, um dos notebook disponibilizados ao departamento está perdendo conexão com a rede. Aparentemente não seria uma situação de ausência de sinal de Internet, já que as informações normalmente fornecidas pela placa de rede não estão aparecendo. Outra questão é que quando a tampa é fechada ou o notebook fica sem uso, entra em hibernação e não volta.4) ARQUIVO:: Documento anexado';

  return (
    <div className='p-4 max-w-4xl mx-auto'>
      <h2 className='text-2xl font-bold mb-4'>Teste de Formatação de Descrição</h2>

      <div className='mb-6'>
        <h3 className='text-lg font-semibold mb-2'>Descrição Original:</h3>
        <div className='p-3 bg-gray-100 rounded border text-sm font-mono'>{testDescription}</div>
      </div>

      <div className='mb-6'>
        <h3 className='text-lg font-semibold mb-2'>Descrição Formatada:</h3>
        <div className='border rounded-lg p-4'>
          <TicketDescriptionFormatter description={testDescription} />
        </div>
      </div>
    </div>
  );
};
