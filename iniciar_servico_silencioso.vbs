' Script para iniciar o sistema como um serviço em segundo plano
' Sem abrir janelas de prompt de comando visíveis

Option Explicit

Dim WshShell, oExec
Set WshShell = CreateObject("WScript.Shell")

' Caminho para o script batch que inicia o serviço
Dim scriptPath
scriptPath = WshShell.CurrentDirectory & "\iniciar_sistema.bat"

' Registrar início no log
WriteToLog "Iniciando serviço Lion Dedetizadora em " & Now()

' Executar o batch em segundo plano (0 = escondido)
WshShell.Run "cmd /c " & scriptPath, 0, False

' Registrar confirmação no log
WriteToLog "Serviço iniciado com sucesso."

' Mostrar mensagem para o usuário
MsgBox "O serviço de gerenciamento de anúncios da Lion Dedetizadora foi iniciado em segundo plano." & vbCrLf & vbCrLf & _
       "O sistema está rodando e acessível em:" & vbCrLf & _
       "http://localhost:5000" & vbCrLf & vbCrLf & _
       "Para encerrar o serviço, use o Gerenciador de Tarefas para finalizar o processo 'python.exe'.", _
       vbInformation, "Lion Dedetizadora - Serviço Iniciado"

' Função para escrever no arquivo de log
Sub WriteToLog(logMessage)
    Dim fso, logFile
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Criar pasta de logs se não existir
    If Not fso.FolderExists("logs") Then
        fso.CreateFolder("logs")
    End If
    
    ' Abrir ou criar arquivo de log
    Set logFile = fso.OpenTextFile("logs\service_log.txt", 8, True)
    logFile.WriteLine Now() & " - " & logMessage
    logFile.Close
End Sub
