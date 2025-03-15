import os
import logging
import json
import numpy as np
import pandas as pd
import pickle
import sqlite3
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, db_path="campaign_data.db"):
        """
        Inicializa o motor de IA para otimização de campanhas
        
        Args:
            db_path (str): Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self.models = {
            'cpc': None,
            'ctr': None,
            'conversion_rate': None
        }
        self.scalers = {
            'cpc': None,
            'ctr': None,
            'conversion_rate': None
        }
        
        # Criar diretório de modelos se não existir
        if not os.path.exists('models'):
            os.makedirs('models')
    
    def load_data(self):
        """
        Carrega dados históricos do banco de dados
        
        Returns:
            pd.DataFrame: DataFrame com dados processados
        """
        try:
            if not os.path.exists(self.db_path):
                logger.warning(f"Banco de dados {self.db_path} não encontrado. Gerando dados simulados para teste.")
                return self._generate_demo_data()
            
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT 
                c.id, c.name, c.objective, c.status, c.daily_budget,
                p.date, p.impressions, p.clicks, p.spend, p.conversions,
                strftime('%w', p.date) as day_of_week,
                strftime('%m', p.date) as month
            FROM campaigns c
            JOIN performance p ON c.id = p.campaign_id
            WHERE p.date >= date('now', '-90 days')
            ORDER BY p.date DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Processar dados
            df['ctr'] = (df['clicks'] / df['impressions']) * 100
            df['cpc'] = df['spend'] / df['clicks'].apply(lambda x: max(x, 1))  # Evitar divisão por zero
            df['conversion_rate'] = (df['conversions'] / df['clicks']) * 100
            df['day_of_week'] = df['day_of_week'].astype(int)
            df['month'] = df['month'].astype(int)
            
            # One-hot encoding para variáveis categóricas
            df = pd.get_dummies(df, columns=['status', 'objective'])
            
            return df
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            return self._generate_demo_data()
    
    def _generate_demo_data(self):
        """
        Gera dados simulados para testes
        
        Returns:
            pd.DataFrame: DataFrame com dados simulados
        """
        np.random.seed(42)
        
        # Definir parâmetros para simulação
        n_campaigns = 5
        n_days = 90
        campaign_ids = [f"camp_{i}" for i in range(1, n_campaigns + 1)]
        campaign_names = [f"Campanha {i}" for i in range(1, n_campaigns + 1)]
        objectives = ["CONVERSIONS", "TRAFFIC", "AWARENESS"]
        statuses = ["ACTIVE", "PAUSED"]
        
        # Gerar dados base
        data = []
        
        for camp_idx in range(n_campaigns):
            campaign_id = campaign_ids[camp_idx]
            campaign_name = campaign_names[camp_idx]
            objective = np.random.choice(objectives)
            status = np.random.choice(statuses)
            daily_budget = np.random.uniform(10, 50)
            
            # Simular tendências temporais realistas
            base_impressions = np.random.uniform(1000, 5000)
            base_ctr = np.random.uniform(1.0, 3.0)
            base_conv_rate = np.random.uniform(2.0, 8.0)
            
            for day in range(n_days):
                date = (datetime.now() - pd.Timedelta(days=n_days-day)).strftime('%Y-%m-%d')
                
                # Adicionar tendências e sazonalidade
                day_of_week = pd.Timestamp(date).dayofweek
                month = pd.Timestamp(date).month
                
                # Ajustar por dia da semana (fim de semana tem menos tráfego)
                dow_factor = 0.8 if day_of_week >= 5 else 1.0
                
                # Tendência crescente ao longo do tempo
                trend_factor = 1.0 + (day * 0.002)
                
                # Adicionar ruído normal
                noise = np.random.normal(1.0, 0.1)
                
                # Calcular métricas finais
                impressions = int(base_impressions * dow_factor * trend_factor * noise)
                ctr = base_ctr * dow_factor * noise
                clicks = int((ctr / 100) * impressions)
                spend = daily_budget * np.random.uniform(0.8, 1.0)
                conversion_rate = base_conv_rate * noise
                conversions = int((conversion_rate / 100) * clicks)
                
                # Adicionar à lista de dados
                data.append({
                    'id': campaign_id,
                    'name': campaign_name,
                    'objective': objective,
                    'status': status,
                    'daily_budget': daily_budget,
                    'date': date,
                    'impressions': impressions,
                    'clicks': clicks,
                    'spend': spend,
                    'conversions': conversions,
                    'day_of_week': day_of_week,
                    'month': month
                })
        
        # Criar DataFrame
        df = pd.DataFrame(data)
        
        # Adicionar métricas calculadas
        df['ctr'] = (df['clicks'] / df['impressions']) * 100
        df['cpc'] = df['spend'] / df['clicks'].apply(lambda x: max(x, 1))
        df['conversion_rate'] = (df['conversions'] / df['clicks']) * 100
        
        # One-hot encoding
        df = pd.get_dummies(df, columns=['status', 'objective'])
        
        return df
    
    def train_model(self):
        """
        Treina o modelo de Machine Learning para prever CPC, CTR e conversões
        
        Returns:
            bool: True se o treinamento foi bem-sucedido
        """
        try:
            df = self.load_data()
            if df.empty or len(df) < 10:
                logger.warning("Dados insuficientes para treinamento de modelo")
                return False
            
            # Features para treinamento 
            feature_cols = [
                'impressions', 'daily_budget', 
                'day_of_week', 'month'
            ]
            
            # Adicionar colunas de status e objetivo (one-hot encoded)
            status_cols = [col for col in df.columns if col.startswith('status_')]
            objective_cols = [col for col in df.columns if col.startswith('objective_')]
            feature_cols.extend(status_cols)
            feature_cols.extend(objective_cols)
            
            # Treinar um modelo para cada métrica alvo
            target_metrics = ['cpc', 'ctr', 'conversion_rate']
            
            for metric in target_metrics:
                logger.info(f"Treinando modelo para prever {metric}...")
                
                # Preparar dados
                X = df[feature_cols]
                y = df[metric]
                
                # Dividir em treino e teste
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Escalar features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Treinar modelo
                model = RandomForestRegressor(
                    n_estimators=100, 
                    max_depth=10,
                    random_state=42
                )
                model.fit(X_train_scaled, y_train)
                
                # Avaliar modelo
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                logger.info(f"Modelo para {metric}: MAE={mae:.4f}, R²={r2:.4f}")
                
                # Salvar modelo e scaler
                self.models[metric] = model
                self.scalers[metric] = scaler
                
                self._save_model(model, f"models/{metric}_model.pkl")
                self._save_model(scaler, f"models/{metric}_scaler.pkl")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            return False
    
    def _save_model(self, model, filename):
        """
        Salva um modelo treinado em arquivo
        
        Args:
            model: Modelo treinado
            filename (str): Nome do arquivo para salvar
        """
        try:
            with open(filename, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Modelo salvo em {filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar modelo em {filename}: {str(e)}")
    
    def _load_model(self, filename):
        """
        Carrega um modelo salvo a partir de um arquivo
        
        Args:
            filename (str): Nome do arquivo do modelo
            
        Returns:
            object: Modelo carregado ou None em caso de erro
        """
        try:
            if not os.path.exists(filename):
                logger.warning(f"Arquivo de modelo {filename} não encontrado")
                return None
                
            with open(filename, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Modelo carregado de {filename}")
            return model
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de {filename}: {str(e)}")
            return None
    
    def load_models(self):
        """
        Carrega todos os modelos salvos
        
        Returns:
            bool: True se pelo menos um modelo foi carregado com sucesso
        """
        try:
            metrics = ['cpc', 'ctr', 'conversion_rate']
            success = False
            
            for metric in metrics:
                model_path = f"models/{metric}_model.pkl"
                scaler_path = f"models/{metric}_scaler.pkl"
                
                model = self._load_model(model_path)
                scaler = self._load_model(scaler_path)
                
                if model is not None and scaler is not None:
                    self.models[metric] = model
                    self.scalers[metric] = scaler
                    success = True
            
            # Se não tiver modelos salvos, treinar novos
            if not success:
                logger.info("Nenhum modelo encontrado. Treinando novos modelos...")
                return self.train_model()
                
            return success
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {str(e)}")
            return False
    
    def predict_cpc(self, impressions, day_of_week=None, month=None, status='ACTIVE', objective='CONVERSIONS'):
        """
        Faz uma previsão do CPC baseado em novas impressões
        
        Args:
            impressions (int): Número de impressões esperado
            day_of_week (int, optional): Dia da semana (0-6, onde 0 é segunda)
            month (int, optional): Mês (1-12)
            status (str): Status da campanha
            objective (str): Objetivo da campanha
            
        Returns:
            float: CPC previsto
        """
        try:
            # Verificar se o modelo está carregado
            if self.models['cpc'] is None or self.scalers['cpc'] is None:
                if not self.load_models():
                    logger.error("Modelo de CPC não disponível. Retornando estimativa básica.")
                    return impressions * 0.01  # Estimativa simples: 1% do total de impressões
            
            # Obter data atual se não especificada
            if day_of_week is None:
                day_of_week = datetime.now().weekday()
            if month is None:
                month = datetime.now().month
                
            # Preparar dados para previsão
            data = {
                'impressions': [impressions],
                'daily_budget': [10.0],  # Valor padrão
                'day_of_week': [day_of_week],
                'month': [month],
            }
            
            # Adicionar colunas one-hot para status e objetivo
            for s in ['ACTIVE', 'PAUSED']:
                data[f'status_{s}'] = [1 if status == s else 0]
                
            for o in ['CONVERSIONS', 'TRAFFIC', 'AWARENESS']:
                data[f'objective_{o}'] = [1 if objective == o else 0]
            
            # Criar DataFrame
            X = pd.DataFrame(data)
            
            # Ajustar colunas ao formato esperado pelo modelo
            model_columns = self.models['cpc'].feature_names_in_
            for col in model_columns:
                if col not in X.columns:
                    X[col] = 0
            X = X[model_columns]
            
            # Escalar dados
            X_scaled = self.scalers['cpc'].transform(X)
            
            # Fazer previsão
            cpc_pred = self.models['cpc'].predict(X_scaled)[0]
            
            # Garantir que o CPC seja positivo
            return max(0.01, cpc_pred)
            
        except Exception as e:
            logger.error(f"Erro ao prever CPC: {str(e)}")
            return impressions * 0.01  # Estimativa simples: 1% do total de impressões
    
    def adjust_budget(self, roi, ctr, budget):
        """
        Ajusta o orçamento automaticamente baseado no desempenho
        
        Args:
            roi (float): ROI atual em percentual
            ctr (float): CTR atual em percentual
            budget (float): Orçamento atual
            
        Returns:
            float: Novo orçamento recomendado
        """
        try:
            # Lógica de ajuste baseada em ROI e CTR
            if roi > 300 and ctr > 2.0:
                # Desempenho excelente: aumentar orçamento em 30%
                return budget * 1.3
            elif roi > 200 and ctr > 1.5:
                # Desempenho muito bom: aumentar orçamento em 20%
                return budget * 1.2
            elif roi > 150 and ctr > 1.0:
                # Desempenho bom: aumentar orçamento em 10%
                return budget * 1.1
            elif roi < 100 and ctr < 0.8:
                # Desempenho ruim: reduzir orçamento em 20%
                return budget * 0.8
            elif roi < 50 and ctr < 0.5:
                # Desempenho muito ruim: reduzir orçamento em 50%
                return budget * 0.5
            else:
                # Desempenho médio: manter orçamento
                return budget
        except Exception as e:
            logger.error(f"Erro ao ajustar orçamento: {str(e)}")
            return budget
    
    def check_creative_performance(self, ctr_history):
        """
        Avalia o desempenho do criativo baseado no histórico de CTR
        
        Args:
            ctr_history (list): Lista de valores históricos de CTR
            
        Returns:
            dict: Avaliação do desempenho e recomendações
        """
        try:
            if not ctr_history or len(ctr_history) < 3:
                return {
                    "status": "insufficient_data",
                    "message": "Dados insuficientes para avaliação do criativo",
                    "recommendation": "Continue coletando dados por pelo menos 3 dias"
                }
            
            # Calcular métricas
            current_ctr = ctr_history[-1]
            avg_ctr = sum(ctr_history) / len(ctr_history)
            trend = current_ctr - ctr_history[0]
            
            # Avaliar desempenho e gerar recomendações
            if current_ctr > 2.0 and trend >= 0:
                status = "excellent"
                message = "O criativo está tendo um desempenho excelente e melhorando"
                recommendation = "Mantenha o criativo atual e considere aumentar o orçamento"
            elif current_ctr > 1.5 and trend >= 0:
                status = "good"
                message = "O criativo está tendo um bom desempenho"
                recommendation = "Mantenha o criativo atual"
            elif current_ctr < 1.0 and trend < 0:
                status = "poor"
                message = "O criativo está tendo um desempenho abaixo do esperado e piorando"
                recommendation = "Considere atualizar o criativo com um novo texto ou imagem"
            elif current_ctr < 0.8:
                status = "critical"
                message = "O criativo está tendo um desempenho muito ruim"
                recommendation = "Substitua o criativo imediatamente"
            else:
                status = "average"
                message = "O criativo está tendo um desempenho médio"
                recommendation = "Considere fazer testes A/B com novos criativos"
            
            return {
                "status": status,
                "message": message,
                "recommendation": recommendation,
                "metrics": {
                    "current_ctr": current_ctr,
                    "average_ctr": avg_ctr,
                    "trend": trend
                }
            }
        except Exception as e:
            logger.error(f"Erro ao avaliar desempenho do criativo: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao avaliar desempenho: {str(e)}",
                "recommendation": "Verifique os dados de entrada"
            }
    
    def predict_campaign_performance(self, campaign_data):
        """
        Prevê o desempenho futuro de uma campanha com base nos dados atuais
        
        Args:
            campaign_data (dict): Dados atuais da campanha
            
        Returns:
            dict: Previsões de desempenho
        """
        try:
            # Extrair dados da campanha
            impressions = campaign_data.get('impressions', 1000)
            current_ctr = campaign_data.get('ctr', 1.0)
            current_budget = campaign_data.get('budget', 10.0)
            current_cpc = campaign_data.get('cpc', 0.5)
            current_conversions = campaign_data.get('conversions', 0)
            
            # Carregar modelos se necessário
            if any(model is None for model in self.models.values()):
                self.load_models()
            
            # Fazer previsões
            predicted_cpc = self.predict_cpc(impressions)
            
            # Estimar CTR baseado em tendências históricas ou usar modelo
            if self.models['ctr'] is not None:
                predicted_ctr = max(0.1, current_ctr * 1.05)  # Aumento simples de 5%
            else:
                predicted_ctr = current_ctr
            
            # Calcular métricas estimadas
            estimated_clicks = (predicted_ctr / 100) * impressions
            estimated_cost = estimated_clicks * predicted_cpc
            
            # Estimar conversões
            if current_conversions > 0 and estimated_clicks > 0:
                current_conversion_rate = (current_conversions / (current_ctr / 100 * impressions)) * 100
                estimated_conversions = (current_conversion_rate / 100) * estimated_clicks
            else:
                # Valor padrão se não houver dados de conversão
                estimated_conversions = estimated_clicks * 0.02  # Assumir taxa de conversão de 2%
            
            # Ajustar orçamento recomendado
            if estimated_cost > current_budget * 1.5:
                budget_recommendation = current_budget * 1.2  # Limite o aumento a 20%
                budget_message = "Aumente o orçamento em 20% para maximizar resultados"
            elif estimated_cost < current_budget * 0.7:
                budget_recommendation = current_budget * 0.9  # Redução suave de 10%
                budget_message = "Você pode reduzir o orçamento em 10% mantendo resultados"
            else:
                budget_recommendation = current_budget
                budget_message = "O orçamento atual está adequado para o desempenho esperado"
            
            return {
                "metrics": {
                    "estimated_impressions": int(impressions * 1.1),  # Crescimento de 10%
                    "estimated_ctr": round(predicted_ctr, 2),
                    "estimated_clicks": int(estimated_clicks),
                    "estimated_cpc": round(predicted_cpc, 2),
                    "estimated_cost": round(estimated_cost, 2),
                    "estimated_conversions": int(estimated_conversions)
                },
                "recommendations": {
                    "budget": round(budget_recommendation, 2),
                    "budget_message": budget_message,
                    "targeting": "Mantenha a segmentação atual com foco em proprietários de imóveis",
                    "creative": "Considere destacar a garantia do serviço e produtos seguros para pets"
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao prever desempenho da campanha: {str(e)}")
            return {
                "error": str(e),
                "recommendations": {
                    "budget": campaign_data.get('budget', 10.0),
                    "message": "Erro ao gerar previsões. Mantenha as configurações atuais."
                }
            }
