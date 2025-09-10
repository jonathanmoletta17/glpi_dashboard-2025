# Script de Extração Completa GLPI

Este script extrai **todos os dados** do GLPI (tickets, usuários, técnicos, solicitantes) com paginação automática e salva em arquivos CSV separados.

## 🎯 Características

- ✅ **Extração completa**: Mais de 10.000 tickets e todos os usuários
- ✅ **Paginação automática**: Não há limite de registros
- ✅ **Todos os campos**: Extrai todos os campos disponíveis na API
- ✅ **Arquivos separados**: CSV organizados por entidade
- ✅ **Retry automático**: Tratamento robusto de erros
- ✅ **Logging detalhado**: Acompanhamento completo do processo
- ✅ **Estatísticas**: Relatório final com métricas

## 📋 Pré-requisitos

1. **Python 3.7+**
2. **API GLPI v10** habilitada
3. **Tokens válidos** (User Token e App Token)
4. **Dependências Python**:
   ```bash
   pip install -r requirements_extractor.txt
   ```

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` ou configure as variáveis:

```bash
# Configurações obrigatórias do GLPI
GLPI_URL=http://seu-servidor-glpi/glpi/apirest.php
GLPI_USER_TOKEN=seu-user-token-aqui
GLPI_APP_TOKEN=seu-app-token-aqui
```

### 2. Verificar Tokens

- **User Token**: Token do usuário com permissões de leitura
- **App Token**: Token da aplicação configurado no GLPI
- **URL**: Deve terminar com `/apirest.php`

## 🚀 Execução

### Execução Simples
```bash
python scripts/glpi_complete_extractor.py
```

### Execução com Log Detalhado
```bash
python scripts/glpi_complete_extractor.py 2>&1 | tee extraction.log
```

## 📊 Arquivos Gerados

O script gera 4 arquivos CSV:

| Arquivo | Descrição | Conteúdo |
|---------|-----------|----------|
| `tickets.csv` | Todos os tickets | Tickets completos com todos os campos |
| `usuarios.csv` | Todos os usuários | Base completa de usuários |
| `tecnicos.csv` | Usuários técnicos | Filtro de usuários com perfis técnicos |
| `solicitantes.csv` | Usuários solicitantes | Usuários ativos (solicitantes) |

## 📈 Estatísticas

Ao final da execução, o script exibe:

```
============================================================
ESTATÍSTICAS DA EXTRAÇÃO GLPI
============================================================
Início: 2024-01-15 10:30:00
Fim: 2024-01-15 10:45:30
Duração: 0:15:30
Total de chamadas à API: 127

DADOS EXTRAÍDOS:
  • Tickets: 12,547
  • Usuários: 1,834
  • Técnicos: 19
  • Solicitantes: 1,834

ARQUIVOS GERADOS:
  • tickets.csv
  • usuarios.csv
  • tecnicos.csv
  • solicitantes.csv
============================================================
```

## 🔧 Configurações Avançadas

### Tamanho da Página
Por padrão, o script usa páginas de 1000 registros. Para ajustar:

```python
self.page_size = 500  # Reduzir se houver timeouts
```

### Timeout das Requisições
```python
response = self.session.get(url, headers=headers, params=params, timeout=120)
```

### Retry e Backoff
```python
self.max_retries = 5  # Aumentar para APIs instáveis
self.retry_delay = 3  # Aumentar delay base
```

## 🐛 Solução de Problemas

### Erro de Autenticação
```
Erro na autenticação: 401 Unauthorized
```
**Solução**: Verificar tokens e permissões no GLPI

### Timeout de Requisição
```
Tentativa 1 falhou para Ticket: Read timeout
```
**Solução**: Reduzir `page_size` ou aumentar `timeout`

### Memória Insuficiente
```
MemoryError: Unable to allocate array
```
**Solução**: Processar em lotes menores ou aumentar RAM

### API Rate Limiting
```
429 Too Many Requests
```
**Solução**: Aumentar `time.sleep()` entre requisições

## 📝 Logs

O script gera logs em:
- **Console**: Output em tempo real
- **Arquivo**: `glpi_extraction.log`

Nível de log configurável:
```python
logging.basicConfig(level=logging.DEBUG)  # Para debug detalhado
```

## 🎯 Uso para Treinamento Copilot

Os arquivos CSV gerados são otimizados para:

- ✅ **Formato estruturado**: Headers claros e dados consistentes
- ✅ **Encoding UTF-8**: Suporte completo a caracteres especiais
- ✅ **Campos expandidos**: Dropdowns expandidos para legibilidade
- ✅ **JSON aninhado**: Objetos complexos serializados adequadamente
- ✅ **Dados completos**: Sem truncamento ou limitações

## 🔒 Segurança

- ✅ Tokens não são logados
- ✅ Sessões são encerradas adequadamente
- ✅ Timeouts configurados para evitar travamentos
- ✅ Tratamento de erros sem exposição de dados sensíveis

## 📞 Suporte

Para problemas ou melhorias:
1. Verificar logs detalhados
2. Testar conectividade com GLPI
3. Validar permissões dos tokens
4. Ajustar configurações conforme ambiente

---

**Desenvolvido para extração completa e confiável de dados GLPI** 🚀
