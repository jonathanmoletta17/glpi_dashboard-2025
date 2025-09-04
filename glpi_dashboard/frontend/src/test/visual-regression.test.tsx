import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { LevelsSection } from '../components/LevelsSection';
import { MetricsData } from '../types';

// Mock data para testes
const mockMetrics: MetricsData = {
  niveis: {
    n1: { novos: 10, progresso: 5, pendentes: 3, resolvidos: 25 },
    n2: { novos: 8, progresso: 12, pendentes: 7, resolvidos: 30 },
    n3: { novos: 15, progresso: 8, pendentes: 5, resolvidos: 20 },
    n4: { novos: 5, progresso: 3, pendentes: 2, resolvidos: 15 }
  },
  novos: 38,
  progresso: 28,
  pendentes: 17,
  resolvidos: 90,
  total: 173
};

describe('Visual Regression Tests - CSS Migration', () => {
  beforeEach(() => {
    // Limpar qualquer estado anterior
    document.head.innerHTML = '';
  });

  describe('LevelsSection - Classes CSS Legacy', () => {
    it('deve renderizar corretamente com classes atuais (baseline)', () => {
      render(<LevelsSection metrics={mockMetrics} />);
      
      // Verificar se os elementos principais estão presentes
      expect(screen.getByText('Níveis de Atendimento')).toBeInTheDocument();
      expect(screen.getByText('Nível 1')).toBeInTheDocument();
      expect(screen.getByText('Nível 2')).toBeInTheDocument();
      expect(screen.getByText('Nível 3')).toBeInTheDocument();
      expect(screen.getByText('Nível 4')).toBeInTheDocument();
      
      // Verificar métricas específicas
      expect(screen.getByText('10')).toBeInTheDocument(); // Novos N1
      expect(screen.getByText('25')).toBeInTheDocument(); // Resolvidos N1
      
      // Verificar taxa de resolução calculada
      expect(screen.getByText('58% Resolução')).toBeInTheDocument(); // N1: 25/43 = 58%
    });

    it('deve manter estrutura DOM após migração', () => {
      const { container } = render(<LevelsSection metrics={mockMetrics} />);
      
      // Verificar estrutura de grid com classes Tailwind CSS
      const gridContainer = container.querySelector('.grid.grid-cols-12');
      expect(gridContainer).toBeInTheDocument();

      // Verificar cards de nível (agora usando Shadcn Card)
      const levelCards = container.querySelectorAll('.grid.grid-cols-2');
      expect(levelCards).toHaveLength(4);
      
      // Verificar barras de progresso (agora usando classes Tailwind CSS)
      const progressBars = container.querySelectorAll('.bg-green-500');
      expect(progressBars).toHaveLength(4);
    });

    it('deve preservar funcionalidade de cálculo de taxa de resolução', () => {
      render(<LevelsSection metrics={mockMetrics} />);
      
      // Verificar cálculos corretos para cada nível
      expect(screen.getByText('58% Resolução')).toBeInTheDocument(); // N1: 25/(10+5+3+25) = 58%
      expect(screen.getByText('53% Resolução')).toBeInTheDocument(); // N2: 30/(8+12+7+30) = 53%
      expect(screen.getByText('42% Resolução')).toBeInTheDocument(); // N3: 20/(15+8+5+20) = 42%
      expect(screen.getByText('60% Resolução')).toBeInTheDocument(); // N4: 15/(5+3+2+15) = 60%
    });

    it('deve aplicar classes de status corretamente', () => {
      const { container } = render(<LevelsSection metrics={mockMetrics} />);
      
      // Verificar elementos de status por classes Tailwind CSS
      const statusElements = {
        new: container.querySelectorAll('.text-blue-600'),
        progress: container.querySelectorAll('.text-yellow-600'),
        pending: container.querySelectorAll('.text-orange-600'),
        resolved: container.querySelectorAll('.text-green-600')
      };
      
      // Cada nível deve ter elementos com cada status
      expect(statusElements.new.length).toBeGreaterThan(0);
      expect(statusElements.progress.length).toBeGreaterThan(0);
      expect(statusElements.pending.length).toBeGreaterThan(0);
      expect(statusElements.resolved.length).toBeGreaterThan(0);
    });
  });

  describe('Compatibilidade com Shadcn UI', () => {
    it('deve usar componentes Card do Shadcn UI', () => {
      // Verificar se a migração para Shadcn Card foi bem-sucedida
      const { container } = render(<LevelsSection metrics={mockMetrics} />);
      
      // Verificar que os componentes Shadcn Card estão sendo usados
      const cards = container.querySelectorAll('[data-testid="card"], .border.rounded-lg, .bg-card');
      expect(cards.length).toBeGreaterThan(0);
      
      // Cada card deve ter estrutura de grid para métricas
      const metricsGrids = container.querySelectorAll('.grid.grid-cols-2');
      expect(metricsGrids).toHaveLength(4);
      
      // Cada card deve ter barra de progresso
      const progressBars = container.querySelectorAll('.bg-gray-200.rounded-full');
      expect(progressBars).toHaveLength(4);
    });
  });

  describe('Responsividade', () => {
    it('deve manter classes responsivas após migração', () => {
      const { container } = render(<LevelsSection metrics={mockMetrics} />);
      
      // Verificar classes de grid responsivo
      const responsiveElements = container.querySelectorAll('[class*="md:col-span"]');
      expect(responsiveElements.length).toBeGreaterThan(0);
      
      const lgElements = container.querySelectorAll('[class*="lg:col-span"]');
      expect(lgElements.length).toBeGreaterThan(0);
    });
  });
});