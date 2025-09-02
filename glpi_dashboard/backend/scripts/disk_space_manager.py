#!/usr/bin/env python3
"""
Gerenciador de Espaço em Disco - GLPI Dashboard
Script para otimizar espaço e configurar cache alternativo para modelos de IA

Autor: Sistema de IA Colaborativo
Data: 30/01/2025
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

class DiskSpaceManager:
    """Gerenciador de espaço em disco para otimização de IA."""
    
    def __init__(self):
        self.min_required_space = 50 * 1024**3  # 50GB em bytes
        self.recommended_space = 100 * 1024**3  # 100GB em bytes
        self.analysis_results = {}
        self.cleanup_log = []
        
    def _log_action(self, message: str, action_type: str = "INFO"):
        """Registra ações do gerenciador."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'message': message
        }
        self.cleanup_log.append(log_entry)
        print(f"[{action_type}] {message}")
    
    def analyze_disk_usage(self) -> Dict:
        """Analisa uso de disco em todas as unidades."""
        self._log_action("Analisando uso de disco...")
        
        drives = []
        
        # Verificar todas as unidades no Windows
        for drive_letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = f"{drive_letter}:\\"
            if os.path.exists(drive_path):
                try:
                    total, used, free = shutil.disk_usage(drive_path)
                    drive_info = {
                        'letter': drive_letter,
                        'path': drive_path,
                        'total_gb': total / (1024**3),
                        'used_gb': used / (1024**3),
                        'free_gb': free / (1024**3),
                        'usage_percent': (used / total) * 100,
                        'suitable_for_cache': free > self.min_required_space
                    }
                    drives.append(drive_info)
                    
                    self._log_action(
                        f"Drive {drive_letter}: {drive_info['free_gb']:.1f}GB livre / {drive_info['total_gb']:.1f}GB total"
                    )
                    
                except (OSError, PermissionError):
                    continue
        
        self.analysis_results['drives'] = drives
        return drives
    
    def find_large_files(self, directory: str, min_size_mb: int = 100) -> List[Dict]:
        """Encontra arquivos grandes em um diretório."""
        self._log_action(f"Procurando arquivos grandes em {directory}...")
        
        large_files = []
        min_size_bytes = min_size_mb * 1024 * 1024
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        
                        if file_size > min_size_bytes:
                            large_files.append({
                                'path': file_path,
                                'size_mb': file_size / (1024 * 1024),
                                'size_gb': file_size / (1024**3),
                                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            })
                    except (OSError, PermissionError):
                        continue
        except Exception as e:
            self._log_action(f"Erro ao analisar {directory}: {e}", "ERROR")
        
        # Ordenar por tamanho (maior primeiro)
        large_files.sort(key=lambda x: x['size_mb'], reverse=True)
        
        self._log_action(f"Encontrados {len(large_files)} arquivos grandes")
        return large_files
    
    def analyze_temp_directories(self) -> Dict:
        """Analisa diretórios temporários para limpeza."""
        self._log_action("Analisando diretórios temporários...")
        
        temp_dirs = {
            'windows_temp': os.environ.get('TEMP', 'C:\\Windows\\Temp'),
            'user_temp': os.environ.get('TMP', 'C:\\Users\\%USERNAME%\\AppData\\Local\\Temp'),
            'python_cache': os.path.expanduser('~/.cache'),
            'pip_cache': os.path.expanduser('~/.cache/pip'),
            'npm_cache': os.path.expanduser('~/.npm'),
            'conda_cache': os.path.expanduser('~/.conda'),
        }
        
        temp_analysis = {}
        
        for name, path in temp_dirs.items():
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
                    
                    temp_analysis[name] = {
                        'path': path,
                        'size_gb': total_size / (1024**3),
                        'file_count': file_count,
                        'cleanable': total_size > 100 * 1024 * 1024  # > 100MB
                    }
                    
                    self._log_action(
                        f"{name}: {temp_analysis[name]['size_gb']:.2f}GB ({file_count} arquivos)"
                    )
                    
                except Exception as e:
                    self._log_action(f"Erro ao analisar {name}: {e}", "WARNING")
        
        return temp_analysis
    
    def suggest_cleanup_actions(self) -> List[Dict]:
        """Sugere ações de limpeza baseadas na análise."""
        self._log_action("Gerando sugestões de limpeza...")
        
        suggestions = []
        
        # Limpeza automática do Windows
        suggestions.append({
            'action': 'windows_cleanup',
            'description': 'Executar limpeza de disco do Windows',
            'command': 'cleanmgr /sagerun:1',
            'estimated_space_gb': 5,
            'risk': 'low',
            'automatic': True
        })
        
        # Limpeza de cache do navegador
        suggestions.append({
            'action': 'browser_cache',
            'description': 'Limpar cache de navegadores',
            'command': 'manual',
            'estimated_space_gb': 2,
            'risk': 'low',
            'automatic': False
        })
        
        # Arquivos temporários
        temp_analysis = self.analyze_temp_directories()
        for name, info in temp_analysis.items():
            if info.get('cleanable', False):
                suggestions.append({
                    'action': f'clean_{name}',
                    'description': f'Limpar {name}',
                    'path': info['path'],
                    'estimated_space_gb': info['size_gb'],
                    'risk': 'medium',
                    'automatic': True
                })
        
        # Arquivos grandes específicos
        large_files = self.find_large_files('C:\\', 500)  # > 500MB
        for file_info in large_files[:10]:  # Top 10
            suggestions.append({
                'action': 'review_large_file',
                'description': f'Revisar arquivo grande: {os.path.basename(file_info["path"])}',
                'path': file_info['path'],
                'estimated_space_gb': file_info['size_gb'],
                'risk': 'high',
                'automatic': False
            })
        
        return suggestions
    
    def setup_alternative_cache(self) -> Optional[str]:
        """Configura cache alternativo em drive com espaço."""
        self._log_action("Configurando cache alternativo...")
        
        drives = self.analysis_results.get('drives', [])
        
        # Encontrar melhor drive para cache
        suitable_drives = [
            drive for drive in drives 
            if drive['suitable_for_cache'] and drive['letter'] != 'C'
        ]
        
        if not suitable_drives:
            self._log_action("Nenhum drive alternativo adequado encontrado", "WARNING")
            return None
        
        # Escolher drive com mais espaço livre
        best_drive = max(suitable_drives, key=lambda x: x['free_gb'])
        cache_path = f"{best_drive['letter']}:\\ai_models_cache"
        
        try:
            # Criar diretório de cache
            os.makedirs(cache_path, exist_ok=True)
            
            # Criar subdiretórios
            subdirs = ['transformers', 'huggingface', 'torch', 'datasets']
            for subdir in subdirs:
                os.makedirs(os.path.join(cache_path, subdir), exist_ok=True)
            
            self._log_action(f"Cache configurado em: {cache_path}", "SUCCESS")
            
            # Gerar script de configuração de ambiente
            env_script = f'''
@echo off
REM Configuração de Cache Alternativo - GLPI Dashboard
REM Gerado automaticamente em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

echo Configurando cache alternativo em {cache_path}...

REM Variáveis de ambiente para cache
set TRANSFORMERS_CACHE={cache_path}\\transformers
set HF_HOME={cache_path}\\huggingface
set TORCH_HOME={cache_path}\\torch
set HF_DATASETS_CACHE={cache_path}\\datasets

REM Configuração permanente (requer admin)
setx TRANSFORMERS_CACHE "{cache_path}\\transformers"
setx HF_HOME "{cache_path}\\huggingface"
setx TORCH_HOME "{cache_path}\\torch"
setx HF_DATASETS_CACHE "{cache_path}\\datasets"

echo Cache configurado com sucesso!
echo Reinicie o terminal para aplicar as configurações.
pause
'''
            
            script_path = "setup_cache_env.bat"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(env_script)
            
            self._log_action(f"Script de configuração criado: {script_path}", "SUCCESS")
            
            return cache_path
            
        except Exception as e:
            self._log_action(f"Erro ao configurar cache: {e}", "ERROR")
            return None
    
    def execute_safe_cleanup(self, suggestions: List[Dict]) -> Dict:
        """Executa limpeza segura baseada nas sugestões."""
        self._log_action("Iniciando limpeza segura...")
        
        results = {
            'executed': [],
            'skipped': [],
            'errors': [],
            'space_freed_gb': 0
        }
        
        for suggestion in suggestions:
            if suggestion.get('automatic', False) and suggestion.get('risk') == 'low':
                try:
                    action = suggestion['action']
                    
                    if action == 'windows_cleanup':
                        # Executar limpeza do Windows
                        result = subprocess.run(
                            ['cleanmgr', '/sagerun:1'], 
                            capture_output=True, 
                            timeout=300
                        )
                        if result.returncode == 0:
                            results['executed'].append(suggestion)
                            results['space_freed_gb'] += suggestion.get('estimated_space_gb', 0)
                        else:
                            results['errors'].append(f"Falha na limpeza do Windows: {result.stderr}")
                    
                    elif action.startswith('clean_') and 'path' in suggestion:
                        # Limpeza de diretórios temporários
                        path = suggestion['path']
                        if os.path.exists(path):
                            initial_size = self._get_directory_size(path)
                            self._safe_clean_directory(path)
                            final_size = self._get_directory_size(path)
                            freed = (initial_size - final_size) / (1024**3)
                            
                            results['executed'].append(suggestion)
                            results['space_freed_gb'] += freed
                            
                            self._log_action(
                                f"Limpeza de {path}: {freed:.2f}GB liberados", 
                                "SUCCESS"
                            )
                    
                except Exception as e:
                    results['errors'].append(f"Erro em {suggestion['action']}: {e}")
                    self._log_action(f"Erro em {suggestion['action']}: {e}", "ERROR")
            else:
                results['skipped'].append(suggestion)
        
        self._log_action(
            f"Limpeza concluída: {results['space_freed_gb']:.2f}GB liberados", 
            "SUCCESS"
        )
        
        return results
    
    def _get_directory_size(self, directory: str) -> int:
        """Calcula tamanho de um diretório em bytes."""
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        continue
        except Exception:
            pass
        return total_size
    
    def _safe_clean_directory(self, directory: str, max_age_days: int = 7):
        """Limpa diretório de forma segura (apenas arquivos antigos)."""
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_age = current_time - os.path.getmtime(file_path)
                        
                        if file_age > max_age_seconds:
                            os.remove(file_path)
                    except (OSError, PermissionError):
                        continue
        except Exception as e:
            self._log_action(f"Erro na limpeza segura de {directory}: {e}", "WARNING")
    
    def generate_space_report(self) -> str:
        """Gera relatório completo de espaço em disco."""
        drives = self.analysis_results.get('drives', [])
        suggestions = self.suggest_cleanup_actions()
        
        report = f'''
# Relatório de Espaço em Disco - GLPI Dashboard
## Análise Completa e Recomendações

**Data**: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}  
**Status**: {'✅ Espaço Adequado' if any(d['free_gb'] > 50 for d in drives) else '⚠️ Espaço Crítico'}

## 💾 Análise de Unidades

'''
        
        for drive in drives:
            status = "✅" if drive['free_gb'] > 50 else "⚠️" if drive['free_gb'] > 10 else "❌"
            report += f'''
### Drive {drive['letter']}:
- **Espaço Total**: {drive['total_gb']:.1f}GB
- **Espaço Usado**: {drive['used_gb']:.1f}GB ({drive['usage_percent']:.1f}%)
- **Espaço Livre**: {drive['free_gb']:.1f}GB {status}
- **Adequado para Cache**: {'✅ Sim' if drive['suitable_for_cache'] else '❌ Não'}

'''
        
        report += '''
## 🧹 Sugestões de Limpeza

'''
        
        total_potential = sum(s.get('estimated_space_gb', 0) for s in suggestions)
        report += f"**Espaço Potencial a Liberar**: {total_potential:.1f}GB\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            risk_emoji = {'low': '✅', 'medium': '⚠️', 'high': '❌'}[suggestion.get('risk', 'medium')]
            auto_emoji = '🤖' if suggestion.get('automatic', False) else '👤'
            
            report += f'''
### {i}. {suggestion['description']}
- **Espaço Estimado**: {suggestion.get('estimated_space_gb', 0):.1f}GB
- **Risco**: {risk_emoji} {suggestion.get('risk', 'medium').title()}
- **Execução**: {auto_emoji} {'Automática' if suggestion.get('automatic', False) else 'Manual'}
'''
            
            if 'path' in suggestion:
                report += f"- **Caminho**: `{suggestion['path']}`\n"
            if 'command' in suggestion and suggestion['command'] != 'manual':
                report += f"- **Comando**: `{suggestion['command']}`\n"
        
        report += f'''

## 🎯 Plano de Ação Recomendado

### Imediato (Automático)
1. Executar limpeza do Windows (`cleanmgr`)
2. Limpar caches temporários seguros
3. Configurar cache alternativo em drive adequado

### Manual (Revisão Necessária)
1. Revisar arquivos grandes identificados
2. Mover dados não essenciais para armazenamento externo
3. Desinstalar programas não utilizados

## 📊 Configuração de Cache Alternativo

'''
        
        suitable_drives = [d for d in drives if d['suitable_for_cache'] and d['letter'] != 'C']
        if suitable_drives:
            best_drive = max(suitable_drives, key=lambda x: x['free_gb'])
            report += f'''
**Drive Recomendado**: {best_drive['letter']}: ({best_drive['free_gb']:.1f}GB livres)

```bash
# Configurar variáveis de ambiente
set TRANSFORMERS_CACHE={best_drive['letter']}:\\ai_models_cache\\transformers
set HF_HOME={best_drive['letter']}:\\ai_models_cache\\huggingface
set TORCH_HOME={best_drive['letter']}:\\ai_models_cache\\torch
```
'''
        else:
            report += "❌ Nenhum drive alternativo adequado encontrado\n"
        
        report += f'''

## 🚀 Próximos Passos

1. **Executar limpeza automática**: `python scripts/disk_space_manager.py --cleanup`
2. **Configurar cache alternativo**: `python scripts/disk_space_manager.py --setup-cache`
3. **Verificar espaço liberado**: `python scripts/quick_gpu_check.py`
4. **Continuar instalação IA**: Após liberar espaço suficiente

---
**Gerado por**: DiskSpaceManager v1.0  
**Projeto**: GLPI Dashboard - Integração GPU
'''
        
        return report
    
    def run_full_analysis(self) -> Dict:
        """Executa análise completa de espaço em disco."""
        self._log_action("🔍 Iniciando análise completa de espaço em disco...")
        
        # Análise de drives
        drives = self.analyze_disk_usage()
        
        # Análise de arquivos temporários
        temp_analysis = self.analyze_temp_directories()
        
        # Sugestões de limpeza
        suggestions = self.suggest_cleanup_actions()
        
        # Configuração de cache alternativo
        cache_path = self.setup_alternative_cache()
        
        # Gerar relatório
        report = self.generate_space_report()
        
        # Salvar relatório
        report_path = "disk_space_analysis_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self._log_action(f"📊 Relatório salvo em: {report_path}", "SUCCESS")
        
        results = {
            'drives': drives,
            'temp_analysis': temp_analysis,
            'suggestions': suggestions,
            'cache_path': cache_path,
            'report_path': report_path,
            'total_free_space_gb': sum(d['free_gb'] for d in drives),
            'space_adequate': any(d['free_gb'] > 50 for d in drives)
        }
        
        return results

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador de Espaço em Disco - GLPI Dashboard')
    parser.add_argument('--cleanup', action='store_true', help='Executar limpeza automática')
    parser.add_argument('--setup-cache', action='store_true', help='Configurar cache alternativo')
    parser.add_argument('--analyze-only', action='store_true', help='Apenas analisar (sem ações)')
    
    args = parser.parse_args()
    
    manager = DiskSpaceManager()
    
    try:
        print("🔧 Gerenciador de Espaço em Disco - GLPI Dashboard")
        print("=" * 55)
        
        # Análise completa
        results = manager.run_full_analysis()
        
        if args.cleanup:
            print("\n🧹 Executando limpeza automática...")
            cleanup_results = manager.execute_safe_cleanup(results['suggestions'])
            print(f"✅ Limpeza concluída: {cleanup_results['space_freed_gb']:.2f}GB liberados")
        
        elif args.setup_cache:
            print("\n📁 Configurando cache alternativo...")
            cache_path = manager.setup_alternative_cache()
            if cache_path:
                print(f"✅ Cache configurado em: {cache_path}")
            else:
                print("❌ Não foi possível configurar cache alternativo")
        
        elif args.analyze_only:
            print("\n📊 Análise concluída - verifique o relatório gerado")
        
        else:
            # Modo interativo
            print(f"\n📊 Análise concluída:")
            print(f"- Espaço total livre: {results['total_free_space_gb']:.1f}GB")
            print(f"- Espaço adequado: {'✅ Sim' if results['space_adequate'] else '❌ Não'}")
            print(f"- Relatório: {results['report_path']}")
            
            if not results['space_adequate']:
                print("\n⚠️ Espaço insuficiente detectado!")
                response = input("Executar limpeza automática? (s/N): ")
                if response.lower() in ['s', 'sim', 'y', 'yes']:
                    cleanup_results = manager.execute_safe_cleanup(results['suggestions'])
                    print(f"✅ Limpeza concluída: {cleanup_results['space_freed_gb']:.2f}GB liberados")
        
        print("\n✅ Operação concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n❌ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())