#!/usr/bin/env python3
"""
Ponto de entrada ASGI para uvicorn
"""

from asgiref.wsgi import WsgiToAsgi
from app import app

# Converte a aplicação Flask para ASGI
asgi_app = WsgiToAsgi(app)

# Exporta como 'app' para uvicorn
app = asgi_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)