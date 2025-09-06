import React from 'react';
import { TicketList } from './TicketList';
import { Ticket } from '../types/ticket';

interface TicketsPageProps {
  onTicketClick: (ticket: Ticket) => void;
}

export const TicketsPage: React.FC<TicketsPageProps> = ({ onTicketClick }) => {
  return (
    <div className='p-6'>
      <div className='mb-6'>
        <h1 className='text-2xl font-bold text-gray-900 mb-2'>Tickets</h1>
        <p className='text-gray-600'>Gerencie e visualize todos os tickets do sistema</p>
      </div>

      <TicketList onTicketClick={onTicketClick} />
    </div>
  );
};
