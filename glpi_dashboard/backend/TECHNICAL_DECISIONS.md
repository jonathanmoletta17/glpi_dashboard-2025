# Decisões Técnicas - GLPI Dashboard

## Otimização do HTML Decoder

### Problema Identificado
- O arquivo `html_decoder.py` utilizava a biblioteca `BeautifulSoup4` para processamento de HTML
- Análise do código mostrou que apenas 3 pontos no `glpi_service.py` utilizavam o método `clean_html_content`
- A funcionalidade era limitada a decodificação de entidades HTML e remoção de tags

### Solução Implementada
- **Substituição**: Criado novo arquivo `html_cleaner.py` usando apenas bibliotecas nativas do Python
- **Bibliotecas utilizadas**: `html.unescape()` e `re` (expressões regulares)
- **Funcionalidade mantida**: Decodificação de entidades HTML e remoção de tags HTML
- **Benefícios**: Redução de dependências externas e melhoria na performance

### Arquivos Modificados
- ✅ Criado: `backend/utils/html_cleaner.py`
- ✅ Atualizado: `backend/services/glpi_service.py` (substituição das importações)
- ✅ Removido: `backend/utils/html_decoder.py`

## Resolução de Problemas de Inicialização

### Problema Identificado
- Erros `TypeError: Flask.__call__() missing 1 required positional argument: 'start_response'`
- Erro `500 Internal Server Error` ao acessar endpoints
- **Causa raiz**: Incompatibilidade entre Flask (WSGI) e Uvicorn (ASGI)

### Solução Implementada
- **Adaptador WSGI-to-ASGI**: Criado arquivo `asgi.py` usando `WsgiToAsgi` do `asgiref`
- **Dependências adicionadas**: `uvicorn==0.24.0` e `asgiref==3.7.2` no `requirements.txt`
- **Novo ponto de entrada**: `python -m uvicorn asgi:asgi_app --reload --host 0.0.0.0 --port 8000`

### Arquivos Criados/Modificados
- ✅ Criado: `backend/asgi.py`
- ✅ Atualizado: `backend/requirements.txt`
- ✅ Instaladas dependências necessárias

## Status Atual
- ✅ Servidor backend funcionando corretamente com Uvicorn
- ✅ Logs de inicialização limpos (sem os 18 erros anteriores)
- ✅ Aplicação Flask adaptada para ASGI
- ✅ HTML decoder otimizado e funcional

## Próximos Passos Recomendados
1. Monitorar performance da aplicação com as otimizações
2. Considerar migração completa para FastAPI no futuro (se necessário)
3. Revisar outras dependências que podem ser otimizadas

---
*Documentação criada em: Janeiro 2025*
*Última atualização: Janeiro 2025*
