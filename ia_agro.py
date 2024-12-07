import requests
import datetime
import pytz
from flask import Flask, render_template_string

app = Flask(__name__)

# Sua chave da API do OpenWeather
API_KEY = 'e8c29d83306d3ec8eb601348ca9ffe36'

# Dados de plantio com mais opções de cultivo
plantios = [
    {
        "nome": "Mandioca",
        "descricao": "Tolerante à seca",
        "ciclo": "8-18 meses",
        "tipo_solo": "Argiloso ou arenoso",
        "necessidade_irrigacao": "Baixa",
        "clima_ideal": "Quente e seco - 30.0°C",
        "frequencia_adubacao": "Anual",
        "pragas_comuns": "Broca-da-mandioca",
        "producao_estimada": 20000,  # em kg/ha
        "mercado_local": "Farinha e consumo local",
        "epoca_ano": "Verão"
    },
    {
        "nome": "Milho",
        "descricao": "Resistente a solos ácidos",
        "ciclo": "3-4 meses",
        "tipo_solo": "Fértil, bem drenado",
        "necessidade_irrigacao": "Alta",
        "clima_ideal": "Quente e úmido - 25.0°C",
        "frequencia_adubacao": "A cada 30 dias",
        "pragas_comuns": "Lagarta-do-cartucho",
        "producao_estimada": 12000,  # em kg/ha
        "mercado_local": "Milho verde, ração animal",
        "epoca_ano": "Primavera"
    },
    # Adicione outros dados de plantio conforme necessário
]

# Função para determinar a estação do ano
def determinar_estacao(mes):
    if mes in [12, 1, 2]:
        return "Verão"
    elif mes in [3, 4, 5]:
        return "Outono"
    elif mes in [6, 7, 8]:
        return "Inverno"
    elif mes in [9, 10, 11]:
        return "Primavera"

# Função para calcular a acurácia da recomendação
def calcular_acuracia(clima_ideal, temperatura_atual, umidade_atual):
    temperatura_ideal = float(clima_ideal.split(' - ')[1].replace('°C', ''))
    erro_temperatura = abs(temperatura_atual - temperatura_ideal)
    acuracia_temperatura = max(0, 100 - erro_temperatura)
    
    umidade_ideal = 50  # Valor fixo para exemplo
    erro_umidade = abs(umidade_atual - umidade_ideal)
    acuracia_umidade = max(0, 100 - erro_umidade)
    
    acuracia_final = (acuracia_temperatura + acuracia_umidade) / 2
    return acuracia_final

# Função para determinar a melhor recomendação de plantio com base nas condições locais
def recomendar_plantio(temperatura_atual, umidade_atual):
    melhor_recomendacao = None
    maior_acuracia = 0
    
    for plantio in plantios:
        acuracia = calcular_acuracia(plantio['clima_ideal'], temperatura_atual, umidade_atual)
        
        if acuracia > maior_acuracia:
            maior_acuracia = acuracia
            melhor_recomendacao = plantio
    
    return melhor_recomendacao, maior_acuracia

# Função para obter a localização de Jequié, Bahia, Brasil
def obter_localizacao():
    # Definindo a cidade de Jequié diretamente
    cidade = "Jequié"
    estado = "BA"
    pais = "BR"
    
    # Usando as coordenadas de Jequié, Bahia (aproximadamente)
    latitude = -13.291
    longitude = -40.070
    
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric'
    resposta = requests.get(url)
    dados = resposta.json()
    
    if dados and isinstance(dados, dict):
        temperatura = dados['main']['temp']
        umidade = dados['main']['humidity']
        descricao = dados['weather'][0]['description']
        descricao_traduzida = {
            'clear sky': 'Céu limpo',
            'few clouds': 'Poucas nuvens',
            'scattered clouds': 'Nuvens dispersas',
            'broken clouds': 'Nuvens quebradas',
            'shower rain': 'Chuva forte',
            'rain': 'Chuva',
            'thunderstorm': 'Tempestade',
            'snow': 'Neve',
            'mist': 'Névoa',
            'overcast clouds': 'Nuvens nubladas'
        }
        descricao = descricao_traduzida.get(descricao, descricao)
        
        chuva = dados.get('rain', {}).get('1h', 0)
        sol_unix = dados['sys']['sunrise']
        sol = datetime.datetime.fromtimestamp(sol_unix, pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')
        
        return {
            'cidade': cidade,
            'pais': pais,
            'temperatura': temperatura,
            'umidade': umidade,
            'descricao': descricao,
            'chuva': chuva,
            'sol': sol,
            'latitude': latitude,
            'longitude': longitude
        }
    else:
        return {'erro': 'Não foi possível obter dados meteorológicos'}

# Página inicial
@app.route('/')
def index():
    fuso_horario = pytz.timezone('America/Sao_Paulo')
    data_atual = datetime.datetime.now(fuso_horario).strftime("%d/%m/%Y %H:%M:%S")
    mes_atual = datetime.datetime.now(fuso_horario).month
    estacao_atual = determinar_estacao(mes_atual)

    dados_localizacao = obter_localizacao()

    if 'erro' in dados_localizacao:
        return render_template_string(f"<h1>{dados_localizacao['erro']}</h1>")
    
    melhor_plantio, acuracia = recomendar_plantio(dados_localizacao['temperatura'], dados_localizacao['umidade'])
    
    recomendacoes_html = f"""
    <h2>Recomendação de Plantio</h2>
    <h3>Plantio Recomendado: {melhor_plantio['nome']}</h3>
    <p><strong>Descrição:</strong> {melhor_plantio['descricao']}</p>
    <p><strong>Ciclo de Cultivo:</strong> {melhor_plantio['ciclo']}</p>
    <p><strong>Tipo de Solo:</strong> {melhor_plantio['tipo_solo']}</p>
    <p><strong>Necessidade de Irrigação:</strong> {melhor_plantio['necessidade_irrigacao']}</p>
    <p><strong>Clima Ideal:</strong> {melhor_plantio['clima_ideal']}</p>
    <p><strong>Frequência de Adubação:</strong> {melhor_plantio['frequencia_adubacao']}</p>
    <p><strong>Pragas Comuns:</strong> {melhor_plantio['pragas_comuns']}</p>
    <p><strong>Produção Estimada:</strong> {melhor_plantio['producao_estimada']} kg/ha</p>
    <p><strong>Mercado Local:</strong> {melhor_plantio['mercado_local']}</p>
    <p><strong>Estação do Ano:</strong> {estacao_atual}</p>
    <p><strong>Acurácia da Recomendação:</strong> {acuracia:.2f}%</p>
    <h4>Dados Locais</h4>
    <p><strong>Cidade:</strong> {dados_localizacao['cidade']}, {dados_localizacao['pais']}</p>
    <p><strong>Temperatura:</strong> {dados_localizacao['temperatura']}°C</p>
    <p><strong>Umidade:</strong> {dados_localizacao['umidade']}%</p>
    <p><strong>Descrição do Clima:</strong> {dados_localizacao['descricao']}</p>
    <p><strong>Chuva:</strong> {dados_localizacao['chuva']} mm/hora</p>
    <p><strong>Sol:</strong> {dados_localizacao['sol']}</p>
    <p><strong>Data e Hora:</strong> {data_atual}</p>
    """
    return render_template_string(recomendacoes_html)

if __name__ == '__main__':
    app.run(debug=True)
