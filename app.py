import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Ads Prospector", layout="wide")

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
        return ""

def extract_name(html, url):
    soup = BeautifulSoup(html, "html.parser")

    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        name = og["content"]
    elif soup.title:
        name = soup.title.string
    else:
        name = url

    name = re.split(r'[\|\-–]', name)[0]
    return name.strip()

def find_social_links(html):
    socials = {"instagram": None, "facebook": None}

    # método 1: links
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "instagram.com" in href:
            socials["instagram"] = href
        if "facebook.com" in href:
            socials["facebook"] = href

    # método 2: regex (melhor)
    if not socials["instagram"]:
        match = re.search(r"(https?:\/\/(www\.)?instagram\.com\/[A-Za-z0-9_.]+)", html)
        if match:
            socials["instagram"] = match.group(0)

    if not socials["facebook"]:
        match = re.search(r"(https?:\/\/(www\.)?facebook\.com\/[A-Za-z0-9_.]+)", html)
        if match:
            socials["facebook"] = match.group(0)

    return socials

def get_domain(url):
    return url.split("//")[-1].split("/")[0]

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
        "google": f"https://adstransparency.google.com/advertiser?q={domain}"
    }

# -------------------------
# PROCESS
# -------------------------
if st.button(t("Analisar", "Analyze")):
    if not url:
        st.warning(t("Insira um link", "Insert a link"))
    else:
        html = get_html(url)
        name = extract_name(html, url)
        socials = find_social_links(html)
        domain = get_domain(url)

        st.subheader(t("🏢 Empresa", "🏢 Company"))
        st.write(name)

        st.subheader(t("🌐 Presença Digital", "🌐 Digital Presence"))

        st.write("🌐 Site:", url)

        if socials["instagram"]:
            st.markdown(f"📸 [Instagram]({socials['instagram']})")
        else:
            st.warning("Instagram não encontrado")

        if socials["facebook"]:
            st.markdown(f"👍 [Facebook]({socials['facebook']})")
        else:
            st.warning("Facebook não encontrado")

        st.subheader(t("📢 Anúncios", "📢 Ads"))

        ads_links = create_ads_links(name, domain, socials["facebook"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("Meta")
            if ads_links["meta"]:
                st.markdown(f"[🔍 Ver anúncios]({ads_links['meta']})")
            else:
                st.warning("Sem página do Facebook")

        with col2:
            st.write("TikTok")
            st.markdown(f"[🔍 Ver anúncios]({ads_links['tiktok']})")

        with col3:
            st.write("Google")
            st.markdown(f"[🔍 Ver anúncios]({ads_links['google']})")

        st.success("Análise concluída")
