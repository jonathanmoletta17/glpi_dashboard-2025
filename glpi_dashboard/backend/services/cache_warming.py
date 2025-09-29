import logging
import threading
import time
from typing import Dict, List, Optional, Tuple
import requests
from datetime import datetime, timedelta

from config.settings import get_cache_config, active_config
from utils.performance import performance_monitor

logger = logging.getLogger(__name__)


class CacheWarming:
    """Serviço inteligente para aquecimento de cache do GLPI Dashboard."""

    def __init__(self):
        self.logger = logger
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        self._config = active_config()
        self._base_url = f"http://{self._config.HOST}:{self._config.PORT}/api"
        self._warming_stats = {
            "cycles_completed": 0,
            "endpoints_warmed": 0,
            "errors": 0,
            "last_run": None,
            "average_cycle_time": 0.0
        }

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

    def _get_critical_endpoints(self) -> List[Tuple[str, Dict]]:
        """Retorna lista de endpoints críticos para aquecimento."""
        # Datas para filtros comuns
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        endpoints = [
            # Métricas principais - mais críticas
            ("/metrics", {}),
            ("/metrics", {"start_date": week_ago.strftime("%Y-%m-%d"), "end_date": today.strftime("%Y-%m-%d")}),
            ("/metrics", {"start_date": month_ago.strftime("%Y-%m-%d"), "end_date": today.strftime("%Y-%m-%d")}),

            # Métricas filtradas
            ("/metrics/filtered", {}),
            ("/metrics/filtered", {"start_date": week_ago.strftime("%Y-%m-%d")}),

            # Ranking de técnicos
            ("/technicians/ranking", {}),
            ("/technicians/ranking", {"start_date": week_ago.strftime("%Y-%m-%d")}),

            # Técnicos
            ("/technicians", {}),

            # Tickets novos
            ("/tickets/new", {}),
            ("/tickets/new", {"start_date": week_ago.strftime("%Y-%m-%d")}),

            # Status e health checks
            ("/status", {}),
            ("/health", {}),
            ("/health/glpi", {}),
        ]

        return endpoints

    def _warm_endpoint(self, endpoint: str, params: Dict) -> bool:
        """Aquece um endpoint específico."""
        try:
            url = f"{self._base_url}{endpoint}"

            # Timeout baixo para não impactar performance
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                self.logger.debug(f"Cache warmed: {endpoint} with params {params}")
                return True
            else:
                self.logger.warning(f"Cache warming failed for {endpoint}: HTTP {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            self.logger.warning(f"Cache warming timeout for {endpoint}")
            return False
        except Exception as e:
            self.logger.error(f"Error warming cache for {endpoint}: {e}")
            return False

    def _warming_cycle(self) -> Dict:
        """Executa um ciclo completo de aquecimento."""
        cycle_start = time.time()
        endpoints = self._get_critical_endpoints()

        warmed_count = 0
        error_count = 0

        self.logger.info(f"Iniciando ciclo de aquecimento com {len(endpoints)} endpoints")

        for endpoint, params in endpoints:
            if self._stop_event.is_set():
                break

            if self._warm_endpoint(endpoint, params):
                warmed_count += 1
            else:
                error_count += 1

            # Pequena pausa entre requests para não sobrecarregar
            time.sleep(0.5)

        cycle_time = time.time() - cycle_start

        # Atualiza estatísticas
        self._warming_stats["cycles_completed"] += 1
        self._warming_stats["endpoints_warmed"] += warmed_count
        self._warming_stats["errors"] += error_count
        self._warming_stats["last_run"] = datetime.now().isoformat()

        # Calcula tempo médio de ciclo
        total_cycles = self._warming_stats["cycles_completed"]
        current_avg = self._warming_stats["average_cycle_time"]
        self._warming_stats["average_cycle_time"] = ((current_avg * (total_cycles - 1)) + cycle_time) / total_cycles

        cycle_stats = {
            "cycle_time": cycle_time,
            "endpoints_warmed": warmed_count,
            "errors": error_count,
            "total_endpoints": len(endpoints)
        }

        self.logger.info(f"Ciclo de aquecimento concluído: {warmed_count}/{len(endpoints)} endpoints aquecidos em {cycle_time:.2f}s")

        return cycle_stats

    def _warming_loop(self):
        """Loop principal do aquecimento de cache."""
        while not self._stop_event.is_set():
            try:
                cycle_stats = self._warming_cycle()

                # Log estatísticas se houver muitos erros
                if cycle_stats["errors"] > cycle_stats["total_endpoints"] * 0.3:
                    self.logger.warning(f"Alto número de erros no aquecimento: {cycle_stats['errors']}/{cycle_stats['total_endpoints']}")

                # Aguarda 5 minutos antes do próximo ciclo (ou menos se houver muitos erros)
                wait_time = 180 if cycle_stats["errors"] > 3 else 300  # 3 ou 5 minutos

                if self._stop_event.wait(wait_time):
                    break

            except Exception as e:
                self.logger.error(f"Erro crítico no aquecimento de cache: {e}")
                self._warming_stats["errors"] += 1
                # Aguarda 2 minutos antes de tentar novamente
                if self._stop_event.wait(120):
                    break

    def get_stats(self) -> Dict:
        """Retorna estatísticas do aquecimento de cache."""
        stats = self._warming_stats.copy()
        stats["is_running"] = self._running

        # Adiciona estatísticas de performance do cache
        cache_stats = performance_monitor.get_cache_hit_rate()
        stats["cache_hit_rate"] = cache_stats

        return stats


# Funções de conveniência para instanciação manual
def create_cache_warming():
    """Cria uma nova instância do serviço de cache warming"""
    return CacheWarming()
