import os
import logging
import json
import datetime
import numpy as np
from typing import Dict, List, Union, Optional

# Configurar logging
logger = logging.getLogger(__name__)

class CampaignOptimizer:
    def __init__(self):
        # Criar diretório para recomendações se não existir
        if not os.path.exists('recommendations'):
            os.makedirs('recommendations')
    
    def adjust_budget(self, roi, ctr, budget, campaign_id=None):
        """
        Ajusta o orçamento da campanha baseado no ROI e CTR
        
        Args:
            roi (float): Retorno sobre Investimento (ROI) em percentual
            ctr (float): Taxa de Cliques (CTR) em percentual
            budget (float): Orçamento atual da campanha
            campaign_id (str): Identificador da campanha
            
        Returns:
            float: Novo orçamento recomendado
        """
        try:
            # Definir fatores de ajuste
            performance_factor = 1.0  # Fator base (sem alteração)
            
            # Ajustar com base no ROI
            if roi >= 500:
                # ROI excelente (> 500%)
                performance_factor *= 1.3  # Aumentar em 30%
                roi_message = "ROI excelente, aumentando orçamento em 30%"
            elif roi >= 300:
                # ROI muito bom (300-500%)
                performance_factor *= 1.2  # Aumentar em 20%
                roi_message = "ROI muito bom, aumentando orçamento em 20%"
            elif roi >= 200:
                # ROI bom (200-300%)
                performance_factor *= 1.1  # Aumentar em 10%
                roi_message = "ROI bom, aumentando orçamento em 10%"
            elif roi <= 50:
                # ROI muito baixo (< 50%)
                performance_factor *= 0.7  # Reduzir em 30%
                roi_message = "ROI muito baixo, reduzindo orçamento em 30%"
            elif roi <= 100:
                # ROI baixo (50-100%)
                performance_factor *= 0.85  # Reduzir em 15%
                roi_message = "ROI baixo, reduzindo orçamento em 15%"
            else:
                # ROI médio (100-200%)
                roi_message = "ROI médio, mantendo orçamento base"
            
            # Ajustar com base no CTR
            if ctr >= 3.0:
                # CTR excelente (> 3%)
                performance_factor *= 1.1  # Aumentar em mais 10%
                ctr_message = "CTR excelente, aumentando orçamento em 10% adicional"
            elif ctr >= 2.0:
                # CTR muito bom (2-3%)
                performance_factor *= 1.05  # Aumentar em mais 5%
                ctr_message = "CTR muito bom, aumentando orçamento em 5% adicional"
            elif ctr <= 0.5:
                # CTR muito baixo (< 0.5%)
                performance_factor *= 0.9  # Reduzir em mais 10%
                ctr_message = "CTR muito baixo, reduzindo orçamento em 10% adicional"
            elif ctr <= 1.0:
                # CTR baixo (0.5-1%)
                performance_factor *= 0.95  # Reduzir em mais 5%
                ctr_message = "CTR baixo, reduzindo orçamento em 5% adicional"
            else:
                # CTR médio (1-2%)
                ctr_message = "CTR médio, sem ajuste adicional"
            
            # Calcular novo orçamento
            new_budget = budget * performance_factor
            
            # Garantir que o novo orçamento não seja muito baixo
            new_budget = max(new_budget, budget * 0.5)
            
            # Limitar aumento máximo para evitar gastos excessivos repentinos
            new_budget = min(new_budget, budget * 2.0)
            
            # Arredondar para 2 casas decimais
            new_budget = round(new_budget, 2)
            
            # Registrar a recomendação
            logger.info(f"Ajustando orçamento da campanha {campaign_id}:")
            logger.info(f"ROI: {roi:.2f}% - {roi_message}")
            logger.info(f"CTR: {ctr:.2f}% - {ctr_message}")
            logger.info(f"Orçamento anterior: R${budget:.2f}")
            logger.info(f"Novo orçamento recomendado: R${new_budget:.2f}")
            
            # Salvar recomendação
            recommendation = {
                "campaign_id": campaign_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "performance": {
                    "roi": roi,
                    "ctr": ctr
                },
                "budget": {
                    "previous": budget,
                    "recommended": new_budget,
                    "change_percent": ((new_budget / budget) - 1) * 100
                },
                "messages": {
                    "roi_assessment": roi_message,
                    "ctr_assessment": ctr_message
                }
            }
            
            self.save_recommendations(recommendation, campaign_id)
            
            return new_budget
            
        except Exception as e:
            logger.error(f"Erro ao ajustar orçamento: {str(e)}")
            return budget
    
    def reallocate_budget(self, ads_performance):
        """
        Realoca orçamento entre anúncios baseado em desempenho
        
        Args:
            ads_performance (list): Lista de dicionários com dados de desempenho de anúncios
            
        Returns:
            list: Lista atualizada com orçamentos ajustados
        """
        try:
            if not ads_performance or len(ads_performance) < 2:
                logger.warning("Não há anúncios suficientes para realocação de orçamento")
                return ads_performance
            
            # Calcular pontuação de desempenho para cada anúncio
            for ad in ads_performance:
                # Garantir que os dados necessários existem
                roi = ad.get('roi', 0)
                ctr = ad.get('ctr', 0)
                conversion_rate = ad.get('conversion_rate', 0)
                
                # Calcular pontuação ponderada (ROI tem maior peso)
                performance_score = (roi * 0.5) + (ctr * 0.3) + (conversion_rate * 0.2)
                ad['performance_score'] = performance_score
            
            # Calcular pontuação total e média
            total_score = sum(ad['performance_score'] for ad in ads_performance)
            average_score = total_score / len(ads_performance)
            
            # Calcular orçamento total atual
            total_budget = sum(ad.get('budget', 0) for ad in ads_performance)
            
            # Se não houver orçamento total, não há o que realocar
            if total_budget <= 0:
                logger.warning("Orçamento total zero, não é possível realocar")
                return ads_performance
            
            # Calcular novos orçamentos baseados em desempenho
            for ad in ads_performance:
                # Calcular fator de ajuste relativo à média
                relative_performance = ad['performance_score'] / average_score
                
                # Definir limites para evitar mudanças extremas
                adjustment_factor = min(max(relative_performance, 0.7), 1.5)
                
                # Calcular novo orçamento ideal
                ideal_budget = (ad['performance_score'] / total_score) * total_budget
                
                # Ajustar gradualmente para evitar mudanças bruscas (mescla 70/30)
                current_budget = ad.get('budget', 0)
                new_budget = (current_budget * 0.7) + (ideal_budget * 0.3)
                
                # Arredondar para 2 casas decimais
                new_budget = round(new_budget, 2)
                
                # Registrar mudança
                logger.info(f"Anúncio {ad.get('id', 'desconhecido')}: " +
                           f"Orçamento {current_budget:.2f} -> {new_budget:.2f} " +
                           f"(Ajuste: {((new_budget/current_budget) - 1) * 100:.1f}%)")
                
                # Atualizar orçamento no objeto
                ad['previous_budget'] = current_budget
                ad['budget'] = new_budget
                ad['budget_change_percent'] = ((new_budget/current_budget) - 1) * 100
            
            return ads_performance
            
        except Exception as e:
            logger.error(f"Erro ao realocar orçamento: {str(e)}")
            return ads_performance
    
    def optimize_bids(self, campaign_data, target_cpa=None):
        """
        Otimiza os lances (bids) da campanha para atingir o CPA alvo
        
        Args:
            campaign_data (dict): Dados da campanha
            target_cpa (float): CPA alvo, se None usa o CPA atual + 10%
            
        Returns:
            dict: Recomendações de novos lances
        """
        try:
            # Extrair dados da campanha
            cpa = campaign_data.get('cpa', 0)
            cpc = campaign_data.get('cpc', 0)
            conversion_rate = campaign_data.get('conversion_rate', 0) / 100  # Converter para decimal
            
            # Se não há dados suficientes, não podemos otimizar
            if cpc <= 0 or conversion_rate <= 0:
                return {
                    "status": "insufficient_data",
                    "message": "Dados insuficientes para otimização de lances",
                    "recommendations": None
                }
            
            # Definir CPA alvo
            if target_cpa is None:
                if cpa > 0:
                    # Se já temos um CPA, usamos ele como referência
                    target_cpa = cpa * 0.9  # Tentar reduzir o CPA em 10%
                else:
                    # Se não temos CPA, calculamos a partir do CPC e taxa de conversão
                    calculated_cpa = cpc / conversion_rate
                    target_cpa = calculated_cpa * 0.9  # Tentar reduzir o CPA calculado em 10%
            
            # Calcular lance ideal baseado no CPA alvo e taxa de conversão
            ideal_bid = target_cpa * conversion_rate
            
            # Ajustar gradualmente para evitar mudanças bruscas
            bid_adjustment = (ideal_bid / cpc) if cpc > 0 else 1.0
            
            # Limitar ajustes para evitar mudanças extremas
            bid_adjustment = min(max(bid_adjustment, 0.7), 1.3)
            
            # Calcular novo lance
            new_bid = cpc * bid_adjustment
            
            # Arredondar para 2 casas decimais
            new_bid = round(new_bid, 2)
            
            # Registrar recomendação
            logger.info(f"Otimização de lances para campanha {campaign_data.get('id', 'desconhecida')}:")
            logger.info(f"CPA atual/alvo: R${cpa:.2f} -> R${target_cpa:.2f}")
            logger.info(f"Lance atual: R${cpc:.2f}")
            logger.info(f"Lance recomendado: R${new_bid:.2f} (Ajuste: {(bid_adjustment-1)*100:.1f}%)")
            
            # Resultados detalhados
            recommendations = {
                "status": "success",
                "message": f"Lance otimizado para atingir CPA alvo de R${target_cpa:.2f}",
                "current_metrics": {
                    "cpc": cpc,
                    "cpa": cpa,
                    "conversion_rate": conversion_rate * 100  # Converter para percentual
                },
                "recommendations": {
                    "new_bid": new_bid,
                    "bid_adjustment": (bid_adjustment - 1) * 100,  # Percentual de ajuste
                    "target_cpa": target_cpa
                }
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao otimizar lances: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao otimizar lances: {str(e)}",
                "recommendations": None
            }
    
    def save_recommendations(self, recommendations, campaign_id=None):
        """
        Salva as recomendações de otimização em um arquivo
        
        Args:
            recommendations (dict): Recomendações geradas
            campaign_id (str): Identificador da campanha
            
        Returns:
            str: Caminho do arquivo salvo
        """
        try:
            # Gerar nome de arquivo baseado na data atual
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"budget_recommendations_{timestamp}.txt"
            
            if campaign_id:
                # Se tiver ID da campanha, incluir no nome
                filename = f"budget_recommendations_{campaign_id}_{timestamp}.txt"
            
            # Caminho completo
            file_path = os.path.join(os.getcwd(), filename)
            
            # Salvar recomendações
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"=== RECOMENDAÇÕES DE OTIMIZAÇÃO ===\n")
                f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Campanha: {campaign_id or 'Não especificada'}\n\n")
                
                # Converter recomendações para formato texto
                if isinstance(recommendations, dict):
                    # Se for um dicionário, formatar detalhadamente
                    for key, value in recommendations.items():
                        if isinstance(value, dict):
                            f.write(f"=== {key.upper()} ===\n")
                            for sub_key, sub_value in value.items():
                                f.write(f"{sub_key}: {sub_value}\n")
                            f.write("\n")
                        else:
                            f.write(f"{key}: {value}\n")
                else:
                    # Caso contrário, converter para string
                    f.write(str(recommendations))
            
            logger.info(f"Recomendações salvas em: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Erro ao salvar recomendações: {str(e)}")
            error_path = os.path.join(os.getcwd(), "error_log.txt")
            with open(error_path, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.datetime.now()}: Erro ao salvar recomendações: {str(e)}\n")
            return None
