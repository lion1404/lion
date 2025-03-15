import logging
import math
from typing import Dict, List, Union, Optional

logger = logging.getLogger(__name__)

class CampaignAnalytics:
    """
    Classe para análise e cálculo de métricas de campanhas publicitárias.
    """
    
    @staticmethod
    def calculate_ctr(clicks, impressions):
        """
        Calcula a Taxa de Cliques (CTR)
        
        Args:
            clicks (int): Número de cliques
            impressions (int): Número de impressões
            
        Returns:
            float: Taxa de cliques (CTR) em percentual
        """
        if not impressions:
            return 0.0
        return (clicks / impressions) * 100
    
    @staticmethod
    def calculate_cpc(cost, clicks):
        """
        Calcula o Custo por Clique (CPC)
        
        Args:
            cost (float): Custo total
            clicks (int): Número de cliques
            
        Returns:
            float: Custo por clique (CPC)
        """
        if not clicks:
            return 0.0
        return cost / clicks
    
    @staticmethod
    def calculate_cpa(cost, conversions):
        """
        Calcula o Custo por Aquisição (CPA)
        
        Args:
            cost (float): Custo total
            conversions (int): Número de conversões
            
        Returns:
            float: Custo por aquisição (CPA)
        """
        if not conversions:
            return 0.0
        return cost / conversions
    
    @staticmethod
    def calculate_roi(revenue, cost):
        """
        Calcula o Retorno sobre Investimento (ROI)
        
        Args:
            revenue (float): Receita total
            cost (float): Custo total
            
        Returns:
            float: ROI em percentual
        """
        if not cost:
            return 0.0
        return ((revenue - cost) / cost) * 100
    
    @staticmethod
    def calculate_frequency(impressions, reach):
        """
        Calcula a frequência média de impressões por usuário
        
        Args:
            impressions (int): Número total de impressões
            reach (int): Número de usuários únicos alcançados
            
        Returns:
            float: Frequência média de impressões por usuário
        """
        if not reach:
            return 0.0
        return impressions / reach
    
    @staticmethod
    def analyze_trend(metrics_history, metric_name):
        """
        Analisa a tendência de uma métrica ao longo do tempo
        
        Args:
            metrics_history (List[Dict]): Lista de métricas históricas
            metric_name (str): Nome da métrica a ser analisada
            
        Returns:
            Dict: Análise da tendência
        """
        if not metrics_history or len(metrics_history) < 2:
            return {
                "trend": "unknown",
                "change": 0.0,
                "change_percent": 0.0,
                "message": "Dados históricos insuficientes para análise de tendência"
            }
        
        # Extrair valores da métrica
        values = [entry.get(metric_name, 0) for entry in metrics_history]
        
        # Calcular variação
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            change_percent = 100.0 if last_value > 0 else 0.0
        else:
            change_percent = ((last_value - first_value) / first_value) * 100
        
        # Determinar tendência
        if change_percent > 10:
            trend = "increasing"
            message = f"{metric_name} aumentou {change_percent:.1f}% no período analisado"
        elif change_percent < -10:
            trend = "decreasing"
            message = f"{metric_name} diminuiu {abs(change_percent):.1f}% no período analisado"
        else:
            trend = "stable"
            message = f"{metric_name} manteve-se estável no período analisado"
        
        return {
            "trend": trend,
            "change": last_value - first_value,
            "change_percent": change_percent,
            "message": message
        }
    
    def __init__(self, campaign_data=None):
        """
        Inicializa o analisador de campanhas
        
        Args:
            campaign_data (Dict, optional): Dados da campanha para análise
        """
        self.campaign_data = campaign_data or {}
        self.metrics = {}
        
        # Inicializar logger
        self.logger = logging.getLogger(__name__)
    
    def set_campaign_data(self, campaign_data):
        """
        Define os dados da campanha para análise
        
        Args:
            campaign_data (Dict): Dados da campanha
        """
        self.campaign_data = campaign_data
        # Limpar métricas calculadas anteriormente
        self.metrics = {}
    
    def calculate_all_metrics(self):
        """
        Calcula todas as métricas disponíveis para a campanha
        
        Returns:
            Dict: Dicionário com todas as métricas calculadas
        """
        try:
            # Extrair dados da campanha
            clicks = self.campaign_data.get('clicks', 0)
            impressions = self.campaign_data.get('impressions', 0)
            cost = self.campaign_data.get('cost', 0.0)
            conversions = self.campaign_data.get('conversions', 0)
            revenue = self.campaign_data.get('revenue', 0.0)
            reach = self.campaign_data.get('reach', 0)
            
            # Calcular métricas básicas
            self.metrics['ctr'] = self.calculate_ctr(clicks, impressions)
            self.metrics['cpc'] = self.calculate_cpc(cost, clicks)
            self.metrics['cpa'] = self.calculate_cpa(cost, conversions)
            self.metrics['roi'] = self.calculate_roi(revenue, cost)
            
            if reach:
                self.metrics['frequency'] = self.calculate_frequency(impressions, reach)
            
            # Adicionar métricas derivadas
            if conversions and clicks:
                self.metrics['conversion_rate'] = (conversions / clicks) * 100
            else:
                self.metrics['conversion_rate'] = 0.0
                
            if impressions:
                self.metrics['cpm'] = (cost / impressions) * 1000
            else:
                self.metrics['cpm'] = 0.0
            
            # Adicionar dados brutos
            self.metrics['raw'] = {
                'clicks': clicks,
                'impressions': impressions,
                'cost': cost,
                'conversions': conversions,
                'revenue': revenue
            }
            
            return self.metrics
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas: {str(e)}")
            return {}
    
    def generate_insights(self, benchmarks=None):
        """
        Gera insights baseados nos dados da campanha
        
        Args:
            benchmarks (Dict, optional): Valores de referência para comparação
            
        Returns:
            List[str]: Lista de insights gerados
        """
        insights = []
        
        # Garantir que as métricas foram calculadas
        if not self.metrics:
            self.calculate_all_metrics()
        
        # Usar benchmarks padrão se não forem fornecidos
        if not benchmarks:
            benchmarks = {
                'ctr': 1.0,  # CTR médio de 1%
                'cpc': 0.5,  # CPC médio de R$0,50
                'conversion_rate': 2.0,  # Taxa de conversão média de 2%
                'roi': 200.0  # ROI médio de 200%
            }
        
        # Analisar CTR
        ctr = self.metrics.get('ctr', 0)
        if ctr > benchmarks['ctr'] * 1.5:
            insights.append(f"CTR excelente de {ctr:.2f}%, superando a média do setor em {(ctr/benchmarks['ctr']-1)*100:.0f}%")
        elif ctr < benchmarks['ctr'] * 0.7:
            insights.append(f"CTR baixo de {ctr:.2f}%. Considere revisar o criativo ou a segmentação.")
        
        # Analisar CPC
        cpc = self.metrics.get('cpc', 0)
        if cpc < benchmarks['cpc'] * 0.8:
            insights.append(f"CPC eficiente de R${cpc:.2f}, abaixo da média do setor.")
        elif cpc > benchmarks['cpc'] * 1.3:
            insights.append(f"CPC elevado de R${cpc:.2f}. Considere ajustar lances ou melhorar a relevância dos anúncios.")
        
        # Analisar taxa de conversão
        conv_rate = self.metrics.get('conversion_rate', 0)
        if conv_rate > benchmarks['conversion_rate'] * 1.5:
            insights.append(f"Taxa de conversão excepcional de {conv_rate:.2f}%. Considere aumentar o orçamento.")
        elif conv_rate < benchmarks['conversion_rate'] * 0.7:
            insights.append(f"Taxa de conversão baixa de {conv_rate:.2f}%. Verifique a página de destino e a jornada de conversão.")
        
        # Analisar ROI
        roi = self.metrics.get('roi', 0)
        if roi > benchmarks['roi'] * 1.2:
            insights.append(f"ROI excelente de {roi:.2f}%. A campanha está gerando um retorno acima da média.")
        elif roi < benchmarks['roi'] * 0.7:
            insights.append(f"ROI baixo de {roi:.2f}%. Revise a estratégia de preços ou custos de aquisição.")
        elif roi < 0:
            insights.append(f"ROI negativo de {roi:.2f}%. A campanha está gerando prejuízo. Recomenda-se uma revisão urgente.")
        
        # Insights baseados na relação entre métricas
        clicks = self.metrics.get('raw', {}).get('clicks', 0)
        conversions = self.metrics.get('raw', {}).get('conversions', 0)
        
        if ctr > benchmarks['ctr'] * 1.2 and conv_rate < benchmarks['conversion_rate'] * 0.8:
            insights.append("Anúncios atraentes, mas com baixa conversão. Revise a página de destino e a coerência da oferta.")
        
        if clicks > 200 and conversions == 0:
            insights.append("Muitos cliques sem conversões. Verifique problemas técnicos no processo de conversão.")
        
        # Adicionar recomendações gerais se houver poucos insights
        if len(insights) < 2:
            if not insights:
                insights.append("Desempenho dentro das médias esperadas para o setor.")
            
            # Adicionar recomendação geral baseada no ROI
            if roi > 0:
                insights.append("Considere testes A/B para otimizar ainda mais o desempenho da campanha.")
            else:
                insights.append("Recomenda-se revisar a segmentação e o criativo para melhorar o desempenho.")
        
        return insights
    
    def get_performance_summary(self):
        """
        Obtém um resumo do desempenho da campanha
        
        Returns:
            Dict: Resumo do desempenho
        """
        # Garantir que as métricas foram calculadas
        if not self.metrics:
            self.calculate_all_metrics()
        
        # Obter insights
        insights = self.generate_insights()
        
        # Calcular classificação de desempenho
        performance_rating = self._calculate_performance_rating()
        
        # Montar resumo
        summary = {
            "campaign_name": self.campaign_data.get('name', 'Campanha sem nome'),
            "period": self.campaign_data.get('period', 'Período não especificado'),
            "metrics": {
                "ctr": round(self.metrics.get('ctr', 0), 2),
                "cpc": round(self.metrics.get('cpc', 0), 2),
                "conversion_rate": round(self.metrics.get('conversion_rate', 0), 2),
                "roi": round(self.metrics.get('roi', 0), 2),
                "clicks": self.metrics.get('raw', {}).get('clicks', 0),
                "impressions": self.metrics.get('raw', {}).get('impressions', 0),
                "cost": round(self.metrics.get('raw', {}).get('cost', 0), 2),
                "conversions": self.metrics.get('raw', {}).get('conversions', 0),
                "revenue": round(self.metrics.get('raw', {}).get('revenue', 0), 2)
            },
            "insights": insights,
            "performance_rating": performance_rating
        }
        
        return summary
    
    def _calculate_performance_rating(self):
        """
        Calcula uma classificação geral de desempenho da campanha
        
        Returns:
            Dict: Classificação de desempenho
        """
        # Definir pesos para as métricas
        weights = {
            'roi': 0.4,
            'ctr': 0.2,
            'conversion_rate': 0.3,
            'cpc': 0.1
        }
        
        # Definir valores de referência (benchmarks)
        benchmarks = {
            'roi': 200.0,  # ROI médio de 200%
            'ctr': 1.0,    # CTR médio de 1%
            'conversion_rate': 2.0,  # Taxa de conversão média de 2%
            'cpc': 0.5     # CPC médio de R$0,50 (medir inversamente)
        }
        
        # Inicializar pontuação
        score = 0.0
        
        # Calcular pontuação para ROI
        roi = self.metrics.get('roi', 0)
        roi_score = min(roi / benchmarks['roi'], 2.0) * weights['roi']
        
        # Calcular pontuação para CTR
        ctr = self.metrics.get('ctr', 0)
        ctr_score = min(ctr / benchmarks['ctr'], 2.0) * weights['ctr']
        
        # Calcular pontuação para taxa de conversão
        conv_rate = self.metrics.get('conversion_rate', 0)
        conv_score = min(conv_rate / benchmarks['conversion_rate'], 2.0) * weights['conversion_rate']
        
        # Calcular pontuação para CPC (inversamente proporcional)
        cpc = self.metrics.get('cpc', 0)
        if cpc > 0:
            cpc_ratio = benchmarks['cpc'] / cpc
            cpc_score = min(cpc_ratio, 2.0) * weights['cpc']
        else:
            cpc_score = 0
        
        # Somar pontuações
        score = roi_score + ctr_score + conv_score + cpc_score
        
        # Normalizar para escala 0-100
        normalized_score = min(score * 50, 100)
        
        # Determinar classificação
        if normalized_score >= 90:
            rating = "Excelente"
            color = "#28a745"  # Verde
        elif normalized_score >= 75:
            rating = "Muito Bom"
            color = "#5cb85c"  # Verde claro
        elif normalized_score >= 60:
            rating = "Bom"
            color = "#4e9dd0"  # Azul
        elif normalized_score >= 40:
            rating = "Regular"
            color = "#f0ad4e"  # Amarelo
        elif normalized_score >= 20:
            rating = "Baixo"
            color = "#d9534f"  # Vermelho
        else:
            rating = "Crítico"
            color = "#dc3545"  # Vermelho escuro
        
        return {
            "score": round(normalized_score, 1),
            "rating": rating,
            "color": color
        }
    
    def export_report(self, format="json"):
        """
        Exporta relatório de análise no formato desejado
        
        Args:
            format (str): Formato de exportação ("json" ou "text")
            
        Returns:
            str: Relatório no formato especificado
        """
        # Obter resumo de desempenho
        summary = self.get_performance_summary()
        
        if format.lower() == "json":
            import json
            return json.dumps(summary, indent=4)
        
        elif format.lower() == "text":
            # Formatar relatório em texto
            report = []
            
            report.append("=" * 60)
            report.append(f"RELATÓRIO DE DESEMPENHO: {summary['campaign_name']}")
            report.append(f"Período: {summary['period']}")
            report.append("=" * 60)
            report.append("")
            
            # Métricas principais
            report.append("MÉTRICAS PRINCIPAIS:")
            report.append(f"CTR: {summary['metrics']['ctr']}%")
            report.append(f"CPC: R${summary['metrics']['cpc']}")
            report.append(f"Taxa de Conversão: {summary['metrics']['conversion_rate']}%")
            report.append(f"ROI: {summary['metrics']['roi']}%")
            report.append("")
            
            # Dados brutos
            report.append("DADOS DE DESEMPENHO:")
            report.append(f"Impressões: {summary['metrics']['impressions']}")
            report.append(f"Cliques: {summary['metrics']['clicks']}")
            report.append(f"Conversões: {summary['metrics']['conversions']}")
            report.append(f"Custo: R${summary['metrics']['cost']}")
            report.append(f"Receita: R${summary['metrics']['revenue']}")
            report.append("")
            
            # Avaliação de desempenho
            report.append("AVALIAÇÃO DE DESEMPENHO:")
            report.append(f"Pontuação: {summary['performance_rating']['score']}/100")
            report.append(f"Classificação: {summary['performance_rating']['rating']}")
            report.append("")
            
            # Insights
            report.append("INSIGHTS E RECOMENDAÇÕES:")
            for i, insight in enumerate(summary['insights'], 1):
                report.append(f"{i}. {insight}")
            
            return "\n".join(report)
        
        else:
            raise ValueError(f"Formato de exportação '{format}' não suportado. Use 'json' ou 'text'.")


def analyze_campaign_batch(campaigns_data):
    """
    Analisa um lote de campanhas e retorna resultados consolidados
    
    Args:
        campaigns_data (List[Dict]): Lista de dados de campanhas
        
    Returns:
        Dict: Resultados consolidados da análise
    """
    results = {
        "campaigns": [],
        "overall": {
            "total_cost": 0,
            "total_revenue": 0,
            "total_conversions": 0,
            "average_ctr": 0,
            "average_conversion_rate": 0,
            "roi": 0,
            "best_performing": None,
            "needs_attention": []
        }
    }
    
    if not campaigns_data:
        return results
    
    # Variáveis para consolidação
    total_clicks = 0
    total_impressions = 0
    best_score = -1
    worst_campaigns = []
    
    # Analisar cada campanha
    for campaign_data in campaigns_data:
        analyzer = CampaignAnalytics(campaign_data)
        analyzer.calculate_all_metrics()
        summary = analyzer.get_performance_summary()
        
        # Adicionar ao resultado de campanhas
        results["campaigns"].append(summary)
        
        # Atualizar métricas consolidadas
        metrics = summary["metrics"]
        results["overall"]["total_cost"] += metrics["cost"]
        results["overall"]["total_revenue"] += metrics["revenue"]
        results["overall"]["total_conversions"] += metrics["conversions"]
        
        total_clicks += metrics["clicks"]
        total_impressions += metrics["impressions"]
        
        # Identificar melhor campanha
        score = summary["performance_rating"]["score"]
        if score > best_score:
            best_score = score
            results["overall"]["best_performing"] = {
                "name": summary["campaign_name"],
                "score": score,
                "roi": metrics["roi"]
            }
        
        # Identificar campanhas com baixo desempenho
        if score < 40:
            worst_campaigns.append({
                "name": summary["campaign_name"],
                "score": score,
                "issue": "Baixo desempenho geral"
            })
        elif metrics["roi"] < 0:
            worst_campaigns.append({
                "name": summary["campaign_name"],
                "score": score,
                "issue": "ROI negativo"
            })
    
    # Calcular médias
    if total_impressions > 0:
        results["overall"]["average_ctr"] = (total_clicks / total_impressions) * 100
    
    if total_clicks > 0:
        results["overall"]["average_conversion_rate"] = (results["overall"]["total_conversions"] / total_clicks) * 100
    
    if results["overall"]["total_cost"] > 0:
        results["overall"]["roi"] = ((results["overall"]["total_revenue"] - results["overall"]["total_cost"]) / results["overall"]["total_cost"]) * 100
    
    # Ordenar campanhas com problemas por pontuação
    worst_campaigns.sort(key=lambda x: x["score"])
    results["overall"]["needs_attention"] = worst_campaigns[:3]  # Top 3 piores campanhas
    
    return results
