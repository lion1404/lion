@echo off
title Lion Dedetizadora - Configuração de E-mail
color 0A

echo =============================================================
echo        CONFIGURACAO DE E-MAIL - LION DEDETIZADORA        
echo =============================================================
echo.
echo Este assistente irá configurar o serviço de e-mail para
echo envio de relatórios automáticos.
echo.
echo IMPORTANTE: Para o Gmail, você precisa criar uma senha de app
echo específica em: https://myaccount.google.com/apppasswords
echo (É necessário ter verificação em duas etapas ativada)
echo.
echo =============================================================
echo.

setlocal EnableDelayedExpansion

:: Verificar se o arquivo .env existe
if not exist .env (
    echo [!] Arquivo .env não encontrado. Executando instalador de dependências...
    call instalar_dependencias.bat
)

:: Coletar informações de e-mail
set /p EMAIL_USERNAME=Digite o endereço de e-mail para envio de relatórios [dedetizadoralion@gmail.com]: 
if "!EMAIL_USERNAME!"=="" set EMAIL_USERNAME=dedetizadoralion@gmail.com

set /p EMAIL_PASSWORD=Digite a senha de aplicativo do Gmail: 

set /p EMAIL_RECIPIENT=Digite o e-mail do destinatário para receber relatórios: 

:: Atualizar o arquivo .env
echo.
echo [*] Atualizando configurações de e-mail...

powershell -Command "$content = Get-Content -Path '.env' -Raw; $content = $content -replace 'EMAIL_USERNAME=.*', 'EMAIL_USERNAME=%EMAIL_USERNAME%'; $content = $content -replace 'EMAIL_PASSWORD=.*', 'EMAIL_PASSWORD=%EMAIL_PASSWORD%'; $content = $content -replace 'EMAIL_RECIPIENT=.*', 'EMAIL_RECIPIENT=%EMAIL_RECIPIENT%'; Set-Content -Path '.env' -Value $content"

echo.
echo [+] Configurações de e-mail atualizadas com sucesso!
echo.
echo [*] Testando conexão com o servidor de e-mail...

:: Executar teste de conexão
call venv\Scripts\activate.bat
python -c "from ad_manager.services.email_service import test_smtp_connection; success, message = test_smtp_connection(); print(f'Resultado: {'Sucesso' if success else 'Falha'}'); print(f'Mensagem: {message}')"
call venv\Scripts\deactivate.bat

echo.
echo =============================================================
echo.
echo [+] Configuração concluída!
echo.
echo Se o teste falhou, verifique:
echo  1. Se a senha de app do Gmail está correta
echo  2. Se você habilitou a verificação em duas etapas
echo  3. Se criou uma senha específica para o app em:
echo     https://myaccount.google.com/apppasswords
echo.
echo =============================================================
echo.

pause
exit
