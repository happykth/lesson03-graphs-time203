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
    "graph2": "",
    "graph3": "",
    "graph4": "",
    "graph5": "",
}

# 여러 영화를 한 그래프에 그릴 때 쓰는 따뜻한 색 5개
WARM_COLORS = ["#E8743B", "#C0392B", "#F2B134", "#8E5B3A", "#D98880"]


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


def section_top5(df: pd.DataFrame) -> None:
    st.header("② 일관객 합계 상위 5편 비교")

    # 기간 내 일관객 합계가 가장 큰 5편
    top5 = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
    sub = df[df["영화명"].isin(top5)].sort_values(["영화명", "날짜"])

    fig = px.line(
        sub,
        x="날짜",
        y="일관객",
        color="영화명",
        category_orders={"영화명": top5},  # 합계 큰 순서로 범례 표시
        color_discrete_sequence=WARM_COLORS,
    )
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra>%{fullData.name}</extra>"
    )
    fig.update_layout(
        title="일관객 합계 상위 5편 — 날짜별 일관객",
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        legend_title_text="영화 (클릭하면 켜고 끄기)",
    )
    st.plotly_chart(fig, use_container_width=True)
    show_insight("graph2")


def section_daily_total(df: pd.DataFrame) -> None:
    st.header("③ 날짜별 10위권 일관객 합계")

    # 날짜별로 그날 10위권 일관객을 모두 더하기
    daily = df.groupby("날짜", as_index=False)["일관객"].sum().sort_values("날짜")
    top3 = daily.nlargest(3, "일관객")  # 합계가 가장 컸던 3일

    fig = px.area(daily, x="날짜", y="일관객", color_discrete_sequence=[WARM])
    fig.update_traces(hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>")

    # 가장 컸던 3일을 점과 날짜 글자로 표시
    fig.add_scatter(
        x=top3["날짜"],
        y=top3["일관객"],
        mode="markers+text",
        text=top3["날짜"].dt.strftime("%Y-%m-%d"),
        textposition="top center",
        cliponaxis=False,
        marker=dict(color="#C0392B", size=11, line=dict(color="white", width=1.5)),
        name="합계 상위 3일",
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra>상위 3일</extra>",
    )
    fig.update_layout(
        title="날짜별 10위권 일관객 합계",
        xaxis_title="날짜",
        yaxis_title="일관객 합계(명)",
        yaxis_range=[0, daily["일관객"].max() * 1.15],  # 글자가 잘리지 않게 위쪽 여유
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    show_insight("graph3")


def section_top10_movies(df: pd.DataFrame) -> None:
    st.header("④ 일관객 합계 TOP 10 영화")

    # 영화별 일관객 합계와, 개봉 후 10위권에 든 날수(관측된 날의 수)
    summary = (
        df.groupby("영화명")
        .agg(합계=("일관객", "sum"), 순위권_일수=("날짜", "count"))
        .nlargest(10, "합계")
        .sort_values("합계")  # 가로 막대는 아래→위로 그려지므로 오름차순 정렬
    )

    fig = px.bar(
        summary,
        x="합계",
        y=summary.index,
        orientation="h",
        color_discrete_sequence=[WARM],
        custom_data=["순위권_일수"],
    )
    fig.update_traces(
        hovertemplate="%{y}<br>일관객 합계: %{x:,}명<br>10위권에 든 날수: %{customdata[0]}일<extra></extra>"
    )
    fig.update_layout(
        title="일관객 합계 TOP 10 영화",
        xaxis_title="일관객 합계(명)",
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)
    show_insight("graph4")


def section_month_weekday_heatmap(df: pd.DataFrame) -> None:
    st.header("⑤ 월 × 요일별 일관객 합계")

    WEEKDAY_ORDER = ["월", "화", "수", "목", "금", "토", "일"]
    WEEKDAY_MAP = dict(zip(range(7), WEEKDAY_ORDER))  # 0=월요일 ... 6=일요일

    tmp = df.copy()
    tmp["월"] = tmp["날짜"].dt.month
    tmp["요일"] = tmp["날짜"].dt.dayofweek.map(WEEKDAY_MAP)

    pivot = (
        tmp.groupby(["월", "요일"])["일관객"]
        .sum()
        .unstack("요일")
        .reindex(columns=WEEKDAY_ORDER)  # 요일을 월~일 순서로
        .sort_index()  # 월을 1~12 순서로
    )

    fig = px.imshow(
        pivot,
        color_continuous_scale=[
            "#FDEEE3",
            "#F2B134",
            "#E8743B",
            "#C0392B",
        ],  # 연한 색 → 진한 색(관객 많을수록 진하게)
        aspect="auto",
        labels=dict(x="요일", y="월", color="일관객 합계"),
    )
    fig.update_traces(
        hovertemplate="%{y}월 %{x}요일<br>일관객 합계: %{z:,}명<extra></extra>"
    )
    fig.update_layout(
        title="월 × 요일별 일관객 합계",
        yaxis=dict(tickmode="array", tickvals=pivot.index, ticktext=[f"{m}월" for m in pivot.index]),
    )
    st.plotly_chart(fig, use_container_width=True)
    show_insight("graph5")


# ─────────────────────────────────────────────
# 화면 구성 (그래프 구역을 여기에 계속 추가)
# ─────────────────────────────────────────────
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 10위권 기록(365일)")

data = load_data()

section_time(data)
st.divider()

section_top5(data)
st.divider()

section_daily_total(data)
st.divider()

section_top10_movies(data)
st.divider()

section_month_weekday_heatmap(data)
st.divider()

# 새 구역은 아래처럼 함수를 만들어 이어 붙이면 됩니다.
# section_xxx(data)
# st.divider()
