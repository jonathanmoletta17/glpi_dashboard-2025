@echo off
echo 🚀 Configurando GLPI Dashboard...

REM Verificar dependências
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado. Instale Node.js 18+ primeiro.
    exit /b 1
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale Python 3.12+ primeiro.
    exit /b 1
)

REM Configurar frontend
echo 📦 Configurando frontend...
cd glpi_dashboard\frontend
npm install
npm run build
cd ..\..

REM Configurar backend
echo 🐍 Configurando backend...
cd glpi_dashboard\backend
python -m venv venv
call venv\Scripts\activate
pip install -r ..\requirements.txt
cd ..\..

REM Configurar variáveis de ambiente
echo ⚙️ Configurando variáveis de ambiente...
if not exist .env (
    copy .env.example .env
    echo 📝 Arquivo .env criado. Configure as variáveis necessárias.
)

echo ✅ Configuração concluída!
echo 🔧 Configure as variáveis no arquivo .env
echo 🚀 Execute: npm run dev (frontend) e python app.py (backend)

