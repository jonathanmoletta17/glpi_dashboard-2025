#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final para demonstrar uso otimizado da GPU
"""

import torch
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from datetime import datetime
import gc

def clear_gpu_cache():
    """Limpa cache da GPU"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()

def get_gpu_memory():
    """Obtém informações de memória da GPU"""
    if not torch.cuda.is_available():
        return {"error": "CUDA não disponível"}
    
    return {
        "allocated_gb": torch.cuda.memory_allocated(0) / (1024**3),
        "reserved_gb": torch.cuda.memory_reserved(0) / (1024**3),
        "total_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3)
    }

def test_model_with_quantization():
    """Testa modelo com quantização para maximizar uso da GPU"""
    model_name = "codellama/CodeLlama-7b-Python-hf"
    
    print(f"🚀 Testando modelo: {model_name}")
    print(f"📊 Memória inicial: {get_gpu_memory()}")
    
    # Configuração de quantização 4-bit
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    try:
        # Carregar tokenizer
        print("🔄 Carregando tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Carregar modelo com quantização
        print("🔄 Carregando modelo com quantização 4-bit...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        
        memory_after_load = get_gpu_memory()
        print(f"📊 Memória após carregar modelo: {memory_after_load}")
        
        # Teste de inferência
        prompts = [
            "def analyze_glpi_ticket():",
            "# Função para processar tickets GLPI\ndef process_ticket(ticket_data):",
            "SELECT COUNT(*) FROM glpi_tickets WHERE status = 'open'"
        ]
        
        results = []
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n🧪 Teste {i}/3: {prompt[:50]}...")
            
            # Tokenizar
            inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Gerar resposta
            with torch.no_grad():
                start_time = datetime.now()
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=tokenizer.eos_token_id
                )
                end_time = datetime.now()
            
            # Decodificar resposta
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            inference_time = (end_time - start_time).total_seconds()
            
            result = {
                "prompt": prompt,
                "response": response[len(prompt):].strip()[:200],
                "inference_time_seconds": inference_time,
                "memory_usage": get_gpu_memory()
            }
            
            results.append(result)
            print(f"   ✅ Resposta gerada em {inference_time:.2f}s")
            print(f"   📝 Resposta: {result['response'][:100]}...")
        
        # Relatório final
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "quantization": "4-bit",
            "initial_memory": get_gpu_memory(),
            "final_memory": memory_after_load,
            "test_results": results,
            "summary": {
                "memory_used_gb": memory_after_load["allocated_gb"],
                "memory_efficiency": f"{(memory_after_load['allocated_gb'] / memory_after_load['total_gb']) * 100:.1f}%",
                "avg_inference_time": sum(r["inference_time_seconds"] for r in results) / len(results)
            }
        }
        
        # Salvar relatório
        with open('final_gpu_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("🎯 TESTE FINAL CONCLUÍDO COM SUCESSO")
        print("="*60)
        print(f"💾 Uso de memória: {memory_after_load['allocated_gb']:.2f}GB / {memory_after_load['total_gb']:.1f}GB")
        print(f"⚡ Eficiência: {(memory_after_load['allocated_gb'] / memory_after_load['total_gb']) * 100:.1f}%")
        print(f"⏱️  Tempo médio de inferência: {final_report['summary']['avg_inference_time']:.2f}s")
        print(f"📄 Relatório salvo em: final_gpu_test_results.json")
        
        if memory_after_load['allocated_gb'] > 3:
            print("✅ SUCESSO: Uso da GPU significativamente aumentado!")
        else:
            print("🟡 ATENÇÃO: Uso da GPU ainda baixo")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False
    
    finally:
        clear_gpu_cache()

if __name__ == "__main__":
    print("🔍 Iniciando teste final de otimização da GPU...")
    
    # Limpar cache inicial
    clear_gpu_cache()
    
    # Executar teste
    success = test_model_with_quantization()
    
    if success:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou. Verifique os logs acima.")