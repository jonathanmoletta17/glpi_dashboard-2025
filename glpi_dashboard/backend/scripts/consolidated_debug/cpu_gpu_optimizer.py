#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador de balanceamento CPU/GPU para reduzir carga da CPU
"""

import torch
import psutil
import time
import json
import threading
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import gc
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class CPUGPUOptimizer:
    def __init__(self):
        self.monitoring = False
        self.performance_data = []
        self.model = None
        self.tokenizer = None
        
    def get_system_metrics(self):
        """Obtém métricas do sistema em tempo real"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        gpu_metrics = {"error": "CUDA não disponível"}
        if torch.cuda.is_available():
            gpu_metrics = {
                "allocated_gb": torch.cuda.memory_allocated(0) / (1024**3),
                "reserved_gb": torch.cuda.memory_reserved(0) / (1024**3),
                "total_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3),
                "utilization_percent": (torch.cuda.memory_allocated(0) / torch.cuda.get_device_properties(0).total_memory) * 100
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "gpu_metrics": gpu_metrics
        }
    
    def start_monitoring(self, duration_seconds=60):
        """Inicia monitoramento contínuo do sistema"""
        print(f"🔍 Iniciando monitoramento por {duration_seconds} segundos...")
        self.monitoring = True
        self.performance_data = []
        
        def monitor_loop():
            start_time = time.time()
            while self.monitoring and (time.time() - start_time) < duration_seconds:
                metrics = self.get_system_metrics()
                self.performance_data.append(metrics)
                
                # Exibir métricas em tempo real
                cpu = metrics['cpu_percent']
                gpu_util = metrics['gpu_metrics'].get('utilization_percent', 0)
                print(f"\r⚡ CPU: {cpu:5.1f}% | GPU: {gpu_util:5.1f}% | Mem: {metrics['memory_percent']:5.1f}%", end="", flush=True)
                
                time.sleep(1)
            
            self.monitoring = False
            print("\n✅ Monitoramento concluído")
        
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.start()
        return monitor_thread
    
    def optimize_model_loading(self, model_name="codellama/CodeLlama-7b-Python-hf"):
        """Carrega modelo com configurações otimizadas para GPU"""
        print(f"🚀 Carregando modelo otimizado: {model_name}")
        
        # Configuração agressiva para GPU
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        try:
            # Limpar cache antes de carregar
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            # Carregar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Carregar modelo com máxima utilização da GPU
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True,  # Reduz uso de CPU
                offload_folder="./temp",  # Offload para disco se necessário
                max_memory={0: "14GB"}  # Força uso máximo da GPU
            )
            
            print("✅ Modelo carregado com otimizações para GPU")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {str(e)}")
            return False
    
    def gpu_accelerated_inference(self, prompts, batch_size=4):
        """Executa inferência otimizada para GPU com processamento em lote"""
        if not self.model or not self.tokenizer:
            print("❌ Modelo não carregado")
            return []
        
        print(f"🧠 Executando inferência em lote (batch_size={batch_size})...")
        results = []
        
        # Processar em lotes para maximizar uso da GPU
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i+batch_size]
            
            # Tokenizar lote
            inputs = self.tokenizer(
                batch_prompts, 
                return_tensors="pt", 
                padding=True, 
                truncation=True,
                max_length=512
            )
            
            # Mover para GPU
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Inferência otimizada
            with torch.no_grad():
                start_time = time.time()
                
                # Configurações para máxima utilização da GPU
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.7,
                    num_beams=1,  # Reduz uso de CPU
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=True  # Usa cache da GPU
                )
                
                inference_time = time.time() - start_time
            
            # Decodificar resultados
            batch_results = []
            for j, output in enumerate(outputs):
                response = self.tokenizer.decode(output, skip_special_tokens=True)
                original_prompt = batch_prompts[j]
                generated_text = response[len(original_prompt):].strip()
                
                batch_results.append({
                    "prompt": original_prompt,
                    "response": generated_text[:200],
                    "inference_time": inference_time / len(batch_prompts)
                })
            
            results.extend(batch_results)
            print(f"✅ Lote {i//batch_size + 1} processado em {inference_time:.2f}s")
        
        return results
    
    def parallel_cpu_tasks(self, tasks, max_workers=2):
        """Executa tarefas CPU em paralelo limitado para não sobrecarregar"""
        print(f"🔄 Executando {len(tasks)} tarefas CPU em paralelo (workers={max_workers})...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.simulate_cpu_task, tasks))
        
        return results
    
    def simulate_cpu_task(self, task_data):
        """Simula tarefa CPU otimizada"""
        # Simular processamento CPU leve
        time.sleep(0.1)  # Reduzido de processamento pesado
        return f"Processado: {task_data}"
    
    def generate_optimization_report(self):
        """Gera relatório de otimização"""
        if not self.performance_data:
            print("❌ Nenhum dado de performance coletado")
            return
        
        # Calcular estatísticas
        cpu_usage = [d['cpu_percent'] for d in self.performance_data]
        gpu_usage = [d['gpu_metrics'].get('utilization_percent', 0) for d in self.performance_data]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_duration": len(self.performance_data),
            "cpu_stats": {
                "avg_usage": np.mean(cpu_usage),
                "max_usage": np.max(cpu_usage),
                "min_usage": np.min(cpu_usage),
                "over_80_percent": sum(1 for x in cpu_usage if x > 80)
            },
            "gpu_stats": {
                "avg_usage": np.mean(gpu_usage),
                "max_usage": np.max(gpu_usage),
                "min_usage": np.min(gpu_usage),
                "under_50_percent": sum(1 for x in gpu_usage if x < 50)
            },
            "recommendations": self.get_optimization_recommendations(cpu_usage, gpu_usage)
        }
        
        # Salvar relatório
        with open('cpu_gpu_optimization_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE OTIMIZAÇÃO CPU/GPU")
        print("="*60)
        print(f"⏱️  Duração do monitoramento: {len(self.performance_data)} segundos")
        print(f"🔥 CPU - Média: {report['cpu_stats']['avg_usage']:.1f}% | Máx: {report['cpu_stats']['max_usage']:.1f}%")
        print(f"⚡ GPU - Média: {report['gpu_stats']['avg_usage']:.1f}% | Máx: {report['gpu_stats']['max_usage']:.1f}%")
        print(f"⚠️  CPU > 80%: {report['cpu_stats']['over_80_percent']} vezes")
        print(f"💡 GPU < 50%: {report['gpu_stats']['under_50_percent']} vezes")
        
        print("\n🎯 Recomendações:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
        
        print(f"\n💾 Relatório salvo em: cpu_gpu_optimization_report.json")
        print("="*60)
        
        return report
    
    def get_optimization_recommendations(self, cpu_usage, gpu_usage):
        """Gera recomendações de otimização"""
        recommendations = []
        
        avg_cpu = np.mean(cpu_usage)
        avg_gpu = np.mean(gpu_usage)
        
        if avg_cpu > 80:
            recommendations.append("CPU sobregregada - implementar mais offloading para GPU")
        
        if avg_gpu < 30:
            recommendations.append("GPU subutilizada - aumentar batch size e quantização")
        
        if avg_cpu > 70 and avg_gpu < 40:
            recommendations.append("Desbalanceamento crítico - priorizar transferência CPU→GPU")
        
        if max(cpu_usage) == 100:
            recommendations.append("CPU atingiu 100% - implementar limitação de threads")
        
        if avg_gpu > 80:
            recommendations.append("Excelente utilização da GPU - manter configurações")
        
        return recommendations

def main():
    print("🚀 Iniciando otimizador de balanceamento CPU/GPU...")
    
    optimizer = CPUGPUOptimizer()
    
    # 1. Iniciar monitoramento
    monitor_thread = optimizer.start_monitoring(duration_seconds=30)
    
    # 2. Carregar modelo otimizado
    if optimizer.optimize_model_loading():
        
        # 3. Teste de inferência otimizada
        test_prompts = [
            "def optimize_glpi_performance():",
            "# Função para balancear CPU e GPU\ndef balance_resources():",
            "SELECT * FROM glpi_tickets WHERE priority = 'high'",
            "class GPUOptimizer:",
            "import torch\n# Configuração CUDA"
        ]
        
        print("\n🧪 Executando teste de inferência otimizada...")
        results = optimizer.gpu_accelerated_inference(test_prompts, batch_size=2)
        
        print(f"\n✅ {len(results)} inferências concluídas")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['prompt'][:30]}... → {result['inference_time']:.2f}s")
    
    # 4. Aguardar monitoramento terminar
    monitor_thread.join()
    
    # 5. Gerar relatório
    optimizer.generate_optimization_report()
    
    print("\n🎉 Otimização concluída!")

if __name__ == "__main__":
    main()