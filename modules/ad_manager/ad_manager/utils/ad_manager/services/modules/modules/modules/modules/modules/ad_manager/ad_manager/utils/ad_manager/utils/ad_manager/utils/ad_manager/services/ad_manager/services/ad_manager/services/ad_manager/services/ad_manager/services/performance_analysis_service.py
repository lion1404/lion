import os
import logging
import json
import random
import time
import schedule
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Importar utilitários
from ad_manager.utils.facebook_integration import FacebookAdsAPI
from ad_manager.utils.openai_utils import get_ai_suggestions
from ad_manager.utils.messaging import create_channel, publish_message
from modules.analytics import CampaignAnalytics

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

def get_demo_performance_data(ad_id=None):
    """
    Gera dados de demonstração para análise de desempenho quando não é possível acessar a API.
    
    Args:
        ad_id (str, optional): ID do anúncio específico para análise
        
    Returns:
        tuple: (sugestões da IA, ROI calculado, dados de desempenho)
    """
    # Criar dados de performance simulados
    performance_data = {
        'name': 'Campanha Dedetização Residencial',
        'period': 'Últimos 30 dias',
        'metrics': {
            'impressions': random.randint(5000, 15000),
            'clicks': random.randint(100, 500),
            'cost': round(random.uniform(500, 1500), 2),
            'conversions': random.randint(10, 50),
            'revenue': 0  # Será calculado baseado nas conversões
        }
    }
    
    # Calcular métricas derivadas
    clicks = performance_data['metrics']['clicks']
    impressions = performance_data['metrics']['impressions']
    conversions = performance_data['metrics']['conversions']
    cost = performance_data['metrics']['cost']
    
    # Calcular receita (valor médio de serviço * conversões)
    avg_service_value = random.uniform(250, 500)  # Valor médio de um serviço de dedetização
    revenue = conversions * avg_service_value
    performance_data['metrics']['revenue'] = round(revenue, 2)
    
    # Calcular métricas de desempenho
    ctr = (clicks / impressions) * 100 if impressions > 0 else 0
    cpc = cost / clicks if clicks > 0 else 0
    conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0
    roi = ((revenue - cost) / cost) * 100 if cost > 0 else 0
    
    performance_data['metrics']['ctr'] = round(ctr, 2)
    performance_data['metrics']['cpc'] = round(cpc, 2)
    performance_data['metrics']['conversion_rate'] = round(conversion_rate, 2)
    performance_data['metrics']['roi'] = round(roi, 2)
    
    # Obter sugestões da IA
    suggestions = get_ai_suggestions(performance_data)
    
    return suggestions, roi, performance_data

def analyze_ad_performance(ad_id=None):
    """
    Analisa o desempenho de um anúncio ou de todos os anúncios da conta.
    
    Args:
        ad_id (str, optional): ID do anúncio específico para análise
        
    Returns:
        tuple: (sugestões da IA, ROI calculado, dados de desempenho)
    """
    # Inicializar API do Facebook
    fb_api = FacebookAdsAPI()
    
    # Verificar se conseguimos acessar a API
    if not fb_api.api_initialized:
        logger.warning("API do Facebook não inicializada. Usando dados simulados para análise.")
        return get_demo_performance_data(ad_id)
    
    try:
        # Obter insights de desempenho
        insights = fb_api.get_campaign_insights(ad_id)
        
        if not insights:
            logger.warning("Sem dados de insights disponíveis. Usando dados simulados.")
            return get_demo_performance_data(ad_id)
        
        # Processar dados de insights para análise
        impressions = sum(insight.get('impressions', 0) for insight in insights)
        clicks = sum(insight.get('clicks', 0) for insight in insights)
        spend = sum(insight.get('spend', 0) for insight in insights)
        
        # Obter conversões - na API real seria algo como:
        # conversions = sum(insight.get('actions', {}).get('offsite_conversion.fb_pixel_purchase', 0) for insight in insights)
        # Como estamos simulando, vamos calcular baseado em uma taxa de conversão
        estimated_conv_rate = random.uniform(0.01, 0.05)  # 1-5% de conversão
        conversions = int(clicks * estimated_conv_rate)
        
        # Estimar receita baseada em valor médio de serviço
        avg_service_value = random.uniform(250, 500)  # Valor médio de um serviço de dedetização
        revenue = conversions * avg_service_value
        
        # Criar objeto de dados de desempenho
        performance_data = {
            'name': 'Campanha de Anúncios Lion',
            'period': 'Últimos 30 dias',
            'metrics': {
                'impressions': impressions,
                'clicks': clicks,
                'cost': spend,
                'conversions': conversions,
                'revenue': revenue,
                'ctr': (clicks / impressions) * 100 if impressions > 0 else 0,
                'cpc': spend / clicks if clicks > 0 else 0,
                'conversion_rate': (conversions / clicks) * 100 if clicks > 0 else 0
            }
        }
        
        # Calcular ROI
        roi = ((revenue - spend) / spend) * 100 if spend > 0 else 0
        performance_data['metrics']['roi'] = roi
        
        # Utilizar a classe CampaignAnalytics para análise detalhada
        analyzer = CampaignAnalytics(performance_data)
        detailed_metrics = analyzer.calculate_all_metrics()
        
        # Obter sugestões da IA
        suggestions = get_ai_suggestions(performance_data)
        
        return suggestions, roi, performance_data
        
    except Exception as e:
        logger.error(f"Erro ao analisar desempenho do anúncio: {str(e)}")
        return get_demo_performance_data(ad_id)

def process_performance_analysis_message(ch, method, properties, body):
    """
    Processa mensagens da fila de análise de desempenho.
    """
    try:
        # Decodificar a mensagem
        message = json.loads(body)
        
        # Extrair parâmetros
        ad_id = message.get('ad_id')
        send_email = message.get('send_email', True)
        is_daily_report = message.get('is_daily_report', False)
        
        # Realizar análise
        logger.info(f"Analisando desempenho do anúncio: {ad_id}")
        suggestions, roi, analysis_data = analyze_ad_performance(ad_id)
        
        # Salvar relatório
        save_analysis_report(roi, suggestions, analysis_data, is_daily_report)
        
        # Enviar e-mail se solicitado
        if send_email:
            # Criar canal para envio de e-mail
            channel = create_channel()
            
            # Enviar para fila de e-mail
            email_message = {
                'subject': 'Relatório Diário - Lion Dedetizadora' if is_daily_report else 'Análise de Desempenho - Lion Dedetizadora',
                'roi': roi,
                'suggestions': suggestions,
                'analysis_data': analysis_data,
                'is_daily_report': is_daily_report
            }
            
            publish_message(channel, 'email_queue', json.dumps(email_message))
        
        # Enviar para fila de otimização de orçamento
        channel = create_channel()
        budget_message = {
            'ad_id': ad_id,
            'roi': roi,
            'ctr': analysis_data['metrics']['ctr'],
            'budget': 10.0  # Orçamento atual (em uma implementação real, viria dos dados da campanha)
        }
        
        publish_message(channel, 'budget_optimization_queue', json.dumps(budget_message))
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem de análise de desempenho: {str(e)}")

def start_service():
    """
    Inicia o serviço de análise de desempenho escutando a fila.
    """
    from ad_manager.utils.messaging import create_channel, consume_queue
    
    logger.info("Iniciando serviço de análise de desempenho")
    
    # Criar canal para fila de mensagens
    channel = create_channel()
    
    # Consumir mensagens da fila
    consume_queue("performance_analysis_queue", process_performance_analysis_message)
    
    logger.info("Serviço de análise de desempenho iniciado com sucesso")

def save_analysis_report(roi, suggestions, analysis_data, is_daily_report=False):
    """
    Salva um relatório de análise em arquivo quando não é possível enviar por e-mail.
    
    Args:
        roi (float): ROI calculado
        suggestions (str): Sugestões da IA
        analysis_data (dict): Dados de análise de desempenho
        is_daily_report (bool): Indica se é um relatório diário
        
    Returns:
        str: Caminho do arquivo salvo
    """
    try:
        # Gerar nome de arquivo baseado na data atual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "analise_diario" if is_daily_report else "analise_campanha"
        filename = f"{prefix}_{timestamp}.txt"
        
        # Caminho completo
        file_path = os.path.join(os.getcwd(), filename)
        
        # Formatar dados de análise
        metrics = analysis_data.get('metrics', {})
        
        # Salvar relatório
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"=== {'RELATÓRIO DIÁRIO' if is_daily_report else 'ANÁLISE DE DESEMPENHO'} - LION DEDETIZADORA ===\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Campanha: {analysis_data.get('name', 'Não especificada')}\n")
            f.write(f"Período: {analysis_data.get('period', 'Não especificado')}\n\n")
            
            f.write("=== MÉTRICAS DE DESEMPENHO ===\n")
            f.write(f"Impressões: {metrics.get('impressions', 0):,}\n".replace(',', '.'))
            f.write(f"Cliques: {metrics.get('clicks', 0):,}\n".replace(',', '.'))
            f.write(f"CTR: {metrics.get('ctr', 0):.2f}%\n")
            f.write(f"CPC: R${metrics.get('cpc', 0):.2f}\n")
            f.write(f"Conversões: {metrics.get('conversions', 0):,}\n".replace(',', '.'))
            f.write(f"Taxa de Conversão: {metrics.get('conversion_rate', 0):.2f}%\n")
            f.write(f"Custo: R${metrics.get('cost', 0):.2f}\n")
            f.write(f"Receita: R${metrics.get('revenue', 0):.2f}\n")
            f.write(f"ROI: {roi:.2f}%\n\n")
            
            f.write("=== SUGESTÕES DE OTIMIZAÇÃO ===\n")
            f.write(suggestions)
        
        logger.info(f"Relatório de análise salvo em arquivo: {filename}")
        return file_path
        
    except Exception as e:
        logger.error(f"Erro ao salvar relatório de análise: {str(e)}")
        error_path = os.path.join(os.getcwd(), "error_log.txt")
        with open(error_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: Erro ao salvar relatório de análise: {str(e)}\n")
        return None

def schedule_daily_analysis():
    """
    Agenda análise diária de desempenho para todos os anúncios.
    """
    def run_daily_analysis():
        logger.info("Executando análise diária automatizada")
        try:
            # Realizar análise
            suggestions, roi, analysis_data = analyze_ad_performance()
            
            # Salvar relatório
            save_analysis_report(roi, suggestions, analysis_data, is_daily_report=True)
            
            # Enviar e-mail com relatório
            channel = create_channel()
            
            email_message = {
                'subject': 'Relatório Diário - Lion Dedetizadora',
                'roi': roi,
                'suggestions': suggestions,
                'analysis_data': analysis_data,
                'is_daily_report': True
            }
            
            publish_message(channel, 'email_queue', json.dumps(email_message))
            
            # Enviar para fila de otimização de orçamento
            budget_message = {
                'ad_id': None,  # Todas as campanhas
                'roi': roi,
                'ctr': analysis_data['metrics']['ctr'],
                'budget': 10.0  # Orçamento atual (em uma implementação real, viria dos dados da campanha)
            }
            
            publish_message(channel, 'budget_optimization_queue', json.dumps(budget_message))
            
            logger.info(f"Análise diária concluída com ROI: {roi:.2f}%")
            
        except Exception as e:
            logger.error(f"Erro ao executar análise diária: {str(e)}")
    
    # Agendar para executar todos os dias às 9h da manhã
    schedule.every().day.at("09:00").do(run_daily_analysis)
    
    # Executar uma análise inicial imediatamente
    run_daily_analysis()
    
    logger.info("Análise diária agendada com sucesso")
    
    # Loop para verificar agendamentos
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto
