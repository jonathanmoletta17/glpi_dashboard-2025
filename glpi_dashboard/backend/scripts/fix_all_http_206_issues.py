#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o problema HTTP 206 em todos os arquivos do projeto
Substitui todas as ocorrências de response.ok por verificações explícitas de status code
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

def backup_file(file_path):
    """Cria backup do arquivo antes da modificação"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path

def fix_response_ok_patterns(content):
    """Corrige os padrões de response.ok no conteúdo"""
    fixes_applied = 0
    
    # Padrão 1: if not response.ok:
    pattern1 = r'if not (\w+)\.ok:'
    replacement1 = r'if \1.status_code not in [200, 206]:'
    content, count1 = re.subn(pattern1, replacement1, content)
    fixes_applied += count1
    
    # Padrão 2: if response.ok:
    pattern2 = r'if (\w+)\.ok:'
    replacement2 = r'if \1.status_code in [200, 206]:'
    content, count2 = re.subn(pattern2, replacement2, content)
    fixes_applied += count2
    
    # Padrão 3: if not response or not response.ok:
    pattern3 = r'if not (\w+) or not \1\.ok:'
    replacement3 = r'if not \1 or \1.status_code not in [200, 206]:'
    content, count3 = re.subn(pattern3, replacement3, content)
    fixes_applied += count3
    
    # Padrão 4: if response and response.ok:
    pattern4 = r'if (\w+) and \1\.ok:'
    replacement4 = r'if \1 and \1.status_code in [200, 206]:'
    content, count4 = re.subn(pattern4, replacement4, content)
    fixes_applied += count4
    
    # Padrão 5: if response and response.ok and "Content-Range" in response.headers:
    pattern5 = r'if (\w+) and \1\.ok and "Content-Range" in \1\.headers:'
    replacement5 = r'if \1 and \1.status_code in [200, 206] and "Content-Range" in \1.headers:'
    content, count5 = re.subn(pattern5, replacement5, content)
    fixes_applied += count5
    
    return content, fixes_applied, [count1, count2, count3, count4, count5]

def fix_file(file_path):
    """Corrige um arquivo específico"""
    print(f"\n🔧 Processando: {file_path}")
    
    try:
        # Ler conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar correções
        fixed_content, fixes_count, pattern_counts = fix_response_ok_patterns(content)
        
        if fixes_count > 0:
            # Criar backup
            backup_path = backup_file(file_path)
            
            # Escrever arquivo corrigido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"📊 Correções aplicadas:")
            print(f"   - Padrão 'if not response.ok:': {pattern_counts[0]}")
            print(f"   - Padrão 'if response.ok:': {pattern_counts[1]}")
            print(f"   - Padrão 'if not response or not response.ok:': {pattern_counts[2]}")
            print(f"   - Padrão 'if response and response.ok:': {pattern_counts[3]}")
            print(f"   - Padrão 'if response and response.ok and Content-Range:': {pattern_counts[4]}")
            print(f"   - Total: {fixes_count}")
            
            # Validar sintaxe Python
            try:
                compile(fixed_content, file_path, 'exec')
                print("✅ Sintaxe Python validada com sucesso")
                return True, fixes_count
            except SyntaxError as e:
                print(f"❌ Erro de sintaxe detectado: {e}")
                print("🔄 Restaurando backup...")
                shutil.copy2(backup_path, file_path)
                return False, 0
                
        else:
            print("ℹ️ Nenhuma correção necessária")
            return True, 0
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False, 0

def main():
    """Função principal"""
    print("🔧 Iniciando correção do problema HTTP 206 em todos os arquivos...")
    
    # Lista de arquivos para corrigir
    files_to_fix = [
        "mapping/map_glpi_entities.py",
        "optimization/assignment_based_technician_solution.py"
    ]
    
    total_fixes = 0
    successful_files = 0
    failed_files = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            success, fixes = fix_file(file_path)
            if success:
                successful_files += 1
                total_fixes += fixes
            else:
                failed_files += 1
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
            failed_files += 1
    
    print(f"\n📊 Resumo da correção:")
    print(f"   - Arquivos processados com sucesso: {successful_files}")
    print(f"   - Arquivos com falha: {failed_files}")
    print(f"   - Total de correções aplicadas: {total_fixes}")
    
    if failed_files == 0:
        print("\n🎉 Todas as correções foram aplicadas com sucesso!")
        print("📋 Próximos passos:")
        print("   1. Testar o dashboard")
        print("   2. Verificar logs de erro")
        print("   3. Validar métricas")
        return True
    else:
        print(f"\n⚠️ {failed_files} arquivo(s) falharam na correção")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Algumas correções falharam. Verifique os logs acima.")