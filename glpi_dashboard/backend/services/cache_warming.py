import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


class CacheWarming:
    """Serviço para aquecimento de cache."""

    def __init__(self):
        self.logger = logger
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    def start(self):
        """Inicia o aquecimento de cache."""
        if self._running:
            self.logger.warning("Cache warming já está em execução")
            return

        self.logger.info("Iniciando cache warming")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._warming_loop, daemon=True)
        self._thread.start()
        self._running = True

    def stop(self):
        """Para o aquecimento de cache."""
        if not self._running:
            return

        self.logger.info("Parando cache warming")
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        self._running = False

    def _warming_loop(self):
        """Loop principal do aquecimento de cache."""
        while not self._stop_event.is_set():
            try:
                # Aqui você pode implementar a lógica de aquecimento
                # Por exemplo, fazer chamadas para endpoints críticos
                self.logger.debug("Executando ciclo de aquecimento de cache")

                # Aguarda 5 minutos antes do próximo ciclo
                if self._stop_event.wait(300):  # 300 segundos = 5 minutos
                    break

            except Exception as e:
                self.logger.error(f"Erro no aquecimento de cache: {e}")
                # Aguarda 1 minuto antes de tentar novamente
                if self._stop_event.wait(60):
                    break


# Instância global
_cache_warming = CacheWarming()


def start_cache_warming():
    """Inicia o aquecimento de cache."""
    _cache_warming.start()


def stop_cache_warming():
    """Para o aquecimento de cache."""
    _cache_warming.stop()
