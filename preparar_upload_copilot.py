#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparar Upload para Copilot
Prepara a base de conhecimento para upload no Copilot
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def preparar_upload_copilot():
    """Prepara a base de conhecimento para upload no Copilot"""
    
    print("🤖 PREPARANDO UPLOAD PARA COPILOT")
    print("=" * 50)
    
    # Diretórios
    base_original = Path("base_conhecimento_copilot_completa_final")
    base_upload = Path("base_conhecimento_copilot_upload_final")
    
    if not base_original.exists():
        print("❌ Base de conhecimento original não encontrada!")
        return
    
    # Limpar diretório de upload se existir
    if base_upload.exists():
        shutil.rmtree(base_upload)
    
    # Criar estrutura de upload
    base_upload.mkdir(exist_ok=True)
    
    print("📁 Copiando arquivos...")
    
    # Copiar tickets resolvidos
    tickets_orig = base_original / "tickets_resolvidos"
    tickets_dest = base_upload / "tickets_resolvidos"
    
    if tickets_orig.exists():
        shutil.copytree(tickets_orig, tickets_dest)
        print(f"   ✅ Tickets copiados: {tickets_dest}")
    
    # Copiar soluções padrão
    solucoes_orig = base_original / "solucoes_padrao"
    solucoes_dest = base_upload / "solucoes_padrao"
    
    if solucoes_orig.exists():
        shutil.copytree(solucoes_orig, solucoes_dest)
        print(f"   ✅ Soluções padrão copiadas: {solucoes_dest}")
    
    # Copiar metadados
    metadados_orig = base_original / "metadados"
    metadados_dest = base_upload / "metadados"
    
    if metadados_orig.exists():
        shutil.copytree(metadados_orig, metadados_dest)
        print(f"   ✅ Metadados copiados: {metadados_dest}")
    
    # Criar arquivo de índice para o Copilot
    criar_indice_copilot(base_upload)
    
    # Criar arquivo de instruções
    criar_instrucoes_copilot(base_upload)
    
    # Criar resumo da base
    criar_resumo_base(base_upload)
    
    print(f"\n✅ PREPARAÇÃO CONCLUÍDA!")
    print(f"📁 Base pronta para upload: {base_upload}")
    print(f"📊 Total de arquivos: {contar_arquivos(base_upload)}")
    
    # Mostrar estrutura
    print(f"\n📋 ESTRUTURA CRIADA:")
    mostrar_estrutura(base_upload)

def criar_indice_copilot(base_path: Path):
    """Cria arquivo de índice para o Copilot"""
    
    indice = {
        "nome": "Base de Conhecimento GLPI - Casa Civil",
        "versao": "1.0",
        "data_criacao": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "descricao": "Base de conhecimento extraída do GLPI com 1.412 tickets resolvidos",
        "categorias": {
            "rede_wifi": "Problemas de rede e WiFi",
            "sistemas_configuracoes": "Configurações de sistemas",
            "hardware_computador": "Problemas de hardware de computador",
            "software_aplicativos": "Problemas de software e aplicativos",
            "hardware_impressora": "Problemas de impressoras",
            "sistemas_email": "Problemas de email",
            "sistemas_acesso": "Problemas de acesso e login",
            "geral": "Problemas gerais",
            "rede_vpn": "Problemas de VPN"
        },
        "estatisticas": {
            "total_tickets": 1412,
            "categorias_principais": 9,
            "tecnico_principal": "N3 (73%)",
            "periodo": "2023-2025"
        },
        "instrucoes_uso": [
            "Use esta base para responder perguntas sobre problemas de TI",
            "Cada arquivo contém um problema e sua solução",
            "Categorize problemas por tipo antes de responder",
            "Sempre forneça soluções passo a passo",
            "Se não encontrar solução específica, sugira contato técnico"
        ]
    }
    
    indice_file = base_path / "indice_copilot.json"
    with open(indice_file, 'w', encoding='utf-8') as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Índice criado: {indice_file}")

def criar_instrucoes_copilot(base_path: Path):
    """Cria arquivo de instruções para o Copilot"""
    
    instrucoes = """# INSTRUÇÕES PARA O COPILOT

## FUNÇÃO PRINCIPAL
Você é um assistente especializado em suporte técnico de TI para servidores da Casa Civil. Sua função é auxiliar com dúvidas e problemas relacionados a equipamentos de TI, redes, sistemas e software.

## BASE DE CONHECIMENTO
Esta base contém 1.412 tickets resolvidos do GLPI, organizados por categoria:
- Rede/WiFi: 424 tickets
- Sistemas/Configurações: 380 tickets  
- Hardware/Computador: 200 tickets
- Software/Aplicativos: 173 tickets
- Hardware/Impressora: 82 tickets
- Sistemas/Email: 77 tickets
- Sistemas/Acesso: 68 tickets
- Geral: 6 tickets
- Rede/VPN: 2 tickets

## INSTRUÇÕES DE USO
1. **Identifique o problema** do usuário
2. **Categorize** por tipo (rede, hardware, software, etc.)
3. **Busque** na base de conhecimento casos similares
4. **Forneça solução** baseada nos tickets resolvidos
5. **Inclua passos detalhados** para resolução
6. **Sugira prevenção** se aplicável
7. **Indique contato técnico** se necessário

## FORMATO DE RESPOSTA
1. **Identificação do problema**
2. **Solução baseada em casos similares**
3. **Passos detalhados**
4. **Dicas de prevenção**
5. **Contato técnico se necessário**

## LINGUAGEM
- Use linguagem simples e compreensível
- Evite jargões técnicos desnecessários
- Seja direto e objetivo
- Mantenha tom profissional mas acessível

## LIMITAÇÕES
- Se não encontrar solução específica, sugira contato com a equipe técnica
- Sempre baseie respostas na base de conhecimento
- Não invente soluções não validadas
- Priorize soluções testadas e aprovadas
"""
    
    instrucoes_file = base_path / "INSTRUCOES_COPILOT.md"
    with open(instrucoes_file, 'w', encoding='utf-8') as f:
        f.write(instrucoes)
    
    print(f"   ✅ Instruções criadas: {instrucoes_file}")

def criar_resumo_base(base_path: Path):
    """Cria resumo da base de conhecimento"""
    
    resumo = """# RESUMO DA BASE DE CONHECIMENTO GLPI

## ESTATÍSTICAS GERAIS
- **Total de tickets:** 1.412
- **Período:** 2023-2025
- **Taxa de sucesso:** 100%
- **Categorias:** 9 principais

## DISTRIBUIÇÃO POR CATEGORIA
| Categoria | Quantidade | Percentual |
|-----------|------------|------------|
| Rede/WiFi | 424 | 30.0% |
| Sistemas/Configurações | 380 | 26.9% |
| Hardware/Computador | 200 | 14.2% |
| Software/Aplicativos | 173 | 12.3% |
| Hardware/Impressora | 82 | 5.8% |
| Sistemas/Email | 77 | 5.5% |
| Sistemas/Acesso | 68 | 4.8% |
| Geral | 6 | 0.4% |
| Rede/VPN | 2 | 0.1% |

## DISTRIBUIÇÃO POR TÉCNICO
- **N3 (Nível 3):** 1.031 tickets (73.0%)
- **N2 (Nível 2):** 130 tickets (9.2%)
- **N1 (Nível 1):** 34 tickets (2.4%)
- **Múltiplos níveis:** 247 tickets (17.5%)

## QUALIDADE DOS DADOS
- ✅ Todos os tickets têm soluções válidas
- ✅ Categorização automática implementada
- ✅ Metadados completos
- ✅ Formato padronizado para Copilot
- ✅ Limpeza de HTML aplicada

## ESTRUTURA DE ARQUIVOS
Cada arquivo Markdown contém:
- Título do problema
- Descrição detalhada
- Solução implementada
- Técnico responsável
- Data de resolução
- Tags para categorização
- Metadados completos
- Instruções para o Copilot

## COMO USAR
1. Identifique o tipo de problema
2. Navegue para a categoria apropriada
3. Busque por palavras-chave similares
4. Use a solução como base para resposta
5. Adapte conforme necessário
"""
    
    resumo_file = base_path / "RESUMO_BASE.md"
    with open(resumo_file, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(f"   ✅ Resumo criado: {resumo_file}")

def contar_arquivos(diretorio: Path) -> int:
    """Conta total de arquivos em um diretório"""
    
    total = 0
    for item in diretorio.rglob('*'):
        if item.is_file():
            total += 1
    
    return total

def mostrar_estrutura(diretorio: Path, nivel: int = 0):
    """Mostra estrutura de diretórios"""
    
    indent = "  " * nivel
    
    for item in sorted(diretorio.iterdir()):
        if item.is_dir():
            print(f"{indent}📁 {item.name}/")
            mostrar_estrutura(item, nivel + 1)
        else:
            tamanho = item.stat().st_size
            if tamanho > 1024:
                tamanho_str = f"{tamanho // 1024}KB"
            else:
                tamanho_str = f"{tamanho}B"
            print(f"{indent}📄 {item.name} ({tamanho_str})")

def main():
    """Função principal"""
    preparar_upload_copilot()

if __name__ == "__main__":
    main()
