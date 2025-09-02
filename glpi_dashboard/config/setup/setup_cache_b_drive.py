#!/usr/bin/env python3
"""
Configurador de Cache Drive B: - GLPI Dashboard
Script para configurar cache de modelos de IA no Drive B: (1,847GB disponíveis)

Autor: Sistema de IA Colaborativo
Data: 30/01/2025
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class CacheBDriveSetup:
    """Configurador de cache no Drive B: para modelos de IA."""

    def __init__(self):
        self.cache_root = "B:\\ai_models_cache"
        self.subdirs = {
            'transformers': 'B:\\ai_models_cache\\transformers',
            'huggingface': 'B:\\ai_models_cache\\huggingface',
            'torch': 'B:\\ai_models_cache\\torch',
            'datasets': 'B:\\ai_models_cache\\datasets',
            'temp': 'B:\\ai_models_cache\\temp',
            'models': 'B:\\ai_models_cache\\models',
            'checkpoints': 'B:\\ai_models_cache\\checkpoints'
        }
        self.env_vars = {
            'TRANSFORMERS_CACHE': 'B:\\ai_models_cache\\transformers',
            'HF_HOME': 'B:\\ai_models_cache\\huggingface',
            'TORCH_HOME': 'B:\\ai_models_cache\\torch',
            'HF_DATASETS_CACHE': 'B:\\ai_models_cache\\datasets',
            'PYTORCH_KERNEL_CACHE_PATH': 'B:\\ai_models_cache\\torch\\kernels',
            'CUDA_CACHE_PATH': 'B:\\ai_models_cache\\cuda'
        }

    def log(self, message: str, level: str = "INFO"):
        """Log de ações."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_drive_b_availability(self) -> bool:
        """Verifica se o Drive B: está disponível e acessível."""
        self.log("Verificando disponibilidade do Drive B:...")

        if not os.path.exists("B:\\"):
            self.log("❌ Drive B: não encontrado!", "ERROR")
            return False

        try:
            # Testar escrita no drive
            test_file = "B:\\test_write_access.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)

            # Verificar espaço disponível
            import shutil
            total, used, free = shutil.disk_usage("B:\\")
            free_gb = free / (1024**3)

            self.log(f"✅ Drive B: disponível - {free_gb:.1f}GB livres")

            if free_gb < 50:
                self.log(f"⚠️ Espaço limitado: {free_gb:.1f}GB (mínimo recomendado: 50GB)", "WARNING")
                return False

            return True

        except Exception as e:
            self.log(f"❌ Erro ao acessar Drive B:: {e}", "ERROR")
            return False

    def create_cache_structure(self) -> bool:
        """Cria estrutura de diretórios de cache."""
        self.log("Criando estrutura de cache no Drive B:...")

        try:
            # Criar diretório raiz
            os.makedirs(self.cache_root, exist_ok=True)
            self.log(f"📁 Diretório raiz criado: {self.cache_root}")

            # Criar subdiretórios
            for name, path in self.subdirs.items():
                os.makedirs(path, exist_ok=True)
                self.log(f"📁 Subdiretório criado: {name} -> {path}")

            # Criar arquivo de informações
            info_file = os.path.join(self.cache_root, "cache_info.txt")
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"""Cache de Modelos de IA - GLPI Dashboard
Configurado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Versão: 1.0

Estrutura:
""")
                for name, path in self.subdirs.items():
                    f.write(f"- {name}: {path}\n")

            self.log("✅ Estrutura de cache criada com sucesso!")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao criar estrutura: {e}", "ERROR")
            return False

    def configure_environment_variables(self) -> bool:
        """Configura variáveis de ambiente para o cache."""
        self.log("Configurando variáveis de ambiente...")

        try:
            # Configurar para sessão atual
            for var, value in self.env_vars.items():
                os.environ[var] = value
                self.log(f"🔧 Variável configurada (sessão): {var}={value}")

            # Gerar script para configuração permanente
            script_content = f"""@echo off
REM Configuração Permanente de Cache - Drive B:
REM Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

echo Configurando variáveis de ambiente permanentes...
echo.

"""

            for var, value in self.env_vars.items():
                script_content += f'setx {var} "{value}"\n'
                script_content += f'echo {var} configurado\n'

            script_content += """
echo.
echo ✅ Configuração concluída!
echo ⚠️  IMPORTANTE: Reinicie o terminal/IDE para aplicar as configurações.
echo.
pause
"""

            script_path = "setup_env_permanent.bat"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            self.log(f"📄 Script de configuração permanente criado: {script_path}")
            self.log("⚠️ Execute como administrador para configuração permanente")

            return True

        except Exception as e:
            self.log(f"❌ Erro ao configurar variáveis: {e}", "ERROR")
            return False

    def create_python_config(self) -> bool:
        """Cria configuração Python para usar o cache."""
        self.log("Criando configuração Python...")

        try:
            config_content = f'''
"""
Configuração de Cache - GLPI Dashboard
Configuração automática para usar Drive B: como cache

Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""

import os

# Configuração de cache no Drive B:
CACHE_CONFIG = {{
    'root': r"{self.cache_root}",
    'transformers': r"{self.subdirs['transformers']}",
    'huggingface': r"{self.subdirs['huggingface']}",
    'torch': r"{self.subdirs['torch']}",
    'datasets': r"{self.subdirs['datasets']}",
    'temp': r"{self.subdirs['temp']}",
    'models': r"{self.subdirs['models']}",
    'checkpoints': r"{self.subdirs['checkpoints']}"
}}

# Aplicar configurações automaticamente
def setup_cache_environment():
    """Configura ambiente de cache automaticamente."""
    env_vars = {{
        'TRANSFORMERS_CACHE': CACHE_CONFIG['transformers'],
        'HF_HOME': CACHE_CONFIG['huggingface'],
        'TORCH_HOME': CACHE_CONFIG['torch'],
        'HF_DATASETS_CACHE': CACHE_CONFIG['datasets'],
        'PYTORCH_KERNEL_CACHE_PATH': os.path.join(CACHE_CONFIG['torch'], 'kernels'),
        'CUDA_CACHE_PATH': os.path.join(CACHE_CONFIG['root'], 'cuda')
    }}

    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"Cache configurado: {{var}} -> {{value}}")

    return True

# Configurar automaticamente ao importar
if __name__ != "__main__":
    setup_cache_environment()

# Funções utilitárias
def get_cache_path(cache_type: str) -> str:
    """Retorna caminho do cache especificado."""
    return CACHE_CONFIG.get(cache_type, CACHE_CONFIG['root'])

def get_cache_usage():
    """Retorna informações de uso do cache."""
    import shutil

    usage = {{}}
    for name, path in CACHE_CONFIG.items():
        if os.path.exists(path):
            try:
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except (OSError, PermissionError):
                            continue

                usage[name] = {{
                    'size_gb': total_size / (1024**3),
                    'file_count': file_count,
                    'path': path
                }}
            except Exception as e:
                usage[name] = {{'error': str(e), 'path': path}}
        else:
            usage[name] = {{'status': 'not_created', 'path': path}}

    return usage

def clear_cache(cache_type: str = None):
    """Limpa cache especificado ou todos."""
    import shutil

    if cache_type and cache_type in CACHE_CONFIG:
        paths_to_clear = [CACHE_CONFIG[cache_type]]
    else:
        paths_to_clear = list(CACHE_CONFIG.values())

    cleared = []
    for path in paths_to_clear:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                os.makedirs(path, exist_ok=True)
                cleared.append(path)
            except Exception as e:
                print(f"Erro ao limpar {{path}}: {{e}}")

    return cleared

if __name__ == "__main__":
    print("Configuração de Cache - Drive B:")
    print("=" * 40)

    setup_cache_environment()

    print("\\nCaminhos configurados:")
    for name, path in CACHE_CONFIG.items():
        print(f"- {{name}}: {{path}}")

    print("\\nUso do cache:")
    usage = get_cache_usage()
    for name, info in usage.items():
        if 'size_gb' in info:
            print(f"- {{name}}: {{info['size_gb']:.2f}}GB ({{info['file_count']}} arquivos)")
        else:
            print(f"- {{name}}: {{info.get('status', 'erro')}}")
'''

            config_path = "cache_config.py"
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)

            self.log(f"🐍 Configuração Python criada: {config_path}")
            return True

        except Exception as e:
            self.log(f"❌ Erro ao criar configuração Python: {e}", "ERROR")
            return False

    def test_cache_configuration(self) -> bool:
        """Testa a configuração do cache."""
        self.log("Testando configuração de cache...")

        try:
            # Testar criação de arquivo de teste
            test_file = os.path.join(self.cache_root, "test_cache.tmp")
            with open(test_file, 'w') as f:
                f.write(f"Teste de cache - {datetime.now()}")

            # Verificar se arquivo foi criado
            if os.path.exists(test_file):
                os.remove(test_file)
                self.log("✅ Teste de escrita: OK")
            else:
                self.log("❌ Teste de escrita: FALHOU", "ERROR")
                return False

            # Testar variáveis de ambiente
            missing_vars = []
            for var in self.env_vars.keys():
                if var not in os.environ:
                    missing_vars.append(var)

            if missing_vars:
                self.log(f"⚠️ Variáveis não configuradas: {', '.join(missing_vars)}", "WARNING")
            else:
                self.log("✅ Variáveis de ambiente: OK")

            # Testar estrutura de diretórios
            missing_dirs = []
            for name, path in self.subdirs.items():
                if not os.path.exists(path):
                    missing_dirs.append(name)

            if missing_dirs:
                self.log(f"❌ Diretórios não encontrados: {', '.join(missing_dirs)}", "ERROR")
                return False
            else:
                self.log("✅ Estrutura de diretórios: OK")

            self.log("🎉 Configuração de cache testada com sucesso!")
            return True

        except Exception as e:
            self.log(f"❌ Erro no teste: {e}", "ERROR")
            return False

    def generate_usage_report(self) -> str:
        """Gera relatório de uso do cache."""
        import shutil

        report = f'''
# Relatório de Cache - Drive B:
## Configuração e Status

**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Localização**: {self.cache_root}
**Status**: ✅ Configurado e Operacional

## 📊 Informações do Drive B:

'''

        try:
            total, used, free = shutil.disk_usage("B:\\")
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)

            report += f'''
- **Espaço Total**: {total_gb:.1f}GB
- **Espaço Usado**: {used_gb:.1f}GB
- **Espaço Livre**: {free_gb:.1f}GB
- **Adequado para IA**: ✅ Sim ({free_gb:.0f}GB disponíveis)

'''
        except:
            report += "- **Status**: ❌ Erro ao acessar informações do drive\n\n"

        report += f'''
## 📁 Estrutura de Cache Configurada

'''

        for name, path in self.subdirs.items():
            exists = "✅" if os.path.exists(path) else "❌"
            report += f"- **{name.title()}**: `{path}` {exists}\n"

        report += f'''

## 🔧 Variáveis de Ambiente

'''

        for var, value in self.env_vars.items():
            configured = "✅" if var in os.environ else "❌"
            report += f"- **{var}**: `{value}` {configured}\n"

        report += f'''

## 🚀 Próximos Passos

### 1. Configuração Permanente
```batch
# Execute como administrador:
setup_env_permanent.bat
```

### 2. Teste da Configuração
```python
# Importe e teste:
import cache_config
print(cache_config.get_cache_usage())
```

### 3. Continuar Instalação
```batch
# Prosseguir com instalação GPU:
python config/setup/setup_gpu_integration.py
```

## ✅ Status Final

**Cache Drive B:**: ✅ Configurado
**Espaço Disponível**: ✅ Adequado
**Pronto para IA**: ✅ Sim

---
*Relatório gerado por CacheBDriveSetup v1.0*
'''

        return report

    def run_full_setup(self) -> bool:
        """Executa configuração completa do cache."""
        print("🔧 Configurador de Cache Drive B: - GLPI Dashboard")
        print("=" * 55)

        # Verificar disponibilidade do Drive B:
        if not self.check_drive_b_availability():
            return False

        # Criar estrutura de cache
        if not self.create_cache_structure():
            return False

        # Configurar variáveis de ambiente
        if not self.configure_environment_variables():
            return False

        # Criar configuração Python
        if not self.create_python_config():
            return False

        # Testar configuração
        if not self.test_cache_configuration():
            return False

        # Gerar relatório
        report = self.generate_usage_report()
        report_path = "cache_b_drive_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        self.log(f"📊 Relatório salvo: {report_path}")

        print("\n" + "=" * 55)
        self.log("🎉 CONFIGURAÇÃO DE CACHE CONCLUÍDA COM SUCESSO!")
        print("=" * 55)

        print(f"\n📁 Cache configurado em: {self.cache_root}")
        print(f"📊 Relatório disponível: {report_path}")
        print(f"🔧 Script permanente: setup_env_permanent.bat")
        print(f"🐍 Configuração Python: cache_config.py")

        print("\n⚠️ IMPORTANTE:")
        print("1. Execute 'setup_env_permanent.bat' como administrador")
        print("2. Reinicie o terminal/IDE após configuração permanente")
        print("3. Continue com: python config/setup/setup_gpu_integration.py")

        return True

def main():
    """Função principal."""
    setup = CacheBDriveSetup()

    try:
        success = setup.run_full_setup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n❌ Configuração interrompida pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
