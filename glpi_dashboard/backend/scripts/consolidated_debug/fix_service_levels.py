#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir os service_levels no GLPIService
Identifica grupos corretos e atualiza a configuração
"""

import json
import sys
import os
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'glpi_dashboard', 'backend'))

from services.glpi_service import GLPIService

def main():
    print("🔧 Corrigindo configuração de service_levels...")
    print()
    
    try:
        # Inicializar serviço
        glpi_service = GLPIService()
        
        # Autenticar
        print("🔐 Autenticando...")
        glpi_service._ensure_authenticated()
        print("✅ Autenticação realizada com sucesso")
        print()
        
        # Buscar todos os grupos
        print("🔍 Buscando grupos no GLPI...")
        response = glpi_service._make_authenticated_request(
            "GET",
            f"{glpi_service.glpi_url}/Group",
            params={"range": "0-200"}
        )
        
        if not response or not response.ok:
            print(f"❌ Erro ao buscar grupos: {response.status_code if response else 'None'}")
            return
        
        groups_data = response.json()
        if not isinstance(groups_data, list):
            print("❌ Formato de resposta inválido")
            return
        
        print(f"📊 Total de grupos encontrados: {len(groups_data)}")
        print()
        
        # Procurar grupos que contenham N1, N2, N3, N4
        level_groups = {}
        potential_groups = []
        
        for group in groups_data:
            if isinstance(group, dict) and 'id' in group and 'name' in group:
                group_id = group['id']
                group_name = group['name']
                
                # Procurar por padrões de nível
                name_upper = group_name.upper()
                if any(level in name_upper for level in ['N1', 'N2', 'N3', 'N4']):
                    potential_groups.append({
                        'id': group_id,
                        'name': group_name
                    })
                    
                    # Tentar identificar o nível
                    for level in ['N1', 'N2', 'N3', 'N4']:
                        if level in name_upper:
                            if level not in level_groups:
                                level_groups[level] = []
                            level_groups[level].append({
                                'id': group_id,
                                'name': group_name
                            })
        
        print("🎯 Grupos potenciais para níveis de serviço:")
        for group in potential_groups:
            print(f"   - ID {group['id']}: {group['name']}")
        print()
        
        print("📋 Grupos por nível identificado:")
        for level, groups in level_groups.items():
            print(f"   {level}:")
            for group in groups:
                print(f"      - ID {group['id']}: {group['name']}")
        print()
        
        # Sugerir configuração correta
        suggested_config = {}
        for level in ['N1', 'N2', 'N3', 'N4']:
            if level in level_groups and level_groups[level]:
                # Pegar o primeiro grupo encontrado para cada nível
                suggested_config[level] = level_groups[level][0]['id']
                print(f"✅ {level}: ID {level_groups[level][0]['id']} - {level_groups[level][0]['name']}")
            else:
                print(f"❌ {level}: Nenhum grupo encontrado")
        
        print()
        print("🔧 Configuração sugerida para service_levels:")
        print(json.dumps(suggested_config, indent=2))
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fix_service_levels_{timestamp}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_groups": len(groups_data),
            "potential_groups": potential_groups,
            "groups_by_level": level_groups,
            "current_config": glpi_service.service_levels,
            "suggested_config": suggested_config
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados salvos em: {filename}")
        
        # Mostrar como aplicar a correção
        if suggested_config:
            print()
            print("🛠️ Para aplicar a correção, edite o arquivo:")
            print("   glpi_dashboard/backend/services/glpi_service.py")
            print()
            print("   Substitua a seção service_levels por:")
            print("   self.service_levels = {")
            for level, group_id in suggested_config.items():
                print(f'       "{level}": {group_id},  # {next(g["name"] for g in level_groups[level] if g["id"] == group_id)}')
            print("   }")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()