import os
import logging
import json
import random
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

def check_api_key():
    """
    Verifica se a chave de API da OpenAI está disponível.
    
    Returns:
        tuple: (bool, chave_api) - Status da disponibilidade da chave e a chave se disponível
    """
    api_key = os.environ.get('OPENAI_API_KEY', '')
    
    if not api_key:
        logger.warning("Chave de API da OpenAI não encontrada no ambiente")
        return False, None
    
    return True, api_key

def get_ai_suggestions(analysis_data):
    """
    Obtém sugestões da OpenAI com base nos dados de desempenho.
    
    Args:
        analysis_data (dict): Dados de análise de desempenho
        
    Returns:
        str: Sugestões de otimização da IA
    """
    # Verificar se temos a chave da API
    api_available, api_key = check_api_key()
    
    if not api_available:
        logger.warning("Chave de API da OpenAI não disponível. Usando sugestões padrão.")
        return get_default_suggestions(analysis_data)
    
    try:
        # Tentar importar a biblioteca da OpenAI
        try:
            import openai
            openai.api_key = api_key
        except ImportError:
            logger.error("Biblioteca OpenAI não instalada")
            return get_default_suggestions(analysis_data)
        
        # Preparar os dados para o prompt
        metrics = analysis_data.get('metrics', {})
        
        ctr = metrics.get('ctr', 0)
        cpc = metrics.get('cpc', 0)
        conversion_rate = metrics.get('conversion_rate', 0)
        roi = metrics.get('roi', 0)
        clicks = metrics.get('clicks', 0)
        impressions = metrics.get('impressions', 0)
        conversions = metrics.get('conversions', 0)
        cost = metrics.get('cost', 0)
        
        # Criar prompt baseado nos dados
        prompt = f"""
        Você é um especialista em marketing digital para empresas de dedetização.
        
        Analise os seguintes dados de desempenho de uma campanha publicitária:
        
        - CTR (Taxa de Cliques): {ctr:.2f}%
        - CPC (Custo por Clique): R${cpc:.2f}
        - Taxa de Conversão: {conversion_rate:.2f}%
        - ROI: {roi:.2f}%
        - Cliques: {clicks}
        - Impressões: {impressions}
        - Conversões: {conversions}
        - Custo Total: R${cost:.2f}
        
        Forneça 3-5 recomendações específicas para melhorar o desempenho da campanha,
        considerando que se trata de uma empresa de dedetização (controle de pragas).
        
        Suas recomendações devem ser práticas, específicas e orientadas a resultados.
        Foque em ajustes de segmentação, texto do anúncio, orçamento e estratégia geral.
        """
        
        # Fazer chamada para a API da OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing digital para empresas de controle de pragas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Obter a resposta
        suggestions = response.choices[0].message.content.strip()
        
        logger.info("Sugestões geradas com sucesso usando a API da OpenAI")
        return suggestions
        
    except Exception as e:
        logger.error(f"Erro na API da OpenAI: {str(e)}")
        return get_default_suggestions(analysis_data)

def get_default_suggestions(analysis_data):
    """
    Gera sugestões padrão avançadas quando não é possível usar a API da OpenAI.
    
    Args:
        analysis_data (dict): Dados de análise de desempenho
        
    Returns:
        str: Sugestões padrão detalhadas
    """
    # Extrair métricas
    metrics = analysis_data.get('metrics', {})
    
    ctr = metrics.get('ctr', 0)
    cpc = metrics.get('cpc', 0)
    conversion_rate = metrics.get('conversion_rate', 0)
    roi = metrics.get('roi', 0)
    
    # Lista de sugestões base
    base_suggestions = [
        "Refine sua segmentação para focar em proprietários de imóveis em áreas residenciais com casas mais antigas, onde problemas de pragas são mais comuns.",
        "Adicione imagens antes/depois nos anúncios para demonstrar visualmente a eficácia do serviço de controle de pragas.",
        "Crie anúncios específicos para cada tipo de serviço (controle de baratas, ratos, cupins) em vez de anúncios genéricos.",
        "Implemente uma oferta de avaliação gratuita ou desconto no primeiro serviço para aumentar as conversões iniciais.",
        "Desenvolva conteúdo educativo sobre riscos de pragas para aumentar o engajamento e construir autoridade.",
        "Considere ajustar os horários de veiculação dos anúncios para períodos noturnos quando as pessoas estão mais propensas a notar pragas em casa.",
        "Inclua depoimentos de clientes satisfeitos para aumentar a credibilidade e a taxa de conversão.",
        "Destaque seus diferenciais como produtos seguros para pets e crianças para reduzir objeções comuns.",
        "Experimente landing pages específicas para cada tipo de praga para melhorar a relevância e as taxas de conversão.",
        "Utilize remarketing para alcançar pessoas que visitaram seu site mas não converteram."
    ]
    
    # Sugestões específicas com base nas métricas
    specific_suggestions = []
    
    # Sugestões baseadas no CTR
    if ctr < 1.0:
        specific_suggestions.append("Seu CTR está abaixo da média do setor. Revise os textos dos anúncios para torná-los mais envolventes e enfatize os principais problemas que os clientes enfrentam com pragas.")
    elif ctr > 2.5:
        specific_suggestions.append("Seu CTR está acima da média. Continue otimizando os títulos e descrições dos anúncios que estão performando melhor.")
    
    # Sugestões baseadas no CPC
    if cpc > 1.5:
        specific_suggestions.append("Seu CPC está elevado. Concentre-se em melhorar a relevância dos anúncios e considere palavras-chave de cauda longa mais específicas para reduzir a concorrência.")
    elif cpc < 0.5 and conversion_rate > 2.0:
        specific_suggestions.append("Seu CPC está excelente com boa taxa de conversão. Considere aumentar o orçamento para escalar os resultados positivos.")
    
    # Sugestões baseadas na taxa de conversão
    if conversion_rate < 2.0:
        specific_suggestions.append("Sua taxa de conversão pode ser melhorada. Simplifique o formulário de contato e destaque garantias de satisfação para reduzir a resistência dos clientes.")
    elif conversion_rate > 5.0:
        specific_suggestions.append("Sua taxa de conversão está excelente. Analise o que está funcionando bem em sua página de destino e aplique essas lições em outras campanhas.")
    
    # Sugestões baseadas no ROI
    if roi < 100:
        specific_suggestions.append("Seu ROI está abaixo do ideal. Avalie seu modelo de precificação e considere pacotes de serviço recorrente para aumentar o valor do cliente ao longo do tempo.")
    elif roi > 300:
        specific_suggestions.append("Seu ROI está excepcional. Continue monitorando as métricas de qualidade e considere expandir para áreas geográficas semelhantes.")
    
    # Selecionar sugestões para incluir
    selected_specific = specific_suggestions[:3]  # Até 3 sugestões específicas
    
    # Selecionar sugestões base aleatórias (excluindo as específicas)
    needed_base = 5 - len(selected_specific)
    random.shuffle(base_suggestions)
    selected_base = base_suggestions[:needed_base]
    
    # Combinar as sugestões
    all_suggestions = selected_specific + selected_base
    
    # Formatar o resultado
    result = "# Recomendações para Otimização da Campanha\n\n"
    
    for i, suggestion in enumerate(all_suggestions, 1):
        result += f"{i}. {suggestion}\n\n"
    
    # Adicionar conclusão
    result += "\n## Resumo da Análise\n\n"
    
    if roi > 200:
        result += "Sua campanha está apresentando um bom retorno sobre investimento. As recomendações acima ajudarão a otimizar ainda mais os resultados."
    elif roi > 100:
        result += "Sua campanha está apresentando um retorno positivo, mas há oportunidades significativas de otimização conforme as recomendações acima."
    else:
        result += "Sua campanha precisa de ajustes para melhorar o retorno sobre investimento. Implementar as recomendações acima deve produzir resultados positivos a curto e médio prazo."
    
    logger.info("Sugestões padrão geradas com sucesso")
    return result

def generate_ad_copy(target_audience, service_focus=None):
    """
    Gera texto para anúncios com base no público-alvo.
    
    Args:
        target_audience (str): Descrição do público-alvo
        service_focus (str, optional): Foco específico do serviço
        
    Returns:
        dict: Textos gerados para o anúncio (título, descrição, etc.)
    """
    # Verificar se temos a chave da API
    api_available, api_key = check_api_key()
    
    if not api_available:
        logger.warning("Chave de API da OpenAI não disponível. Usando textos padrão.")
        return get_default_ad_copy(target_audience, service_focus)
    
    try:
        # Tentar importar a biblioteca da OpenAI
        try:
            import openai
            openai.api_key = api_key
        except ImportError:
            logger.error("Biblioteca OpenAI não instalada")
            return get_default_ad_copy(target_audience, service_focus)
        
        # Determinar o foco do serviço se não for especificado
        if not service_focus:
            service_focus = "dedetização residencial"
        
        # Criar prompt baseado nos dados
        prompt = f"""
        Crie textos persuasivos para um anúncio de Facebook para uma empresa de dedetização chamada "Lion Dedetizadora".
        
        Público-alvo: {target_audience}
        Foco do serviço: {service_focus}
        
        O anúncio deve incluir:
        1. Título principal (máximo 40 caracteres)
        2. Título secundário (máximo 40 caracteres)
        3. Descrição (máximo 125 caracteres)
        4. Lista de 3 benefícios em formato de tópicos curtos
        5. Call to action final
        
        Os textos devem ser persuasivos, focados nos problemas que as pragas causam e na solução oferecida.
        Use linguagem emocional que ressoe com o público específico.
        Enfatize segurança, eficácia e profissionalismo.
        """
        
        # Fazer chamada para a API da OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um copywriter especialista em marketing digital para empresas de controle de pragas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Obter a resposta e processá-la
        raw_text = response.choices[0].message.content.strip()
        
        # Tentar extrair as diferentes partes do texto
        try:
            # Buscar padrões no texto para extrair cada componente
            lines = raw_text.split('\n')
            title_main = ""
            title_secondary = ""
            description = ""
            benefits = []
            cta = ""
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detectar seções
                if "título principal" in line.lower() or "1." in line and "título" in line.lower():
                    current_section = "title_main"
                    # Extrair texto após o marcador
                    if ":" in line:
                        title_main = line.split(":", 1)[1].strip().strip('"')
                    continue
                elif "título secundário" in line.lower() or "2." in line and "título" in line.lower():
                    current_section = "title_secondary"
                    if ":" in line:
                        title_secondary = line.split(":", 1)[1].strip().strip('"')
                    continue
                elif "descrição" in line.lower() or "3." in line and "descrição" in line.lower():
                    current_section = "description"
                    if ":" in line:
                        description = line.split(":", 1)[1].strip().strip('"')
                    continue
                elif "benefícios" in line.lower() or "4." in line and "benefícios" in line.lower():
                    current_section = "benefits"
                    continue
                elif "call to action" in line.lower() or "cta" in line.lower() or "5." in line and "call" in line.lower():
                    current_section = "cta"
                    if ":" in line:
                        cta = line.split(":", 1)[1].strip().strip('"')
                    continue
                
                # Processar linha com base na seção atual
                if current_section == "title_main" and not title_main:
                    title_main = line.strip('"- ')
                elif current_section == "title_secondary" and not title_secondary:
                    title_secondary = line.strip('"- ')
                elif current_section == "description" and not description:
                    description = line.strip('"- ')
                elif current_section == "benefits":
                    # Remover marcadores de lista e adicionar à lista de benefícios
                    benefit = line.lstrip('•-*#').strip()
                    if benefit and len(benefits) < 3:
                        benefits.append(benefit)
                elif current_section == "cta" and not cta:
                    cta = line.strip('"- ')
            
            # Se não conseguimos extrair adequadamente, vamos usar um método mais simples
            if not title_main or not description:
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if not title_main and i < 5:
                        title_main = line.strip('"- ')
                    elif not title_secondary and i < 8:
                        title_secondary = line.strip('"- ')
                    elif not description and i < 10:
                        description = line.strip('"- ')
                    elif len(benefits) < 3 and i < 15:
                        # Se a linha parece um benefício (curta e não é CTA)
                        if 10 < len(line) < 80 and not ("entre em contato" in line.lower() or "ligue" in line.lower()):
                            benefits.append(line.lstrip('•-*#').strip())
                    elif not cta and i > 10:
                        # Provavelmente o CTA é uma das últimas linhas
                        if "contato" in line.lower() or "ligue" in line.lower() or "agende" in line.lower():
                            cta = line.strip('"- ')
            
            # Garantir que temos todos os componentes necessários
            if not title_main:
                title_main = f"Elimine Pragas com a Lion Dedetizadora"
                
            if not title_secondary:
                title_secondary = f"Serviço Profissional de {service_focus.title()}"
                
            if not description:
                description = f"Solução definitiva contra pragas para {target_audience}. Atendimento rápido e eficiente!"
                
            if len(benefits) < 3:
                default_benefits = [
                    "Produtos seguros para crianças e pets",
                    "Técnicos certificados e experientes",
                    "Garantia de satisfação ou seu dinheiro de volta"
                ]
                benefits.extend(default_benefits[len(benefits):])
                
            if not cta:
                cta = "Agende uma vistoria gratuita hoje mesmo!"
            
            # Formatar o resultado
            result = {
                "title_main": title_main[:40],
                "title_secondary": title_secondary[:40],
                "description": description[:125],
                "benefits": [b[:60] for b in benefits[:3]],
                "cta": cta[:40],
                "source": "openai"
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta da OpenAI: {str(e)}")
            result = get_default_ad_copy(target_audience, service_focus)
            result["error"] = str(e)
            return result
        
        logger.info(f"Texto de anúncio gerado com sucesso para público: {target_audience}")
        return result
        
    except Exception as e:
        logger.error(f"Erro na API da OpenAI: {str(e)}")
        return get_default_ad_copy(target_audience, service_focus)

def get_default_ad_copy(target_audience, service_focus=None):
    """
    Gera textos avançados para anúncios quando não é possível usar a API da OpenAI.
    Oferece uma variedade maior de opções e mensagens persuasivas.
    
    Args:
        target_audience (str): Descrição do público-alvo
        service_focus (str, optional): Foco específico do serviço
        
    Returns:
        dict: Textos para o anúncio
    """
    # Determinar o foco do serviço se não for especificado
    if not service_focus:
        service_focus = "dedetização residencial"
    
    # Normalizar texto para minúsculas
    target_audience = target_audience.lower()
    service_focus = service_focus.lower()
    
    # Dicionário de templates por tipo de público
    audience_templates = {
        "proprietários de casas": {
            "titles_main": [
                "Proteja sua família de pragas indesejadas",
                "Casa livre de pragas com a Lion",
                "Adeus insetos! Sua casa merece o melhor",
                "Dedetização profissional para sua casa"
            ],
            "titles_secondary": [
                "Serviço profissional e garantido",
                "Produtos seguros para família e pets",
                "Atendimento rápido e eficiente",
                "Ambiente saudável para sua família"
            ],
            "descriptions": [
                "Elimine baratas, ratos e outras pragas com técnicos certificados. Atendimento em 24h e garantia de satisfação!",
                "Proteja seu lar contra pragas com produtos seguros para crianças e animais de estimação. Agende já!",
                "Serviço completo de dedetização com garantia. Sua casa livre de pragas durante todo o ano!"
            ],
            "benefits": [
                "Produtos seguros para crianças e pets",
                "Garantia de satisfação ou dinheiro de volta",
                "Técnicos certificados e experientes",
                "Sem cheiro forte após aplicação",
                "Solução duradoura, não apenas temporária",
                "Atendimento disponível aos finais de semana"
            ],
            "ctas": [
                "Agende uma vistoria gratuita hoje mesmo!",
                "Proteja sua família! Fale conosco agora",
                "Solicite um orçamento sem compromisso",
                "Livre-se das pragas! Clique e agende"
            ]
        },
        "condomínios": {
            "titles_main": [
                "Solução completa para condomínios",
                "Controle de pragas para áreas comuns",
                "Dedetização profissional em condomínios",
                "Livre seu condomínio de pragas"
            ],
            "titles_secondary": [
                "Atendimento especial para síndicos",
                "Segurança para todos os moradores",
                "Planos mensais com desconto",
                "Serviço discreto e eficiente"
            ],
            "descriptions": [
                "Soluções personalizadas para condomínios residenciais. Planos contínuos com condições especiais!",
                "Dedetização completa de áreas comuns e apartamentos. Elimine reclamações de moradores!",
                "Controle preventivo de pragas específico para condomínios. Orçamento sem compromisso!"
            ],
            "benefits": [
                "Planos especiais para áreas comuns",
                "Atendimento prioritário para emergências",
                "Relatórios técnicos para prestação de contas",
                "Produtos seguros para moradores e pets",
                "Equipe treinada para grandes estruturas",
                "Certificado de controle de pragas"
            ],
            "ctas": [
                "Solicite uma proposta para seu condomínio",
                "Fale com nossa equipe especializada",
                "Agende uma visita técnica gratuita",
                "Elimine pragas do seu condomínio agora"
            ]
        },
        "empresas": {
            "titles_main": [
                "Controle de pragas para empresas",
                "Proteja seu negócio contra infestações",
                "Soluções corporativas de dedetização",
                "Ambiente de trabalho livre de pragas"
            ],
            "titles_secondary": [
                "Conformidade com normas sanitárias",
                "Atendimento 24h para emergências",
                "Proteção contínua para seu negócio",
                "Discreto, rápido e eficiente"
            ],
            "descriptions": [
                "Controle integrado de pragas para empresas. Mantenha sua operação em conformidade com as normas sanitárias!",
                "Proteja funcionários e clientes. Serviço discreto e eficiente para não interromper sua operação!",
                "Planos corporativos de controle preventivo. Evite prejuízos e proteja a reputação do seu negócio!"
            ],
            "benefits": [
                "Certificado de controle de pragas",
                "Adequação às normas da vigilância sanitária",
                "Atendimento fora do horário comercial",
                "Controle de pragas específicas do seu setor",
                "Relatórios técnicos para auditorias",
                "Produtos com baixo odor para ambientes internos"
            ],
            "ctas": [
                "Solicite uma proposta comercial",
                "Agende uma visita técnica sem compromisso",
                "Entre em contato com nossa equipe B2B",
                "Proteja seu negócio! Fale conosco"
            ]
        },
        "restaurantes": {
            "titles_main": [
                "Controle de pragas para restaurantes",
                "Proteja seu estabelecimento e clientes",
                "Dedetização para área alimentícia",
                "Mantenha seu restaurante em conformidade"
            ],
            "titles_secondary": [
                "Conformidade com vigilância sanitária",
                "Produtos seguros para área alimentícia",
                "Serviço discreto e fora do horário",
                "Proteção contínua contra pragas"
            ],
            "descriptions": [
                "Soluções específicas para estabelecimentos alimentícios. Adequação às normas da vigilância sanitária!",
                "Controle preventivo de pragas urbanas. Evite autuações e proteja a reputação do seu restaurante!",
                "Serviço discreto realizado fora do horário de funcionamento. Sem riscos para seus clientes!"
            ],
            "benefits": [
                "Certificado para vigilância sanitária",
                "Produtos aprovados para área alimentícia",
                "Serviço realizado fora do horário comercial",
                "Controle específico de pragas de cozinha",
                "Planos preventivos mensais",
                "Auditoria prévia gratuita de pontos críticos"
            ],
            "ctas": [
                "Solicite uma visita técnica hoje mesmo",
                "Agende fora do horário de funcionamento",
                "Garanta a reputação do seu restaurante",
                "Adeque-se às normas sanitárias agora"
            ]
        }
    }
    
    # Escolher o template mais adequado ao público
    template = None
    
    for audience_key in audience_templates:
        if audience_key in target_audience:
            template = audience_templates[audience_key]
            break
    
    # Se não encontrou um template específico, usar o de proprietários de casas
    if not template:
        template = audience_templates["proprietários de casas"]
    
    # Adaptar ao foco do serviço
    service_terms = {
        "dedetização": ["dedetização", "controle de pragas", "elimine pragas"],
        "descupinização": ["descupinização", "elimine cupins", "proteção contra cupins"],
        "desratização": ["desratização", "controle de roedores", "elimine ratos"],
        "controle de baratas": ["controle de baratas", "elimine baratas", "proteção contra baratas"],
        "controle de escorpiões": ["controle de escorpiões", "proteção contra escorpiões", "elimine escorpiões"],
        "controle de formiga": ["controle de formigas", "elimine formigas", "proteção contra formigas"],
        "sanitização": ["sanitização", "desinfecção", "ambiente livre de vírus e bactérias"]
    }
    
    # Detectar termos do serviço
    service_term = "dedetização"  # padrão
    for key, terms in service_terms.items():
        if key in service_focus:
            service_term = random.choice(terms)
            break
    
    # Selecionar aleatoriamente textos de cada categoria
    title_main = random.choice(template["titles_main"])
    title_secondary = random.choice(template["titles_secondary"])
    description = random.choice(template["descriptions"])
    
    # Selecionar 3 benefícios aleatórios sem repetição
    random.shuffle(template["benefits"])
    benefits = template["benefits"][:3]
    
    cta = random.choice(template["ctas"])
    
    # Personalizar para o serviço específico, se necessário
    if service_term != "dedetização" and "dedetização" in title_main:
        title_main = title_main.replace("dedetização", service_term)
    
    # Formatar o resultado
    result = {
        "title_main": title_main[:40],
        "title_secondary": title_secondary[:40],
        "description": description[:125],
        "benefits": benefits,
        "cta": cta[:40],
        "source": "template"
    }
    
    logger.info(f"Texto de anúncio padrão gerado para público: {target_audience}")
    return result
