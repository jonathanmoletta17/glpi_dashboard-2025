#!/usr/bin/env python3
"""
Adaptador ASGI para a aplicação Flask GLPI Dashboard
Permite executar Flask com servidores ASGI como Uvicorn
"""

from asgiref.wsgi import WsgiToAsgi
from app import app

# Converte a aplicação Flask WSGI para ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("asgi:asgi_app", host="0.0.0.0", port=8000, reload=True)