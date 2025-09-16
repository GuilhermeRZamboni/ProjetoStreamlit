import streamlit as st
import requests
import datetime
import matplotlib.pyplot as plt

# ==== CHAVES DE API ====
OPENWEATHER_API_KEY = "d56b07f5053f9bcf3be82a4df9f6cbf6"
NEWS_API_KEY = "6eb8d82ad76a4331837ccc182c2fe6ab"

# ==== CONFIG STREAMLIT ====
st.set_page_config(page_title="Clima + Notícias", layout="centered")
st.title("🌤 Clima Atual + 📰 Notícias Locais")


def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units={unidade}&lang=pt"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_forecast(city_name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={OPENWEATHER_API_KEY}&units={unidade}&lang=pt"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=pt&pageSize=5"
    response = requests.get(url)
    return response.json().get("articles", []) if response.status_code == 200 else []

def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M")

# ==== INTERFACE ====
aba1, aba2 = st.tabs(["Clima", "Notícias"])

with aba1:
    st.sidebar.header("⚙️ Configurações")
    cidade = st.sidebar.text_input("Digite o nome da cidade:", "São Paulo")
    unidade = st.sidebar.radio("Unidade de temperatura:", ("Graus Celcius", "Grau Fahrenheit"))
    simbolo_unidade = "°C" if unidade == "Graus Celcius" else "°F"
    if unidade == "Graus Celcius":
        unidade = "metric"
    else:
        unidade="Imperial"
    with st.spinner("Buscando clima..."):
        weather_data = get_weather(cidade)
        forecast_data = get_forecast(cidade)

    if weather_data:
        st.subheader("☁️ Clima Atual")
        
        # Ícone do clima
        icon = weather_data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        st.image(icon_url, width=100)

        # Informações principais
        st.write(f"**Cidade:** {weather_data['name']}, {weather_data['sys']['country']}")
        st.write(f"**Temperatura:** {weather_data['main']['temp']}{simbolo_unidade}")
        st.write(f"**Sensação térmica:** {weather_data['main']['feels_like']}{simbolo_unidade}")
        st.write(f"**Clima:** {weather_data['weather'][0]['description'].capitalize()}")
        st.write(f"**Umidade:** {weather_data['main']['humidity']}%")
        st.write(f"**Pressão:** {weather_data['main']['pressure']} hPa")
        st.write(f"**Vento:** {weather_data['wind']['speed']} m/s")
        st.write(f"**Nascer do sol:** {format_time(weather_data['sys']['sunrise'])} ⛅")
        st.write(f"**Pôr do sol:** {format_time(weather_data['sys']['sunset'])} 🌇")

        # Previsão 5 dias (gráfico)
        if forecast_data:
            st.subheader("📊 Previsão para os próximos dias")
            temps, dates = [], []
            for item in forecast_data["list"][::8]:  # Pega 1 previsão por dia (a cada 8 registros de 3h)
                temps.append(item["main"]["temp"])
                dates.append(item["dt_txt"].split(" ")[0])

            fig, ax = plt.subplots()
            ax.plot(dates, temps, marker="o")
            ax.set_title("Temperatura nos próximos dias")
            ax.set_ylabel(f"Temperatura ({simbolo_unidade})")
            ax.set_xlabel("Data")
            st.pyplot(fig)

    else:
        st.error("Cidade não encontrada ou erro na API de clima.")

with aba2: 
    pesquisa = st.chat_input("Olá, oque você deseja pesquisar?")
    with st.spinner("Buscando notícias..."):
        news_articles = get_news(pesquisa)

    if news_articles:
        st.subheader("📰 Notícias Relacionadas")
        for article in news_articles:
            if article.get("urlToImage"):
                st.image(article["urlToImage"], use_column_width=True)
            st.markdown(f"### [{article['title']}]({article['url']})")
            st.write(article.get("description", ""))
            st.caption(f"Fonte: {article['source']['name']} | Publicado em: {article['publishedAt'][:10]}")
            st.markdown("---")
    else:
        st.warning("Nenhuma notícia encontrada para esta cidade.")
