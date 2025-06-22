
import streamlit as st
from googlesearch import search as gsearch
from duckduckgo_search import ddg
import requests
from bs4 import BeautifulSoup
import re
import tldextract
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

def expand_keywords(keyword):
    prompt = f"اكتب لي 5 كلمات مفتاحية مرتبطة بـ '{keyword}'"
    resp = openai.Completion.create(model="gpt-3.5-turbo", prompt=prompt, max_tokens=50)
    return [kw.strip() for kw in resp.choices[0].text.split('\n') if kw.strip()]

def fetch_urls(keyword):
    urls = set()
    for q in [keyword] + expand_keywords(keyword):
        for u in gsearch(q, num_results=5, lang="ar"):
            urls.add(u)
        for result in ddg(q, max_results=5):
            urls.add(result['href'])
    return list(urls)

def extract_from_page(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        phones = re.findall(r'05\d{8}', text)
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        wa = re.findall(r'https://wa\.me/\d+', text)
        domain = tldextract.extract(url).domain
        name = soup.title.string if soup.title else domain
        return {"اسم المتجر": name, "الرابط": url, "جوال": phones[0] if phones else "", 
                "إيميل": emails[0] if emails else "", "واتساب": wa[0] if wa else ""}
    except:
        return None

st.set_page_config(page_title="أداة البحث المتقدمة", layout="centered")
st.title("🔍 أداة البحث الذكية – النسخة 1.5")

st.markdown("### المفاتيح")
keyword = st.text_input("🔑 أدخل الكلمة المفتاحية")
custom_sites = st.text_area("🌐 مواقع إضافية (واحدة في السطر)")
if st.button("🔎 ابحث"):
    if not keyword:
        st.warning("أدخل كلمة مفتاحية أولاً")
    else:
        st.info("...جاري البحث وجمع البيانات")
        urls = fetch_urls(keyword)
        for s in custom_sites.splitlines():
            if s.startswith("http"):
                urls.append(s.strip())
        data = []
        for u in urls[:15]:
            res = extract_from_page(u)
            if res: data.append(res)
        st.write(f"تم استخراج {len(data)} صف")
        st.dataframe(data)
