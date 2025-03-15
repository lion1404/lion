import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_config():
    """
    Verifica quais configurações estão disponíveis e retorna um relatório de status.
    Não levanta exceções para permitir que o sistema funcione em modo degradado.
    
    Returns:
        tuple: (status geral, dict com status específicos)
    """
    status = {}
    
    # Verificar configurações do Facebook
    fb_token = os.environ.get('FB_ACCESS_TOKEN')
    fb_account = os.environ.get('FB_ACCOUNT_ID')
    
    status['facebook_api'] = {
        'configured': bool(fb_token and fb_account),
        'details': {
            'access_token': bool(fb_token),
            'account_id': bool(fb_account)
        }
    }
    
    # Verificar configurações de e-mail
    email_username = os.environ.get('EMAIL_USERNAME')
    email_password = os.environ.get('EMAIL_PASSWORD')
    email_recipient = os.environ.get('EMAIL_RECIPIENT')
    
    status['email'] = {
        'configured': bool(email_username and email_password and email_recipient),
        'details': {
            'username': bool(email_username),
            'password': bool(email_password),
            'recipient': bool(email_recipient)
        }
    }
    
    # Verificar configurações da OpenAI
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    status['openai_api'] = {
        'configured': bool(openai_key),
        'details': {
            'api_key': bool(openai_key)
        }
    }
    
    # Verificar status geral
    overall_status = all([
        status['facebook_api']['configured'],
        status['email']['configured'],
        status['openai_api']['configured']
    ])
    
    return overall_status, status
