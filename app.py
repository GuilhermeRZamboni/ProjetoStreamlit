import streamlit as st
import requests
import datetime
import matplotlib.pyplot as plt
import pandas as pd

# ==== CHAVES DE API ====
CHAVE_CLIMA = "d56b07f5053f9bcf3be82a4df9f6cbf6"
CHAVE_NOTICIAS = "6eb8d82ad76a4331837ccc182c2fe6ab"

# ==== CONFIGURAÇÃO STREAMLIT ====
st.set_page_config(page_title="Clima + Notícias", layout="centered")
st.title("🌤 Clima Atual + 📰 Notícias Locais")

# ==== FUNÇÕES ====
def buscar_clima(cidade, unidade):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={CHAVE_CLIMA}&units={unidade}&lang=pt"
    resposta = requests.get(url)
    return resposta.json() if resposta.status_code == 200 else None

def buscar_previsao(cidade, unidade):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={CHAVE_CLIMA}&units={unidade}&lang=pt"
    resposta = requests.get(url)
    return resposta.json() if resposta.status_code == 200 else None

def buscar_noticias(termo):
    url = f"https://newsapi.org/v2/everything?q={termo}&apiKey={CHAVE_NOTICIAS}&language=pt&pageSize=5"
    resposta = requests.get(url)
    return resposta.json().get("articles", []) if resposta.status_code == 200 else []

def formatar_hora(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M")

# ==== INTERFACE ====
aba_clima, aba_noticias = st.tabs(["Clima", "Notícias"])

with aba_clima:
    cidade = st.text_input("Digite o nome da cidade:", "São Paulo")

    # Unidade antes de chamar API
    escolha_unidade = st.radio("Unidade de temperatura:", ("Celsius", "Fahrenheit"))
    simbolo_unidade = "°C" if escolha_unidade == "Celsius" else "°F"
    unidade = "metric" if escolha_unidade == "Celsius" else "imperial"

    with st.spinner("Buscando clima..."):
        dados_clima = buscar_clima(cidade, unidade)
        dados_previsao = buscar_previsao(cidade, unidade)

    if dados_clima:
        st.subheader("☁️ Clima Atual")

        # Ícone do clima
        icone = dados_clima['weather'][0]['icon']
        icone_url = f"http://openweathermap.org/img/wn/{icone}@2x.png"
        st.image(icone_url, width=100)

        # Detalhes do clima
        st.write(f"**Cidade:** {dados_clima['name']}, {dados_clima['sys']['country']}")
        st.write(f"**Temperatura:** {dados_clima['main']['temp']}{simbolo_unidade}")
        st.write(f"**Sensação térmica:** {dados_clima['main']['feels_like']}{simbolo_unidade}")
        st.write(f"**Condição:** {dados_clima['weather'][0]['description'].capitalize()}")
        st.write(f"**Umidade:** {dados_clima['main']['humidity']}%")
        st.write(f"**Pressão:** {dados_clima['main']['pressure']} hPa")
        st.write(f"**Vento:** {dados_clima['wind']['speed']} m/s")
        st.write(f"**Nascer do sol:** {formatar_hora(dados_clima['sys']['sunrise'])} ⛅")
        st.write(f"**Pôr do sol:** {formatar_hora(dados_clima['sys']['sunset'])} 🌇")

    # Previsão de 5 dias (mínimas e máximas)
    if dados_previsao:
        st.subheader("📊 Previsão para os próximos 5 dias")

        previsao_lista = dados_previsao["list"]
        df = pd.DataFrame([
            {
                "data": item["dt_txt"].split(" ")[0],
                "temp": item["main"]["temp"]
            }
            for item in previsao_lista
        ])

        diario = df.groupby("data").agg({"temp": ["min", "max"]}).reset_index()
        diario.columns = ["Data", "Mínima", "Máxima"]

        # Mostrar tabela
        st.dataframe(diario.set_index("Data"))

        # Gráfico min vs max
        fig, ax = plt.subplots()
        ax.plot(diario["Data"], diario["Máxima"], marker="o", label="Máxima", color="red")
        ax.plot(diario["Data"], diario["Mínima"], marker="o", label="Mínima", color="blue")
        ax.set_title("Temperaturas máximas e mínimas")
        ax.set_ylabel(f"Temperatura ({simbolo_unidade})")
        ax.set_xlabel("Data")
        ax.legend()
        st.pyplot(fig)
    else:
        st.error("Cidade não encontrada ou erro na API de clima.")

with aba_noticias:
    termo_pesquisa = st.chat_input("Digite o termo para pesquisar notícias:")
    if termo_pesquisa:
        with st.spinner("Buscando notícias..."):
            artigos = buscar_noticias(termo_pesquisa)

        if artigos:
            st.subheader("📰 Notícias Relacionadas")
            for artigo in artigos:
                if artigo.get("urlToImage"):
                    st.image(artigo["urlToImage"], use_container_width=True)
                st.markdown(f"### [{artigo['title']}]({artigo['url']})")
                st.write(artigo.get("description", ""))
                st.caption(f"Fonte: {artigo['source']['name']} | Publicado em: {artigo['publishedAt'][:10]}")
                st.markdown("---")
        else:
            st.warning("Nenhuma notícia encontrada para essa pesquisa.")
