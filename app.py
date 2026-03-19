import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Ads Prospector", layout="wide")

# LANGUAGE
lang = st.selectbox("Language / Idioma", ["Português", "English"])

def t(pt, en):
    return pt if lang == "Português" else en

st.title(t("🔎 Analisador de Empresas", "🔎 Company Analyzer"))

url = st.text_input(t("Cole um site, Instagram ou Facebook", "Paste a website, Instagram or Facebook"))

def get_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        return requests.get(url, headers=headers, timeout=10).text
    except:
        return None

def find_social_links(html):
    socials = {"instagram": None, "facebook": None}
    if not html:
        return socials
    
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    
    for link in links:
        href = link["href"]
        if "instagram.com" in href:
            socials["instagram"] = href
        if "facebook.com" in href:
            socials["facebook"] = href
    
    return socials

def create_ads_links(name):
    return {
        "meta": f"https://www.facebook.com/ads/library/?q={name}",
        "tiktok": f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/search/{name}",
        "google": f"https://adstransparency.google.com/?q={name}"
    }

if st.button(t("Analisar", "Analyze")):
    if not url:
        st.warning(t("Insira um link", "Insert a link"))
    else:
        html = get_html(url)
        socials = find_social_links(html)

        st.subheader(t("🌐 Presença Digital", "🌐 Digital Presence"))

        st.write("🌐 Site:", "✅")
        st.write("📸 Instagram:", socials["instagram"] or "❌")
        st.write("👍 Facebook:", socials["facebook"] or "❌")

        st.subheader(t("📢 Anúncios", "📢 Ads"))

        name = url.split("//")[-1].split("/")[0]
        ads_links = create_ads_links(name)

        st.write(f"[Meta Ads]({ads_links['meta']})")
        st.write(f"[TikTok Ads]({ads_links['tiktok']})")
        st.write(f"[Google Ads]({ads_links['google']})")

        st.success(t("Análise concluída", "Analysis completed"))
