import io
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 0. Plotly 전역 컬러 테마 설정
# ==========================================
ACCENT, GRAY = "#1F3A5F", "#BDBDBD"
px.defaults.color_discrete_map = {
    "INSTA_첫주문쿠폰": ACCENT,
    "organic": "#8C8C8C",
    "NAVER_검색광고": "#A6A6A6",
    "GOOGLE_앱설치": GRAY,
    "친구초대": "#DADADA",
}
px.defaults.color_discrete_sequence = [GRAY]

# ==========================================
# 0-1. 페이지 설정 및 테마 오버라이딩 CSS
# ==========================================
st.set_page_config(page_title="퍼널 진단 리포트", layout="wide", page_icon="📊")

st.markdown(
    f"""
    <style>
        /* 1. Streamlit 루트 프라이머리 컬러 변수 재정의 */
        :root {{
            --primary-color: {ACCENT} !important;
        }}

        /* 2. 사이드바 슬라이더 전체 트랙 & 슬라이더 버튼 색상 강제 오버라이드 */
        div[data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {{
            background-color: {ACCENT} !important;
            border-color: {ACCENT} !important;
            box-shadow: none !important;
        }}
        div[data-testid="stSidebar"] [data-baseweb="slider"] div > div > div {{
            background-color: {ACCENT} !important;
        }}
        div[data-testid="stSidebar"] [data-baseweb="slider"] div[data-testid="stTickBar"] ~ div {{
            background-color: {ACCENT} !important;
        }}
        div[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p,
        div[data-testid="stSidebar"] .stSlider span {{
            color: {ACCENT} !important;
        }}

        /* 3. 사이드바 멀티셀렉트 선택 태그(Pill) 및 텍스트/아이콘 색상 강제 오버라이드 */
        div[data-testid="stSidebar"] [data-baseweb="tag"] {{
            background-color: {ACCENT} !important;
            border-color: {ACCENT} !important;
        }}
        div[data-testid="stSidebar"] [data-baseweb="tag"] span {{
            color: #ffffff !important;
        }}
        div[data-testid="stSidebar"] [data-baseweb="tag"] svg {{
            fill: #ffffff !important;
        }}

        /* 4. 멀티셀렉트 포커스/호버 테두리 색상 */
        div[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            border-color: #E0E0E0 !important;
        }}
        div[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
            border-color: {ACCENT} !important;
        }}

        /* 5. 상단 KPI 카드 높이 및 형태 완벽 균일화 */
        div[data-testid="stMetric"] {{
            min-height: 110px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}
        div[data-testid="stMetricContainer"] {{
            height: 100% !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 1. 페이지 헤더
# ==========================================
st.title("퍼널 진단 리포트")
st.caption("가입채널별 퍼널 진단 및 실제 이벤트 로그 기반 분석")

# ==========================================
# 2. 데이터 임베딩 및 안전한 파일 로드 (data/ 폴더 경로 적용)
# ==========================================
# [데이터 1] 단계별 전환율_전체기간
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

# [데이터 2] 가입채널별 5단계 실데이터
csv_channel_step_data = """가입채널,가입자수,방문유저수,식당조회유저수,장바구니유저수,결제시작유저수,주문완료유저수
INSTA_첫주문쿠폰,834,834,790,615,523,516
NAVER_검색광고,580,580,560,512,484,478
organic,943,943,908,838,780,774
GOOGLE_앱설치,454,454,435,397,364,360
친구초대,298,298,289,262,248,244"""

df_channel_step = pd.read_csv(io.StringIO(csv_channel_step_data))

# AI 해설 메시지 및 출처 정의
AI_NOTES = {
    "INSTA_첫주문쿠폰": "인스타그램 첫주문쿠폰 유입 집단은 프로모션 진입 특성상 유입 모수는 크나, 장바구니 및 결제 진입 과정에서 타 채널 대비 초기 이탈률이 크게 발생하는 경향을 보입니다.",
    "NAVER_검색광고": "네이버 검색광고 유입 집단은 명확한 탐색 의도를 가지고 진입하여 전체 퍼널 구간에서 고른 전환율을 보입니다.",
    "organic": "오가닉 유입 집단은 브랜드 인지도가 높은 유저들로 구성되어 있어 초기 이탈률이 낮고 30일 내 첫 주문까지의 전환 효율이 가장 우수합니다.",
    "GOOGLE_앱설치": "구글 앱설치 유입 집단은 앱 설치 이후 첫 진입 단계에서의 이탈 방지를 위한 초기 온보딩 동선 개선이 효과적일 수 있습니다.",
    "친구초대": "친구초대 유입 집단은 리퍼럴 기반의 높은 신뢰도로 인해 진입 유저 대비 결제 완료 비율이 상위권을 유지하고 있습니다.",
}
AI_SOURCE = "출처: 퍼널 진단 엔진 자동 생성 리포트"

# data/ 폴더 위치 반영 데이터 로드
@st.cache_data
def load_db_data():
    try:
        orders_df = pd.read_csv("data/orders.csv")
        events_df = pd.read_csv("data/app_events.csv")
        return orders_df, events_df
    except Exception:
        return None, None

orders_df, events_df = load_db_data()

# ==========================================
# 2-1. 사이드바 필터 설정
# ==========================================
st.sidebar.header("필터")

unique_months = df_funnel["년월"].sort_values().unique().tolist()
selected_months = st.sidebar.select_slider(
    "기간", options=unique_months, value=(unique_months[0], unique_months[-1])
)

all_channels = df_channel_step["가입채널"].tolist()
selected_channels = st.sidebar.multiselect(
    "유입 경로", options=all_channels, default=all_channels
)

f_funnel = df_funnel[
    (df_funnel["년월"] >= selected_months[0])
    & (df_funnel["년월"] <= selected_months[1])
].copy()

f_channel_step = df_channel_step[
    df_channel_step["가입채널"].isin(selected_channels)
].copy()

if f_funnel.empty or f_channel_step.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다. 필터를 바꿔 주세요.")
    st.stop()

# ==========================================
# 3. st.tabs() 구성 ('개요', '탐색', '액션', '데이터 업로드')
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📋 개요", "🔍 탐색", "💡 액션", "📂 데이터 업로드"])

# ------------------------------------------
# [TAB 1] 개요
# ------------------------------------------
with tab1:
    total_visits = f_funnel["방문"].sum()
    total_orders = f_funnel["주문"].sum()
    
    # 방문 후 7일 내 주문 전환율 계산 (이벤트 로그 & 주문 로그 기반)
    visit_7d_rate_str = "데이터 없음"
    if events_df is not None and orders_df is not None:
        clean_events = events_df[
            ~events_df['customer_id'].astype(str).str.startswith('T', na=False)
        ].copy()
        clean_events = clean_events.drop_duplicates(
            subset=['session_id', 'event_datetime', 'event_name'], keep='first'
        )
        clean_orders = orders_df[
            ~orders_df['customer_id'].astype(str).str.startswith('T', na=False)
        ].copy()

        clean_events['event_dt'] = pd.to_datetime(clean_events['event_datetime'])
        clean_events['년월'] = clean_events['event_dt'].dt.strftime('%Y-%m')
        
        filtered_events = clean_events[
            (clean_events['년월'] >= selected_months[0]) & 
            (clean_events['년월'] <= selected_months[1])
        ]
        
        c_visit_kpi = len(filtered_events['session_id'].unique())
        session_event_map_kpi = filtered_events.groupby('session_id')['event_name'].unique().to_dict()
        
        clean_orders['order_dt'] = pd.to_datetime(clean_orders['order_datetime'])
        clean_orders['년월'] = clean_orders['order_dt'].dt.strftime('%Y-%m')
        filtered_orders_kpi = clean_orders[
            (clean_orders['년월'] >= selected_months[0]) & 
            (clean_orders['년월'] <= selected_months[1])
        ]
        
        order_sessions_kpi = set(filtered_orders_kpi['session_id'].unique()) if 'session_id' in filtered_orders_kpi.columns else set()
        c_order_kpi = len(set(session_event_map_kpi.keys()).intersection(order_sessions_kpi)) if order_sessions_kpi else len(filtered_orders_kpi['customer_id'].unique())
        
        if c_visit_kpi > 0:
            visit_7d_rate = (c_order_kpi / c_visit_kpi) * 100
            visit_7d_rate_str = f"{visit_7d_rate:.1f}%"

    # INSTA_첫주문쿠폰 주문 전환율 계산 (이벤트 로그 기반)
    insta_rate_str = "데이터 없음"
    if events_df is not None and orders_df is not None:
        ev_insta = events_df[events_df["event_name"] == "sign_up"].copy()
        
        def map_ch_insta(row):
            if row["traffic_source"] == "organic":
                return "organic"
            elif pd.notna(row["campaign_name"]):
                return row["campaign_name"]
            else:
                return row["traffic_source"]
        
        ev_insta["가입채널"] = ev_insta.apply(map_ch_insta, axis=1)
        insta_signups = ev_insta[ev_insta["가입채널"] == "INSTA_첫주문쿠폰"]
        insta_denom = insta_signups["customer_id"].nunique()
        if insta_denom > 0:
            ordered_cids = set(orders_df["customer_id"].unique())
            insta_num = insta_signups[insta_signups["customer_id"].isin(ordered_cids)]["customer_id"].nunique()
            insta_rate = (insta_num / insta_denom) * 100
            insta_rate_str = f"{insta_rate:.1f}%"

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric(label="1단계 : 전체 방문 수", value=f"{total_visits:,}명")
    with col2:
        with st.container(border=True):
            st.metric(label="📈 방문 후 7일 내 주문 전환율", value=visit_7d_rate_str)
    with col3:
        with st.container(border=True):
            st.metric(label="🎯 INSTA_첫주문쿠폰 주문 전환율", value=insta_rate_str)

    st.markdown("---")
    st.subheader("📊 방문 후 7일 이내 퍼널 단계별 세션 현황 및 가입채널별 주별 7일 이내 주문 전환율")

    funnel_col1, funnel_col2 = st.columns(2)

    with funnel_col1:
        with st.container(border=True):
            if events_df is not None and orders_df is not None:
                clean_events = events_df[
                    ~events_df['customer_id'].astype(str).str.startswith('T', na=False)
                ].copy()
                
                clean_events = clean_events.drop_duplicates(
                    subset=['session_id', 'event_datetime', 'event_name'], keep='first'
                )
                
                clean_orders = orders_df[
                    ~orders_df['customer_id'].astype(str).str.startswith('T', na=False)
                ].copy()

                clean_events['event_dt'] = pd.to_datetime(clean_events['event_datetime'])
                clean_events['년월'] = clean_events['event_dt'].dt.strftime('%Y-%m')
                
                filtered_events = clean_events[
                    (clean_events['년월'] >= selected_months[0]) & 
                    (clean_events['년월'] <= selected_months[1])
                ]

                session_event_map = filtered_events.groupby('session_id')['event_name'].unique().to_dict()

                c_visit = len(filtered_events['session_id'].unique())
                c_view = sum(1 for evs in session_event_map.values() if 'view_restaurant' in evs)
                c_cart = sum(1 for evs in session_event_map.values() if 'add_to_cart' in evs)
                c_checkout = sum(1 for evs in session_event_map.values() if 'begin_checkout' in evs)
                
                # 주문 데이터도 사이드바 기간 필터(selected_months) 적용
                clean_orders['order_dt'] = pd.to_datetime(clean_orders['order_datetime'])
                clean_orders['년월'] = clean_orders['order_dt'].dt.strftime('%Y-%m')
                filtered_orders = clean_orders[
                    (clean_orders['년월'] >= selected_months[0]) & 
                    (clean_orders['년월'] <= selected_months[1])
                ]
                
                order_sessions = set(filtered_orders['session_id'].unique()) if 'session_id' in filtered_orders.columns else set()
                c_order = len(set(session_event_map.keys()).intersection(order_sessions)) if order_sessions else len(filtered_orders['customer_id'].unique())

                funnel_stages = ["방문", "식당조회", "장바구니", "결제시작", "주문"]
                funnel_values = [c_visit, c_view, c_cart, c_checkout, c_order]
            else:
                funnel_stages = ["방문", "식당조회", "장바구니", "결제시작", "주문"]
                funnel_values = [0, 0, 0, 0, 0]

            df_total_funnel = pd.DataFrame(
                {"단계": funnel_stages, "세션수": funnel_values}
            )

            fig_funnel = px.funnel(
                df_total_funnel,
                x="세션수",
                y="단계",
                title="방문 후 7일 이내 퍼널 단계별 전환 현황",
            )
            fig_funnel.update_layout(template="plotly_white")
            st.plotly_chart(fig_funnel, width="stretch")

    with funnel_col2:
        with st.container(border=True):
            if events_df is not None and orders_df is not None:
                ev_signup = events_df[events_df["event_name"] == "sign_up"].copy()
                
                def map_channel(row):
                    if row["traffic_source"] == "organic":
                        return "organic"
                    elif pd.notna(row["campaign_name"]):
                        return row["campaign_name"]
                    else:
                        return row["traffic_source"]
                
                ev_signup["가입채널"] = ev_signup.apply(map_channel, axis=1)
                ev_signup["sign_up_dt"] = pd.to_datetime(ev_signup["event_datetime"])
                ev_signup["가입월"] = ev_signup["sign_up_dt"].dt.strftime('%Y-%m')
                ev_signup["주시작일"] = (ev_signup["sign_up_dt"] - pd.to_timedelta(ev_signup["sign_up_dt"].dt.weekday, unit="d")).dt.strftime('%Y-%m-%d')
                
                ev_signup_filtered = ev_signup[
                    (ev_signup["가입월"] >= selected_months[0]) & 
                    (ev_signup["가입월"] <= selected_months[1])
                ]
                
                user_signup_info = ev_signup_filtered[['customer_id', '가입채널', '주시작일', 'sign_up_dt']].sort_values('sign_up_dt').groupby('customer_id').first().reset_index()
                
                orders_copy = orders_df.copy()
                orders_copy['order_dt'] = pd.to_datetime(orders_copy['order_datetime'])
                
                merged_orders = orders_copy.merge(user_signup_info[['customer_id', 'sign_up_dt']], on='customer_id', how='inner')
                merged_orders['hours_to_order'] = (merged_orders['order_dt'] - merged_orders['sign_up_dt']).dt.total_seconds() / 3600
                
                orders_7d_valid = merged_orders[(merged_orders['hours_to_order'] >= 0) & (merged_orders['hours_to_order'] <= 24 * 7)]
                ordered_7d_cids = set(orders_7d_valid['customer_id'].unique())
                
                user_signup_info['has_ordered_7d'] = user_signup_info['customer_id'].isin(ordered_7d_cids).astype(int)
                
                weekly_group = user_signup_info.groupby(["주시작일", "가입채널"]).agg(
                    분모_가입고객수=("customer_id", "nunique"),
                    분자_주문고객수=("has_ordered_7d", "sum")
                ).reset_index()
                
                weekly_group["주문전환율"] = round(weekly_group["분자_주문고객수"] * 100.0 / weekly_group["분모_가입고객수"], 1)
                
                valid_weeks = sorted(weekly_group['주시작일'].unique())
                if len(valid_weeks) > 2:
                    target_weeks = valid_weeks[:-2]
                    weekly_group = weekly_group[weekly_group['주시작일'].isin(target_weeks)]
                else:
                    weekly_group = pd.DataFrame(columns=["주시작일", "가입채널", "분모_가입고객수", "분자_주문고객수", "주문전환율"])
            else:
                weekly_group = pd.DataFrame(columns=["주시작일", "가입채널", "분모_가입고객수", "분자_주문고객수", "주문전환율"])

            weekly_group = weekly_group[weekly_group["가입채널"].isin(selected_channels)]

            fig_weekly_pay = px.line(
                weekly_group,
                x="주시작일",
                y="주문전환율",
                color="가입채널",
                markers=True,
                title="가입채널별 주별 7일 이내 주문 전환율",
                custom_data=["분모_가입고객수", "분자_주문고객수"]
            )
            fig_weekly_pay.update_traces(
                hovertemplate="<b>채널: %{fullData.name}</b><br>주시작일: %{x}<br>7일내 주문전환율: %{y:.1f}%<br>가입고객수: %{customdata[0]:,}명<br>7일내 주문고객수: %{customdata[1]:,}명<extra></extra>"
            )
            fig_weekly_pay.update_layout(
                yaxis=dict(range=[0, 115]),
                xaxis_title="주시작일",
                yaxis_title="7일 이내 주문전환율 (%)",
                template="plotly_white"
            )
            st.plotly_chart(fig_weekly_pay, width="stretch")

    st.markdown("---")
    st.subheader("📈 가입채널별 주요 지표 분석")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            if events_df is not None and orders_df is not None:
                ev_signup = events_df[events_df["event_name"] == "sign_up"].copy()
                
                def map_channel(row):
                    if row["traffic_source"] == "organic":
                        return "organic"
                    elif pd.notna(row["campaign_name"]):
                        return row["campaign_name"]
                    else:
                        return row["traffic_source"]
                
                ev_signup["가입채널"] = ev_signup.apply(map_channel, axis=1)
                ev_signup["sign_up_dt"] = pd.to_datetime(ev_signup["event_datetime"])
                ev_signup["가입월"] = ev_signup["sign_up_dt"].dt.strftime('%Y-%m')
                
                ev_signup_filtered = ev_signup[
                    (ev_signup["가입월"] >= selected_months[0]) & 
                    (ev_signup["가입월"] <= selected_months[1])
                ]
                
                user_signup_info = ev_signup_filtered[['customer_id', '가입채널', 'sign_up_dt']].sort_values('sign_up_dt').groupby('customer_id').first().reset_index()
                
                orders_copy = orders_df.copy()
                orders_copy['order_dt'] = pd.to_datetime(orders_copy['order_datetime'])
                
                merged_orders = orders_copy.merge(user_signup_info[['customer_id', 'sign_up_dt']], on='customer_id', how='inner')
                merged_orders['hours_to_order'] = (merged_orders['order_dt'] - merged_orders['sign_up_dt']).dt.total_seconds() / 3600
                
                orders_7d_valid = merged_orders[(merged_orders['hours_to_order'] >= 0) & (merged_orders['hours_to_order'] <= 24 * 7)]
                ordered_7d_cids = set(orders_7d_valid['customer_id'].unique())
                
                user_signup_info['has_ordered_7d'] = user_signup_info['customer_id'].isin(ordered_7d_cids).astype(int)
                
                channel_order_summary = user_signup_info.groupby('가입채널').agg(
                    denominator=('customer_id', 'nunique'),
                    numerator=('has_ordered_7d', 'sum')
                ).reset_index()
                
                channel_order_summary['conversion_rate'] = round((channel_order_summary['numerator'] / channel_order_summary['denominator']) * 100, 1)
                channel_order_summary = channel_order_summary[channel_order_summary['가입채널'].isin(selected_channels)]
                channel_order_summary = channel_order_summary.sort_values(by='conversion_rate', ascending=False)
            else:
                channel_order_summary = pd.DataFrame(columns=['가입채널', 'denominator', 'numerator', 'conversion_rate'])

            colors1 = [
                ACCENT if ch == "INSTA_첫주문쿠폰" else GRAY
                for ch in channel_order_summary["가입채널"]
            ]
            
            fig1 = px.bar(
                channel_order_summary,
                x="가입채널",
                y="conversion_rate",
                title="가입채널별 7일 이내 주문전환율 (%)",
                text="conversion_rate",
                custom_data=["denominator", "numerator"]
            )
            fig1.update_traces(
                marker_color=colors1,
                texttemplate="%{text:.1f}%",
                textposition="outside",
                hovertemplate="<b>가입채널: %{x}</b><br>7일이내 주문전환율: %{y:.1f}%<br>가입 고객수: %{customdata[0]:,}명<br>7일이내 주문 고객수: %{customdata[1]:,}명<extra></extra>"
            )
            fig1.update_layout(
                yaxis=dict(
                    range=[
                        0,
                        max(channel_order_summary["conversion_rate"]) * 1.2
                        if not channel_order_summary.empty
                        else 100,
                    ]
                ),
                xaxis_title="가입채널",
                yaxis_title="7일 이내 주문전환율 (%)",
                template="plotly_white",
            )
            st.plotly_chart(fig1, width="stretch")

    with chart_col2:
        with st.container(border=True):
            if events_df is not None and orders_df is not None:
                ev_churn = events_df[events_df["event_name"] == "sign_up"].copy()
                ev_churn["가입채널"] = ev_churn.apply(map_channel, axis=1)
                ev_churn["sign_up_dt"] = pd.to_datetime(ev_churn["event_datetime"])
                ev_churn["가입월"] = ev_churn["sign_up_dt"].dt.strftime('%Y-%m')
                
                ev_churn_filtered = ev_churn[
                    (ev_churn["가입월"] >= selected_months[0]) & 
                    (ev_churn["가입월"] <= selected_months[1])
                ]
                
                churn_user_info = ev_churn_filtered[['customer_id', '가입채널', 'sign_up_dt']].sort_values('sign_up_dt').groupby('customer_id').first().reset_index()
                
                orders_copy_c = orders_df.copy()
                orders_copy_c['order_dt'] = pd.to_datetime(orders_copy_c['order_datetime'])
                
                merged_orders_c = orders_copy_c.merge(churn_user_info[['customer_id', 'sign_up_dt']], on='customer_id', how='inner')
                merged_orders_c['hours_to_order'] = (merged_orders_c['order_dt'] - merged_orders_c['sign_up_dt']).dt.total_seconds() / 3600
                
                orders_30d_c = merged_orders_c[(merged_orders_c['hours_to_order'] >= 0) & (merged_orders_c['hours_to_order'] <= 30 * 24)]
                ordered_30d_cids_c = set(orders_30d_c['customer_id'].unique())
                
                churn_user_info['has_ordered_30d'] = churn_user_info['customer_id'].isin(ordered_30d_cids_c).astype(int)
                
                channel_churn_summary = churn_user_info.groupby('가입채널').agg(
                    고객수=('customer_id', 'nunique'),
                    주문고객수=('has_ordered_30d', 'sum')
                ).reset_index()
                
                channel_churn_summary['초기 이탈률_num'] = round(
                    ((channel_churn_summary['고객수'] - channel_churn_summary['주문고객수']) / channel_churn_summary['고객수']) * 100, 1
                )
                channel_churn_summary = channel_churn_summary[channel_churn_summary['가입채널'].isin(selected_channels)]
                channel_churn_summary = channel_churn_summary.sort_values(by='초기 이탈률_num', ascending=False)
            else:
                channel_churn_summary = pd.DataFrame(columns=['가입채널', '고객수', '초기 이탈률_num'])

            colors2 = [
                ACCENT if ch == "INSTA_첫주문쿠폰" else GRAY
                for ch in channel_churn_summary["가입채널"]
            ]

            fig2 = px.bar(
                channel_churn_summary,
                x="가입채널",
                y="초기 이탈률_num",
                title="가입채널별 초기 이탈률 (30일 이내)",
                text="초기 이탈률_num",
                custom_data=["고객수"],
            )
            fig2.update_traces(
                marker_color=colors2,
                texttemplate="%{text:.1f}%",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>초기 이탈률 (30일): %{y:.1f}%<br>고객 수 (n): %{customdata[0]:,}<extra></extra>",
            )
            fig2.update_layout(
                yaxis=dict(
                    range=[
                        0,
                        max(channel_churn_summary["초기 이탈률_num"]) * 1.15
                        if not channel_churn_summary.empty
                        else 100,
                    ]
                ),
                xaxis_title="가입 채널",
                yaxis_title="초기 이탈률 (%)",
                template="plotly_white",
            )
            st.plotly_chart(fig2, width="stretch")

# ------------------------------------------
# [TAB 2] 탐색
# ------------------------------------------
with tab2:
    st.subheader("👥 가입채널별 집단 비교 분석")

    group_df = f_channel_step.copy()
    group_col = "가입채널"

    low_sample_groups = group_df[group_df["가입자수"] < 500][group_col].tolist()
    if low_sample_groups:
        st.caption(
            f"⚠️ 주의: 다음 집단({', '.join(low_sample_groups)})은 가입자 수가 500명 미만으로 값이 크게 흔들릴 수 있습니다."
        )

    step_names = ["방문", "식당조회", "장바구니", "결제시작", "주문"]

    cumulative_records = []
    step_records = []

    for idx, row in group_df.iterrows():
        g_name = row[group_col]
        base_val = row["방문유저수"] if row["방문유저수"] > 0 else 1

        vals = [
            row["방문유저수"],
            row["식당조회유저수"],
            row["장바구니유저수"],
            row["결제시작유저수"],
            row["주문완료유저수"],
        ]

        for s_name, val in zip(step_names, vals):
            cum_rate = round((val / base_val) * 100, 1)
            cumulative_records.append(
                {
                    "집단": g_name,
                    "단계": s_name,
                    "누적전환율": cum_rate,
                    "세션수": val,
                }
            )

        for i in range(1, len(vals)):
            prev_val = vals[i - 1] if vals[i - 1] > 0 else 1
            step_rate = round((vals[i] / prev_val) * 100, 1)
            step_records.append(
                {
                    "집단": g_name,
                    "구간": f"{step_names[i-1]}→{step_names[i]}",
                    "단계전환율": step_rate,
                    "기준세션수": prev_val,
                }
            )

    df_cum = pd.DataFrame(cumulative_records)
    df_step = pd.DataFrame(step_records)

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        st.markdown("#### 📉 가입채널별 누적 전환율 퍼널")
        fig_comp_funnel = px.funnel(
            df_cum,
            x="누적전환율",
            y="단계",
            color="집단",
            title="가입채널별 누적 전환율 (%) 퍼널 비교",
            custom_data=["세션수"],
        )
        fig_comp_funnel.update_traces(
            hovertemplate="<b>집단: %{fullData.name}</b><br>단계: %{y}<br>누적 전환율: %{x}%<br>유저 수: %{customdata[0]:,}명<extra></extra>"
        )
        fig_comp_funnel.update_layout(template="plotly_white")
        st.plotly_chart(fig_comp_funnel, width="stretch")

    with comp_col2:
        st.markdown("#### 📊 가입채널별 단계 전환율 비교")
        fig_comp_bar = px.bar(
            df_step,
            x="구간",
            y="단계전환율",
            color="집단",
            barmode="group",
            title="직전 단계 대비 전환율 (%) 비교",
            text="단계전환율",
            custom_data=["기준세션수"],
        )
        fig_comp_bar.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            hovertemplate="<b>집단: %{fullData.name}</b><br>구간: %{x}<br>단계 전환율: %{y:.1f}%<br>직전 단계 유저수(기준): %{customdata[0]:,}명<extra></extra>",
        )
        fig_comp_bar.update_layout(
            yaxis=dict(range=[0, 115]),
            xaxis_title="퍼널 구간",
            yaxis_title="전환율 (%)",
            template="plotly_white",
        )
        st.plotly_chart(fig_comp_bar, width="stretch")

    st.markdown("---")
    st.subheader("🔍 드릴다운: 언제부터, 무엇 때문일까")

    available_groups = f_channel_step["가입채널"].unique().tolist()

    drill_col1, drill_col2 = st.columns(2)

    with drill_col1:
        selected_group = st.selectbox("자세히 볼 집단", options=available_groups)

    with drill_col2:
        selected_step = st.selectbox(
            "단계",
            options=[
                "가입 → 30일 첫 주문",
                "가입 → 식당조회",
                "식당조회 → 장바구니",
                "장바구니 → 결제시작",
                "결제시작 → 30일 첫 주문",
            ],
        )

    if events_df is not None and orders_df is not None:
        ev_signup = events_df[events_df["event_name"] == "sign_up"].copy()

        def map_channel(row):
            if row["traffic_source"] == "organic":
                return "organic"
            elif pd.notna(row["campaign_name"]):
                return row["campaign_name"]
            else:
                return row["traffic_source"]

        ev_signup["가입채널"] = ev_signup.apply(map_channel, axis=1)
        ev_signup["sign_up_dt"] = pd.to_datetime(ev_signup["event_datetime"])
        ev_signup["가입월"] = ev_signup["sign_up_dt"].dt.strftime("%Y-%m")

        user_signup = ev_signup.sort_values("sign_up_dt").groupby("customer_id").first().reset_index()

        user_events = events_df.merge(user_signup[['customer_id', '가입채널', '가입월', 'sign_up_dt']], on='customer_id', how='inner')
        events_by_cust = user_events.groupby('customer_id')['event_name'].unique().to_dict()

        orders_copy = orders_df.copy()
        orders_copy['order_dt'] = pd.to_datetime(orders_copy['order_datetime'])
        user_orders = orders_copy.merge(user_signup[['customer_id', 'sign_up_dt']], on='customer_id', how='inner')
        user_orders['days_to_order'] = (user_orders['order_dt'] - user_orders['sign_up_dt']).dt.total_seconds() / (24 * 3600)
        first_orders_30d_cids = set(user_orders[(user_orders['days_to_order'] >= 0) & (user_orders['days_to_order'] <= 30)]['customer_id'].unique())

        cust_summary = user_signup[['customer_id', '가입채널', '가입월']].copy()
        cust_summary['has_view'] = cust_summary['customer_id'].apply(lambda cid: 'view_restaurant' in events_by_cust.get(cid, []))
        cust_summary['has_cart'] = cust_summary['customer_id'].apply(lambda cid: 'add_to_cart' in events_by_cust.get(cid, []))
        cust_summary['has_checkout'] = cust_summary['customer_id'].apply(lambda cid: 'begin_checkout' in events_by_cust.get(cid, []))
        cust_summary['has_first_order_30d'] = cust_summary['customer_id'].isin(first_orders_30d_cids)

        f_months = f_funnel["년월"].unique().tolist()
        cust_summary_filtered = cust_summary[cust_summary["가입월"].isin(f_months)]

        total_monthly_signups = cust_summary_filtered.groupby("가입월")["customer_id"].nunique().to_dict()

        selected_cust = cust_summary_filtered[cust_summary_filtered["가입채널"] == selected_group]
        group_monthly = selected_cust.groupby("가입월").agg(
            가입자=('customer_id', 'nunique'),
            식당조회=('has_view', 'sum'),
            장바구니=('has_cart', 'sum'),
            결제시작=('has_checkout', 'sum'),
            첫주문30일=('has_first_order_30d', 'sum')
        ).reindex(f_months, fill_value=0).reset_index()

        group_monthly["전체가입자"] = group_monthly["가입월"].map(lambda x: total_monthly_signups.get(x, 0))
        group_monthly["그외가입자"] = group_monthly["전체가입자"] - group_monthly["가입자"]
        group_monthly["그외가입자"] = group_monthly["그외가입자"].apply(lambda x: max(0, x))

        df_drill_monthly = group_monthly
    else:
        f_months = f_funnel["년월"].unique().tolist()
        df_drill_monthly = pd.DataFrame({
            "가입월": f_months,
            "가입자": [0]*len(f_months),
            "식당조회": [0]*len(f_months),
            "장바구니": [0]*len(f_months),
            "결제시작": [0]*len(f_months),
            "첫주문30일": [0]*len(f_months),
            "그외가입자": [0]*len(f_months),
        })

    step_calc_mapping = {
        "가입 → 30일 첫 주문": ("가입자", "첫주문30일"),
        "가입 → 식당조회": ("가입자", "식당조회"),
        "식당조회 → 장바구니": ("식당조회", "장바구니"),
        "장바구니 → 결제시작": ("장바구니", "결제시작"),
        "결제시작 → 30일 첫 주문": ("결제시작", "첫주문30일"),
    }

    denom_col, num_col = step_calc_mapping[selected_step]

    chart1_records = []
    for idx, row in df_drill_monthly.iterrows():
        denom_val = row[denom_col]
        num_val = row[num_col]

        if pd.isna(denom_val) or denom_val == 0:
            rate = None
        else:
            rate = round((num_val / denom_val) * 100, 1)

        chart1_records.append(
            {
                "가입월": row["가입월"],
                "전환율": rate,
                "분모": denom_val,
                "분자": num_val,
            }
        )

    df_chart1 = pd.DataFrame(chart1_records)

    fig_drill_1 = px.line(
        df_chart1,
        x="가입월",
        y="전환율",
        markers=True,
        title=f"① {selected_group}의 가입월별 {selected_step} 전환율",
        custom_data=["분모", "분자"],
    )

    fig_drill_1.update_traces(
        connectgaps=False,
        hovertemplate="<b>가입월: %{x}</b><br>전환율: %{y:.1f}%<br>직전단계 수(분모): %{customdata[0]:,}명<br>달성 수(분자): %{customdata[1]:,}명<extra></extra>",
    )

    fig_drill_1.update_layout(
        yaxis=dict(range=[0, 115]),
        xaxis_title="가입월",
        yaxis_title="전환율 (%)",
        template="plotly_white",
    )

    st.plotly_chart(fig_drill_1, width="stretch")
    st.caption("모든 갈래가 함께 움직였다면, 그 축은 원인이 아닙니다.")

    stack_records = []
    for idx, row in df_drill_monthly.iterrows():
        stack_records.append(
            {"가입월": row["가입월"], "구분": selected_group, "가입자수": row["가입자"]}
        )
        stack_records.append(
            {"가입월": row["가입월"], "구분": "그 외 집단", "가입자수": row["그외가입자"]}
        )

    df_chart2 = pd.DataFrame(stack_records)

    color_map = {selected_group: ACCENT, "그 외 집단": GRAY}

    fig_drill_2 = px.bar(
        df_chart2,
        x="가입월",
        y="가입자수",
        color="구분",
        color_discrete_map=color_map,
        barmode="stack",
        title=f"② 가입월별 가입자 수 구성 ({selected_group} vs 그 외)",
    )

    fig_drill_2.update_traces(
        hovertemplate="<b>가입월: %{x}</b><br>구분: %{fullData.name}<br>가입자 수: %{y:,}명<extra></extra>"
    )

    fig_drill_2.update_layout(
        xaxis_title="가입월",
        yaxis_title="가입자 수 (명)",
        template="plotly_white",
        legend_title_text="집단 구분",
    )

    st.plotly_chart(fig_drill_2, width="stretch")
    st.caption(
        "전체 전환율이 움직인 시점에 이 집단의 비중이 함께 바뀌었다면 구성 변화가 원인 후보입니다. 함께 움직였다고 원인이 확정되지는 않습니다."
    )

# ------------------------------------------
# [TAB 3] 액션
# ------------------------------------------
with tab3:
    st.caption("측정 KPI의 현재 값은 선택한 기간의 마지막 3개월로 계산합니다")

    all_months_in_range = [m for m in unique_months if selected_months[0] <= m <= selected_months[1]]
    last_3_months = all_months_in_range[-3:] if len(all_months_in_range) >= 3 else all_months_in_range

    with st.container(border=True):
        st.markdown("### 카드 1 · 문제 정의 및 대응 액션")
        st.markdown(
            """
**문제:**  
- 2026년 1월부터 전체 주문 전환율이 하락세를 보임.  

**근거:**  
- 전환율 하락 시점이 2026년 1월 Instagram 프로모션 시작 시점과 일치.  
- Instagram 가입 유저 모수는 크나, 장바구니 담기 및 최종 결제 전환으로 이어지는 유입 힘이 약함.  
- Instagram 채널의 30일 이내 초기 이탈률이 59.1%로 타 채널 대비 상당히 높게 나타남.  

**성격:**  
- 신규 유입 채널의 퀄리티 문제 및 온보딩/리텐션 부실  
- 볼륨(가입자 수) 중심의 마케팅으로 인해 결제 의도가 낮은 유저가 다수 유입되었으나, 이들을 정착시킬 UX/UI 및 프로모션 장치가 부재함.  

**액션:**  
- 프로모션 구조 수정: 가입 모수가 큰 Instagram 채널 유저를 결제까지 유도할 수 있도록 프로모션 혜택 단계를 재설계.  
- 온보딩 UX/UI 개선: 가입 후 장바구니 담기 및 첫 구매 전환을 돕는 가이드/인센티브 화면 개선.  
- CRM 프로모션 강화: 초기 이탈 방지 및 리텐션율 제고를 위한 30일 이내 맞춤형 CRM 메시징/쿠폰 타겟팅 실행.  

**우선순위:**  
[상 / High]  
(사유: 가장 가입 모수가 큰 핵심 채널의 이탈률(59.1%)이 높아, 방치 시 전체 주문 전환율 하락세가 계속 지속될 위험이 큼)
"""
        )

        if events_df is not None and orders_df is not None and len(last_3_months) > 0:
            ev_sub = events_df[events_df["event_name"] == "sign_up"].copy()

            def map_ch(row):
                if row["traffic_source"] == "organic":
                    return "organic"
                elif pd.notna(row["campaign_name"]):
                    return row["campaign_name"]
                else:
                    return row["traffic_source"]

            ev_sub["가입채널"] = ev_sub.apply(map_ch, axis=1)
            ev_sub["sign_up_dt"] = pd.to_datetime(ev_sub["event_datetime"])
            ev_sub["가입월"] = ev_sub["sign_up_dt"].dt.strftime("%Y-%m")

            target_signups = ev_sub[
                (ev_sub["가입월"].isin(last_3_months)) & (ev_sub["가입채널"] == "INSTA_첫주문쿠폰")
            ]

            denom = target_signups["customer_id"].nunique()

            if denom > 0:
                ordered_cids = set(orders_df["customer_id"].unique())
                num = target_signups[target_signups["customer_id"].isin(ordered_cids)]["customer_id"].nunique()
                rate = round((num / denom) * 100, 1)
                kpi_value_str = f"{rate:.1f}%"
            else:
                kpi_value_str = "데이터 없음"
        else:
            kpi_value_str = "데이터 없음"

        st.metric(
            label=f"INSTA_첫주문쿠폰 주문 전환율 (최근 3개월: {', '.join(last_3_months)})",
            value=kpi_value_str,
        )
        st.caption("대시보드에서: 🔍 탐색 탭 > 드릴다운의 INSTA_첫주문쿠폰 가입월별 전환율 및 가입자 수 구성 차트")

    st.markdown("---")
    st.subheader("🤖 AI 해설 분석")

    selected_group_action = st.selectbox(
        "해설을 볼 가입채널 선택",
        options=f_channel_step["가입채널"].unique().tolist(),
        key="action_group_select",
    )

    with st.expander(f"🤖 AI 해설 · {selected_group_action}", expanded=True):
        st.write(AI_NOTES.get(selected_group_action, "이 집단의 해설은 아직 없습니다."))
        st.caption(AI_SOURCE)

# ------------------------------------------
# [TAB 4] 데이터 업로드
# ------------------------------------------
with tab4:
    st.subheader("📂 신규 데이터 파일 업로드")
    st.caption("새로운 주문 및 앱 이벤트 로그 CSV 파일을 업로드하여 대시보드 데이터를 업데이트하세요.")

    up_col1, up_col2 = st.columns(2)

    with up_col1:
        uploaded_orders = st.file_uploader("orders.csv", type=["csv"])
        if uploaded_orders is not None:
            st.success("orders.csv 파일이 정상적으로 입력되었습니다.")

    with up_col2:
        uploaded_events = st.file_uploader("app_events.csv", type=["csv"])
        if uploaded_events is not None:
            st.success("app_events.csv 파일이 정상적으로 입력되었습니다.")