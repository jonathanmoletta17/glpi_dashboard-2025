#!/usr/bin/env python3
"""
Verificação Rápida de GPU - GLPI Dashboard
Script para verificar rapidamente o status da GPU e ambiente
"""

import sys
import platform
import subprocess
from pathlib import Path

def check_system_info():
    """Verifica informações básicas do sistema."""
    print("🖥️ Informações do Sistema")
    print("=" * 30)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Plataforma: {platform.platform()}")
    print()

def check_nvidia_driver():
    """Verifica driver NVIDIA."""
    print("🎮 Status da GPU NVIDIA")
    print("=" * 30)
    
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'NVIDIA-SMI' in line:
                    print(f"✅ Driver: {line.strip()}")
                elif 'RTX A4000' in line or 'GPU' in line and '|' in line:
                    print(f"✅ GPU: {line.strip()}")
                elif 'MiB' in line and '|' in line:
                    print(f"📊 Memória: {line.strip()}")
            print("✅ NVIDIA Driver funcionando")
        else:
            print("❌ nvidia-smi falhou")
            print(result.stderr)
    except FileNotFoundError:
        print("❌ nvidia-smi não encontrado")
        print("Instale os drivers NVIDIA")
    except subprocess.TimeoutExpired:
        print("⏱️ nvidia-smi timeout")
    except Exception as e:
        print(f"❌ Erro: {e}")
    print()

def check_cuda_installation():
    """Verifica instalação CUDA."""
    print("🔧 Status CUDA")
    print("=" * 30)
    
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'release' in line.lower():
                    print(f"✅ CUDA: {line.strip()}")
        else:
            print("❌ NVCC não encontrado")
    except FileNotFoundError:
        print("❌ CUDA Toolkit não instalado")
        print("Baixe de: https://developer.nvidia.com/cuda-toolkit")
    except Exception as e:
        print(f"❌ Erro CUDA: {e}")
    print()

def check_python_packages():
    """Verifica pacotes Python relevantes."""
    print("🐍 Pacotes Python")
    print("=" * 30)
    
    packages = [
        'torch', 'torchvision', 'torchaudio',
        'tensorflow', 'transformers', 'accelerate',
        'langchain', 'gradio', 'streamlit'
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}: Instalado")
        except ImportError:
            print(f"❌ {package}: Não instalado")
    print()

def check_pytorch_gpu():
    """Verifica PyTorch com GPU."""
    print("🔥 PyTorch GPU")
    print("=" * 30)
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"CUDA disponível: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"Dispositivos CUDA: {torch.cuda.device_count()}")
            print(f"GPU atual: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
            
            # Teste rápido
            try:
                x = torch.randn(100, 100).cuda()
                y = torch.randn(100, 100).cuda()
                z = torch.matmul(x, y)
                print("✅ Teste GPU: Sucesso")
                del x, y, z
                torch.cuda.empty_cache()
            except Exception as e:
                print(f"❌ Teste GPU falhou: {e}")
        else:
            print("❌ CUDA não disponível no PyTorch")
            
    except ImportError:
        print("❌ PyTorch não instalado")
    except Exception as e:
        print(f"❌ Erro PyTorch: {e}")
    print()

def check_tensorflow_gpu():
    """Verifica TensorFlow com GPU."""
    print("🧠 TensorFlow GPU")
    print("=" * 30)
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow: {tf.__version__}")
        
        gpus = tf.config.list_physical_devices('GPU')
        print(f"GPUs físicas: {len(gpus)}")
        
        if gpus:
            for i, gpu in enumerate(gpus):
                print(f"GPU {i}: {gpu}")
            print("✅ TensorFlow GPU disponível")
        else:
            print("❌ TensorFlow GPU não disponível")
            
    except ImportError:
        print("❌ TensorFlow não instalado")
    except Exception as e:
        print(f"❌ Erro TensorFlow: {e}")
    print()

def check_disk_space():
    """Verifica espaço em disco."""
    print("💾 Espaço em Disco")
    print("=" * 30)
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        
        print(f"Total: {total // (1024**3)} GB")
        print(f"Usado: {used // (1024**3)} GB")
        print(f"Livre: {free // (1024**3)} GB")
        
        if free < 10 * 1024**3:  # Menos de 10GB
            print("⚠️ Pouco espaço livre (< 10GB)")
        else:
            print("✅ Espaço suficiente")
            
    except Exception as e:
        print(f"❌ Erro ao verificar disco: {e}")
    print()

def check_memory():
    """Verifica memória RAM."""
    print("🧠 Memória RAM")
    print("=" * 30)
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        print(f"Total: {memory.total // (1024**3)} GB")
        print(f"Disponível: {memory.available // (1024**3)} GB")
        print(f"Uso: {memory.percent}%")
        
        if memory.available < 8 * 1024**3:  # Menos de 8GB
            print("⚠️ Pouca memória disponível (< 8GB)")
        else:
            print("✅ Memória suficiente")
            
    except ImportError:
        print("❌ psutil não instalado")
        print("Execute: pip install psutil")
    except Exception as e:
        print(f"❌ Erro ao verificar memória: {e}")
    print()

def generate_recommendations():
    """Gera recomendações baseadas na verificação."""
    print("💡 Recomendações")
    print("=" * 30)
    
    recommendations = []
    
    # Verificar se nvidia-smi funciona
    try:
        subprocess.run(["nvidia-smi"], capture_output=True, timeout=5)
    except:
        recommendations.append("1. Instalar/atualizar drivers NVIDIA")
    
    # Verificar CUDA
    try:
        subprocess.run(["nvcc", "--version"], capture_output=True, timeout=5)
    except:
        recommendations.append("2. Instalar CUDA Toolkit 11.8 ou 12.1")
    
    # Verificar PyTorch
    try:
        import torch
        if not torch.cuda.is_available():
            recommendations.append("3. Reinstalar PyTorch com suporte CUDA")
    except:
        recommendations.append("3. Instalar PyTorch com CUDA")
    
    if not recommendations:
        print("✅ Sistema configurado corretamente!")
        print("Pronto para usar modelos de IA com GPU")
    else:
        print("Ações necessárias:")
        for rec in recommendations:
            print(rec)
    
    print("\n📚 Links úteis:")
    print("- NVIDIA Drivers: https://www.nvidia.com/drivers")
    print("- CUDA Toolkit: https://developer.nvidia.com/cuda-toolkit")
    print("- PyTorch: https://pytorch.org/get-started/locally/")
    print()

def main():
    """Executa verificação completa."""
    print("🚀 Verificação Rápida de GPU - GLPI Dashboard")
    print("=" * 50)
    print()
    
    checks = [
        check_system_info,
        check_nvidia_driver,
        check_cuda_installation,
        check_python_packages,
        check_pytorch_gpu,
        check_tensorflow_gpu,
        check_disk_space,
        check_memory,
        generate_recommendations
    ]
    
    for check in checks:
        try:
            check()
        except KeyboardInterrupt:
            print("\n❌ Verificação interrompida")
            break
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")
            continue
    
    print("✅ Verificação concluída!")

if __name__ == "__main__":
    main()