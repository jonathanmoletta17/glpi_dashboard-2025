#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o problema HTTP 206 no GLPI Service
Substitui todas as ocorrências de response.ok por verificações explícitas de status code
"""

import os
import re
import shutil
from datetime import datetime

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
    
    print(f"📊 Correções aplicadas:")
    print(f"   - Padrão 'if not response.ok:': {count1}")
    print(f"   - Padrão 'if response.ok:': {count2}")
    print(f"   - Padrão 'if not response or not response.ok:': {count3}")
    print(f"   - Padrão 'if response and response.ok:': {count4}")
    print(f"   - Padrão 'if response and response.ok and Content-Range:': {count5}")
    print(f"   - Total: {fixes_applied}")
    
    return content, fixes_applied

def main():
    """Função principal"""
    print("🔧 Iniciando correção do problema HTTP 206...")
    
    # Caminho do arquivo principal
    glpi_service_path = "../services/glpi_service.py"
    
    # Verificar se o arquivo existe
    if not os.path.exists(glpi_service_path):
        print(f"❌ Arquivo não encontrado: {glpi_service_path}")
        return False
    
    try:
        # Criar backup
        backup_path = backup_file(glpi_service_path)
        
        # Ler conteúdo do arquivo
        with open(glpi_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 Arquivo lido: {len(content)} caracteres")
        
        # Aplicar correções
        fixed_content, fixes_count = fix_response_ok_patterns(content)
        
        if fixes_count > 0:
            # Escrever arquivo corrigido
            with open(glpi_service_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"✅ Arquivo corrigido com {fixes_count} alterações")
            print(f"💾 Backup disponível em: {backup_path}")
            
            # Validar sintaxe Python
            try:
                compile(fixed_content, glpi_service_path, 'exec')
                print("✅ Sintaxe Python validada com sucesso")
            except SyntaxError as e:
                print(f"❌ Erro de sintaxe detectado: {e}")
                print("🔄 Restaurando backup...")
                shutil.copy2(backup_path, glpi_service_path)
                return False
                
        else:
            print("ℹ️ Nenhuma correção necessária encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Correção concluída com sucesso!")
        print("📋 Próximos passos:")
        print("   1. Testar o dashboard")
        print("   2. Verificar logs de erro")
        print("   3. Validar métricas")
    else:
        print("\n❌ Correção falhou. Verifique os logs acima.")