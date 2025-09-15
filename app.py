import streamlit as st
import requests

# ==== CHAVES DE API ====
OPENWEATHER_API_KEY = "d56b07f5053f9bcf3be82a4df9f6cbf6"
NEWS_API_KEY = "6eb8d82ad76a4331837ccc182c2fe6ab"

st.set_page_config(page_title="Clima + Notícias", layout="centered")
st.title("🌤 Clima Atual + 📰 Notícias Relacionadas")

city = st.text_input("Digite o nome da cidade:", "São Paulo")

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=pt&pageSize=5"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        return []
aba1, aba2 = st.tabs(["Clima", "Notícias"])
with aba1:
    with st.spinner("Buscando clima..."):
        weather_data = get_weather(city)
    if weather_data:
        st.subheader("☁️ Clima Atual")
        st.write(f"**Cidade:** {weather_data['name']}, {weather_data['sys']['country']}")
        st.write(f"**Temperatura:** {weather_data['main']['temp']}°C")
        st.write(f"**Sensação térmica:** {weather_data['main']['feels_like']}°C")
        st.write(f"**Clima:** {weather_data['weather'][0]['description'].capitalize()}")
        st.write(f"**Vento:** {weather_data['wind']['speed']} m/s")
    else:
        st.error("Cidade não encontrada ou erro na API de clima.")
with aba2: 
    with st.spinner("Buscando notícias..."):
        news_articles = get_news(city)

    if news_articles:
        st.subheader("📰 Notícias Relacionadas")
        for article in news_articles:
            st.markdown(f"### [{article['title']}]({article['url']})")
            st.write(article["description"])
            st.caption(f"Fonte: {article['source']['name']} | Publicado em: {article['publishedAt'][:10]}")
    else:
        st.warning("Nenhuma notícia encontrada para esta cidade.")