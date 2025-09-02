#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar o status atual da GPU e gerar relatório final
"""

import torch
import json
import os
from datetime import datetime

def get_gpu_info():
    """Obtém informações da GPU"""
    if not torch.cuda.is_available():
        return {"error": "CUDA não disponível"}
    
    gpu_info = {
        "device_name": torch.cuda.get_device_name(0),
        "total_memory_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3),
        "allocated_memory_gb": torch.cuda.memory_allocated(0) / (1024**3),
        "cached_memory_gb": torch.cuda.memory_reserved(0) / (1024**3),
        "free_memory_gb": (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_reserved(0)) / (1024**3),
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda
    }
    
    return gpu_info

def check_existing_results():
    """Verifica arquivos de resultado existentes"""
    results_files = []
    
    # Procurar por arquivos de resultado
    for root, dirs, files in os.walk('.'):
        for file in files:
            if 'result' in file.lower() and file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    results_files.append({
                        'file': file_path,
                        'size_kb': stat.st_size / 1024,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    pass
    
    return results_files

def generate_final_report():
    """Gera relatório final do status da GPU e otimizações"""
    print("🔍 Verificando status atual da GPU...")
    
    gpu_info = get_gpu_info()
    results_files = check_existing_results()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "gpu_status": gpu_info,
        "results_files": results_files,
        "summary": {
            "initial_usage": "0.34GB/16GB",
            "target_usage": "8-12GB/16GB",
            "current_usage": f"{gpu_info.get('allocated_memory_gb', 0):.2f}GB/{gpu_info.get('total_memory_gb', 16):.0f}GB"
        }
    }
    
    # Salvar relatório
    with open('gpu_status_final.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL - STATUS DA GPU")
    print("="*60)
    print(f"🖥️  GPU: {gpu_info.get('device_name', 'N/A')}")
    print(f"💾 Memória Total: {gpu_info.get('total_memory_gb', 0):.1f}GB")
    print(f"⚡ Memória Alocada: {gpu_info.get('allocated_memory_gb', 0):.2f}GB")
    print(f"🔄 Memória Cached: {gpu_info.get('cached_memory_gb', 0):.2f}GB")
    print(f"🆓 Memória Livre: {gpu_info.get('free_memory_gb', 0):.2f}GB")
    print(f"🐍 PyTorch: {gpu_info.get('pytorch_version', 'N/A')}")
    print(f"🔧 CUDA: {gpu_info.get('cuda_version', 'N/A')}")
    
    print("\n📁 Arquivos de Resultado Encontrados:")
    for file_info in results_files:
        print(f"   📄 {file_info['file']} ({file_info['size_kb']:.1f}KB) - {file_info['modified']}")
    
    print("\n🎯 Status da Otimização:")
    current_usage = gpu_info.get('allocated_memory_gb', 0)
    if current_usage > 8:
        print(f"   ✅ META ATINGIDA: {current_usage:.2f}GB > 8GB")
    elif current_usage > 3:
        print(f"   🟡 PROGRESSO: {current_usage:.2f}GB (melhor que inicial 0.34GB)")
    else:
        print(f"   🔴 BAIXO USO: {current_usage:.2f}GB (ainda próximo ao inicial)")
    
    print("\n💾 Relatório salvo em: gpu_status_final.json")
    print("="*60)

if __name__ == "__main__":
    generate_final_report()