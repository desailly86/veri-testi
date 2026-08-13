# -*- coding: utf-8 -*-
"""
sofascore_test_app.py — Sofascore/365scores Streamlit'ten çalışıyor mu? TEŞHİS
==============================================================================
Bunu GEÇİCİ, AYRI bir Streamlit uygulaması olarak deploy et (ana uygulamana
DOKUNMA). Amaç tek: Sofascore ve 365scores, Streamlit'in veri-merkezi IP'sinden
erişilebiliyor mu, yoksa 403 mü yiyoruz? ESPN 403'ünü çözen güçlü başlıkları
deniyoruz — belki bunları da aşar.

KULLANIM: Yeni bir GitHub reposu (ya da ana reponda ayrı bir dosya) + Streamlit
Cloud'da bu dosyayı ana dosya olarak seç. Butona bas, sonucu gör.
requirements.txt: streamlit, requests
"""
import streamlit as st
import requests

st.set_page_config(page_title="Veri Kaynağı Testi", page_icon="🔬")
st.title("🔬 Sofascore / 365scores — Streamlit Erişim Testi")
st.caption("Bu geçici bir test. Sofascore ve 365scores'un Streamlit sunucusundan "
           "(veri-merkezi IP) erişilebilir olup olmadığını ölçer.")

# ESPN 403'ünü çözen güçlü tarayıcı başlıkları — Sofascore'u da aşabilir
BASLIKLAR = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.sofascore.com/",
    "Origin": "https://www.sofascore.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Cache-Control": "no-cache",
}

# Kanıtlanmış ID'ler: Süper Lig = 52, sezon 2026/27 = 98080
SOFA = "https://api.sofascore.com/api/v1"
TESTLER = [
    ("Sofascore — Süper Lig sezonları",
     f"{SOFA}/unique-tournament/52/seasons", "sofascore"),
    ("Sofascore — 2026/27 puan durumu",
     f"{SOFA}/unique-tournament/52/season/98080/standings/total", "sofascore"),
    ("Sofascore — 1. hafta maçları",
     f"{SOFA}/unique-tournament/52/season/98080/events/round/1", "sofascore"),
    ("365scores — Türkçe sonuçlar",
     "https://webws.365scores.com/web/games/results/?langId=1&appTypeId=5&competitions=113",
     "365scores"),
]


def test_et(url, baslik_kullan):
    """İki yöntemle dene: (1) başlıksız, (2) güçlü başlıklarla."""
    sonuclar = {}
    # Yöntem 1: düz istek (başlıksız)
    try:
        r = requests.get(url, timeout=15)
        sonuclar["baslikSIZ"] = r.status_code
    except Exception as e:
        sonuclar["baslikSIZ"] = f"hata: {type(e).__name__}"
    # Yöntem 2: güçlü başlıklarla
    try:
        r = requests.get(url, headers=BASLIKLAR, timeout=15)
        sonuclar["baslikLI"] = r.status_code
        if r.status_code == 200:
            try:
                veri = r.json()
                # kaç kayıt geldiğini kabaca say
                if "seasons" in veri:
                    sonuclar["kayit"] = f"{len(veri['seasons'])} sezon"
                elif "standings" in veri:
                    n = sum(len(s.get("rows", [])) for s in veri.get("standings", []))
                    sonuclar["kayit"] = f"{n} takım (puan durumu)"
                elif "events" in veri:
                    sonuclar["kayit"] = f"{len(veri['events'])} maç"
                elif "games" in veri:
                    sonuclar["kayit"] = f"{len(veri['games'])} maç (365scores)"
                else:
                    sonuclar["kayit"] = "JSON geldi"
            except Exception:
                sonuclar["kayit"] = "200 ama JSON değil"
    except Exception as e:
        sonuclar["baslikLI"] = f"hata: {type(e).__name__}"
    return sonuclar


if st.button("🔬 Testi çalıştır", type="primary"):
    for ad, url, kaynak in TESTLER:
        st.markdown(f"**{ad}**")
        with st.spinner("Deneniyor…"):
            s = test_et(url, kaynak)
        c1, c2, c3 = st.columns(3)
        # başlıksız sonuç
        bsiz = s.get("baslikSIZ")
        c1.metric("Başlıksız", str(bsiz),
                  delta="✅" if bsiz == 200 else "❌", delta_color="off")
        # başlıklı sonuç
        bli = s.get("baslikLI")
        c2.metric("Güçlü başlıkla", str(bli),
                  delta="✅" if bli == 200 else "❌", delta_color="off")
        # kayıt
        c3.metric("Veri", s.get("kayit", "—"))

        if bli == 200:
            st.success(f"✅ {kaynak.upper()} Streamlit'ten ÇALIŞIYOR! Bu kaynağı doğrudan kullanabiliriz.")
        elif bsiz == 200:
            st.success(f"✅ {kaynak.upper()} başlıksız çalışıyor!")
        elif str(bli) == "403" or str(bsiz) == "403":
            st.error(f"❌ {kaynak.upper()} 403 verdi — Streamlit IP'si engelli. Proxy ya da "
                     "'evden çek' yöntemi gerekir.")
        else:
            st.warning(f"⚠️ {kaynak.upper()} belirsiz sonuç: {s}")
        st.divider()

    st.info("**Yorum:** Yeşil (200) gördüğün kaynağı doğrudan kullanabiliriz. Kırmızı (403) "
            "görürsen o kaynak Streamlit'ten engelli — ama senin bilgisayarından çalışıyordu, "
            "yani veri hâlâ erişilebilir, sadece farklı bir yöntemle (proxy ya da evden çekme).")
else:
    st.write("Yukarıdaki butona bas, dört kaynak da test edilsin.")
