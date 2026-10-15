import io
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 0. 페이지 설정 (와이드 레이아웃 적용)
# ==========================================
st.set_page_config(page_title="퍼널 진단 리포트", layout="wide")

# ==========================================
# 1. 페이지 헤더
# ==========================================
st.title("퍼널 진단 리포트")
st.caption("가입채널별 조회→장바구니 전환 및 핵심 지표 분석")

# ==========================================
# 2. 데이터 임베딩
# ==========================================
# [데이터 1] 단계별 전환율_전체기간.csv
csv_funnel_data = """년월,방문,식당조회,장바구니,결제시작,주문,방문to조회,조회to장바구니,장바구니to결제,결제to주문
2025-09,914,511,256,185,170,55.9,50.1,72.3,91.9
2025-10,1977,1201,605,445,429,60.7,50.4,73.6,96.4
2025-11,2707,1625,838,612,583,60.0,51.6,73.0,95.3
2025-12,3327,2027,1085,787,765,60.9,53.5,72.5,97.2
2026-01,4641,2827,1377,1015,965,60.9,48.7,73.7,95.1
2026-02,5543,3413,1575,1127,1076,61.6,46.1,71.6,95.5
2026-03,7108,4359,1966,1338,1276,61.3,45.1,68.1,95.4
2026-04,7492,4590,2007,1357,1309,61.3,43.7,67.6,96.5
2026-05,8630,5384,2361,1607,1543,62.4,43.9,68.1,96.0
2026-06,8667,5291,2361,1625,1559,61.0,44.6,68.8,95.9
2026-07,9183,5770,2543,1723,1640,62.8,44.1,67.8,95.2
2026-08,8993,5534,2483,1695,1619,61.5,44.9,68.3,95.5"""

df_funnel = pd.read_csv(io.StringIO(csv_funnel_data))

# [데이터 2] 가입채널별_전환율.csv
csv_channel_conv_data = """가입채널,가입자수,식당 조회수,장바구니 담기수,조회to장바구니_전환율
친구초대,298,3026190,668414,22.1
organic,943,34206382,6757538,19.8
NAVER_검색광고,580,14957620,2857660,19.1
GOOGLE_앱설치,454,8822128,1612608,18.3
INSTA_첫주문쿠폰,834,18416388,1738056,9.4"""

df_channel_conv = pd.read_csv(io.StringIO(csv_channel_conv_data))

# [데이터 3] 가입채널별_초기이탈률.csv
csv_channel_churn_data = """가입 채널,고객 수,초기 이탈률
organic,774,29.3%
INSTA_첫주문쿠폰,516,59.1%
NAVER_검색광고,478,29.3%
GOOGLE_앱설치,360,30.3%
친구초대,244,27.5%
전체 합계,2372,35.8%"""

df_channel_churn = pd.read_csv(io.StringIO(csv_channel_churn_data))
df_channel_churn = df_channel_churn.rename(columns=lambda x: x.strip())

# ==========================================
# 2-1. 사이드바 필터 설정
# ==========================================
st.sidebar.header("필터")

# 1. 기간 필터 (select_slider)
unique_months = df_funnel["년월"].sort_values().unique().tolist()
selected_months = st.sidebar.select_slider(
    "기간", options=unique_months, value=(unique_months[0], unique_months[-1])
)

# 2. 유입 경로 필터 (multiselect)
all_channels = df_channel_conv["가입채널"].tolist()
selected_channels = st.sidebar.multiselect(
    "유입 경로", options=all_channels, default=all_channels
)

# 필터 적용 데이터프레임 생성 (f)
f_funnel = df_funnel[
    (df_funnel["년월"] >= selected_months[0])
    & (df_funnel["년월"] <= selected_months[1])
].copy()

f_channel_conv = df_channel_conv[
    df_channel_conv["가입채널"].isin(selected_channels)
].copy()

f_churn = df_channel_churn[
    (df_channel_churn["가입 채널"] != "전체 합계")
    & (df_channel_churn["가입 채널"].isin(selected_channels))
].copy()

# 예외 처리: 필터링 결과가 비어있는 경우
if f_funnel.empty or f_channel_conv.empty or f_churn.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다. 필터를 바꿔 주세요.")
    st.stop()

# ==========================================
# 3. KPI 메트릭 카드 (필터링된 데이터 f 기반 계산)
# ==========================================
total_visits = f_funnel["방문"].sum()
total_orders = f_funnel["주문"].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="1단계 : 전체 방문 수", value=f"{total_visits:,}명")

with col2:
    st.metric(label="🚨 최대 병목 (조회→장바구니)", value="이탈률 53.3%")

with col3:
    st.metric(label="5단계: 최종 주문 수", value=f"{total_orders:,}건")

# ==========================================
# 4. 차트 0: 전체 기간 누적 퍼널 차트 & 핵심 인사이트
# ==========================================
st.subheader("📊 전체 기간 단계별 퍼널 흐름")

funnel_stages = ["방문", "식당조회", "장바구니", "결제시작", "주문"]
funnel_values = [
    f_funnel["방문"].sum(),
    f_funnel["식당조회"].sum(),
    f_funnel["장바구니"].sum(),
    f_funnel["결제시작"].sum(),
    f_funnel["주문"].sum(),
]

df_total_funnel = pd.DataFrame(
    {"단계": funnel_stages, "고객수": funnel_values}
)

fig_funnel = px.funnel(
    df_total_funnel,
    x="고객수",
    y="단계",
    title="전체 기간 퍼널 단계별 전환 현황",
)
fig_funnel.update_layout(template="plotly_white")

st.plotly_chart(fig_funnel, width="stretch")

if selected_months[0] >= "2026-01":
    st.error(
        "🚨 **[주요 이벤트 감지]** 2026년 1월 전체 퍼널의 [조회 ➔ 장바구니] 전환율이 급격한 하락세로 전환되었으며, 이는 INSTA 첫구매 프로모션 시작 시점과 일치함."
    )

# ==========================================
# 5 & 6. 차트 1과 차트 2를 2열로 배치 (신뢰할 수 있는 원본 기반 지표)
# ==========================================
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    colors1 = [
        "#1f77b4" if ch == "INSTA_첫주문쿠폰" else "#d3d3d3"
        for ch in f_channel_conv["가입채널"]
    ]

    fig1 = px.bar(
        f_channel_conv,
        x="가입채널",
        y="조회to장바구니_전환율",
        title="가입채널별 조회to장바구니 전환율 (실제 데이터)",
        text="조회to장바구니_전환율",
    )

    fig1.update_traces(
        marker_color=colors1,
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )

    fig1.update_layout(
        yaxis=dict(
            range=[
                0,
                max(f_channel_conv["조회to장바구니_전환율"]) * 1.15
                if not f_channel_conv.empty
                else 100,
            ]
        ),
        xaxis_title="가입채널",
        yaxis_title="전환율 (%)",
        template="plotly_white",
    )

    st.plotly_chart(fig1, width="stretch")

    with st.expander("📌 채널별 전환율 분석 메모 보기"):
        st.info(
            "INSTA_첫주문쿠폰 채널 유저의 조회→장바구니 전환율이 **9.4%**로 다른 채널(18~22%)에 비해 현저히 낮음"
        )

with chart_col2:
    df_churn_filtered = f_churn.copy()
    df_churn_filtered["초기 이탈률_num"] = (
        df_churn_filtered["초기 이탈률"].str.rstrip("%").astype(float)
    )

    df_churn_filtered = df_churn_filtered.sort_values(
        by="초기 이탈률_num", ascending=False
    )

    colors2 = [
        "#d62728" if ch == "INSTA_첫주문쿠폰" else "#d3d3d3"
        for ch in df_churn_filtered["가입 채널"]
    ]

    fig2 = px.bar(
        df_churn_filtered,
        x="가입 채널",
        y="초기 이탈률_num",
        title="가입채널별 초기 이탈률 (실제 데이터)",
        text="초기 이탈률_num",
        custom_data=["고객 수"],
    )

    fig2.update_traces(
        marker_color=colors2,
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>초기 이탈률: %{y:.1f}%<br>고객 수 (n): %{customdata[0]:,}<extra></extra>",
    )

    fig2.update_layout(
        yaxis=dict(
            range=[
                0,
                max(df_churn_filtered["초기 이탈률_num"]) * 1.15
                if not df_churn_filtered.empty
                else 100,
            ]
        ),
        xaxis_title="가입 채널",
        yaxis_title="초기 이탈률 (%)",
        template="plotly_white",
    )

    st.plotly_chart(fig2, width="stretch")

    with st.expander("📌 초기 이탈률 분석 메모 보기"):
        st.info(
            "탐색 구간의 '조회→장바구니 전환율 하락' 문제와 더불어, INSTA 채널 유저의 높은 '초기 이탈률(59.1%)'로 인한 재주문 단절 문제 동시 발견"
        )

# ==========================================
# 7. 핵심 인사이트 & 개선 제안
# ==========================================
st.subheader("📌 핵심 인사이트 & 개선 제안")

st.markdown(
    """
- 2026년 1월 전체 퍼널의 **[조회 ➔ 장바구니]** 전환율이 하락세로 전환되었으며, 이는 INSTA 첫구매 프로모션 시작 시점과 일치함.
- 해당 기간 INSTA 채널의 유입 모수는 확대되었으나, **[조회 ➔ 장바구니]** 전환율은 **9.4%**로 가장 저조하여 대규모 유입이 유저의 적극적인 탐색 행동으로 이어지지 못함.
- 또한 INSTA 채널의 **초기 이탈률이 59.1%**로 매우 높아, 유입된 유저들이 서비스에 정착하지 못하고 이탈하는 구조적 문제가 확인됨.
- 따라서 프로모션 페이지 내 초기 온보딩 및 상품 탐색 UX/UI(혜택 노출 구조 등)를 개선하여 유저의 활발한 장바구니 담기 및 리텐션을 유도해야 함.
"""
)
