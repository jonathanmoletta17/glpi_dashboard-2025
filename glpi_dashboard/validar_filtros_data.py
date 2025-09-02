#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação dos Filtros de Data - Dashboard GLPI
Valida a implementação atual dos filtros de data
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sys

class FiltrosDataValidator:
    """Validador para filtros de data do dashboard GLPI"""
    
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.results = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Registra resultado do teste"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if response_time > 0:
            print(f"   Tempo: {response_time:.2f}s")
        print()
    
    def test_backend_health(self) -> bool:
        """Testa saúde do backend"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Backend Health Check", True, f"Status: {response.status_code}", response_time)
                return True
            else:
                self.log_result("Backend Health Check", False, f"Status: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Erro: {str(e)}")
            return False
    
    def test_metrics_without_filter(self) -> bool:
        """Testa endpoint de métricas sem filtro"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/metrics", timeout=60)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    self.log_result("Métricas sem Filtro", True, f"Status: {response.status_code}", response_time)
                    return True
                else:
                    self.log_result("Métricas sem Filtro", False, "Resposta mal formada", response_time)
                    return False
            else:
                self.log_result("Métricas sem Filtro", False, f"Status: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Métricas sem Filtro", False, f"Erro: {str(e)}")
            return False
    
    def test_metrics_with_date_filter(self) -> bool:
        """Testa endpoint de métricas com filtro de data"""
        try:
            # Usar últimos 7 dias
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            params = {'start_date': start_date, 'end_date': end_date}
            start_time = time.time()
            response = requests.get(f"{self.base_url}/metrics", params=params, timeout=60)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    self.log_result("Métricas com Filtro de Data", True, 
                                  f"Período: {start_date} até {end_date}", response_time)
                    return True
                else:
                    self.log_result("Métricas com Filtro de Data", False, "Resposta mal formada", response_time)
                    return False
            else:
                self.log_result("Métricas com Filtro de Data", False, f"Status: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Métricas com Filtro de Data", False, f"Erro: {str(e)}")
            return False
    
    def test_ranking_with_date_filter(self) -> bool:
        """Testa endpoint de ranking com filtro de data"""
        try:
            # Usar últimos 30 dias
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            params = {'start_date': start_date, 'end_date': end_date}
            start_time = time.time()
            response = requests.get(f"{self.base_url}/technicians/ranking", params=params, timeout=180)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.log_result("Ranking com Filtro de Data", True, 
                                  f"Período: {start_date} até {end_date}", response_time)
                    return True
                else:
                    self.log_result("Ranking com Filtro de Data", False, "Resposta mal formada", response_time)
                    return False
            else:
                self.log_result("Ranking com Filtro de Data", False, f"Status: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("Ranking com Filtro de Data", False, f"Erro: {str(e)}")
            return False
    
    def test_date_validation(self) -> bool:
        """Testa validação de datas"""
        tests = [
            {
                "name": "Formato de Data Inválido",
                "params": {"start_date": "01-08-2025", "end_date": "31-08-2025"},
                "expected_status": 400
            },
            {
                "name": "Range de Data Inválido",
                "params": {"start_date": "2025-08-31", "end_date": "2025-08-01"},
                "expected_status": 400
            },
            {
                "name": "Formato de Data Válido",
                "params": {"start_date": "2025-08-01", "end_date": "2025-08-31"},
                "expected_status": 200
            }
        ]
        
        all_passed = True
        for test in tests:
            try:
                response = requests.get(f"{self.base_url}/metrics", params=test["params"], timeout=30)
                success = response.status_code == test["expected_status"]
                self.log_result(f"Validação: {test['name']}", success, 
                              f"Status: {response.status_code} (esperado: {test['expected_status']})")
                if not success:
                    all_passed = False
            except Exception as e:
                self.log_result(f"Validação: {test['name']}", False, f"Erro: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_performance(self) -> bool:
        """Testa performance dos endpoints"""
        performance_tests = [
            {"name": "Métricas sem Filtro", "url": f"{self.base_url}/metrics", "max_time": 30},
            {"name": "Métricas com Filtro", "url": f"{self.base_url}/metrics", "max_time": 15, 
             "params": {"start_date": "2025-08-01", "end_date": "2025-08-31"}},
            {"name": "Ranking sem Filtro", "url": f"{self.base_url}/technicians/ranking", "max_time": 30},
            {"name": "Ranking com Filtro", "url": f"{self.base_url}/technicians/ranking", "max_time": 30,
             "params": {"start_date": "2025-08-01", "end_date": "2025-08-31"}}
        ]
        
        all_passed = True
        for test in performance_tests:
            try:
                start_time = time.time()
                response = requests.get(test["url"], params=test.get("params", {}), timeout=test["max_time"] + 10)
                response_time = time.time() - start_time
                
                success = response.status_code == 200 and response_time <= test["max_time"]
                self.log_result(f"Performance: {test['name']}", success, 
                              f"Tempo: {response_time:.2f}s (limite: {test['max_time']}s)", response_time)
                if not success:
                    all_passed = False
            except Exception as e:
                self.log_result(f"Performance: {test['name']}", False, f"Erro: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> Dict:
        """Executa todos os testes"""
        print("🧪 INICIANDO VALIDAÇÃO DOS FILTROS DE DATA")
        print("=" * 50)
        print()
        
        # Executar testes
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Métricas sem Filtro", self.test_metrics_without_filter),
            ("Métricas com Filtro", self.test_metrics_with_date_filter),
            ("Ranking com Filtro", self.test_ranking_with_date_filter),
            ("Validação de Datas", self.test_date_validation),
            ("Performance", self.test_performance)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"🔍 Executando: {test_name}")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Erro inesperado: {str(e)}")
            print()
        
        # Resumo
        print("📊 RESUMO DOS TESTES")
        print("=" * 50)
        print(f"Total de testes: {total}")
        print(f"Testes passaram: {passed}")
        print(f"Testes falharam: {total - passed}")
        print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
        print()
        
        # Status geral
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Implementação dos filtros de data está funcionando corretamente")
        else:
            print("⚠️ ALGUNS TESTES FALHARAM")
            print("❌ Verifique os logs acima para identificar problemas")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed/total)*100,
            "results": self.results
        }

def main():
    """Função principal"""
    print("🚀 Validador de Filtros de Data - Dashboard GLPI")
    print("=" * 60)
    print()
    
    # Verificar se backend está rodando
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend não está respondendo na porta 5000")
            print("   Certifique-se de que o backend está rodando:")
            print("   cd glpi_dashboard/backend && python app.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Não foi possível conectar ao backend na porta 5000")
        print("   Certifique-se de que o backend está rodando:")
        print("   cd glpi_dashboard/backend && python app.py")
        sys.exit(1)
    
    # Executar validação
    validator = FiltrosDataValidator()
    results = validator.run_all_tests()
    
    # Salvar resultados
    with open("validacao_filtros_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Resultados salvos em: validacao_filtros_data.json")
    
    # Exit code baseado no resultado
    sys.exit(0 if results["passed"] == results["total"] else 1)

if __name__ == "__main__":
    main()
