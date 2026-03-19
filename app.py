import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Ads Prospector", layout="wide")

# -------------------------
# LANGUAGE
# -------------------------
lang = st.selectbox("Language / Idioma", ["Português", "English"])

def t(pt, en):
    return pt if lang == "Português" else en

st.title(t("🔎 Analisador de Empresas", "🔎 Company Analyzer"))

url = st.text_input(t("Cole um site, Instagram ou Facebook", "Paste a website, Instagram or Facebook"))

# -------------------------
# HELPERS
# -------------------------
def get_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        return requests.get(url, headers=headers, timeout=10).text
    except:
        return None

def extract_name(html, url):
    if not html:
        return url

    soup = BeautifulSoup(html, "html.parser")

    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        name = og["content"]
    else:
        name = soup.title.string if soup.title else url

    name = re.split(r'[\|\-–]', name)[0]
    return name.strip()

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

def get_domain(url):
    return url.split("//")[-1].split("/")[0]

# 🔥 NOVO — usa Facebook correto
def create_ads_links(name, domain, facebook_url):
    fb_page = None

    if facebook_url:
        try:
            fb_page = facebook_url.split("facebook.com/")[-1].split("/")[0]
        except:
            fb_page = None

    return {
        "meta": f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&view_all_page_id={fb_page}" if fb_page else None,
        "tiktok": f"https://ads.tiktok.com/business/creativecenter/inspiration/topads/search/{name}",
        "google": f"https://adstransparency.google.com/?q={domain}"
    }

# -------------------------
# PROCESS
# -------------------------
if st.button(t("Analisar", "Analyze")):
    if not url:
        st.warning(t("Insira um link", "Insert a link"))
    else:
        html = get_html(url)
        socials = find_social_links(html)
        name = extract_name(html, url)
        domain = get_domain(url)

        st.subheader(t("🏢 Empresa", "🏢 Company"))
        st.write(name)

        st.subheader(t("🌐 Presença Digital", "🌐 Digital Presence"))

        st.write("🌐 Site:", url)
        st.write("📸 Instagram:", socials["instagram"] or "❌")
        st.write("👍 Facebook:", socials["facebook"] or "❌")

        st.subheader(t("📢 Anúncios", "📢 Ads"))

        ads_links = create_ads_links(name, domain, socials["facebook"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("Meta")
            if ads_links["meta"]:
                st.markdown(f"[🔍 {t('Ver anúncios','View Ads')}]({ads_links['meta']})")
            else:
                st.warning(t("Página do Facebook não encontrada", "Facebook page not found"))

        with col2:
            st.write("TikTok")
            st.markdown(f"[🔍 {t('Ver anúncios','View Ads')}]({ads_links['tiktok']})")

        with col3:
            st.write("Google")
            st.markdown(f"[🔍 {t('Ver anúncios','View Ads')}]({ads_links['google']})")

        st.subheader(t("🧠 Diagnóstico", "🧠 Insights"))

        if not socials["instagram"]:
            st.warning(t("Empresa não está no Instagram", "Company not on Instagram"))

        if not socials["facebook"]:
            st.warning(t("Empresa não está no Facebook", "Company not on Facebook"))

        st.success(t("Análise concluída", "Analysis completed"))
