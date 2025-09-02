@echo off
REM Configuração Permanente de Cache - Drive B:
REM Gerado automaticamente em 30/08/2025 01:46:16

echo Configurando variáveis de ambiente permanentes...
echo.

setx TRANSFORMERS_CACHE "B:\ai_models_cache\transformers"
echo TRANSFORMERS_CACHE configurado
setx HF_HOME "B:\ai_models_cache\huggingface"
echo HF_HOME configurado
setx TORCH_HOME "B:\ai_models_cache\torch"
echo TORCH_HOME configurado
setx HF_DATASETS_CACHE "B:\ai_models_cache\datasets"
echo HF_DATASETS_CACHE configurado
setx PYTORCH_KERNEL_CACHE_PATH "B:\ai_models_cache\torch\kernels"
echo PYTORCH_KERNEL_CACHE_PATH configurado
setx CUDA_CACHE_PATH "B:\ai_models_cache\cuda"
echo CUDA_CACHE_PATH configurado

echo.
echo ✅ Configuração concluída!
echo ⚠️  IMPORTANTE: Reinicie o terminal/IDE para aplicar as configurações.
echo.
pause
