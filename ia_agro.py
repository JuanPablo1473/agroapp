import pandas as pd
from flask import Flask, render_template_string
from datetime import datetime
import nest_asyncio

# Resolve conflitos do loop do Jupyter
nest_asyncio.apply()

# Inicializando o Flask
app = Flask(__name__)

# Dados de exemplo para o plantio
dados_plantio = pd.DataFrame({
    'Tipo de Plantação': ['Mandioca', 'Milho', 'Feijão', 'Cacau', 'Abacaxi', 'Mamão', 'Coco', 'Umbu', 'Caju', 'Manga', 'Coentro', 'Alface', 'Cebola', 'Cana-de-açúcar'],
    'Ciclo de Cultivo': ['8-18 meses', '90 dias', '70-90 dias', '18-24 meses', '12-18 meses', '9-12 meses', '12-14 meses', '5-6 meses', '5-6 meses', '3-6 meses', '30-45 dias', '30-50 dias', '90-120 dias', '12-18 meses'],
    'Clima Ideal': ['Quente e seco', 'Quente com chuva', 'Quente com chuva', 'Quente e úmido', 'Quente e seco', 'Quente e úmido', 'Quente e úmido', 'Semiárido', 'Semiárido', 'Quente e seco', 'Quente com irrigação', 'Quente com irrigação', 'Quente com irrigação', 'Quente e úmido'],
    'Período de Plantio': ['Ano todo', 'Outubro a Dezembro', 'Março a Maio', 'Ano todo', 'Março a Julho', 'Ano todo', 'Ano todo', 'Janeiro a Abril', 'Janeiro a Abril', 'Janeiro a Abril', 'Ano todo', 'Ano todo', 'Ano todo', 'Março a Junho'],
    'Tipo de Solo': ['Argiloso ou arenoso', 'Argiloso', 'Arenoso', 'Argiloso e fértil', 'Arenoso e drenado', 'Bem drenado', 'Argiloso ou arenoso', 'Rochoso ou arenoso', 'Arenoso', 'Arenoso ou argiloso', 'Fértil', 'Fértil', 'Fértil', 'Argiloso'],
    'Necessidade de Irrigação': ['Baixa', 'Moderada', 'Moderada', 'Alta', 'Moderada', 'Alta', 'Alta', 'Baixa', 'Baixa', 'Baixa', 'Moderada', 'Moderada', 'Moderada', 'Alta'],
    'Frequência de Adubação': ['Anual', 'Mensal', 'Mensal', 'Anual', 'Mensal', 'Mensal', 'Anual', 'Mensal', 'Mensal', 'Mensal', 'Semanal', 'Semanal', 'Mensal', 'Anual'],
    'Pragas Comuns': ['Broca-da-mandioca', 'Lagarta-do-cartucho', 'Mosca-branca', 'Vassoura-de-bruxa', 'Ácaros', 'Pulgões', 'Brocas', 'Mosca-da-fruta', 'Mosca-da-fruta', 'Mosca-da-fruta', 'Pulgões', 'Lesmas', 'Tripes', 'Cigarrinha'],
    'Produção Estimada (kg/ha)': ['20.000', '2.500-6.000', '1.200-2.000', '1.500-2.500', '30.000-45.000', '40.000-50.000', '25.000-35.000', '1.000-2.000', '1.000-2.000', '10.000-20.000', '15.000-20.000', '10.000-15.000', '20.000-25.000', '50.000-60.000'],
    'Mercado Local/Venda': ['Farinha e consumo local', 'Feiras e ração animal', 'Feiras locais', 'Chocolate e cosméticos', 'Mercado nacional', 'Consumo e exportação', 'Mercado local', 'Polpa e consumo', 'Polpa e consumo', 'Consumo in natura', 'Feiras locais', 'Feiras locais', 'Feiras locais', 'Rapadura e caldo'],
    'Observações': ['Tolerante à seca', 'Prefere solo drenado', 'Boa para safras curtas', 'Requer sombra', 'Alta resistência climática', 'Necessita irrigação', 'Boa tolerância à salinidade', 'Produção sazonal', 'Produção sazonal', 'Muito cultivada na região', 'Fácil cultivo', 'Fácil cultivo', 'Requer solo bem preparado', 'Alta demanda de água'],
    'Acuracidade (%)': [95, 85, 80, 70, 90, 85, 80, 60, 60, 75, 85, 80, 70, 90]
})

# Função para determinar a temperatura ideal baseada no clima
def calcular_media_clima(clima):
    clima_para_temperatura = {
        'Quente e seco': '25C-35C',
        'Moderado': '15C-25C',
        'Frio': '5C-15C',
        'Tropical': '20C-30C',
        'Quente com chuva': '20C-30C',
        'Quente e úmido': '20C-30C'
    }

    if clima in clima_para_temperatura:
        temperatura = clima_para_temperatura[clima]
        temperaturas = temperatura.split('-')
        return (float(temperaturas[0].replace('C', '')) + float(temperaturas[1].replace('C', ''))) / 2
    return None

# Função para determinar a estação
def determinar_estacao(mes_atual):
    if mes_atual in [12, 1, 2]:
        return "Verão"
    elif mes_atual in [3, 4, 5]:
        return "Outono"
    elif mes_atual in [6, 7, 8]:
        return "Inverno"
    else:
        return "Primavera"

# Rota principal
@app.route("/")
def index():
    # Obter recomendação com base no tipo de plantação
    recomendado_plantio = dados_plantio[dados_plantio['Tipo de Plantação'] == "Mandioca"].iloc[0]
    
    # Determinar a estação atual
    mes_atual = datetime.now().month
    estacao_atual = determinar_estacao(mes_atual)
    
    # Data Atual
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Modelo de recomendação
    recomendacao_modelo = "Mandioca"
    
    # Gerar a recomendação do usuário
    recomendacao_usuario = f"""
    <h1>Recomendação de Plantio</h1>
    <p><b>Tipo:</b> {recomendacao_modelo}</p>
    <p><b>Descrição:</b> {recomendado_plantio['Observações']}</p>
    <p><b>Ciclo de Cultivo:</b> {recomendado_plantio['Ciclo de Cultivo']}</p>
    <p><b>Tipo de Solo:</b> {recomendado_plantio['Tipo de Solo']}</p>
    <p><b>Necessidade de Irrigação:</b> {recomendado_plantio['Necessidade de Irrigação']}</p>
    <p><b>Clima Ideal:</b> {recomendado_plantio['Clima Ideal']} - {calcular_media_clima(recomendado_plantio['Clima Ideal'])}°C</p>
    <p><b>Frequência de Adubação:</b> {recomendado_plantio['Frequência de Adubação']}</p>
    <p><b>Pragas Comuns:</b> {recomendado_plantio['Pragas Comuns']}</p>
    <p><b>Produção Estimada:</b> {recomendado_plantio['Produção Estimada (kg/ha)']}</p>
    <p><b>Mercado Local:</b> {recomendado_plantio['Mercado Local/Venda']}</p>
    <p><b>Época do Ano:</b> {estacao_atual}</p>
    <p><b>Data Atual:</b> {data_atual}</p>
    <p><b>Acuracidade da Recomendação:</b> {recomendado_plantio['Acuracidade (%)']}%</p>
    """
    
    return render_template_string(recomendacao_usuario)

if __name__ == "__main__":
    app.run(debug=True)
