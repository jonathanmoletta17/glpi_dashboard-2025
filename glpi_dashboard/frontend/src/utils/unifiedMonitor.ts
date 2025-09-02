/**
 * Sistema Unificado de Monitoramento
 * 
 * Consolida todas as funcionalidades de monitoramento em um único sistema
 * para eliminar duplicações e melhorar a eficiência.
 */

import { DashboardMetrics } from '../types/api';
import { SystemStatus, TechnicianRanking } from '../types';
import { httpClient } from '../services/httpClient';

// Interfaces consolidadas
export interface UnifiedMonitoringConfig {
  enabled: boolean;
  checkInterval: number;
  retryAttempts: number;
  retryDelay: number;
  thresholds: {
    responseTime: number;
    zeroMetricsThreshold: number;
    performanceGrade: {
      excellent: number;
      good: number;
      acceptable: number;
    };
  };
  features: {
    realTimeMonitoring: boolean;
    dataIntegrity: boolean;
    visualValidation: boolean;
    performanceTracking: boolean;
    preDeliveryValidation: boolean;
  };
}

export interface MonitoringAlert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  category: 'metrics' | 'api' | 'visual' | 'performance' | 'integrity';
  title: string;
  message: string;
  timestamp: string;
  source: string;
  data?: any;
  resolved: boolean;
  resolvedAt?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  score: number; // 0-100
  details?: any;
  timestamp: string;
}

export interface PerformanceMetrics {
  responseTime: number;
  renderTime: number;
  apiCallDuration: number;
  totalOperationTime: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
}

export interface MonitoringReport {
  overallStatus: 'healthy' | 'warning' | 'critical';
  timestamp: string;
  validationResults: {
    dataIntegrity: ValidationResult;
    visualRendering: ValidationResult;
    apiConnectivity: ValidationResult;
    performance: ValidationResult;
  };
  alerts: MonitoringAlert[];
  metrics: {
    uptime: number;
    totalChecks: number;
    successRate: number;
    averageResponseTime: number;
  };
  recommendations: string[];
}

class UnifiedMonitor {
  private config: UnifiedMonitoringConfig;
  private monitoringInterval: NodeJS.Timeout | null = null;
  private alerts: MonitoringAlert[] = [];
  private alertCounter = 0;
  private checksHistory: ValidationResult[] = [];
  private performanceMetrics: Map<string, number[]> = new Map();
  private listeners: ((report: MonitoringReport) => void)[] = [];

  constructor(config?: Partial<UnifiedMonitoringConfig>) {
    this.config = {
      enabled: true,
      checkInterval: 30000, // 30 segundos
      retryAttempts: 3,
      retryDelay: 1000,
      thresholds: {
        responseTime: 5000,
        zeroMetricsThreshold: 10000,
        performanceGrade: {
          excellent: 1000,
          good: 3000,
          acceptable: 5000,
        },
      },
      features: {
        realTimeMonitoring: true,
        dataIntegrity: true,
        visualValidation: true,
        performanceTracking: true,
        preDeliveryValidation: true,
      },
      ...config,
    };
  }

  /**
   * Inicia o monitoramento unificado
   */
  startMonitoring(): void {
    if (this.monitoringInterval) {
      console.log('⚠️ Monitoramento unificado já está ativo');
      return;
    }

    if (!this.config.enabled) {
      console.log('⏸️ Monitoramento desabilitado na configuração');
      return;
    }

    console.log('🔄 Iniciando monitoramento unificado...');

    this.monitoringInterval = setInterval(async () => {
      try {
        const report = await this.runCompleteCheck();
        this.processReport(report);
        this.notifyListeners(report);
      } catch (error) {
        console.error('💥 Erro durante monitoramento unificado:', error);
        this.createAlert({
          type: 'critical',
          category: 'api',
          title: 'Erro no Monitoramento',
          message: `Falha durante execução: ${error}`,
          source: 'UnifiedMonitor',
          severity: 'critical',
        });
      }
    }, this.config.checkInterval);

    // Executar primeira verificação imediatamente
    setTimeout(() => {
      this.runCompleteCheck().then(report => {
        this.processReport(report);
        this.notifyListeners(report);
      });
    }, 1000);
  }

  /**
   * Para o monitoramento
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      console.log('⏹️ Monitoramento unificado parado');
    }
  }

  /**
   * Executa verificação completa de todos os sistemas
   */
  async runCompleteCheck(): Promise<MonitoringReport> {
    const timestamp = new Date().toISOString();
    const validationResults = {
      dataIntegrity: await this.validateDataIntegrity(),
      visualRendering: await this.validateVisualRendering(),
      apiConnectivity: await this.validateApiConnectivity(),
      performance: await this.validatePerformance(),
    };

    // Calcular status geral
    const criticalIssues = Object.values(validationResults).filter(
      result => !result.isValid && result.errors.some(error => error.includes('critical'))
    );
    const warnings = Object.values(validationResults).filter(
      result => !result.isValid && result.warnings.length > 0
    );

    let overallStatus: MonitoringReport['overallStatus'] = 'healthy';
    if (criticalIssues.length > 0) {
      overallStatus = 'critical';
    } else if (warnings.length > 0) {
      overallStatus = 'warning';
    }

    // Gerar recomendações
    const recommendations = this.generateRecommendations(validationResults);

    // Calcular métricas
    const metrics = this.calculateMetrics();

    return {
      overallStatus,
      timestamp,
      validationResults,
      alerts: this.getActiveAlerts(),
      metrics,
      recommendations,
    };
  }

  /**
   * Validação de integridade de dados
   */
  private async validateDataIntegrity(): Promise<ValidationResult> {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      score: 100,
      timestamp: new Date().toISOString(),
    };

    try {
      // Verificar conectividade da API
      const apiCheck = await this.checkApiConnectivity();
      if (!apiCheck.success) {
        result.isValid = false;
        result.errors.push('API não está respondendo');
        result.score -= 30;
      }

      // Verificar estrutura de dados
      const dataStructure = await this.checkDataStructure();
      if (!dataStructure.success) {
        result.isValid = false;
        result.errors.push('Estrutura de dados inválida');
        result.score -= 25;
      }

      // Verificar métricas zeradas
      const zeroMetrics = await this.checkZeroMetrics();
      if (!zeroMetrics.success) {
        result.warnings.push('Métricas zeradas detectadas');
        result.score -= 15;
      }

    } catch (error) {
      result.isValid = false;
      result.errors.push(`Erro na validação de integridade: ${error}`);
      result.score = 0;
    }

    return result;
  }

  /**
   * Validação de renderização visual
   */
  private async validateVisualRendering(): Promise<ValidationResult> {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      score: 100,
      timestamp: new Date().toISOString(),
    };

    try {
      // Implementar fallback com retry para elementos DOM
      let domElements = this.checkDOMElements();
      
      if (!domElements.success) {
        console.log('🔄 UnifiedMonitor: Elementos DOM não encontrados, tentando novamente após delay...');
        
        // Aguardar um pouco para elementos serem renderizados
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        domElements = this.checkDOMElements();
        
        if (!domElements.success) {
          result.isValid = false;
          result.errors.push('Elementos DOM essenciais não encontrados após retry');
          result.warnings.push('Considere verificar se os componentes estão sendo renderizados corretamente');
          result.score -= 40;
        } else {
          result.warnings.push('Elementos DOM encontrados após retry - possível problema de timing');
          result.score -= 10;
        }
      }

      // Verificar renderização de métricas
      const metricsRendering = this.checkMetricsRendering();
      if (!metricsRendering.success) {
        result.warnings.push('Problemas na renderização de métricas');
        result.warnings.push('Verifique se os dados estão sendo carregados corretamente');
        result.score -= 20;
      }

    } catch (error) {
      result.isValid = false;
      result.errors.push(`Erro na validação visual: ${error}`);
      result.score = 0;
    }

    return result;
  }

  /**
   * Validação de conectividade da API
   */
  private async validateApiConnectivity(): Promise<ValidationResult> {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      score: 100,
      timestamp: new Date().toISOString(),
    };

    try {
      const startTime = Date.now();
      const response = await fetch('/api/health');
      const responseTime = Date.now() - startTime;

      if (!response.ok) {
        result.isValid = false;
        result.errors.push(`API retornou status ${response.status}`);
        result.score -= 50;
      }

      if (responseTime > this.config.thresholds.responseTime) {
        result.warnings.push(`Tempo de resposta alto: ${responseTime}ms`);
        result.score -= 20;
      }

      this.recordPerformanceMetric('apiResponseTime', responseTime);

    } catch (error) {
      result.isValid = false;
      result.errors.push(`Erro de conectividade: ${error}`);
      result.score = 0;
    }

    return result;
  }

  /**
   * Validação de performance
   */
  private async validatePerformance(): Promise<ValidationResult> {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      score: 100,
      timestamp: new Date().toISOString(),
    };

    try {
      const performanceData = this.getPerformanceData();
      
      if (performanceData.averageResponseTime > this.config.thresholds.performanceGrade.acceptable) {
        result.warnings.push('Performance abaixo do aceitável');
        result.score -= 30;
      }

      if (performanceData.grade === 'F') {
        result.isValid = false;
        result.errors.push('Performance crítica detectada');
        result.score -= 50;
      }

      result.details = performanceData;

    } catch (error) {
      result.isValid = false;
      result.errors.push(`Erro na validação de performance: ${error}`);
      result.score = 0;
    }

    return result;
  }

  /**
   * Métodos auxiliares de verificação
   */
  private async checkApiConnectivity(): Promise<{ success: boolean; data?: any }> {
    const maxRetries = this.config.retryAttempts;
    const retryDelay = this.config.retryDelay;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`🔄 UnifiedMonitor: Tentativa ${attempt}/${maxRetries} de conectividade API`);
        const response = await httpClient.get('/metrics');
        console.log(`✅ UnifiedMonitor: API conectada com sucesso na tentativa ${attempt}`);
        return { success: response.data.success, data: response.data };
      } catch (error) {
        console.warn(`❌ UnifiedMonitor: Falha na tentativa ${attempt}/${maxRetries}:`, error);
        
        if (attempt < maxRetries) {
          console.log(`⏳ UnifiedMonitor: Aguardando ${retryDelay}ms antes da próxima tentativa...`);
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
      }
    }
    
    console.error(`❌ UnifiedMonitor: Todas as ${maxRetries} tentativas de conectividade API falharam`);
    return { success: false };
  }

  private async checkDataStructure(): Promise<{ success: boolean }> {
    try {
      const { success, data } = await this.checkApiConnectivity();
      if (!success || !data) return { success: false };

      const requiredFields = ['novos', 'pendentes', 'progresso', 'resolvidos', 'niveis'];
      const hasAllFields = requiredFields.every(field => data.data && typeof data.data[field] !== 'undefined');
      
      return { success: hasAllFields };
    } catch {
      return { success: false };
    }
  }

  private async checkZeroMetrics(): Promise<{ success: boolean }> {
    try {
      const { success, data } = await this.checkApiConnectivity();
      if (!success || !data) return { success: false };

      const metrics = data.data;
      const totalMetrics = metrics.novos + metrics.pendentes + metrics.progresso + metrics.resolvidos;
      
      return { success: totalMetrics > 0 };
    } catch {
      return { success: false };
    }
  }

  private checkDOMElements(): { success: boolean } {
    const essentialElements = [
      '.metrics-grid',
      '.technician-ranking',
      '.dashboard-header'
    ];

    const missingElements: string[] = [];
    const foundElements: string[] = [];

    essentialElements.forEach(selector => {
      const element = document.querySelector(selector);
      if (element) {
        foundElements.push(selector);
        console.log(`✅ UnifiedMonitor: Elemento encontrado: ${selector}`);
      } else {
        missingElements.push(selector);
        console.warn(`❌ UnifiedMonitor: Elemento não encontrado: ${selector}`);
      }
    });

    const allElementsPresent = missingElements.length === 0;
    
    if (allElementsPresent) {
      console.log('✅ UnifiedMonitor: Todos os elementos DOM essenciais foram encontrados');
    } else {
      console.error(`❌ UnifiedMonitor: ${missingElements.length} elemento(s) DOM essencial(is) não encontrado(s):`, missingElements);
    }

    return { success: allElementsPresent };
  }

  private checkMetricsRendering(): { success: boolean } {
    const metricsElements = document.querySelectorAll('[data-metric]');
    const hasMetrics = metricsElements.length > 0;
    
    console.log(`🔍 UnifiedMonitor: Encontrados ${metricsElements.length} elementos com [data-metric]`);
    
    if (!hasMetrics) {
      console.warn('❌ UnifiedMonitor: Nenhum elemento com [data-metric] encontrado');
      return { success: false };
    }
    
    // Verificar se há valores não zerados sendo exibidos
    const nonZeroElements: string[] = [];
    const zeroElements: string[] = [];
    
    Array.from(metricsElements).forEach((element, index) => {
      const value = parseInt(element.textContent || '0');
      const metricName = element.getAttribute('data-metric') || `metric-${index}`;
      
      if (value > 0) {
        nonZeroElements.push(`${metricName}: ${value}`);
      } else {
        zeroElements.push(`${metricName}: ${value}`);
      }
    });
    
    const hasNonZeroValues = nonZeroElements.length > 0;
    
    if (hasNonZeroValues) {
      console.log(`✅ UnifiedMonitor: ${nonZeroElements.length} métricas com valores não-zero:`, nonZeroElements);
    } else {
      console.warn(`❌ UnifiedMonitor: Todas as ${zeroElements.length} métricas têm valor zero:`, zeroElements);
    }

    return { success: hasMetrics && hasNonZeroValues };
  }

  recordPerformanceMetric(name: string, value: number, metadata?: any): void {
    if (!this.performanceMetrics.has(name)) {
      this.performanceMetrics.set(name, []);
    }
    
    const metrics = this.performanceMetrics.get(name)!;
    metrics.push(value);
    
    // Manter apenas os últimos 100 valores
    if (metrics.length > 100) {
      metrics.splice(0, metrics.length - 100);
    }

    // Log em desenvolvimento
    if (import.meta.env.MODE === 'development' && metadata) {
      console.log(`📊 Performance: ${name}`, { value, metadata });
    }
  }

  /**
   * Marca renderização de componente para monitoramento
   */
  markComponentRender(componentName: string, metadata?: any): void {
    const timestamp = performance.now();
    this.recordPerformanceMetric(`component-render-${componentName}`, timestamp, metadata);
    
    if (import.meta.env.MODE === 'development') {
      console.log(`🎨 Component Render: ${componentName}`, metadata);
    }
  }

  private getPerformanceData(): PerformanceMetrics {
    const responseTimeMetrics = this.performanceMetrics.get('apiResponseTime') || [];
    const averageResponseTime = responseTimeMetrics.length > 0 
      ? responseTimeMetrics.reduce((a, b) => a + b, 0) / responseTimeMetrics.length 
      : 0;

    let grade: 'A' | 'B' | 'C' | 'D' | 'F' = 'A';
    if (averageResponseTime > this.config.thresholds.performanceGrade.acceptable) {
      grade = 'F';
    } else if (averageResponseTime > this.config.thresholds.performanceGrade.good) {
      grade = 'C';
    } else if (averageResponseTime > this.config.thresholds.performanceGrade.excellent) {
      grade = 'B';
    }

    return {
      responseTime: averageResponseTime,
      renderTime: 0, // Implementar se necessário
      apiCallDuration: averageResponseTime,
      totalOperationTime: averageResponseTime,
      grade,
    };
  }

  private calculateMetrics() {
    const totalChecks = this.checksHistory.length;
    const successfulChecks = this.checksHistory.filter(check => check.isValid).length;
    const successRate = totalChecks > 0 ? (successfulChecks / totalChecks) * 100 : 0;
    
    const responseTimeMetrics = this.performanceMetrics.get('apiResponseTime') || [];
    const averageResponseTime = responseTimeMetrics.length > 0 
      ? responseTimeMetrics.reduce((a, b) => a + b, 0) / responseTimeMetrics.length 
      : 0;

    return {
      uptime: Date.now() - (this.monitoringInterval ? Date.now() - this.config.checkInterval : Date.now()),
      totalChecks,
      successRate,
      averageResponseTime,
    };
  }

  private generateRecommendations(validationResults: MonitoringReport['validationResults']): string[] {
    const recommendations: string[] = [];

    if (!validationResults.apiConnectivity.isValid) {
      recommendations.push('Verificar conectividade com a API backend');
    }

    if (!validationResults.dataIntegrity.isValid) {
      recommendations.push('Revisar integridade dos dados e estrutura da API');
    }

    if (!validationResults.visualRendering.isValid) {
      recommendations.push('Verificar renderização dos componentes do dashboard');
    }

    if (!validationResults.performance.isValid) {
      recommendations.push('Otimizar performance das chamadas de API');
    }

    if (recommendations.length === 0) {
      recommendations.push('Sistema funcionando normalmente');
    }

    return recommendations;
  }

  private createAlert(alertData: Omit<MonitoringAlert, 'id' | 'timestamp' | 'resolved'>): void {
    const alert: MonitoringAlert = {
      ...alertData,
      id: `alert-${Date.now()}-${++this.alertCounter}`,
      timestamp: new Date().toISOString(),
      resolved: false,
    };

    this.alerts.push(alert);
    
    // Limitar número de alertas
    if (this.alerts.length > 50) {
      this.alerts = this.alerts.slice(-50);
    }
  }

  private getActiveAlerts(): MonitoringAlert[] {
    return this.alerts.filter(alert => !alert.resolved);
  }

  private processReport(report: MonitoringReport): void {
    // Armazenar resultados no histórico
    Object.values(report.validationResults).forEach(result => {
      this.checksHistory.push(result);
    });

    // Limpar histórico antigo
    if (this.checksHistory.length > 1000) {
      this.checksHistory = this.checksHistory.slice(-1000);
    }

    // Criar alertas para problemas críticos
    if (report.overallStatus === 'critical') {
      this.createAlert({
        type: 'critical',
        category: 'api',
        title: 'Sistema em Estado Crítico',
        message: 'Múltiplas falhas detectadas no monitoramento',
        source: 'UnifiedMonitor',
        severity: 'critical',
        data: report,
      });
    }
  }

  private notifyListeners(report: MonitoringReport): void {
    this.listeners.forEach(listener => {
      try {
        listener(report);
      } catch (error) {
        console.error('Erro ao notificar listener:', error);
      }
    });
  }

  /**
   * Métodos públicos para integração
   */
  addListener(listener: (report: MonitoringReport) => void): void {
    this.listeners.push(listener);
  }

  removeListener(listener: (report: MonitoringReport) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  getLatestReport(): MonitoringReport | null {
    // Implementar cache do último relatório se necessário
    return null;
  }

  resolveAlert(alertId: string): void {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      alert.resolvedAt = new Date().toISOString();
    }
  }

  getConfiguration(): UnifiedMonitoringConfig {
    return { ...this.config };
  }

  updateConfiguration(newConfig: Partial<UnifiedMonitoringConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // Reiniciar monitoramento se necessário
    if (this.monitoringInterval && newConfig.checkInterval) {
      this.stopMonitoring();
      this.startMonitoring();
    }
  }

  /**
   * Validação pré-entrega consolidada
   */
  async runPreDeliveryValidation(): Promise<ValidationResult> {
    const report = await this.runCompleteCheck();
    
    const overallScore = Object.values(report.validationResults)
      .reduce((sum, result) => sum + result.score, 0) / Object.keys(report.validationResults).length;

    const allErrors = Object.values(report.validationResults)
      .flatMap(result => result.errors);
    
    const allWarnings = Object.values(report.validationResults)
      .flatMap(result => result.warnings);

    return {
      isValid: report.overallStatus !== 'critical' && overallScore >= 80,
      errors: allErrors,
      warnings: allWarnings,
      score: overallScore,
      timestamp: new Date().toISOString(),
      details: report,
    };
  }
}

// Instância singleton
export const unifiedMonitor = new UnifiedMonitor();

// Exportar para uso global em desenvolvimento
if (typeof window !== 'undefined' && import.meta.env.MODE === 'development') {
  (window as any).unifiedMonitor = unifiedMonitor;
}

export default UnifiedMonitor;