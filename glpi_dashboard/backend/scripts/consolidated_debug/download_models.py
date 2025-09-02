#!/usr/bin/env python3
"""
Script para baixar e testar modelos AI para o sistema GLPI Dashboard
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
import yaml
from pathlib import Path

def load_config():
    """Carrega configuração do sistema"""
    config_path = Path("../../config/ai_agent_system.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return None

def check_gpu_memory():
    """Verifica memória GPU disponível"""
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        gpu_free = (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / (1024**3)
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memória total: {gpu_memory:.1f}GB")
        print(f"Memória livre: {gpu_free:.1f}GB")
        return gpu_memory
    return 0

def download_and_test_model(model_name, model_type="causal_lm"):
    """Baixa e testa um modelo específico"""
    print(f"\n{'='*60}")
    print(f"Testando modelo: {model_name}")
    print(f"{'='*60}")
    
    try:
        # Baixar tokenizer
        print("Baixando tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Configurar pad_token se necessário
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        print("✅ Tokenizer baixado com sucesso")
        
        # Baixar modelo com configurações otimizadas
        print("Baixando modelo...")
        if model_type == "causal_lm":
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        else:
            model = AutoModel.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        
        print("✅ Modelo baixado com sucesso")
        
        # Teste básico
        test_text = "def analyze_glpi_ticket():"
        inputs = tokenizer(test_text, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        print("Executando teste de inferência...")
        with torch.no_grad():
            if model_type == "causal_lm":
                outputs = model.generate(
                    inputs["input_ids"],
                    max_length=inputs["input_ids"].shape[1] + 30,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id
                )
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(f"Texto gerado: {generated_text}")
            else:
                outputs = model(**inputs)
                print(f"Output shape: {outputs.last_hidden_state.shape}")
        
        print("✅ Teste de inferência concluído com sucesso")
        
        # Limpar memória
        del model
        del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar modelo {model_name}: {e}")
        return False

def main():
    print("🤖 Sistema de Download e Teste de Modelos AI")
    print("=" * 50)
    
    # Verificar GPU
    gpu_memory = check_gpu_memory()
    
    # Modelos otimizados para o sistema GLPI (começando com os menores)
    models_to_test = [
        # Modelos pequenos e eficientes para análise de texto
        ("microsoft/DialoGPT-small", "causal_lm"),
        ("distilbert-base-uncased", "encoder"),
        
        # Modelos de código pequenos
        ("Salesforce/codegen-350M-mono", "causal_lm"),
    ]
    
    # Se tiver memória GPU suficiente (>8GB), adicionar modelos maiores
    if gpu_memory > 8:
        models_to_test.extend([
            ("microsoft/CodeBERT-base", "encoder"),
            ("Salesforce/codegen-2B-mono", "causal_lm"),
        ])
    
    # Para GPUs com mais de 12GB, adicionar modelos ainda maiores
    if gpu_memory > 12:
        models_to_test.extend([
            ("codellama/CodeLlama-7b-Python-hf", "causal_lm"),
        ])
    
    successful_models = []
    failed_models = []
    
    for model_name, model_type in models_to_test:
        success = download_and_test_model(model_name, model_type)
        if success:
            successful_models.append(model_name)
        else:
            failed_models.append(model_name)
        
        # Pausa entre downloads para evitar sobrecarga
        print("\nAguardando 2 segundos...")
        import time
        time.sleep(2)
    
    # Relatório final
    print("\n" + "="*60)
    print("RELATÓRIO FINAL")
    print("="*60)
    print(f"✅ Modelos testados com sucesso ({len(successful_models)}):")
    for model in successful_models:
        print(f"  - {model}")
    
    if failed_models:
        print(f"\n❌ Modelos com falha ({len(failed_models)}):")
        for model in failed_models:
            print(f"  - {model}")
    
    print(f"\n🎯 Sistema pronto para usar {len(successful_models)} modelos!")
    
    # Salvar lista de modelos funcionais
    models_file = Path("working_models.txt")
    with open(models_file, 'w') as f:
        for model in successful_models:
            f.write(f"{model}\n")
    print(f"\n📝 Lista de modelos funcionais salva em: {models_file}")

if __name__ == "__main__":
    main()