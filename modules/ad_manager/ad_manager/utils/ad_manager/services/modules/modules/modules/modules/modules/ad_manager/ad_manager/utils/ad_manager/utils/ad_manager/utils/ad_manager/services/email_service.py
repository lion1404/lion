import os
import logging
import smtplib
import json
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

def get_email_template(roi, suggestions, analysis_data, is_daily_report=False):
    """
    Gera o conteúdo HTML do e-mail de relatório.
    
    Args:
        roi (float): Retorno sobre investimento
        suggestions (str): Sugestões da IA
        analysis_data (dict): Dados da análise de desempenho
        is_daily_report (bool): Indica se é um relatório diário
        
    Returns:
        str: Conteúdo HTML do e-mail
    """
    # Extrair dados
    metrics = analysis_data.get('metrics', {})
    
    # Formatação de valores para exibição
    formatted_metrics = {
        'impressions': f"{metrics.get('impressions', 0):,}".replace(',', '.'),
        'clicks': f"{metrics.get('clicks', 0):,}".replace(',', '.'),
        'conversions': f"{metrics.get('conversions', 0):,}".replace(',', '.'),
        'ctr': f"{metrics.get('ctr', 0):.2f}%",
        'cpc': f"R${metrics.get('cpc', 0):.2f}",
        'conversion_rate': f"{metrics.get('conversion_rate', 0):.2f}%",
        'cost': f"R${metrics.get('cost', 0):.2f}",
        'revenue': f"R${metrics.get('revenue', 0):.2f}",
        'roi': f"{roi:.2f}%"
    }
    
    # Determinar classe de estilo baseada no ROI
    if roi >= 300:
        roi_class = "excellent"
        roi_message = "Desempenho excelente! Continue investindo nessa estratégia."
    elif roi >= 200:
        roi_class = "good"
        roi_message = "Bom desempenho. Considere otimizações para melhorar ainda mais."
    elif roi >= 100:
        roi_class = "average"
        roi_message = "Desempenho razoável. Recomendamos alguns ajustes estratégicos."
    else:
        roi_class = "poor"
        roi_message = "Desempenho abaixo do esperado. Atenção às recomendações de otimização."
    
    # Definir a data do relatório
    report_date = datetime.datetime.now().strftime("%d/%m/%Y")
    report_type = "Relatório Diário" if is_daily_report else "Relatório de Análise"
    
    # Criar o conteúdo HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report_type} - Lion Dedetizadora</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 0 0 5px 5px;
                border: 1px solid #ddd;
            }}
            .metrics-container {{
                display: flex;
                flex-wrap: wrap;
                margin: 20px 0;
                gap: 15px;
            }}
            .metric-box {{
                flex: 1;
                min-width: calc(33% - 15px);
                background-color: white;
                border-radius: 5px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #4CAF50;
            }}
            .metric-title {{
                font-size: 14px;
                color: #777;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 22px;
                font-weight: bold;
                color: #333;
            }}
            .recommendations {{
                background-color: white;
                border-radius: 5px;
                padding: 15px;
                margin-top: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .roi-box {{
                text-align: center;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
                color: white;
            }}
            .excellent {{
                background-color: #4CAF50;
            }}
            .good {{
                background-color: #8BC34A;
            }}
            .average {{
                background-color: #FFC107;
                color: #333;
            }}
            .poor {{
                background-color: #F44336;
            }}
            .roi-value {{
                font-size: 36px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .roi-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            h2 {{
                color: #4CAF50;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
            @media (max-width: 600px) {{
                .metric-box {{
                    min-width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Lion Dedetizadora</h1>
            <p>{report_type} - {report_date}</p>
        </div>
        
        <div class="content">
            <div class="roi-box {roi_class}">
                <div class="roi-label">RETORNO SOBRE INVESTIMENTO</div>
                <div class="roi-value">{formatted_metrics['roi']}</div>
                <div>{roi_message}</div>
            </div>
            
            <h2>Métricas de Desempenho</h2>
            <div class="metrics-container">
                <div class="metric-box">
                    <div class="metric-title">Impressões</div>
                    <div class="metric-value">{formatted_metrics['impressions']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Cliques</div>
                    <div class="metric-value">{formatted_metrics['clicks']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Taxa de Cliques (CTR)</div>
                    <div class="metric-value">{formatted_metrics['ctr']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Custo por Clique</div>
                    <div class="metric-value">{formatted_metrics['cpc']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Conversões</div>
                    <div class="metric-value">{formatted_metrics['conversions']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Taxa de Conversão</div>
                    <div class="metric-value">{formatted_metrics['conversion_rate']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Custo Total</div>
                    <div class="metric-value">{formatted_metrics['cost']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-title">Receita</div>
                    <div class="metric-value">{formatted_metrics['revenue']}</div>
                </div>
            </div>
            
            <h2>Recomendações para Otimização</h2>
            <div class="recommendations">
                {suggestions.replace('\n', '<br>')}
            </div>
            
            <div class="footer">
                <p>Este relatório foi gerado automaticamente pelo sistema de gerenciamento de anúncios da Lion Dedetizadora.</p>
                <p>Para mais informações, acesse o painel de controle ou entre em contato com nossa equipe.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(subject, html_content):
    """
    Envia um e-mail HTML.
    
    Args:
        subject (str): Assunto do e-mail
        html_content (str): Conteúdo HTML do e-mail
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False caso contrário
    """
    # Obter configurações de e-mail do ambiente
    email_host = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    email_port = int(os.environ.get('EMAIL_PORT', 587))
    email_username = os.environ.get('EMAIL_USERNAME', '')
    email_password = os.environ.get('EMAIL_PASSWORD', '')
    email_recipient = os.environ.get('EMAIL_RECIPIENT', '')
    
    # Verificar se temos as configurações necessárias
    if not email_username or not email_password or not email_recipient:
        logger.warning("Configurações de e-mail incompletas. Salvando conteúdo em arquivo local.")
        
        # Salvar conteúdo do e-mail em arquivo local
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_content_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Conteúdo do e-mail salvo em arquivo: {filename}")
        return False
    
    try:
        # Criar mensagem
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = email_username
        message['To'] = email_recipient
        
        # Anexar conteúdo HTML
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Conectar ao servidor SMTP
        logger.info(f"Tentando enviar e-mail para {email_recipient}")
        logger.info(f"Tentando conectar ao servidor SMTP: {email_host}:{email_port}")
        
        server = smtplib.SMTP(email_host, email_port)
        server.ehlo()
        
        # Iniciar TLS para segurança
        logger.info("Conexão estabelecida. Iniciando TLS...")
        server.starttls()
        server.ehlo()
        
        # Login com as credenciais
        logger.info(f"TLS iniciado. Tentando login com usuário: {email_username}")
        server.login(email_username, email_password)
        
        # Enviar e-mail
        server.sendmail(email_username, email_recipient, message.as_string())
        server.quit()
        
        logger.info(f"E-mail enviado com sucesso para {email_recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Erro de e-mail: {str(e)}")
        
        # Verificar se é um erro de autenticação do Gmail
        if "Username and Password not accepted" in str(e):
            logger.info("Verifique se você está usando uma senha de app para Gmail.")
            logger.info("Para o Gmail, você precisa criar uma senha de app específica em: https://myaccount.google.com/apppasswords")
        
        # Salvar conteúdo do e-mail em arquivo local
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_content_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"E-mail não foi enviado, mas conteúdo foi salvo para referência")
        return False

def process_email_message(ch, method, properties, body):
    """
    Processa mensagens da fila do serviço de e-mail.
    """
    try:
        # Decodificar a mensagem
        message = json.loads(body)
        
        # Extrair dados
        subject = message.get('subject', 'Relatório - Lion Dedetizadora')
        html_content = message.get('html_content', '')
        
        # Se não tiver conteúdo HTML, tentar gerar
        if not html_content:
            roi = message.get('roi', 0)
            suggestions = message.get('suggestions', '')
            analysis_data = message.get('analysis_data', {})
            is_daily_report = message.get('is_daily_report', False)
            
            html_content = get_email_template(roi, suggestions, analysis_data, is_daily_report)
        
        # Enviar e-mail
        logger.info("Recebida solicitação para envio de relatório por e-mail")
        send_email(subject, html_content)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem de e-mail: {str(e)}")

def test_smtp_connection():
    """
    Testa a conexão com o servidor SMTP do Gmail.
    Útil para diagnóstico de problemas de configuração.
    
    Returns:
        tuple: (bool, str) - Sucesso e mensagem descritiva
    """
    # Obter configurações de e-mail do ambiente
    email_host = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    email_port = int(os.environ.get('EMAIL_PORT', 587))
    email_username = os.environ.get('EMAIL_USERNAME', '')
    email_password = os.environ.get('EMAIL_PASSWORD', '')
    
    # Verificar se temos as configurações necessárias
    if not email_username or not email_password:
        return False, "Configurações de e-mail incompletas. Verifique as variáveis EMAIL_USERNAME e EMAIL_PASSWORD."
    
    try:
        # Tentar conectar ao servidor SMTP
        server = smtplib.SMTP(email_host, email_port)
        server.ehlo()
        
        # Iniciar TLS para segurança
        server.starttls()
        server.ehlo()
        
        # Tentar login
        server.login(email_username, email_password)
        
        # Fechar conexão
        server.quit()
        
        return True, f"Conexão bem-sucedida com o servidor {email_host}:{email_port} usando o usuário {email_username}"
        
    except Exception as e:
        error_message = str(e)
        
        # Adicionar sugestões específicas para problemas comuns
        suggestion = ""
        
        if "Username and Password not accepted" in error_message:
            suggestion = "Para o Gmail, você precisa criar uma senha de app específica em: https://myaccount.google.com/apppasswords"
        elif "Authentication failed" in error_message:
            suggestion = "Falha de autenticação. Verifique se o e-mail e senha estão corretos."
        elif "Connection refused" in error_message:
            suggestion = "Conexão recusada. Verifique se o host e porta estão corretos."
        elif "Certificate verify failed" in error_message:
            suggestion = "Falha na verificação do certificado. Problema de segurança na conexão."
        
        return False, f"Erro ao conectar ao servidor: {error_message}. {suggestion}"

def start_service():
    """
    Inicia o serviço de e-mail escutando a fila.
    """
    from ad_manager.utils.messaging import create_channel, consume_queue
    
    logger.info("Iniciando serviço de e-mail")
    
    # Verificar configurações de e-mail
    email_username = os.environ.get('EMAIL_USERNAME', '')
    email_password = os.environ.get('EMAIL_PASSWORD', '')
    
    if not email_username or not email_password:
        logger.warning("Configurações de e-mail incompletas. Os relatórios serão salvos em arquivos locais.")
    
    # Criar canal para fila de mensagens
    channel = create_channel()
    
    # Consumir mensagens da fila
    consume_queue("email_queue", process_email_message)
    
    logger.info("Serviço de e-mail iniciado com sucesso")
