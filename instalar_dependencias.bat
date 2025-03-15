@echo off
title Lion Dedetizadora - Instalação de Dependências
color 0A

echo =============================================================
echo        INSTALADOR DE DEPENDENCIAS - LION DEDETIZADORA        
echo =============================================================
echo.
echo Este instalador configurará o ambiente para o sistema de
echo gerenciamento de anúncios da Lion Dedetizadora.
echo.
echo Requisitos:
echo  - Conexão com a Internet
echo  - Permissões de administrador
echo.
echo =============================================================
echo.

:: Verificar se Python está instalado
echo [*] Verificando instalação do Python...
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python não encontrado. Instalando Python...
    echo [*] Baixando instalador do Python...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe' -OutFile 'python-installer.exe'}"
    
    echo [*] Executando instalador do Python...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    echo [*] Limpando arquivos temporários...
    del python-installer.exe
) else (
    echo [+] Python já está instalado.
)

:: Atualizar pip
echo.
echo [*] Atualizando pip...
python -m pip install --upgrade pip

:: Criar ambiente virtual
echo.
echo [*] Criando ambiente virtual...
python -m venv venv
call venv\Scripts\activate.bat

:: Instalar dependências
echo.
echo [*] Instalando dependências...
pip install flask flask-sqlalchemy gunicorn python-dotenv requests openai facebook-business pandas scikit-learn numpy matplotlib pika prometheus-client retrying

:: Criar estrutura de pastas
echo.
echo [*] Criando estrutura de pastas (se necessário)...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

:: Criar arquivo .env padrão se ele não existir
echo.
echo [*] Verificando arquivo de configuração...
if not exist .env (
    echo [*] Criando arquivo .env padrão...
    (
        echo # Credenciais para APIs
        echo OPENAI_API_KEY=
        echo FB_ACCESS_TOKEN=
        echo FB_ACCOUNT_ID=
        echo.
        echo # Configurações de e-mail
        echo EMAIL_HOST=smtp.gmail.com
        echo EMAIL_PORT=587
        echo EMAIL_USERNAME=dedetizadoralion@gmail.com
        echo EMAIL_PASSWORD=
        echo EMAIL_RECIPIENT=
        echo.
        echo # Configurações do aplicativo
        echo DEBUG=True
        echo SESSION_SECRET=lion-dedetizadora-secret-key
    ) > .env
    echo [+] Arquivo .env criado com sucesso.
) else (
    echo [+] Arquivo .env já existe.
)

:: Finalizar
echo.
echo =============================================================
echo.
echo [+] Instalação concluída com sucesso!
echo [+] O sistema está pronto para uso.
echo.
echo Para iniciar o sistema, execute o arquivo:
echo   iniciar_sistema.bat
echo.
echo =============================================================
echo.

pause
exit
