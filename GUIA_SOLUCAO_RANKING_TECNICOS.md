# 🎯 **GUIA DE SOLUÇÃO: RANKING DE TÉCNICOS**

## 📋 **PROBLEMAS COMUNS E SOLUÇÕES**

### **🔴 PROBLEMA 1: TÉCNICOS N3 COM ZERO TICKETS**

#### **Sintomas:**
- Técnicos N3 aparecem com 0 tickets no ranking
- Técnicos N1, N2 e N4 aparecem normalmente
- Dados não correspondem à realidade do GLPI

#### **Causa:**
- Limite de range `'0-1000'` na API GLPI
- Técnicos N3 têm mais de 1000 tickets
- API retorna apenas os primeiros 1000 registros

#### **Solução:**
```python
# Localizar em: glpi_dashboard/backend/services/glpi_service.py
# Método: _get_technician_metrics_corrected()

# ANTES (Problemático)
'range': '0-1000'

# DEPOIS (Correto)
'range': '0-5000'  # Aumentar para 5000+ tickets
```

#### **Verificação:**
- Verificar se técnicos N3 agora aparecem com dados
- Confirmar se os números correspondem ao GLPI
- Validar se o processamento está completo

---

### **🔴 PROBLEMA 2: NÍVEIS DE ATENDIMENTO INCORRETOS**

#### **Sintomas:**
- Técnicos aparecem com nível N1 quando deveriam ser N2/N3/N4
- Níveis não correspondem à realidade do GLPI
- Inconsistências no mapeamento

#### **Causa:**
- Nomes incorretos nos arrays de mapeamento
- Falta de acentos e caracteres especiais
- Nomes não correspondem exatamente ao GLPI

#### **Solução:**
```python
# Localizar em: glpi_dashboard/backend/services/glpi_service.py
# Método: _get_technician_level_by_name_fallback()

# Verificar e corrigir arrays de nomes:
n1_names = [
    "gabriel andrade da conceicao",
    "nicolas fernando muniz nunez",
]

n2_names = [
    "alessandro carbonera vieira",
    "jonathan nascimento moletta",
    "thales vinicius paz leite",
    "leonardo trojan repiso riela",
    "edson joel dos santos silva",
    "luciano marcelino da silva",
    "joao pedro wilson dias",  # ✅ ADICIONAR SE NECESSÁRIO
]

n3_names = [
    "anderson da silva morim de oliveira",
    "silvio godinho valim",
    "jorge antonio vicente júnior",  # ✅ COM ACENTO
    "pablo hebling guimaraes",
    "miguelangelo ferreira",
]

n4_names = [
    "gabriel silva machado",
    "luciano de araujo silva",
    "wagner mengue",
    "paulo cesar pedo nunes",
    "alexandre rovinski almoarqueg",
]
```

#### **Verificação:**
- Comparar nomes com o GLPI (Tools > Users)
- Verificar acentos e caracteres especiais
- Testar mapeamento de níveis

---

## 🔍 **DIAGNÓSTICO RÁPIDO**

### **Passo 1: Verificar Técnicos N3**
```bash
# Fazer requisição para o backend
curl -X GET "http://localhost:5000/api/technicians/ranking" | jq '.data[] | select(.level == "N3")'
```

**Resultado esperado:**
- Todos os técnicos N3 devem ter tickets > 0
- Números devem corresponder ao GLPI

### **Passo 2: Verificar Níveis**
```bash
# Verificar se os níveis estão corretos
curl -X GET "http://localhost:5000/api/technicians/ranking" | jq '.data[] | {name: .name, level: .level}'
```

**Resultado esperado:**
- Níveis devem corresponder à realidade do GLPI
- Nenhum técnico deve estar com nível N1 incorreto

### **Passo 3: Verificar Logs**
```bash
# Verificar logs do backend
tail -f glpi_dashboard/backend/logs/app.log | grep "TÉCNICO"
```

**Resultado esperado:**
- Logs devem mostrar processamento completo
- Sem erros de timeout ou limite

---

## 🚀 **IMPLEMENTAÇÃO DE CORREÇÕES**

### **Correção 1: Aumentar Limite de Range**

1. **Localizar arquivo:**
   ```
   glpi_dashboard/backend/services/glpi_service.py
   ```

2. **Localizar método:**
   ```python
   def _get_technician_metrics_corrected(self, tecnico_id: str) -> Dict[str, Any]:
   ```

3. **Alterar linha:**
   ```python
   # ANTES
   'range': '0-1000'

   # DEPOIS
   'range': '0-5000'
   ```

4. **Reiniciar backend:**
   ```bash
   cd glpi_dashboard
   docker-compose restart backend
   ```

### **Correção 2: Atualizar Mapeamento de Níveis**

1. **Localizar método:**
   ```python
   def _get_technician_level_by_name_fallback(self, user_id: str) -> str:
   ```

2. **Verificar arrays de nomes:**
   - Comparar com GLPI (Tools > Users)
   - Adicionar nomes faltantes
   - Corrigir acentos e caracteres especiais

3. **Testar mapeamento:**
   ```python
   # Adicionar logs para debug
   self.logger.info(f"Técnico {tech_name} mapeado para {level}")
   ```

---

## 📊 **VALIDAÇÃO FINAL**

### **Checklist de Validação:**

- [ ] Todos os técnicos N3 aparecem no ranking
- [ ] Técnicos N3 têm números de tickets > 0
- [ ] Níveis de atendimento estão corretos
- [ ] Números correspondem ao GLPI
- [ ] Logs não mostram erros
- [ ] Performance está adequada

### **Teste de Regressão:**

1. **Executar teste comparativo:**
   ```bash
   python teste_comparativo_ranking.py
   ```

2. **Verificar se todos os técnicos aparecem:**
   ```bash
   curl -X GET "http://localhost:5000/api/technicians/ranking" | jq '.data | length'
   ```

3. **Confirmar dados corretos:**
   - Comparar com GLPI
   - Verificar níveis
   - Validar números

---

## 🎯 **MANUTENÇÃO PREVENTIVA**

### **Monitoramento Contínuo:**

1. **Verificar periodicamente:**
   - Se novos técnicos precisam ser adicionados
   - Se os nomes no GLPI mudaram
   - Se o volume de tickets aumentou

2. **Logs de monitoramento:**
   ```python
   # Adicionar logs de monitoramento
   self.logger.info(f"Processando técnico {tech_id}: {total_tickets} tickets")
   ```

3. **Validação automática:**
   - Implementar testes automatizados
   - Verificar consistência dos dados
   - Alertar sobre problemas

### **Atualizações Futuras:**

1. **Novos técnicos:**
   - Adicionar aos arrays de mapeamento
   - Verificar níveis no GLPI
   - Testar mapeamento

2. **Mudanças no GLPI:**
   - Verificar se nomes mudaram
   - Atualizar mapeamentos
   - Validar funcionamento

3. **Otimizações:**
   - Considerar processamento em páginas
   - Implementar cache inteligente
   - Melhorar performance

---

## 🎯 **CONCLUSÃO**

**Este guia fornece soluções para os problemas mais comuns do ranking de técnicos:**

1. ✅ **Técnicos N3 com zero tickets** → Aumentar limite de range
2. ✅ **Níveis de atendimento incorretos** → Corrigir mapeamento de nomes
3. ✅ **Dados não correspondem ao GLPI** → Validar e corrigir mapeamentos

**Seguindo este guia, o ranking de técnicos funcionará corretamente e os dados corresponderão à realidade do GLPI.** 🎯✨
