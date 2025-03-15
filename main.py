import os
import logging
import json
import time
import threading
import signal
from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Importar serviços e utilitários
from ad_manager.utils.facebook_integration import FacebookAdsAPI
from ad_manager.utils.interest_analyzer import get_interests, analyze_interests, get_recommended_interests
from ad_manager.utils.openai_utils import generate_ad_copy
from ad_manager.utils.monitoring import setup_logging, register_performance_metric
from ad_manager.services.performance_analysis_service import analyze_ad_performance, save_analysis_report
from modules.ai_engine import AIEngine
from modules.optimization import CampaignOptimizer

# Inicializar aplicação Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'lion-dedetizadora-secret-key')

# Variáveis globais
services_running = False
service_threads = []

def start_service_thread(service_func, service_name):
    """Start a service in a separate thread."""
    thread = threading.Thread(target=service_func, name=service_name)
    thread.daemon = True
    thread.start()
    logger.info(f"Started service: {service_name}")
    return thread

def start_services():
    """Start all background services."""
    global services_running, service_threads
    
    if not services_running:
        # Importar serviços apenas quando necessário (lazy loading)
        from ad_manager.services.ad_creation_service import start_service as start_ad_creation
        from ad_manager.services.budget_optimization_service import start_service as start_budget_optimization
        from ad_manager.services.performance_analysis_service import start_service as start_performance_analysis, schedule_daily_analysis
        
        # Iniciar serviços em threads separadas
        service_threads = [
            start_service_thread(start_ad_creation, "Ad Creation Service"),
            start_service_thread(start_budget_optimization, "Budget Optimization Service"),
            start_service_thread(start_performance_analysis, "Performance Analysis Service"),
            start_service_thread(schedule_daily_analysis, "Daily Analysis Scheduler")
        ]
        
        services_running = True
        logger.info("All services started successfully")
    else:
        logger.info("Services already running")

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/')
def index():
    return render_template('index.html', title="Lion Dedetizadora - Gerenciador de Anúncios")

@app.route('/config')
def config_page():
    return render_template('config.html', title="Configurações do Sistema")

@app.route('/config/save', methods=['POST'])
def save_config():
    """Salva as configurações de API e serviços no arquivo .env"""
    
    # Obter dados do formulário
    data = request.form
    
    # Lista de chaves a serem salvas
    env_keys = [
        'OPENAI_API_KEY', 'FB_ACCESS_TOKEN', 'FB_ACCOUNT_ID',
        'EMAIL_USERNAME', 'EMAIL_PASSWORD', 'EMAIL_RECIPIENT'
    ]
    
    # Carregar o arquivo .env existente
    env_content = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as file:
            for line in file:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_content[key] = value
    
    # Atualizar com os novos valores
    for key in env_keys:
        if key in data and data[key]:
            env_content[key] = data[key]
    
    # Salvar o arquivo .env atualizado
    with open('.env', 'w', encoding='utf-8') as file:
        for key, value in env_content.items():
            file.write(f"{key}={value}\n")
    
    return redirect(url_for('config_page'))

@app.route('/api/interesses', methods=['GET'])
def interesses_endpoint():
    """Get interests based on pest control industry."""
    query = request.args.get('q', 'dedetização')
    interests = get_interests(query)
    return jsonify(interests)

@app.route('/api/analisar', methods=['POST'])
def analisar_endpoint():
    """Analyze and segment interests based on audience size."""
    interests = request.json.get('interests', [])
    analysis = analyze_interests(interests)
    return jsonify(analysis)

@app.route('/api/recomendacoes', methods=['GET'])
def recomendacoes_endpoint():
    """Get campaign interest recommendations."""
    query = request.args.get('q', 'dedetização')
    recommendations = get_recommended_interests(query)
    return jsonify(recommendations)

@app.route('/api/texto-anuncio', methods=['POST'])
def texto_anuncio_endpoint():
    """Get AI-generated ad copy for a specific target audience and service."""
    data = request.json
    target_audience = data.get('target_audience', 'proprietários de casas')
    service_focus = data.get('service_focus', 'dedetização residencial')
    
    ad_copy = generate_ad_copy(target_audience, service_focus)
    return jsonify(ad_copy)

@app.route('/api/status', methods=['GET'])
def status_endpoint():
    """Get system status information."""
    from ad_manager.config import validate_config
    
    # Verificar status das configurações
    config_status, config_details = validate_config()
    
    # Verificar status da IA
    ai_engine = AIEngine()
    ai_status = ai_engine.load_models()
    
    # Verificar status do Facebook
    fb_api = FacebookAdsAPI()
    fb_status = fb_api.check_connection()
    
    status = {
        "system": {
            "status": "online",
            "services_running": services_running,
            "services_count": len(service_threads) if services_running else 0,
            "timestamp": time.time()
        },
        "configuration": {
            "status": "ok" if config_status else "incomplete",
            "details": config_details
        },
        "facebook_api": {
            "status": "connected" if fb_status else "disconnected"
        },
        "ai_engine": {
            "status": "ready" if ai_status else "unavailable"
        }
    }
    
    return jsonify(status)

@app.route('/api/chart/performance', methods=['GET'])
def performance_chart_data():
    """Fornece dados para o gráfico de desempenho de anúncios com CTR e conversões."""
    
    # Simulação de dados para desenvolvimento
    data = {
        "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "datasets": [
            {
                "label": "CTR (%)",
                "data": [1.8, 2.1, 2.5, 2.3, 3.1, 2.9],
                "borderColor": "rgba(75, 192, 192, 1)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)"
            },
            {
                "label": "Conversões",
                "data": [12, 15, 18, 14, 22, 24],
                "borderColor": "rgba(153, 102, 255, 1)",
                "backgroundColor": "rgba(153, 102, 255, 0.2)"
            }
        ]
    }
    
    # Em um ambiente de produção, buscaríamos esses dados do banco de dados
    # ou da API do Facebook com código como:
    # fb_api = FacebookAdsAPI()
    # campaign_data = fb_api.get_campaign_performance_data(days=180)
    # data = analytics.prepare_chart_data(campaign_data)
    
    return jsonify(data)

@app.route('/api/chart/budget-roi', methods=['GET'])
def budget_roi_chart_data():
    """Fornece dados para o gráfico de orçamento e ROI."""
    
    # Simulação de dados para desenvolvimento
    data = {
        "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        "datasets": [
            {
                "label": "Orçamento (R$)",
                "data": [500, 600, 750, 800, 900, 1000],
                "borderColor": "rgba(54, 162, 235, 1)",
                "backgroundColor": "rgba(54, 162, 235, 0.2)"
            },
            {
                "label": "ROI (%)",
                "data": [220, 245, 290, 275, 310, 330],
                "borderColor": "rgba(255, 99, 132, 1)",
                "backgroundColor": "rgba(255, 99, 132, 0.2)"
            }
        ]
    }
    
    return jsonify(data)

@app.route('/api/chart/audience', methods=['GET'])
def audience_chart_data():
    """Fornece dados para o gráfico de segmentação de público."""
    
    # Simulação de dados para desenvolvimento
    data = {
        "labels": ["Proprietários", "Condomínios", "Empresas", "Restaurantes", "Hotéis", "Clínicas"],
        "datasets": [{
            "label": "Tamanho do Público",
            "data": [120000, 85000, 65000, 45000, 30000, 25000],
            "backgroundColor": [
                "rgba(255, 99, 132, 0.6)",
                "rgba(54, 162, 235, 0.6)",
                "rgba(255, 206, 86, 0.6)",
                "rgba(75, 192, 192, 0.6)",
                "rgba(153, 102, 255, 0.6)",
                "rgba(255, 159, 64, 0.6)"
            ]
        }]
    }
    
    return jsonify(data)

@app.route('/solicitar-chaves', methods=['GET'])
def solicitar_chaves():
    """Solicita ao usuário as chaves de API necessárias"""
    return render_template('solicitar_chaves.html')

if __name__ == '__main__':
    # Configurar manipulador de sinais para encerramento gracioso
    def signal_handler(sig, frame):
        logger.info("Recebido sinal de encerramento. Encerrando threads...")
        global services_running
        services_running = False
        # Allow some time for threads to terminate gracefully
        time.sleep(1)
        logger.info("Sistema encerrado.")
        os._exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar serviços em segundo plano
    start_services()
    
    # Iniciar servidor web
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'True').lower() == 'true')
