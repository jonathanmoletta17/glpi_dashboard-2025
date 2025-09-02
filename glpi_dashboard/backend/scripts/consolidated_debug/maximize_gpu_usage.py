#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Avançado para Maximizar Uso da GPU
Objetivo: Aumentar utilização da GPU de 18% para >50%
"""

import torch
import psutil
import time
import json
import threading
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from concurrent.futures import ThreadPoolExecutor
import gc

class GPUMaximizer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.metrics = {
            'gpu_usage': [],
            'cpu_usage': [],
            'memory_usage': [],
            'inference_times': [],
            'batch_sizes': [],
            'throughput': []
        }
        
    def clear_gpu_cache(self):
        """Limpa cache da GPU para maximizar memória disponível"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
    
    def get_gpu_info(self):
        """Obtém informações detalhadas da GPU"""
        if not torch.cuda.is_available():
            return None
            
        gpu_info = {
            'name': torch.cuda.get_device_name(0),
            'total_memory': torch.cuda.get_device_properties(0).total_memory / 1024**3,
            'allocated': torch.cuda.memory_allocated(0) / 1024**3,
            'cached': torch.cuda.memory_reserved(0) / 1024**3,
            'free': (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_reserved(0)) / 1024**3,
            'utilization': (torch.cuda.memory_allocated(0) / torch.cuda.get_device_properties(0).total_memory) * 100
        }
        return gpu_info
    
    def load_optimized_model(self, model_name="codellama/CodeLlama-7b-Python-hf"):
        """Carrega modelo com configurações para máximo uso da GPU"""
        print(f"🚀 Carregando modelo otimizado: {model_name}")
        
        # Configuração de quantização mais agressiva
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            llm_int8_enable_fp32_cpu_offload=False  # Força tudo na GPU
        )
        
        try:
            # Carrega tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir="./cache"
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Carrega modelo com configurações otimizadas
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                cache_dir="./cache",
                attn_implementation="flash_attention_2" if hasattr(torch.nn, 'MultiheadAttention') else None
            )
            
            # Otimizações adicionais
            if hasattr(self.model, 'gradient_checkpointing_enable'):
                self.model.gradient_checkpointing_enable()
            
            print("✅ Modelo carregado com otimizações máximas para GPU")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return False
    
    def monitor_system(self, duration=60):
        """Monitora sistema em tempo real"""
        print(f"🔍 Monitorando sistema por {duration} segundos...")
        
        def monitor_loop():
            start_time = time.time()
            while time.time() - start_time < duration:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # GPU
                gpu_percent = 0
                if torch.cuda.is_available():
                    gpu_percent = (torch.cuda.memory_allocated(0) / torch.cuda.get_device_properties(0).total_memory) * 100
                
                # Memória
                memory_percent = psutil.virtual_memory().percent
                
                # Armazena métricas
                self.metrics['cpu_usage'].append(cpu_percent)
                self.metrics['gpu_usage'].append(gpu_percent)
                self.metrics['memory_usage'].append(memory_percent)
                
                print(f"⚡ CPU: {cpu_percent:5.1f}% | GPU: {gpu_percent:5.1f}% | Mem: {memory_percent:5.1f}%", end='\r')
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        return monitor_thread
    
    def run_intensive_inference(self, batch_sizes=[4, 8, 16, 32], num_iterations=5):
        """Executa inferência intensiva com diferentes tamanhos de lote"""
        if not self.model or not self.tokenizer:
            print("❌ Modelo não carregado")
            return
        
        print("🧪 Executando inferência intensiva para maximizar GPU...")
        
        # Prompts variados para teste
        test_prompts = [
            "def optimize_gpu_performance():",
            "# Função para maximizar uso da GPU\n",
            "SELECT * FROM glpi_tickets WHERE status = 'open' AND",
            "class GPUAccelerator:\n    def __init__(self):",
            "import torch\n# Configuração CUDA avançada\n",
            "async def process_batch_data(data):",
            "# Algoritmo de otimização de memória GPU\n",
            "def parallel_inference_pipeline():"
        ]
        
        results = []
        
        for batch_size in batch_sizes:
            print(f"\n🔥 Testando batch_size = {batch_size}")
            
            for iteration in range(num_iterations):
                try:
                    # Prepara lote de prompts
                    batch_prompts = test_prompts[:batch_size] if batch_size <= len(test_prompts) else test_prompts * (batch_size // len(test_prompts) + 1)
                    batch_prompts = batch_prompts[:batch_size]
                    
                    # Tokeniza em lote
                    start_time = time.time()
                    
                    inputs = self.tokenizer(
                        batch_prompts,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=128
                    ).to(self.device)
                    
                    # Configuração de geração otimizada
                    generation_config = {
                        'max_new_tokens': 100,
                        'do_sample': True,
                        'temperature': 0.8,
                        'top_p': 0.9,
                        'num_beams': 1,  # Beam search desabilitado para velocidade
                        'pad_token_id': self.tokenizer.eos_token_id,
                        'use_cache': True,
                        'output_attentions': False,
                        'output_hidden_states': False
                    }
                    
                    # Inferência em lote
                    with torch.no_grad():
                        outputs = self.model.generate(
                            inputs.input_ids,
                            attention_mask=inputs.attention_mask,
                            **generation_config
                        )
                    
                    inference_time = time.time() - start_time
                    throughput = batch_size / inference_time
                    
                    # Armazena métricas
                    self.metrics['inference_times'].append(inference_time)
                    self.metrics['batch_sizes'].append(batch_size)
                    self.metrics['throughput'].append(throughput)
                    
                    print(f"✅ Lote {iteration+1}/{num_iterations} (size={batch_size}) processado em {inference_time:.2f}s | Throughput: {throughput:.2f} samples/s")
                    
                    # Força uso da GPU
                    torch.cuda.synchronize()
                    
                    results.append({
                        'batch_size': batch_size,
                        'iteration': iteration + 1,
                        'inference_time': inference_time,
                        'throughput': throughput,
                        'gpu_memory_used': torch.cuda.memory_allocated(0) / 1024**3 if torch.cuda.is_available() else 0
                    })
                    
                except Exception as e:
                    print(f"❌ Erro no lote {batch_size}, iteração {iteration+1}: {e}")
                    continue
        
        return results
    
    def run_parallel_processing(self, num_workers=4):
        """Executa processamento paralelo para maximizar GPU"""
        print(f"🔄 Executando processamento paralelo com {num_workers} workers...")
        
        def worker_task(worker_id):
            prompts = [
                f"# Worker {worker_id} - Processamento paralelo GPU\n",
                f"def worker_{worker_id}_gpu_task():",
                f"SELECT * FROM worker_{worker_id}_data WHERE"
            ]
            
            for i, prompt in enumerate(prompts):
                try:
                    inputs = self.tokenizer(
                        prompt,
                        return_tensors="pt",
                        max_length=64,
                        truncation=True
                    ).to(self.device)
                    
                    with torch.no_grad():
                        outputs = self.model.generate(
                            inputs.input_ids,
                            max_new_tokens=50,
                            do_sample=True,
                            temperature=0.7,
                            pad_token_id=self.tokenizer.eos_token_id
                        )
                    
                    print(f"✅ Worker {worker_id} - Tarefa {i+1} concluída")
                    
                except Exception as e:
                    print(f"❌ Worker {worker_id} - Erro na tarefa {i+1}: {e}")
        
        # Executa workers em paralelo
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_workers)]
            
            # Aguarda conclusão
            for future in futures:
                future.result()
    
    def generate_report(self):
        """Gera relatório detalhado de maximização da GPU"""
        if not self.metrics['gpu_usage']:
            print("❌ Nenhuma métrica coletada")
            return
        
        # Calcula estatísticas
        gpu_avg = sum(self.metrics['gpu_usage']) / len(self.metrics['gpu_usage'])
        gpu_max = max(self.metrics['gpu_usage'])
        cpu_avg = sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage'])
        cpu_max = max(self.metrics['cpu_usage'])
        
        # Throughput médio
        avg_throughput = sum(self.metrics['throughput']) / len(self.metrics['throughput']) if self.metrics['throughput'] else 0
        
        # Melhor configuração de lote
        best_batch = None
        if self.metrics['throughput']:
            best_idx = self.metrics['throughput'].index(max(self.metrics['throughput']))
            best_batch = self.metrics['batch_sizes'][best_idx]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'gpu_optimization': {
                'avg_usage': gpu_avg,
                'max_usage': gpu_max,
                'target_achieved': gpu_avg > 50,
                'improvement_needed': max(0, 50 - gpu_avg)
            },
            'cpu_stats': {
                'avg_usage': cpu_avg,
                'max_usage': cpu_max
            },
            'performance': {
                'avg_throughput': avg_throughput,
                'best_batch_size': best_batch,
                'total_inferences': len(self.metrics['inference_times'])
            },
            'recommendations': []
        }
        
        # Gera recomendações
        if gpu_avg < 30:
            report['recommendations'].append("Aumentar drasticamente o batch_size")
            report['recommendations'].append("Implementar processamento paralelo")
        elif gpu_avg < 50:
            report['recommendations'].append("Otimizar batch_size e usar processamento contínuo")
        else:
            report['recommendations'].append("GPU bem utilizada - manter configurações")
        
        if cpu_avg > 80:
            report['recommendations'].append("CPU sobrecarregada - transferir mais processamento para GPU")
        
        # Salva relatório
        report_file = "gpu_maximization_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Exibe relatório
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE MAXIMIZAÇÃO DA GPU")
        print("="*60)
        print(f"🎯 GPU - Média: {gpu_avg:.1f}% | Máx: {gpu_max:.1f}%")
        print(f"🔥 CPU - Média: {cpu_avg:.1f}% | Máx: {cpu_max:.1f}%")
        print(f"⚡ Throughput médio: {avg_throughput:.2f} samples/s")
        print(f"📦 Melhor batch_size: {best_batch}")
        print(f"✅ Meta de 50% GPU: {'ATINGIDA' if gpu_avg > 50 else 'NÃO ATINGIDA'}")
        
        if report['recommendations']:
            print("\n💡 Recomendações:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        print(f"\n💾 Relatório salvo em: {report_file}")
        print("="*60)
        
        return report

def main():
    print("🚀 Iniciando maximização do uso da GPU...")
    
    maximizer = GPUMaximizer()
    
    # Limpa cache inicial
    maximizer.clear_gpu_cache()
    
    # Exibe informações da GPU
    gpu_info = maximizer.get_gpu_info()
    if gpu_info:
        print(f"🎮 GPU: {gpu_info['name']} ({gpu_info['total_memory']:.1f}GB)")
        print(f"💾 Memória livre: {gpu_info['free']:.2f}GB")
    
    # Carrega modelo otimizado
    if not maximizer.load_optimized_model():
        print("❌ Falha ao carregar modelo")
        return
    
    # Inicia monitoramento
    monitor_thread = maximizer.monitor_system(duration=90)
    
    # Executa testes intensivos
    print("\n🔥 Fase 1: Inferência intensiva com lotes grandes")
    maximizer.run_intensive_inference(batch_sizes=[8, 16, 32, 64], num_iterations=3)
    
    print("\n🔄 Fase 2: Processamento paralelo")
    maximizer.run_parallel_processing(num_workers=6)
    
    print("\n⏳ Aguardando finalização do monitoramento...")
    monitor_thread.join()
    
    # Gera relatório final
    maximizer.generate_report()
    
    print("\n🎉 Maximização da GPU concluída!")

if __name__ == "__main__":
    main()