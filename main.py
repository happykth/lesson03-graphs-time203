import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────
# 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", page_icon="🎬", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
WARM = "#E8743B"  # 그래프 기본 색 (따뜻한 주황)

# 그래프마다 아래에 보여줄 '이 그래프로 알 수 있는 것' 한 문장
# 그래프를 추가할 때마다 키(예: "graph2")를 하나씩 늘려 문장을 적어 주세요.
# 비워 두면 화면에 입력칸이 나타납니다.
INSIGHTS = {
    "graph1": "",
}


# ─────────────────────────────────────────────
# 데이터 불러오기
# ─────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)
    # 하이픈 없는 8자리 숫자(예: 20240101)를 진짜 날짜로 바꾸기
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


def show_insight(key: str) -> None:
    """그래프 아래 '이 그래프로 알 수 있는 것' 한 문장 자리"""
    text = INSIGHTS.get(key, "")
    if text:
        st.info(f"💡 **이 그래프로 알 수 있는 것**  \n{text}")
    else:
        st.text_input(
            "💡 이 그래프로 알 수 있는 것 (한 문장)",
            key=f"insight_{key}",
            placeholder="여기에 한 문장을 적어 보세요.",
        )


# ─────────────────────────────────────────────
# 구역 1: 시간에 따른 변화
# ─────────────────────────────────────────────
def section_time(df: pd.DataFrame) -> None:
    st.header("① 영화 한 편의 일관객 변화")

    # 10위권에 오래 머문 영화가 위에 오도록 정렬
    movies = df["영화명"].value_counts().index.tolist()
    movie = st.selectbox("영화를 골라 보세요", movies)

    one = df[df["영화명"] == movie].sort_values("날짜")

    fig = px.line(one, x="날짜", y="일관객", markers=True, color_discrete_sequence=[WARM])
    fig.update_traces(hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>")
    fig.update_layout(
        title=f"{movie} — 날짜별 일관객",
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    show_insight("graph1")


# ─────────────────────────────────────────────
# 화면 구성 (그래프 구역을 여기에 계속 추가)
# ─────────────────────────────────────────────
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 10위권 기록(365일)")

data = load_data()

section_time(data)
st.divider()

# 새 구역은 아래처럼 함수를 만들어 이어 붙이면 됩니다.
# section_xxx(data)
# st.divider()
