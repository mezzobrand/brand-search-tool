
import re
from urllib.parse import urlencode
import streamlit as st

BRAND_MAP = {
    "愛馬仕": "エルメス", "赫米士": "エルメス", "Hermes": "エルメス", "Hermès": "エルメス",
    "香奈兒": "シャネル", "香奈儿": "シャネル", "CHANEL": "シャネル", "Chanel": "シャネル",
    "路易威登": "ルイヴィトン", "LV": "ルイヴィトン", "Louis Vuitton": "ルイヴィトン",
    "高雅德": "ゴヤール", "Goyard": "ゴヤール",
    "迪奧": "ディオール", "Dior": "ディオール",
    "思琳": "セリーヌ", "CELINE": "セリーヌ", "Celine": "セリーヌ",
    "羅意威": "ロエベ", "Loewe": "ロエベ",
    "寶緹嘉": "ボッテガ", "Bottega": "ボッテガ",
    "勞力士": "ロレックス", "Rolex": "ロレックス",
    "卡地亞": "カルティエ", "Cartier": "カルティエ",
}

WORD_MAP = {
    # Hermes
    "迷你琳迪": "ミニリンディ", "Mini Lindy": "ミニリンディ", "mini lindy": "ミニリンディ",
    "琳迪": "リンディ", "Lindy": "リンディ", "lindy": "リンディ",
    "柏金": "バーキン", "鉑金": "バーキン", "Birkin": "バーキン",
    "凱莉": "ケリー", "Kelly": "ケリー",
    "康康": "コンスタンス", "空姐包": "コンスタンス", "Constance": "コンスタンス",
    "菜籃子": "ピコタン", "菜篮子": "ピコタン", "Picotin": "ピコタン",
    "豬鼻子": "エヴリン", "豬鼻包": "エヴリン", "Evelyne": "エヴリン",
    "花園包": "ガーデンパーティ", "Garden Party": "ガーデンパーティ",
    "保齡球包": "ボリード", "Bolide": "ボリード",
    "Jypsiere": "ジプシエール", "Roulis": "ルーリス", "Geta": "ゲタ", "Herbag": "エールバッグ",

    # CHANEL
    "經典口蓋包": "マトラッセ", "經典翻蓋包": "マトラッセ", "Classic Flap": "マトラッセ",
    "方胖子": "ミニマトラッセ",
    "可可手柄": "ココハンドル", "Coco Handle": "ココハンドル", "coco handle": "ココハンドル",
    "男孩包": "ボーイシャネル", "Boy": "ボーイシャネル",
    "22包": "22", "19包": "19",
    "流浪包": "ガブリエル", "Gabrielle": "ガブリエル",
    "鏈條錢包": "チェーンウォレット", "WOC": "チェーンウォレット",
    "化妝包": "バニティ", "購物包": "ショッピングトート",

    # Louis Vuitton
    "Nano Speedy": "ナノスピーディ", "nano speedy": "ナノスピーディ",
    "Neverfull": "ネヴァーフル", "neverfull": "ネヴァーフル",
    "OnTheGo": "オンザゴー", "On The Go": "オンザゴー", "onthego": "オンザゴー",
    "Speedy": "スピーディ", "speedy": "スピーディ",
    "Alma": "アルマ", "alma": "アルマ",
    "Capucines": "カプシーヌ", "capucines": "カプシーヌ",
    "Dauphine": "ドーフィーヌ", "dauphine": "ドーフィーヌ",
    "Noe": "ノエ", "noe": "ノエ", "水桶包": "ノエ",
    "CarryAll": "キャリーオール", "carryall": "キャリーオール",
    "Pochette Metis": "ポシェットメティス", "pochette metis": "ポシェットメティス",
    "Boulogne": "ブローニュ", "boulogne": "ブローニュ",
    "Loop": "ループ", "loop": "ループ",
    "Twist": "ツイスト", "twist": "ツイスト",
    "Keepall": "キーポル", "keepall": "キーポル",
    "Palm Springs": "パームスプリングス", "palm springs": "パームスプリングス",
    "Discovery": "ディスカバリー", "discovery": "ディスカバリー",
    "Christopher": "クリストファー", "christopher": "クリストファー",

    # Dior
    "戴妃包": "レディディオール", "Lady Dior": "レディディオール", "lady dior": "レディディオール",
    "馬鞍包": "サドル", "Saddle": "サドル", "saddle": "サドル",
    "Book Tote": "ブックトート", "book tote": "ブックトート",

    # CELINE
    "鯰魚包": "ラゲージ", "Luggage": "ラゲージ", "luggage": "ラゲージ",
    "Triomphe": "トリオンフ", "triomphe": "トリオンフ",
    "16包": "セーズ", "Ava": "アヴァ", "ava": "アヴァ",

    # LOEWE
    "Puzzle Fold": "パズルフォルド", "puzzle fold": "パズルフォルド",
    "Puzzle": "パズル", "puzzle": "パズル",
    "Flamenco": "フラメンコ", "flamenco": "フラメンコ",
    "Hammock": "ハンモック", "hammock": "ハンモック",
    "Gate": "ゲート", "gate": "ゲート",

    # GOYARD
    "Saint Louis": "サンルイ", "saint louis": "サンルイ",
    "Anjou": "アンジュ", "anjou": "アンジュ",
    "Belvedere": "ベルヴェデーレ", "belvedere": "ベルヴェデーレ",
    "Saigon": "サイゴン", "saigon": "サイゴン",
    "Boeing": "ボーイング", "boeing": "ボーイング",

    # Materials
    "Epsom": "エプソン", "epsom": "エプソン",
    "Togo": "トゴ", "togo": "トゴ",
    "Swift": "スイフト", "swift": "スイフト",
    "Clemence": "クレマンス", "clemence": "クレマンス",
    "魚子醬": "キャビア", "荔枝皮": "キャビア",
    "羊皮": "ラム", "小羊皮": "ラム",
    "牛皮": "レザー", "小牛皮": "カーフ",
    "漆皮": "パテント", "帆布": "キャンバス",
    "老花": "モノグラム",
    "棋盤格": "ダミエ", "棋盤": "ダミエ",
    "鱷魚皮": "クロコ", "鱷魚": "クロコ",
    "蜥蜴": "リザード", "鴕鳥": "オーストリッチ",

    # Colors
    "金棕色": "ゴールド", "金棕": "ゴールド",
    "大象灰": "エトゥープ", "奶昔白": "ナタ",
    "黑色": "黒", "黑": "黒",
    "白色": "白", "白": "白",
    "灰色": "グレー", "灰": "グレー",
    "橘色": "オレンジ", "橙色": "オレンジ",
    "藍色": "青", "藍": "青",
    "紅色": "赤", "紅": "赤",
    "綠色": "緑", "綠": "緑",
    "紫色": "紫", "紫": "紫",
    "粉色": "ピンク", "粉紅": "ピンク",
    "米色": "ベージュ",
    "咖啡色": "ブラウン", "咖啡": "ブラウン", "棕色": "ブラウン",

    # Hardware
    "銀色五金": "SV金具", "銀扣": "SV金具", "銀釦": "SV金具",
    "金色五金": "G金具", "金扣": "G金具", "金釦": "G金具",
    "香檳金": "シャンパンゴールド",
}

def convert_text(text, mapping):
    if not text:
        return ""
    out = text
    for k in sorted(mapping.keys(), key=len, reverse=True):
        out = out.replace(k, mapping[k])
    out = out.replace("刻", "")
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
    params = {"limit":"50", "sortKey":"1", "q":q, "tab":"general", "tableType":"grid"}
    return "https://www.ecoauc.com/client/market-prices?" + urlencode(params)

st.set_page_config(page_title="繁体字→日本語 RK検索変換 V3.1", layout="wide")
st.title("繁体字 → 日本語 RK検索変換 V3.1")
st.caption("4項目だけ。商品写真・ブランド・商品名・フリーワード。主要辞書追加済み。")

left, right = st.columns(2)

with left:
    st.subheader("① 入力")
    photos = st.file_uploader("商品写真", type=["jpg","jpeg","png","webp"], accept_multiple_files=True)
    if photos:
        cols = st.columns(min(4, len(photos)))
        for i, f in enumerate(photos):
            cols[i % len(cols)].image(f, caption=f.name, use_container_width=True)

    brand_tw = st.text_input("ブランド（繁体字・英語）", placeholder="例：愛馬仕 / 香奈兒 / LV")
    product_tw = st.text_input("商品名（繁体字・英語）", placeholder="例：琳迪26 / 柏金25 / Speedy30")
    freeword_tw = st.text_area("フリーワード（繁体字・英語）", placeholder="例：K Epsom 金棕色 銀扣", height=120)

    if st.button("日本語に変換", type="primary"):
        st.session_state["brand"] = convert_text(brand_tw, BRAND_MAP)
        st.session_state["product"] = convert_text(product_tw, WORD_MAP)
        st.session_state["freeword"] = convert_text(freeword_tw, WORD_MAP)

with right:
    st.subheader("② 変換結果")
    brand = st.session_state.get("brand", convert_text(brand_tw, BRAND_MAP))
    product = st.session_state.get("product", convert_text(product_tw, WORD_MAP))
    freeword = st.session_state.get("freeword", convert_text(freeword_tw, WORD_MAP))

    st.markdown("**ブランド**")
    st.code(brand or "未入力")

    st.markdown("**商品名**")
    st.code(product or "未入力")

    st.markdown("**フリーワード**")
    st.code(freeword or "空欄")

    st.divider()
    st.subheader("③ 検索")
    st.markdown("**RK検索内容**")
    st.code(f"ブランド欄：{brand or '未入力'}\n商品名欄：{product or '未入力'}\nフリーワード欄：{freeword or '空欄'}")

    if brand or product or freeword:
        st.link_button("RKで検索", rk_url(brand, product, freeword))
        st.link_button("エコリングで検索", eco_url(product, freeword))

st.divider()
st.subheader("注意")
st.write("- CHANELランダムシリアルは検索ワードに使わない。")
st.write("- Hermes刻印は「刻」を入れても自動で削除。")
st.write("- 今回は相場抽出・平均価格・台湾ドル換算・AI画像認識は入れていません。")
