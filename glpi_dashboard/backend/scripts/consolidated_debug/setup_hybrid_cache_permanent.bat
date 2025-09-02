@echo off
echo Configurando variaveis de ambiente permanentemente...
echo.
setx TRANSFORMERS_CACHE "B:\ai_models_cache\transformers"
echo ✅ TRANSFORMERS_CACHE configurado
setx HF_HOME "B:\ai_models_cache\huggingface"
echo ✅ HF_HOME configurado
setx TORCH_HOME "B:\ai_models_cache\torch"
echo ✅ TORCH_HOME configurado
setx HF_DATASETS_CACHE "B:\ai_models_cache\datasets"
echo ✅ HF_DATASETS_CACHE configurado
setx CUDA_CACHE_PATH "B:\ai_models_cache\cuda"
echo ✅ CUDA_CACHE_PATH configurado
setx PIP_CACHE_DIR "B:\ai_models_cache\pip"
echo ✅ PIP_CACHE_DIR configurado
setx MYPY_CACHE_DIR "B:\ai_models_cache\mypy"
echo ✅ MYPY_CACHE_DIR configurado
setx PYTEST_CACHE_DIR "B:\ai_models_cache\pytest"
echo ✅ PYTEST_CACHE_DIR configurado
setx TEMP "B:\ai_models_cache\temp"
echo ✅ TEMP configurado
setx TMP "B:\ai_models_cache\temp"
echo ✅ TMP configurado

echo.
echo ✅ Configuracao concluida!
echo ⚠️ Reinicie o terminal para aplicar as mudancas
echo.
pause
