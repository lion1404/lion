import os
import logging
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Tentar importar a biblioteca do Facebook se estiver disponível
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    FB_API_AVAILABLE = True
except ImportError:
    FB_API_AVAILABLE = False
    
# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

class FacebookAdsAPI:
    """
    Classe para interagir com a API de anúncios do Facebook
    """
    def __init__(self):
        self.access_token = os.environ.get('FB_ACCESS_TOKEN')
        self.account_id = os.environ.get('FB_ACCOUNT_ID')
        self.api_initialized = False
        
        # Inicializar API se credenciais estiverem disponíveis
        if self.access_token and self.account_id and FB_API_AVAILABLE:
            try:
                FacebookAdsApi.init(self.access_token)
                self.account = AdAccount('act_' + self.account_id)
                self.api_initialized = True
                logger.info("API do Facebook inicializada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar API do Facebook: {str(e)}")
                self.api_initialized = False
        else:
            if not FB_API_AVAILABLE:
                logger.warning("SDK do Facebook não está disponível. Usando dados simulados.")
            else:
                logger.warning("Credenciais do Facebook não estão configuradas. Usando dados simulados.")
    
    def check_connection(self):
        """
        Verifica se a conexão com a API do Facebook está funcionando
        """
        if not self.api_initialized:
            logger.warning("API do Facebook não inicializada. Não é possível verificar conexão.")
            return False
        
        try:
            # Tentar obter informações básicas da conta
            account_info = self.account.api_get(fields=['name', 'account_status'])
            logger.info(f"Conexão com a API do Facebook verificada. Conta: {account_info.get('name')}")
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com a API do Facebook: {str(e)}")
            return False
    
    def get_ad_accounts(self):
        """
        Obtém as contas de anúncios disponíveis para o usuário autenticado
        """
        if not self.api_initialized:
            logger.warning("API do Facebook não inicializada. Usando dados simulados.")
            return self._simulate_accounts()
        
        try:
            # Tentar obter contas de anúncios
            accounts = self.account.get_ad_accounts(fields=['name', 'account_status', 'amount_spent'])
            accounts_data = [account.export_data() for account in accounts]
            logger.info(f"Obtidas {len(accounts_data)} contas de anúncios")
            return accounts_data
        except Exception as e:
            logger.error(f"Erro ao obter contas de anúncios: {str(e)}")
            return self._simulate_accounts()
    
    def get_campaigns(self):
        """
        Obtém as campanhas da conta de anúncios
        """
        if not self.api_initialized:
            logger.warning("API do Facebook não inicializada. Usando dados simulados.")
            return self._simulate_campaigns()
        
        try:
            # Tentar obter campanhas
            campaigns = self.account.get_campaigns(fields=[
                'name', 'objective', 'status', 'daily_budget', 'lifetime_budget',
                'created_time', 'start_time', 'stop_time'
            ])
            
            campaigns_data = [campaign.export_data() for campaign in campaigns]
            logger.info(f"Obtidas {len(campaigns_data)} campanhas")
            return campaigns_data
        except Exception as e:
            logger.error(f"Erro ao obter campanhas: {str(e)}")
            return self._simulate_campaigns()
    
    def get_campaign_insights(self, campaign_id=None, date_preset="last_30_days"):
        """
        Obtém insights de desempenho para uma campanha específica ou todas as campanhas
        """
        if not self.api_initialized:
            logger.warning("API do Facebook não inicializada. Usando dados simulados.")
            return self._simulate_campaign_insights(campaign_id)
        
        try:
            # Definir parâmetros
            params = {
                'date_preset': date_preset,
                'time_increment': 1  # Dados diários
            }
            
            # Definir campos a serem obtidos
            fields = [
                'campaign_name', 'impressions', 'clicks', 'spend', 'actions',
                'ctr', 'cpc', 'reach', 'frequency', 'cost_per_action_type'
            ]
            
            # Obter insights para uma campanha específica ou todas
            if campaign_id:
                campaign = Campaign(campaign_id)
                insights = campaign.get_insights(fields=fields, params=params)
                logger.info(f"Obtidos insights para a campanha {campaign_id}")
            else:
                insights = self.account.get_insights(fields=fields, params=params)
                logger.info("Obtidos insights para todas as campanhas")
            
            # Processar dados de insights
            insights_data = []
            for insight in insights:
                # Extrair ações (conversões) se disponíveis
                actions = {}
                if 'actions' in insight:
                    for action in insight['actions']:
                        action_type = action['action_type']
                        actions[action_type] = action['value']
                
                # Criar entrada de dados
                data = insight.export_data()
                data['actions_data'] = actions
                insights_data.append(data)
            
            return insights_data
        except Exception as e:
            logger.error(f"Erro ao obter insights: {str(e)}")
            return self._simulate_campaign_insights(campaign_id)
    
    def create_campaign(self, name, objective, budget, status="PAUSED"):
        """
        Cria uma nova campanha
        """
        if not self.api_initialized:
            logger.warning("API do Facebook não inicializada. Usando simulação.")
            return self._simulate_create_campaign(name, objective, budget, status)
        
        try:
            # Definir parâmetros da campanha
            params = {
                'name': name,
                'objective': objective,
                'status': status,
                'special_ad_categories': []
            }
            
            # Definir orçamento
            if budget > 0:
                params['daily_budget'] = int(budget * 100)  # Converter para centavos
            
            # Criar campanha
            campaign = self.account.create_campaign(params=params)
            logger.info(f"Campanha criada com sucesso: {campaign['id']}")
            
            # Obter dados completos da campanha
            campaign_data = campaign.api_get(fields=[
                'id', 'name', 'objective', 'status', 'daily_budget'
            ])
            
            return campaign_data
        except Exception as e:
            logger.error(f"Erro ao criar campanha: {str(e)}")
            return self._simulate_create_campaign(name, objective, budget, status)
    
    def update_campaign_budget(self, campaign_id, budget):
        """
        Atualiza o orçamento de uma campanha existente
        """
        if not self.api_initialized:
            logger.warning("API do Facebook não inicializada. Usando simulação.")
            return self._simulate_update_campaign(campaign_id, {'budget': budget})
        
        try:
            # Converter orçamento para centavos
            budget_in_cents = int(budget * 100)
            
            # Atualizar campanha
            campaign = Campaign(campaign_id)
            result = campaign.api_update(
                params={'daily_budget': budget_in_cents}
            )
            
            if result:
                logger.info(f"Orçamento da campanha {campaign_id} atualizado para R${budget:.2f}")
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'new_budget': budget
                }
            else:
                logger.error(f"Falha ao atualizar orçamento da campanha {campaign_id}")
                return {
                    'success': False,
                    'campaign_id': campaign_id,
                    'error': 'API returned false'
                }
        except Exception as e:
            logger.error(f"Erro ao atualizar orçamento da campanha {campaign_id}: {str(e)}")
            return self._simulate_update_campaign(campaign_id, {'budget': budget})
    
    def _simulate_accounts(self):
        """
        Gera dados simulados para contas de anúncios
        """
        logger.info("Gerando dados simulados para contas de anúncios")
        
        # Definir dados simulados
        accounts = [
            {
                'id': 'act_12345678',
                'name': 'Lion Dedetizadora - Principal',
                'account_status': 1,  # 1 = ativo
                'amount_spent': 1250.75
            },
            {
                'id': 'act_23456789',
                'name': 'Lion Dedetizadora - Testes',
                'account_status': 1,
                'amount_spent': 350.50
            }
        ]
        
        return accounts
    
    def _simulate_campaigns(self):
        """
        Gera dados simulados para campanhas
        """
        logger.info("Gerando dados simulados para campanhas")
        
        # Definir dados simulados
        campaigns = [
            {
                'id': '1001001001001',
                'name': 'Dedetização Residencial - Conversões',
                'objective': 'CONVERSIONS',
                'status': 'ACTIVE',
                'daily_budget': 1000,  # Em centavos
                'created_time': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            },
            {
                'id': '1001001001002',
                'name': 'Dedetização Comercial - Tráfego',
                'objective': 'TRAFFIC',
                'status': 'ACTIVE',
                'daily_budget': 1500,
                'created_time': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
            },
            {
                'id': '1001001001003',
                'name': 'Descupinização - Reconhecimento',
                'objective': 'AWARENESS',
                'status': 'PAUSED',
                'daily_budget': 800,
                'created_time': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
            }
        ]
        
        return campaigns
    
    def _simulate_campaign_insights(self, campaign_id=None):
        """
        Gera dados simulados para insights de campanha
        """
        # Definir período de 30 dias
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Definir dados base para cada campanha
        campaign_base_data = {
            '1001001001001': {  # Dedetização Residencial - Conversões
                'name': 'Dedetização Residencial - Conversões',
                'base_impressions': 1200,
                'base_ctr': 2.5,
                'base_cpc': 0.45,
                'base_conv_rate': 3.0,
                'base_budget': 10.0
            },
            '1001001001002': {  # Dedetização Comercial - Tráfego
                'name': 'Dedetização Comercial - Tráfego',
                'base_impressions': 1800,
                'base_ctr': 3.2,
                'base_cpc': 0.38,
                'base_conv_rate': 2.2,
                'base_budget': 15.0
            },
            '1001001001003': {  # Descupinização - Reconhecimento
                'name': 'Descupinização - Reconhecimento',
                'base_impressions': 2200,
                'base_ctr': 1.8,
                'base_cpc': 0.30,
                'base_conv_rate': 1.5,
                'base_budget': 8.0
            }
        }
        
        # Gerar insights
        insights = []
        
        # Se um ID for especificado, gerar apenas para essa campanha
        campaign_ids = [campaign_id] if campaign_id else list(campaign_base_data.keys())
        
        for camp_id in campaign_ids:
            # Se o ID não estiver nos dados base, usar o primeiro
            if camp_id not in campaign_base_data:
                camp_id = list(campaign_base_data.keys())[0]
            
            base_data = campaign_base_data[camp_id]
            
            # Gerar dados para cada dia
            current_date = start_date
            while current_date <= end_date:
                # Fatores que afetam o desempenho
                day_of_week = current_date.weekday()
                day_factor = 0.8 if day_of_week >= 5 else 1.0  # Fim de semana tem menos tráfego
                
                # Tendência crescente ao longo do tempo
                days_passed = (current_date - start_date).days
                trend_factor = 1.0 + (days_passed * 0.01)
                
                # Ruído aleatório para variação natural
                noise = random.uniform(0.85, 1.15)
                
                # Calcular métricas do dia
                impressions = int(base_data['base_impressions'] * day_factor * trend_factor * noise)
                ctr = base_data['base_ctr'] * day_factor * noise
                clicks = int((ctr / 100) * impressions)
                cpc = base_data['base_cpc'] * noise
                spend = round(clicks * cpc, 2)
                
                # Limite de gasto diário
                spend = min(spend, base_data['base_budget'])
                
                # Conversões e ações
                conv_rate = base_data['base_conv_rate'] * noise
                conversions = int((conv_rate / 100) * clicks)
                
                # Criar objeto de insights
                insight = {
                    'date_start': current_date.strftime('%Y-%m-%d'),
                    'date_stop': current_date.strftime('%Y-%m-%d'),
                    'campaign_id': camp_id,
                    'campaign_name': base_data['name'],
                    'impressions': impressions,
                    'clicks': clicks,
                    'ctr': ctr,
                    'cpc': cpc,
                    'spend': spend,
                    'reach': int(impressions * 0.8),  # 80% das impressões são pessoas únicas
                    'frequency': 1.25,  # Média de 1.25 impressões por pessoa
                    'actions_data': {
                        'lead': conversions,
                        'page_engagement': int(clicks * 1.5),
                        'landing_page_view': int(clicks * 0.9)
                    }
                }
                
                insights.append(insight)
                current_date += timedelta(days=1)
        
        logger.info(f"Gerados {len(insights)} insights simulados")
        return insights
    
    def _simulate_create_campaign(self, name, objective, budget, status):
        """
        Simula a criação de uma campanha
        """
        # Gerar ID aleatório
        campaign_id = ''.join(random.choices('0123456789', k=13))
        
        campaign = {
            'id': campaign_id,
            'name': name,
            'objective': objective,
            'status': status,
            'daily_budget': int(budget * 100),  # Converter para centavos
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'simulated': True
        }
        
        logger.info(f"Simulada criação de campanha: {campaign_id}")
        return campaign
    
    def _simulate_update_campaign(self, campaign_id, params):
        """
        Simula a atualização de uma campanha
        """
        # Verificar se o parâmetro budget está presente
        if 'budget' in params:
            result = {
                'success': True,
                'campaign_id': campaign_id,
                'new_budget': params['budget'],
                'simulated': True
            }
        else:
            result = {
                'success': True,
                'campaign_id': campaign_id,
                'updated_params': params,
                'simulated': True
            }
        
        logger.info(f"Simulada atualização de campanha: {campaign_id}")
        return result
    
    def get_campaign_performance_data(self, days=30):
        """
        Obtém e processa dados de desempenho de campanhas para análise
        Retorna um DataFrame pronto para uso com machine learning
        """
        # Obter insights das campanhas
        insights = self.get_campaign_insights(date_preset=f"last_{days}_days")
        
        # Se não houver dados, retornar DataFrame vazio
        if not insights:
            logger.warning("Não foram encontrados dados de desempenho")
            return pd.DataFrame()
        
        # Processar dados
        data = []
        
        for insight in insights:
            # Extrair data
            date = datetime.strptime(insight['date_start'], '%Y-%m-%d')
            
            # Extrair ações (conversões)
            conversions = 0
            if 'actions_data' in insight and 'lead' in insight['actions_data']:
                conversions = int(insight['actions_data']['lead'])
            
            # Criar entrada
            entry = {
                'date': date,
                'campaign_id': insight['campaign_id'],
                'campaign_name': insight['campaign_name'],
                'impressions': insight['impressions'],
                'clicks': insight['clicks'],
                'spend': insight['spend'],
                'ctr': insight['ctr'],
                'cpc': insight['cpc'],
                'conversions': conversions,
                'day_of_week': date.weekday(),
                'month': date.month
            }
            
            # Calcular métricas derivadas
            if conversions > 0:
                entry['cpa'] = entry['spend'] / conversions
                entry['conversion_rate'] = (conversions / entry['clicks']) * 100 if entry['clicks'] > 0 else 0
            else:
                entry['cpa'] = 0
                entry['conversion_rate'] = 0
            
            data.append(entry)
        
        # Criar DataFrame
        df = pd.DataFrame(data)
        
        # Ordenar por data
        df = df.sort_values('date')
        
        logger.info(f"Processados {len(df)} registros de desempenho de campanhas")
        return df
