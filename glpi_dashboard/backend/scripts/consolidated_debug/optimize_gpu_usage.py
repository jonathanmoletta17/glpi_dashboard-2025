#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para otimizar o uso de GPU para modelos LLM
Otimiza configurações de memória e performance
"""

import torch
import gc
import psutil
import json
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
from transformers import BitsAndBytesConfig
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gpu_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GPUOptimizer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_memory_total = torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0
        self.optimization_results = []
        
    def get_gpu_info(self):
        """Obter informações detalhadas da GPU"""
        if not torch.cuda.is_available():
            return {"error": "CUDA não disponível"}
            
        gpu_info = {
            "device_name": torch.cuda.get_device_name(0),
            "total_memory_gb": self.gpu_memory_total / (1024**3),
            "allocated_memory_gb": torch.cuda.memory_allocated(0) / (1024**3),
            "cached_memory_gb": torch.cuda.memory_reserved(0) / (1024**3),
            "free_memory_gb": (self.gpu_memory_total - torch.cuda.memory_reserved(0)) / (1024**3)
        }
        return gpu_info
        
    def clear_gpu_cache(self):
        """Limpar cache da GPU"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
            logger.info("Cache da GPU limpo")
            
    def get_optimal_batch_size(self, model_size_gb):
        """Calcular batch size ótimo baseado na memória disponível"""
        available_memory = self.gpu_memory_total / (1024**3) * 0.8  # 80% da memória total
        
        # Estimativa conservadora: modelo + overhead + batch
        overhead_factor = 1.5  # 50% overhead para gradientes, ativações, etc.
        memory_per_sample = model_size_gb * overhead_factor / 10  # Estimativa
        
        optimal_batch = max(1, int((available_memory - model_size_gb * overhead_factor) / memory_per_sample))
        return min(optimal_batch, 16)  # Máximo de 16 para estabilidade
        
    def create_quantization_config(self, bits=4):
        """Criar configuração de quantização para economizar memória"""
        return BitsAndBytesConfig(
            load_in_4bit=True if bits == 4 else False,
            load_in_8bit=True if bits == 8 else False,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
    def optimize_model_loading(self, model_name, use_quantization=True):
        """Carregar modelo com configurações otimizadas"""
        logger.info(f"Otimizando carregamento do modelo: {model_name}")
        
        try:
            # Limpar cache antes de carregar
            self.clear_gpu_cache()
            
            # Configurações de otimização
            model_kwargs = {
                "torch_dtype": torch.float16,  # Usar half precision
                "device_map": "auto",  # Distribuição automática
                "low_cpu_mem_usage": True,
                "trust_remote_code": True
            }
            
            # Adicionar quantização se solicitado
            if use_quantization and torch.cuda.is_available():
                model_kwargs["quantization_config"] = self.create_quantization_config()
                logger.info("Usando quantização 4-bit para economizar memória")
                
            # Carregar tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            # Carregar modelo
            if "code" in model_name.lower() or "llama" in model_name.lower():
                model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
            else:
                model = AutoModel.from_pretrained(model_name, **model_kwargs)
                
            # Informações pós-carregamento
            gpu_info_after = self.get_gpu_info()
            
            result = {
                "model_name": model_name,
                "success": True,
                "gpu_info_after_loading": gpu_info_after,
                "memory_used_gb": gpu_info_after["allocated_memory_gb"],
                "quantization_used": use_quantization,
                "optimal_batch_size": self.get_optimal_batch_size(gpu_info_after["allocated_memory_gb"])
            }
            
            logger.info(f"Modelo carregado com sucesso. Memória GPU usada: {gpu_info_after['allocated_memory_gb']:.2f}GB")
            
            return model, tokenizer, result
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo {model_name}: {str(e)}")
            return None, None, {
                "model_name": model_name,
                "success": False,
                "error": str(e)
            }
            
    def test_inference_performance(self, model, tokenizer, model_name):
        """Testar performance de inferência"""
        test_prompts = [
            "def analyze_glpi_ticket():",
            "Como resolver um ticket de suporte técnico?",
            "Analyze the following GLPI data:"
        ]
        
        results = []
        
        for prompt in test_prompts:
            try:
                start_time = datetime.now()
                
                inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
                if torch.cuda.is_available():
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                with torch.no_grad():
                    if hasattr(model, 'generate'):
                        outputs = model.generate(
                            **inputs,
                            max_new_tokens=50,
                            do_sample=True,
                            temperature=0.7,
                            pad_token_id=tokenizer.eos_token_id
                        )
                        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    else:
                        outputs = model(**inputs)
                        response = f"Output shape: {outputs.last_hidden_state.shape}"
                        
                end_time = datetime.now()
                inference_time = (end_time - start_time).total_seconds()
                
                results.append({
                    "prompt": prompt,
                    "response": response,
                    "inference_time_seconds": inference_time,
                    "success": True
                })
                
                logger.info(f"Inferência concluída em {inference_time:.2f}s")
                
            except Exception as e:
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
                logger.error(f"Erro na inferência: {str(e)}")
                
        return results
        
    def optimize_all_models(self):
        """Otimizar todos os modelos disponíveis"""
        # Modelos que funcionaram anteriormente + alguns novos com safetensors
        models_to_test = [
            "microsoft/DialoGPT-small",
            "distilbert-base-uncased",
            "codellama/CodeLlama-7b-Python-hf",
            "microsoft/DialoGPT-medium",  # Versão maior do DialoGPT
            "huggingface/CodeBERTa-small-v1",  # Alternativa ao CodeBERT
            "Salesforce/codet5-small",  # Modelo de código menor
        ]
        
        logger.info("Iniciando otimização de modelos...")
        logger.info(f"GPU Info inicial: {self.get_gpu_info()}")
        
        for model_name in models_to_test:
            logger.info(f"\n{'='*60}")
            logger.info(f"Otimizando modelo: {model_name}")
            logger.info(f"{'='*60}")
            
            # Testar com e sem quantização
            for use_quant in [True, False]:
                quant_label = "com quantização" if use_quant else "sem quantização"
                logger.info(f"Testando {quant_label}...")
                
                model, tokenizer, load_result = self.optimize_model_loading(model_name, use_quant)
                
                if model is not None:
                    # Testar performance
                    inference_results = self.test_inference_performance(model, tokenizer, model_name)
                    
                    # Combinar resultados
                    full_result = {
                        **load_result,
                        "quantization_used": use_quant,
                        "inference_results": inference_results,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.optimization_results.append(full_result)
                    
                    # Limpar modelo da memória
                    del model, tokenizer
                    self.clear_gpu_cache()
                    
                    # Se funcionou com quantização, não testar sem
                    if use_quant and load_result["success"]:
                        logger.info("Modelo funcionou com quantização, pulando teste sem quantização")
                        break
                else:
                    self.optimization_results.append(load_result)
                    
                logger.info(f"GPU Info após teste: {self.get_gpu_info()}")
                
        return self.optimization_results
        
    def save_results(self, filename="reports/gpu_optimization_results.json"):
        """Salvar resultados da otimização"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "optimization_timestamp": datetime.now().isoformat(),
                    "gpu_info": self.get_gpu_info(),
                    "system_info": {
                        "python_version": torch.__version__,
                        "cuda_available": torch.cuda.is_available(),
                        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
                    },
                    "results": self.optimization_results
                }, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Resultados salvos em: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
            
    def generate_report(self):
        """Gerar relatório de otimização"""
        successful_models = [r for r in self.optimization_results if r.get("success", False)]
        failed_models = [r for r in self.optimization_results if not r.get("success", False)]
        
        print("\n" + "="*60)
        print("RELATÓRIO DE OTIMIZAÇÃO DE GPU")
        print("="*60)
        
        gpu_info = self.get_gpu_info()
        print(f"GPU: {gpu_info.get('device_name', 'N/A')}")
        print(f"Memória Total: {gpu_info.get('total_memory_gb', 0):.2f}GB")
        print(f"Memória Livre: {gpu_info.get('free_memory_gb', 0):.2f}GB")
        
        print(f"\n✅ Modelos otimizados com sucesso ({len(successful_models)}):")
        for result in successful_models:
            memory_used = result.get("memory_used_gb", 0)
            batch_size = result.get("optimal_batch_size", 1)
            quant = "(Quantizado)" if result.get("quantization_used", False) else ""
            print(f"  - {result['model_name']} {quant}")
            print(f"    Memória: {memory_used:.2f}GB | Batch ótimo: {batch_size}")
            
        print(f"\n❌ Modelos com falha ({len(failed_models)}):")
        for result in failed_models:
            print(f"  - {result['model_name']}: {result.get('error', 'Erro desconhecido')}")
            
        # Recomendações
        print("\n🎯 RECOMENDAÇÕES:")
        if successful_models:
            best_model = max(successful_models, key=lambda x: x.get("memory_used_gb", 0))
            print(f"  - Modelo com melhor uso de GPU: {best_model['model_name']}")
            print(f"  - Memória recomendada para produção: {best_model['memory_used_gb']*1.2:.2f}GB")
            
        total_memory_available = gpu_info.get('total_memory_gb', 0)
        if total_memory_available > 8:
            print(f"  - Sua GPU tem {total_memory_available:.1f}GB, pode carregar modelos maiores")
            print(f"  - Considere testar modelos de 7B-13B parâmetros")
            
if __name__ == "__main__":
    optimizer = GPUOptimizer()
    
    print("Iniciando otimização de GPU para modelos LLM...")
    print(f"GPU detectada: {optimizer.get_gpu_info()}")
    
    # Executar otimização
    results = optimizer.optimize_all_models()
    
    # Salvar resultados
    optimizer.save_results()
    
    # Gerar relatório
    optimizer.generate_report()
    
    print("\n🚀 Otimização concluída!")
    print("Verifique o arquivo 'reports/gpu_optimization_results.json' para detalhes completos.")