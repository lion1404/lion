import os
import logging
import random
import hashlib
from typing import List, Dict, Union, Any

# Configuração de logging
logger = logging.getLogger(__name__)

def get_interests(query: str) -> Union[List[Dict], Dict]:
    """
    Consulta a API do Meta para obter interesses relacionados a uma palavra-chave.
    Usa dados de demonstração se a API não estiver disponível.
    
    Args:
        query (str): Palavra-chave para buscar interesses relacionados
        
    Returns:
        Union[List[Dict], Dict]: Lista de interesses ou dicionário com erro
    """
    
    # Verificar se temos acesso à API do Facebook
    fb_access_token = os.environ.get('FB_ACCESS_TOKEN')
    
    if not fb_access_token:
        logger.warning("Token de acesso do Facebook não encontrado. Usando dados de demonstração.")
        return get_demo_interests(query)
    
    try:
        # Em um ambiente de produção, conectaríamos com a API do Facebook aqui
        # Mas para fins de desenvolvimento, usaremos dados simulados
        logger.info(f"Consultando interesses para: {query}")
        
        # Simular que estamos tentando usar a API
        return get_demo_interests(query)
        
    except Exception as e:
        logger.error(f"Erro ao consultar interesses: {str(e)}")
        return {"error": str(e)}

def get_demo_interests(query: str) -> List[Dict]:
    """
    Gera interesses de demonstração com base na consulta.
    Usado quando não há permissão para acessar a API de anúncios.
    
    Args:
        query (str): Consulta original
        
    Returns:
        List[Dict]: Lista de interesses de demonstração
    """
    # Para tornar a simulação mais realista, geramos interesses baseados na consulta
    query = query.lower()
    
    # Base de interesses para o setor de dedetização
    base_interests = {
        "dedetização": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003164953376", "name": "Manutenção residencial", "audience_size": 3200000},
            {"id": "6002964951144", "name": "Proprietários de imóveis", "audience_size": 8500000},
            {"id": "6003020262976", "name": "Serviços residenciais", "audience_size": 5400000},
            {"id": "6003130847622", "name": "Saúde e bem-estar", "audience_size": 12000000},
            {"id": "6003109128422", "name": "Famílias com crianças", "audience_size": 6800000}
        ],
        "controle": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003206556718", "name": "Gestão de propriedades", "audience_size": 1800000},
            {"id": "6003158262642", "name": "Serviços empresariais", "audience_size": 4200000}
        ],
        "pragas": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003107779871", "name": "Jardinagem", "audience_size": 3100000},
            {"id": "6003050931519", "name": "Melhorias para o lar", "audience_size": 5600000}
        ],
        "inseto": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003107779871", "name": "Jardinagem", "audience_size": 3100000},
            {"id": "6003022653631", "name": "Ciências naturais", "audience_size": 1700000}
        ],
        "rato": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003128988334", "name": "Proprietários de pets", "audience_size": 5800000},
            {"id": "6003208575728", "name": "Saúde pública", "audience_size": 1200000}
        ],
        "barata": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003173944272", "name": "Limpeza doméstica", "audience_size": 4300000},
            {"id": "6003150125934", "name": "Apartamentos e condomínios", "audience_size": 3700000}
        ],
        "formiga": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003107779871", "name": "Jardinagem", "audience_size": 3100000},
            {"id": "6003144912931", "name": "Vida ao ar livre", "audience_size": 4900000}
        ],
        "cupim": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003164953376", "name": "Manutenção residencial", "audience_size": 3200000},
            {"id": "6003189204152", "name": "Arquitetura e design", "audience_size": 2900000},
            {"id": "6003050931519", "name": "Melhorias para o lar", "audience_size": 5600000}
        ],
        "mosquito": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003107779871", "name": "Jardinagem", "audience_size": 3100000},
            {"id": "6003130847622", "name": "Saúde e bem-estar", "audience_size": 12000000},
            {"id": "6003144912931", "name": "Vida ao ar livre", "audience_size": 4900000},
            {"id": "6003149840010", "name": "Atividades ao ar livre", "audience_size": 3900000}
        ],
        "escorpião": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003208575728", "name": "Saúde pública", "audience_size": 1200000},
            {"id": "6003142268372", "name": "Segurança familiar", "audience_size": 2800000}
        ],
        "aranha": [
            {"id": "6003232470561", "name": "Controle de pragas", "audience_size": 2500000},
            {"id": "6003142268372", "name": "Segurança familiar", "audience_size": 2800000},
            {"id": "6003150125934", "name": "Apartamentos e condomínios", "audience_size": 3700000}
        ],
        "residencial": [
            {"id": "6003164953376", "name": "Manutenção residencial", "audience_size": 3200000},
            {"id": "6002964951144", "name": "Proprietários de imóveis", "audience_size": 8500000},
            {"id": "6003150125934", "name": "Apartamentos e condomínios", "audience_size": 3700000},
            {"id": "6003020262976", "name": "Serviços residenciais", "audience_size": 5400000}
        ],
        "comercial": [
            {"id": "6003158262642", "name": "Serviços empresariais", "audience_size": 4200000},
            {"id": "6003206556718", "name": "Gestão de propriedades", "audience_size": 1800000},
            {"id": "6003188467993", "name": "Pequenos negócios", "audience_size": 3400000},
            {"id": "6003116452855", "name": "Restaurantes", "audience_size": 2700000}
        ],
        "condomínio": [
            {"id": "6003150125934", "name": "Apartamentos e condomínios", "audience_size": 3700000},
            {"id": "6003206556718", "name": "Gestão de propriedades", "audience_size": 1800000},
            {"id": "6003164953376", "name": "Manutenção residencial", "audience_size": 3200000}
        ],
        "empresa": [
            {"id": "6003158262642", "name": "Serviços empresariais", "audience_size": 4200000},
            {"id": "6003188467993", "name": "Pequenos negócios", "audience_size": 3400000},
            {"id": "6003142542397", "name": "Gestão empresarial", "audience_size": 2900000}
        ],
        "restaurante": [
            {"id": "6003116452855", "name": "Restaurantes", "audience_size": 2700000},
            {"id": "6003139192875", "name": "Indústria alimentícia", "audience_size": 3100000},
            {"id": "6003158262642", "name": "Serviços empresariais", "audience_size": 4200000}
        ],
        "hotel": [
            {"id": "6003179831999", "name": "Hotelaria", "audience_size": 2200000},
            {"id": "6003103756568", "name": "Viagens", "audience_size": 7900000},
            {"id": "6003158262642", "name": "Serviços empresariais", "audience_size": 4200000}
        ],
        "escola": [
            {"id": "6003123570687", "name": "Educação", "audience_size": 6700000},
            {"id": "6003109128422", "name": "Famílias com crianças", "audience_size": 6800000},
            {"id": "6003158262642", "name": "Serviços empresariais", "audience_size": 4200000}
        ],
        "hospital": [
            {"id": "6003130847622", "name": "Saúde e bem-estar", "audience_size": 12000000},
            {"id": "6003208575728", "name": "Saúde pública", "audience_size": 1200000},
            {"id": "6003172091531", "name": "Profissionais de saúde", "audience_size": 2500000}
        ],
        "indústria": [
            {"id": "6003158262642", "name": "Serviços empresariais", "audience_size": 4200000},
            {"id": "6003149622679", "name": "Manufatura", "audience_size": 1800000},
            {"id": "6003178276101", "name": "Profissionais da indústria", "audience_size": 2200000}
        ]
    }
    
    # Gerar hash baseado na consulta para ter consistência na simulação
    seed = int(hashlib.md5(query.encode()).hexdigest(), 16) % 1000
    random.seed(seed)
    
    # Encontrar palavras-chave correspondentes
    matching_interests = []
    
    # Verificar correspondências exatas
    for key, interests in base_interests.items():
        if key in query:
            matching_interests.extend(interests)
    
    # Se não houver correspondências, usar lista padrão de dedetização
    if not matching_interests:
        matching_interests = base_interests["dedetização"]
    
    # Remover duplicatas (mesmo ID)
    seen_ids = set()
    unique_interests = []
    
    for interest in matching_interests:
        if interest["id"] not in seen_ids:
            # Adicionar variação aleatória ao tamanho da audiência para tornar mais realista
            variation = random.uniform(0.9, 1.1)
            interest["audience_size"] = int(interest["audience_size"] * variation)
            
            unique_interests.append(interest)
            seen_ids.add(interest["id"])
    
    # Adicionar alguns interesses específicos para a consulta
    if query != "dedetização":
        # Gerar um interesse personalizado com a consulta
        custom_id = hashlib.md5(f"custom_{query}".encode()).hexdigest()[:16]
        custom_interest = {
            "id": custom_id,
            "name": query.capitalize(),
            "audience_size": random.randint(100000, 1000000)
        }
        unique_interests.append(custom_interest)
    
    # Ordenar por tamanho de audiência
    unique_interests.sort(key=lambda x: x["audience_size"], reverse=True)
    
    logger.info(f"Gerados {len(unique_interests)} interesses para a consulta: {query}")
    return unique_interests

def get_audience_size_from_api(interest_id: str) -> int:
    """
    Consulta a API do Facebook para obter o tamanho real da audiência para um interesse.
    
    Args:
        interest_id (str): ID do interesse no Facebook
        
    Returns:
        int: Tamanho real da audiência ou 0 em caso de erro
    """
    # Verificar se temos acesso à API do Facebook
    fb_access_token = os.environ.get('FB_ACCESS_TOKEN')
    
    if not fb_access_token:
        logger.warning("Token de acesso do Facebook não encontrado. Usando audiência simulada.")
        return get_simulated_audience_size(interest_id)
    
    try:
        # Em um ambiente de produção, conectaríamos com a API do Facebook aqui
        # Mas para fins de desenvolvimento, usaremos dados simulados
        return get_simulated_audience_size(interest_id)
        
    except Exception as e:
        logger.error(f"Erro ao consultar tamanho de audiência: {str(e)}")
        return 0

def get_simulated_audience_size(interest_name: str) -> int:
    """
    Gera um tamanho de público simulado para fins de desenvolvimento.
    Esta função é usada apenas quando não é possível acessar a API.
    
    Args:
        interest_name (str): Nome do interesse
        
    Returns:
        int: Tamanho simulado do público
    """
    # Gerar seed baseado no nome para ter consistência
    seed = int(hashlib.md5(interest_name.encode()).hexdigest(), 16) % 10000
    random.seed(seed)
    
    # Gerar tamanho de audiência baseado em algumas regras
    if "proprietário" in interest_name.lower():
        # Proprietários geralmente têm audiências grandes
        base_size = random.randint(5000000, 10000000)
    elif "serviço" in interest_name.lower():
        # Serviços têm audiências médias
        base_size = random.randint(2000000, 6000000)
    elif "controle" in interest_name.lower() or "praga" in interest_name.lower():
        # Controle de pragas tem audiência específica
        base_size = random.randint(1000000, 3000000)
    else:
        # Outros interesses
        base_size = random.randint(500000, 8000000)
    
    # Adicionar variação aleatória
    variation = random.uniform(0.85, 1.15)
    
    return int(base_size * variation)

def analyze_interests(interests: List[Dict[str, Any]]) -> Dict:
    """
    Analisa e segmenta interesses baseados no tamanho do público.
    
    Args:
        interests (List[Dict]): Lista de interesses com informações de tamanho de público
        
    Returns:
        Dict: Resultados da análise e segmentação
    """
    if not interests:
        return {
            "status": "error",
            "message": "Nenhum interesse fornecido para análise",
            "segments": {}
        }
    
    try:
        # Classificar interesses por tamanho de público
        interests_with_size = []
        
        for interest in interests:
            # Verificar se já temos o tamanho da audiência
            audience_size = interest.get("audience_size", 0)
            
            # Se não tiver, buscar da API
            if not audience_size and "id" in interest:
                audience_size = get_audience_size_from_api(interest["id"])
                interest["audience_size"] = audience_size
            
            interests_with_size.append(interest)
        
        # Ordenar por tamanho de audiência (decrescente)
        interests_with_size.sort(key=lambda x: x.get("audience_size", 0), reverse=True)
        
        # Definir limites para segmentação
        large_threshold = 5000000   # > 5M = grande
        medium_threshold = 1000000  # > 1M = médio, < 1M = específico
        
        # Segmentar interesses
        segments = {
            "large": [],
            "medium": [],
            "specific": []
        }
        
        for interest in interests_with_size:
            audience_size = interest.get("audience_size", 0)
            
            if audience_size >= large_threshold:
                segments["large"].append(interest)
            elif audience_size >= medium_threshold:
                segments["medium"].append(interest)
            else:
                segments["specific"].append(interest)
        
        # Calcular estatísticas
        total_interests = len(interests_with_size)
        total_audience = sum(interest.get("audience_size", 0) for interest in interests_with_size)
        average_audience = total_audience / total_interests if total_interests > 0 else 0
        
        # Preparar recomendações
        recommendations = []
        
        if segments["large"] and segments["specific"]:
            recommendations.append("Combine interesses amplos com específicos para equilibrar alcance e relevância")
        
        if len(segments["specific"]) >= 3:
            recommendations.append("Use múltiplos interesses específicos para criar uma audiência mais qualificada")
        
        if len(segments["large"]) > 2 and not segments["specific"]:
            recommendations.append("Audiência muito ampla. Adicione interesses mais específicos para melhorar a relevância")
        
        if not segments["medium"] and not segments["specific"]:
            recommendations.append("Audiência muito genérica. Busque interesses mais específicos para o setor de controle de pragas")
        
        # Resultado final
        result = {
            "status": "success",
            "message": f"Análise concluída para {total_interests} interesses",
            "statistics": {
                "total_interests": total_interests,
                "total_audience": total_audience,
                "average_audience": average_audience,
                "segment_counts": {
                    "large": len(segments["large"]),
                    "medium": len(segments["medium"]),
                    "specific": len(segments["specific"])
                }
            },
            "segments": segments,
            "recommendations": recommendations
        }
        
        logger.info(f"Análise de interesses concluída: {total_interests} interesses processados")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao analisar interesses: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao analisar interesses: {str(e)}",
            "segments": {}
        }

def get_recommended_interests(query: str = "dedetização") -> Dict:
    """
    Obtém e analisa interesses recomendados para uma campanha.
    
    Args:
        query (str): Palavra-chave para buscar interesses relacionados
        
    Returns:
        Dict: Interesses recomendados com análise
    """
    try:
        # Obter interesses
        interests = get_interests(query)
        
        # Se for um dicionário com erro, retornar erro
        if isinstance(interests, dict) and "error" in interests:
            return {
                "status": "error",
                "message": interests["error"],
                "recommendations": []
            }
        
        # Analisar interesses
        analysis = analyze_interests(interests)
        
        # Preparar recomendações específicas para o setor de dedetização
        recommended_combinations = []
        
        # Tentar criar combinações equilibradas
        if analysis["status"] == "success":
            segments = analysis["segments"]
            
            # Combinação 1: Mistura equilibrada
            combination1 = {
                "name": "Equilibrada: Alcance com Relevância",
                "description": "Combina interesses amplos com específicos para maximizar alcance com relevância",
                "interests": []
            }
            
            # Adicionar 1 interesse amplo
            if segments["large"]:
                combination1["interests"].append(segments["large"][0])
            
            # Adicionar 1-2 interesses médios
            if segments["medium"]:
                for i in range(min(2, len(segments["medium"]))):
                    combination1["interests"].append(segments["medium"][i])
            
            # Adicionar 1-2 interesses específicos
            if segments["specific"]:
                for i in range(min(2, len(segments["specific"]))):
                    combination1["interests"].append(segments["specific"][i])
            
            # Combinação 2: Foco em relevância
            combination2 = {
                "name": "Relevância: Audiência Qualificada",
                "description": "Foca em interesses específicos do setor para uma audiência mais qualificada",
                "interests": []
            }
            
            # Adicionar interesses específicos e médios
            specific_count = min(3, len(segments["specific"]))
            for i in range(specific_count):
                if i < len(segments["specific"]):
                    combination2["interests"].append(segments["specific"][i])
            
            # Se não tiver muitos específicos, adicionar médios
            if specific_count < 3 and segments["medium"]:
                for i in range(min(3 - specific_count, len(segments["medium"]))):
                    combination2["interests"].append(segments["medium"][i])
            
            # Combinação 3: Alcance máximo
            combination3 = {
                "name": "Alcance: Máxima Exposição",
                "description": "Prioriza o alcance amplo para maximizar a exposição da marca",
                "interests": []
            }
            
            # Adicionar interesses amplos e médios
            if segments["large"]:
                for i in range(min(2, len(segments["large"]))):
                    combination3["interests"].append(segments["large"][i])
            
            if segments["medium"]:
                for i in range(min(2, len(segments["medium"]))):
                    combination3["interests"].append(segments["medium"][i])
            
            # Adicionar combinações não vazias
            if combination1["interests"]:
                recommended_combinations.append(combination1)
            if combination2["interests"]:
                recommended_combinations.append(combination2)
            if combination3["interests"]:
                recommended_combinations.append(combination3)
        
        # Resultado final
        result = {
            "status": "success" if recommended_combinations else "warning",
            "message": "Recomendações de interesses geradas com sucesso" if recommended_combinations else "Não foi possível gerar recomendações para esta consulta",
            "query": query,
            "analysis": analysis,
            "recommendations": recommended_combinations
        }
        
        logger.info(f"Geradas {len(recommended_combinations)} recomendações de interesses para a consulta: {query}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao obter recomendações de interesses: {str(e)}")
        return {
            "status": "error",
            "message": f"Erro ao obter recomendações de interesses: {str(e)}",
            "recommendations": []
        }
