@echo off
title Lion Dedetizadora - Sistema de Gestão de Anúncios
color 0A

echo =============================================================
echo         SISTEMA DE GESTAO DE ANUNCIOS - LION DEDETIZADORA      
echo =============================================================
echo.
echo Iniciando o sistema...
echo.

:: Ativar ambiente virtual
call venv\Scripts\activate.bat

:: Verificar se pip está atualizado
python -m pip install --upgrade pip > nul

:: Iniciar o servidor
echo [*] Iniciando o servidor web...
echo [*] O sistema estará disponível em: http://localhost:5000
echo.
echo [*] Pressione Ctrl+C para encerrar o sistema
echo =============================================================
echo.

:: Iniciar o aplicativo
python main.py

:: Desativar ambiente virtual quando encerrar
call venv\Scripts\deactivate.bat

pause
