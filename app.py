import re
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

# Googleスプレッドシート辞書CSV
# A列：入力 / B列：日本語
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1aUBVqiZmxDzN8k2eo54wKytqBvEeXxqHLpxBnCWWfv8/export?format=csv"

# スプレッドシートが読めない時だけ使う最低限の予備辞書
FALLBACK_MAP = {
    "愛馬仕": "エルメス",
    "赫米士": "エルメス",
    "Hermes": "エルメス",
    "Hermès": "エルメス",
    "香奈兒": "シャネル",
    "CHANEL": "シャネル",
    "Chanel": "シャネル",
    "路易威登": "ルイヴィトン",
    "LV": "ルイヴィトン",
    "Louis Vuitton": "ルイヴィトン",
    "高雅德": "ゴヤール",
    "Goyard": "ゴヤール",
    "琳迪": "リンディ",
    "迷你琳迪": "ミニリンディ",
    "柏金": "バーキン",
    "鉑金": "バーキン",
    "Birkin": "バーキン",
    "凱莉": "ケリー",
    "Kelly": "ケリー",
    "菜籃子": "ピコタン",
    "Picotin": "ピコタン",
    "Speedy": "スピーディ",
    "Neverfull": "ネヴァーフル",
    "CarryAll": "キャリーオール",
    "OnTheGo": "オンザゴー",
    "老花": "モノグラム",
    "銀扣": "SV金具",
    "金扣": "G金具",
}


@st.cache_data(ttl=60)
def load_dictionary():
    """Googleスプレッドシートから辞書を読み込む。失敗したら予備辞書を使う。"""
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df = df.dropna(how="all")

        mapping = {}
        for _, row in df.iterrows():
            if len(row) < 2:
                continue

            key = str(row.iloc[0]).strip()
            value = str(row.iloc[1]).strip()

            if not key or not value:
                continue
            if key in ["入力", "input", "Input"] or value in ["日本語", "japanese", "Japanese"]:
                continue
            if key == "nan" or value == "nan":
                continue

            mapping[key] = value

        if mapping:
            return mapping, "Googleスプレッドシート"

    except Exception:
        pass

    return FALLBACK_MAP, "内蔵予備辞書"


def convert_text(text, mapping):
    """辞書にある語句を長い順に置換。数字やアルファベットは基本そのまま残る。"""
    if not text:
        return ""

    out = str(text)

    for k in sorted(mapping.keys(), key=len, reverse=True):
        out = out.replace(k, mapping[k])

    # Hermes刻印で「K刻」「W刻」などと入っても、検索では刻を外す
    out = out.replace("刻", "")

    # 余分な空白整理
    out = re.sub(r"\s+", " ", out).strip()
    return out


def rk_url(brand, product, freeword):
    params = {
        "c": "search_thumb_m",
        "i01k96fvxfy3m0b6p6acnmv23cn": brand,
        "keyword": freeword,
        "i01k96kxh9tsmvhmsexc90km2ag": product,
        "name_search": "partial",
        "model_search": "partial",
    }
    return "https://soubakensaku.com/contents.php?" + urlencode(params)


def eco_url(product, freeword):
    q = " ".join([x for x in [product, freeword] if x]).strip()
    params = {
        "limit": "50",
        "sortKey": "1",
        "q": q,
        "tab": "general",
        "tableType": "grid",
    }
    return "https://www.ecoauc.com/client/market-prices?" + urlencode(params)


st.set_page_config(page_title="繁体字→日本語 RK検索変換 V4", layout="wide")

st.title("繁体字 → 日本語 RK検索変換 V4")
st.caption("Googleスプレッドシート辞書対応版。辞書追加はスプレッドシートに1行追加するだけ。")

dictionary, source = load_dictionary()

with st.sidebar:
    st.subheader("辞書状態")
    st.write(f"読み込み元：{source}")
    st.write(f"辞書件数：{len(dictionary)}件")

    if st.button("辞書を再読み込み"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption("辞書はGoogleスプレッドシートのA列→B列で読み込みます。")
    st.caption("A列：入力語 / B列：日本語")

left, right = st.columns(2)

with left:
    st.subheader("① 入力")

    photos = st.file_uploader(
        "商品写真",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )

    if photos:
        cols = st.columns(min(4, len(photos)))
        for i, f in enumerate(photos):
            cols[i % len(cols)].image(f, caption=f.name, use_container_width=True)

    brand_tw = st.text_input("ブランド（繁体字・英語）", placeholder="例：愛馬仕 / 香奈兒 / LV")
    product_tw = st.text_input("商品名（繁体字・英語）", placeholder="例：琳迪26 / 柏金25 / Speedy30")
    freeword_tw = st.text_area("フリーワード（繁体字・英語）", placeholder="例：K Epsom 金棕色 銀扣", height=120)

    if st.button("日本語に変換", type="primary"):
        st.session_state["brand"] = convert_text(brand_tw, dictionary)
        st.session_state["product"] = convert_text(product_tw, dictionary)
        st.session_state["freeword"] = convert_text(freeword_tw, dictionary)

with right:
    st.subheader("② 変換結果")

    brand = st.session_state.get("brand", convert_text(brand_tw, dictionary))
    product = st.session_state.get("product", convert_text(product_tw, dictionary))
    freeword = st.session_state.get("freeword", convert_text(freeword_tw, dictionary))

    st.markdown("**ブランド**")
    st.code(brand or "未入力")

    st.markdown("**商品名**")
    st.code(product or "未入力")

    st.markdown("**フリーワード**")
    st.code(freeword or "空欄")

    st.divider()
    st.subheader("③ 検索")

    st.markdown("**RK検索内容**")
    st.code(
        f"ブランド欄：{brand or '未入力'}\n"
        f"商品名欄：{product or '未入力'}\n"
        f"フリーワード欄：{freeword or '空欄'}"
    )

    if brand or product or freeword:
        st.link_button("RKで検索", rk_url(brand, product, freeword))
        st.link_button("エコリングで検索", eco_url(product, freeword))

st.divider()
st.subheader("注意")
st.write("- CHANELランダムシリアルは検索ワードに使わない。")
st.write("- Hermes刻印は「刻」を入れても自動で削除。")
st.write("- 写真は表示用です。AI画像認識は入れていません。")
st.write("- 辞書を追加したら、左側の「辞書を再読み込み」を押すと反映されます。")
