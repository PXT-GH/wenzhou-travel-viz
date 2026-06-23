"""
基于Streamlit的温州旅游数据可视化交互式Web应用
深蓝色未来感主题 + 景点故事传说 + 酒店价格对比
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os, sys, warnings
from datetime import datetime

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis import *
from realtime_engine import get_weather, get_congestion, get_hotel_prices
from content_data import get_attraction_detail, get_hotel_detail
from trip_planner import plan_trip

st.set_page_config(page_title="温州智旅 — 未来旅游数据平台", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")

# ==================== 深蓝色未来感主题 CSS ====================
st.markdown("""
<style>
    /* ===== 全局根元素 ===== */
    html, body, .stApp, .main, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #12163a 30%, #1a1f4e 60%, #0d1530 100%) !important;
        color: #e0e0e0 !important;
    }

    /* ===== 主内容容器 ===== */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        background: transparent !important;
    }
    section[data-testid="stSidebar"] + .main .block-container {
        background: transparent !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
    }

    /* ===== 所有文字强制深色模式 ===== */
    p, li, span, div, label, .stMarkdown, .stText, .st-bd, .st-c0, .st-c1, .st-c2, .st-c3, .st-c4 {
        color: #e0e0e0 !important;
    }
    p { color: rgba(230, 230, 250, 0.9) !important; line-height: 1.7; }

    /* ===== 指标卡片 — 霓虹光效 ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%) !important;
        border: 1px solid rgba(102,126,234,0.3) !important;
        padding: 1rem 1.2rem !important;
        border-radius: 0.8rem !important;
        box-shadow: 0 0 20px rgba(102,126,234,0.1), inset 0 0 15px rgba(102,126,234,0.05) !important;
        backdrop-filter: blur(10px) !important;
    }
    [data-testid="stMetric"] label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.85rem !important;
        font-weight: normal !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 1.6rem !important;
        font-weight: bold !important;
        text-shadow: 0 0 10px rgba(0,212,255,0.3);
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: rgba(0,212,255,0.8) !important;
    }

    /* ===== 侧边栏 ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(8,12,35,0.98) 0%, rgba(14,18,50,0.98) 50%, rgba(10,16,38,0.98) 100%) !important;
        border-right: 1px solid rgba(102,126,234,0.15) !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: rgba(220, 220, 250, 0.85) !important;
        font-size: 0.95rem !important;
        padding: 0.3rem 0.5rem !important;
        border-radius: 6px !important;
        transition: all 0.3s !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #00d4ff !important;
        background: rgba(0,212,255,0.08) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] h1 {
        color: #00d4ff !important;
        text-shadow: 0 0 20px rgba(0,212,255,0.2);
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] p {
        color: rgba(180,180,220,0.6) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(102,126,234,0.15) !important;
    }

    /* ===== 下拉框 / 滑块 / 选择器等控件 ===== */
    .stSelectbox label, .stSlider label, .stMultiSelect label {
        color: rgba(220,220,250,0.8) !important;
        font-weight: 500 !important;
    }
    /* 下拉框主输入区 */
    .stSelectbox > div > div, .stMultiSelect > div > div {
        background: rgba(20, 25, 60, 0.9) !important;
        border-color: rgba(102,126,234,0.35) !important;
        color: #e0e0f0 !important;
        border-radius: 8px !important;
    }
    /* 下拉框选中文本 */
    .stSelectbox > div > div > div, .stMultiSelect > div > div > div {
        color: #e0e0f0 !important;
    }
    .stSelectbox > div > div:hover, .stMultiSelect > div > div:hover {
        border-color: rgba(0,212,255,0.5) !important;
    }
    /* 下拉框下拉菜单 */
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
        background: rgba(15, 20, 50, 0.98) !important;
        border: 1px solid rgba(102,126,234,0.3) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="popover"] li, div[data-baseweb="menu"] li {
        color: #e0e0f0 !important;
        background: transparent !important;
    }
    div[data-baseweb="popover"] li:hover, div[data-baseweb="menu"] li:hover {
        background: rgba(102,126,234,0.2) !important;
        color: #00d4ff !important;
    }
    div[data-baseweb="popover"] li[aria-selected="true"], div[data-baseweb="menu"] li[aria-selected="true"] {
        background: rgba(102,126,234,0.3) !important;
        color: #00d4ff !important;
    }
    /* 多选标签 */
    .stMultiSelect [data-baseweb="tag"] {
        background: rgba(102,126,234,0.25) !important;
        color: #e0e0f0 !important;
        border-radius: 4px !important;
    }
    .stMultiSelect [data-baseweb="tag"] span {
        color: #e0e0f0 !important;
    }
    .stMultiSelect [data-baseweb="tag"] svg {
        fill: #e0e0f0 !important;
    }
    /* 下拉框箭头 */
    .stSelectbox svg, .stMultiSelect svg {
        fill: rgba(200, 200, 230, 0.6) !important;
    }
    .st-bb, .st-bc, .st-bd, .st-be, .st-bf, .st-bg {
        background: rgba(20, 25, 60, 0.9) !important;
        border-color: rgba(102,126,234,0.25) !important;
        color: #e0e0f0 !important;
    }
    .stSlider > div > div {
        color: #00d4ff !important;
    }
    div[data-baseweb="select"] > div {
        background: rgba(20, 25, 60, 0.9) !important;
        border-color: rgba(102,126,234,0.25) !important;
    }
    /* 数字输入框 */
    .stNumberInput input {
        background: rgba(20, 25, 60, 0.9) !important;
        color: #e0e0f0 !important;
        border-color: rgba(102,126,234,0.25) !important;
    }

    /* ===== 选项卡 ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(102,126,234,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px;
        border-radius: 8px;
        color: rgba(200,200,230,0.7) !important;
        background: transparent;
        transition: all 0.3s;
        font-weight: 500;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }

    /* ===== 标题 ===== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif !important;
        color: #f0f0ff !important;
    }
    h1 {
        font-size: 2rem !important;
        background: linear-gradient(90deg, #00d4ff, #667eea, #764ba2) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 0.5rem !important;
    }
    h2 {
        border-bottom: 1px solid rgba(102,126,234,0.2);
        padding-bottom: 0.5rem;
        color: #c0c0f0 !important;
        font-size: 1.4rem !important;
    }
    h3 { color: #b0b0e8 !important; font-size: 1.2rem !important; }
    h4 { color: #a0a0e0 !important; }

    /* ===== 提示框 ===== */
    .stAlert > div {
        border-radius: 0.6rem !important;
        background: rgba(102,126,234,0.12) !important;
        border: 1px solid rgba(102,126,234,0.2) !important;
        color: #d0d0f0 !important;
    }
    .stAlert p { color: #d0d0f0 !important; }

    /* ===== Dataframe ===== */
    .dataframe, [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.03) !important;
        color: #e0e0e0 !important;
    }
    .dataframe th, [data-testid="stDataFrame"] th {
        background: rgba(102,126,234,0.2) !important;
        color: #00d4ff !important;
    }
    .dataframe td, [data-testid="stDataFrame"] td {
        color: #d0d0e8 !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* ===== 按钮 ===== */
    .stButton > button {
        background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2)) !important;
        border: 1px solid rgba(102,126,234,0.3) !important;
        color: #e0e0f0 !important;
        border-radius: 8px !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }

    /* ===== radio 按钮 ===== */
    .stRadio > div {
        background: transparent !important;
    }
    .stRadio > div > label {
        color: #c0c0e0 !important;
    }
    div[role="radiogroup"] > label {
        color: #c0c0e0 !important;
        background: rgba(255,255,255,0.03) !important;
        border-radius: 6px !important;
        padding: 0.3rem 0.8rem !important;
    }

    /* ===== 自定义组件 ===== */
    .cyber-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.08)) !important;
        border: 1px solid rgba(102,126,234,0.2) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        margin: 0.5rem 0 !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s !important;
        color: #e0e0f0 !important;
    }
    .cyber-card:hover {
        border-color: rgba(0,212,255,0.4) !important;
        box-shadow: 0 0 25px rgba(0,212,255,0.1) !important;
        transform: translateY(-2px);
    }
    .cyber-card p { color: rgba(220, 220, 250, 0.85) !important; }
    .cyber-card h4 { color: #b0b0ff !important; }

    .legend-box {
        background: rgba(0,0,0,0.3) !important;
        border-left: 3px solid #00d4ff !important;
        padding: 1rem 1.2rem !important;
        border-radius: 0 8px 8px 0 !important;
        margin: 0.8rem 0 !important;
        color: #d0d0f0 !important;
    }
    .legend-box p { color: #d0d0f0 !important; }

    .price-tag {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        padding: 0.2rem 0.6rem !important;
        border-radius: 1rem !important;
        font-size: 0.8rem !important;
        color: white !important;
        font-weight: bold !important;
        display: inline-block !important;
        margin: 0.1rem !important;
    }

    /* ===== expander ===== */
    .streamlit-expanderHeader {
        color: #c0c0f0 !important;
        background: rgba(102,126,234,0.08) !important;
        border-radius: 8px !important;
    }
    .streamlit-expanderContent {
        border: none !important;
        background: transparent !important;
    }

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(10,14,39,0.5); }
    ::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(102,126,234,0.5); }

    /* ===== info 提示框 ===== */
    .stInfo { background: rgba(102,126,234,0.1) !important; }
    .stInfo p { color: #c0c0f0 !important; }

    /* ===== caption ===== */
    .stCaption, caption, .caption {
        color: rgba(180,180,220,0.6) !important;
    }
    /* ===== 动画效果 ===== */
    /* 平滑缓动曲线 — 更自然的加减速 */
    :root {
        --ease-natural: cubic-bezier(0.25, 0.46, 0.45, 0.94);
        --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
        --ease-fade: cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(24px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    @keyframes glowPulse {
        0% { box-shadow: 0 0 3px rgba(0,212,255,0.08); }
        50% { box-shadow: 0 0 18px rgba(0,212,255,0.15); }
        100% { box-shadow: 0 0 3px rgba(0,212,255,0.08); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    @keyframes breathe {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }

    /* 页面整体淡入 */
    .main .block-container {
        animation: fadeIn 0.4s var(--ease-fade) !important;
    }

    /* cyber-card 自然上浮 — 不强制每张卡都动画，保留transition */
    .cyber-card {
        transition: all 0.45s var(--ease-natural) !important;
        will-change: transform, opacity !important;
    }
    .cyber-card:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(0,212,255,0.35) !important;
        box-shadow: 0 8px 30px rgba(0,212,255,0.08) !important;
    }

    /* 指标卡片 — 柔和光晕 */
    [data-testid="stMetric"] {
        transition: all 0.5s var(--ease-natural) !important;
        will-change: box-shadow !important;
        animation: glowPulse 4s var(--ease-fade) infinite !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.15) !important;
    }

    /* 图例框左滑 */
    .legend-box {
        animation: fadeIn 0.5s var(--ease-fade) !important;
    }

    /* 天气图标浮动 */
    .weather-icon {
        animation: float 4s var(--ease-natural) infinite !important;
    }

    /* h1 标题淡入 */
    h1 {
        animation: fadeIn 0.5s var(--ease-fade) !important;
    }

    /* 按钮 — 弹性反馈 */
    .stButton > button {
        transition: all 0.3s var(--ease-spring) !important;
        will-change: transform !important;
    }
    .stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 0 25px rgba(102,126,234,0.25) !important;
    }
    .stButton > button:active {
        transform: scale(0.97) !important;
    }

    /* 侧边栏导航 — 柔和高亮 */
    section[data-testid="stSidebar"] .stRadio label {
        transition: all 0.35s var(--ease-natural) !important;
        position: relative !important;
        padding-left: 0.8rem !important;
    }
    section[data-testid="stSidebar"] .stRadio label::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 0;
        background: #00d4ff;
        border-radius: 2px;
        transition: height 0.4s var(--ease-natural);
    }
    section[data-testid="stSidebar"] .stRadio label:hover::before,
    section[data-testid="stSidebar"] .stRadio label[data-selected="true"]::before {
        height: 60%;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #00d4ff !important;
        background: rgba(0,212,255,0.05) !important;
        border-radius: 4px !important;
    }

    /* 列容器 — 依次自然淡入 */
    div[data-testid="column"] {
        animation: fadeIn 0.5s var(--ease-fade) both !important;
    }

    /* 选项卡 — 平滑切换 */
    .stTabs [data-baseweb="tab"] {
        transition: all 0.3s var(--ease-natural) !important;
    }
    .stTabs [aria-selected="true"] {
        transition: all 0.3s var(--ease-spring) !important;
    }

    /* 下拉框 — 柔和展开 */
    div[data-baseweb="select"] > div {
        transition: border-color 0.3s var(--ease-natural) !important;
    }

    /* 滑块 */
    .stSlider > div > div {
        transition: all 0.25s var(--ease-natural) !important;
    }

    /* 页面切换时的全局过渡 */
    .stApp {
        transition: background 0.6s var(--ease-fade) !important;
    }

    /* 信息提示框 */
    .stAlert > div {
        transition: all 0.4s var(--ease-natural) !important;
    }

    /* ===== 代码块（行程导出） ===== */
    .stCodeBlock, .stCodeBlock pre, code, .stCode {
        background: rgba(10, 14, 39, 0.95) !important;
        color: #e0e0f0 !important;
        border: 1px solid rgba(102,126,234,0.2) !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        line-height: 1.6 !important;
    }
    .stCodeBlock code {
        color: #e0e0f0 !important;
        background: transparent !important;
    }
    /* 代码块内部文字强制可见 */
    .stCodeBlock pre * {
        color: #e0e0f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== 加载数据 ==========
def dark_fig(fig, height=None):
    """为图表应用深色主题并返回"""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei", size=13, color="#f0f0ff"),
        title_font=dict(color="#f0f0ff"),
        legend_font=dict(color="#d0d0f0"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", title_font=dict(color="#d0d0f0"), tickfont=dict(color="#d0d0f0")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", title_font=dict(color="#d0d0f0"), tickfont=dict(color="#d0d0f0")),
    )
    if height:
        fig.update_layout(height=height)
    return fig

@st.cache_data
def load_all_data():
    """加载所有预处理数据并缓存"""
    return load_data()

@st.cache_data(ttl=1800)
def get_today_weather():
    """获取今日天气（缓存30分钟）"""
    return get_weather()

@st.cache_data(ttl=300)
def get_today_congestion():
    """获取今日拥挤度（缓存5分钟）"""
    attractions, _, _, _, _, _, _, _ = load_all_data()
    weather = get_today_weather()
    return get_congestion(attractions)

@st.cache_data(ttl=300)
def get_today_hotel_prices():
    """获取今日酒店价格（缓存5分钟）"""
    _, hotels, _, _, _, _, _, _ = load_all_data()
    weather = get_today_weather()
    return get_hotel_prices(hotels)

attractions, hotels, food, transport, links, weather, district_summary, routes = load_all_data()
today_weather = get_today_weather()

# ========== 侧边栏 ==========
st.sidebar.markdown("<h1 style='text-align:center;'>🌐 温州智旅</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align:center;font-size:0.85rem;'>未来旅游数据平台 v2.0</p>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color:rgba(102,126,234,0.2);'>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "**导航菜单**",
    [
        "📊 数据总览",
        "🌤️ 今日出行指南",
        "🤖 智能行程规划",
        "🏞️ 景点探索",
        "🏨 酒店性价比",
        "🔗 游住联动推荐",
        "🗺️ 路线规划",
        "📅 最佳旅行时间",
        "🍜 美食推荐"
    ]
)

st.sidebar.markdown("<hr style='border-color:rgba(102,126,234,0.2);'>", unsafe_allow_html=True)

# 侧边栏底部天气
st.sidebar.markdown(f"""
<div style='text-align:center;font-size:0.8rem;padding:0.5rem;background:rgba(102,126,234,0.1);border-radius:8px;'>
    <div style='color:#00d4ff;'>🌤️ 温州实时</div>
    <div style='color:rgba(255,255,255,0.7);'>{today_weather.get('condition','N/A')} {today_weather.get('temp','N/A')}°C</div>
</div>
""", unsafe_allow_html=True)


# ==================== 页面功能 ====================

def show_detail_page(selected_attraction):
    """显示景点详情页（传说、故事、详细介绍）"""
    attr = attractions[attractions["name"] == selected_attraction].iloc[0]
    detail = get_attraction_detail(selected_attraction)
    
    st.markdown(f"<h1>{attr['type'][:2]} {selected_attraction}</h1>", unsafe_allow_html=True)
    
    # 顶部指标行
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("评分", f"{'⭐' * int(attr['rating'])} {attr['rating']}")
    col2.metric("评论数", f"{attr['reviews']:,d}")
    col3.metric("门票", f"{'免费' if attr['ticket_price']==0 else '¥'+str(int(attr['ticket_price']))}")
    col4.metric("建议游玩", f"{attr['visit_hours']}小时")
    
    # 主内容区：图片占位 + 详细介绍
    col1, col2 = st.columns([2, 1.5])
    
    with col1:
        st.markdown(f"""
        <div class="cyber-card">
            <h3 style="margin-top:0;">🏔️ 景观介绍</h3>
            <p style="line-height:1.8;">{detail['highlights_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 传说故事用折叠卡片展示
        with st.expander("📜 传说故事", expanded=True):
            for i, legend in enumerate(detail['legends'], 1):
                st.markdown(f"""
                <div class="legend-box">
                    <strong style="color:#00d4ff;">📖 传说 {i}</strong>
                    <p style="margin-top:0.5rem;line-height:1.7;">{legend}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="cyber-card">
            <h4>📋 实用信息</h4>
            <p>🎯 <strong>最佳时间：</strong>{detail['best_time_desc']}</p>
            <p>🍽️ <strong>附近美食：</strong>{detail['food_nearby']}</p>
            <p>💡 <strong>门票提示：</strong>{detail['ticket_tip']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 景区内游览路线
        routes_internal = detail.get("internal_routes", [])
        if routes_internal:
            st.markdown("""
            <div class="cyber-card">
                <h4>🗺️ 景区内推荐游览路线</h4>
            </div>
            """, unsafe_allow_html=True)
            for i, route in enumerate(routes_internal):
                colors = ["#00d4ff", "#667eea", "#764ba2", "#fd79a8", "#00b894"]
                c = colors[i % len(colors)]
                st.markdown(f"""
                <div style="display:flex;align-items:stretch;margin:0.6rem 0;gap:0;">
                    <div style="min-width:40px;background:{c};border-radius:8px 0 0 8px;
                                display:flex;align-items:center;justify-content:center;
                                font-weight:bold;color:white;font-size:0.9rem;">
                        {i+1}
                    </div>
                    <div style="flex:1;background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;
                                padding:0.7rem 1rem;border:1px solid rgba(255,255,255,0.05);">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <strong style="color:{c};">{route['title']}</strong>
                            <span style="font-size:0.8rem;color:rgba(255,255,255,0.4);">⏱ {route['duration']}</span>
                        </div>
                        <div style="font-size:0.85rem;color:rgba(255,255,255,0.5);margin:0.2rem 0;">
                            📍 {route['spots']}
                        </div>
                        <div style="font-size:0.85rem;color:rgba(255,255,255,0.7);line-height:1.5;">
                            {route['desc']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # 图片卡片 - 渐变背景模拟景区图
        grad = detail.get("image_gradient", ["#1a1a2e", "#16213e"])
        icon = detail.get("image_icon", "🏔️")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, {grad[0]}, {grad[1]});
                    border-radius:12px;padding:2rem 1.5rem;text-align:center;
                    box-shadow:0 8px 32px rgba(0,0,0,0.3);margin-bottom:1rem;">
            <div style="font-size:5rem;line-height:1;margin-bottom:0.5rem;">{icon}</div>
            <h3 style="color:white;margin:0.5rem 0;text-shadow:0 2px 10px rgba(0,0,0,0.3);">{selected_attraction}</h3>
            <p style="color:rgba(255,255,255,0.7);font-size:0.9rem;">{attr['district']} · {attr['type']}</p>
            <div style="margin:1rem 0;display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;">
                <span class="price-tag">{'免费' if attr['ticket_price']==0 else f'¥{int(attr["ticket_price"])}'}</span>
                <span class="price-tag" style="background:linear-gradient(135deg,#00b894,#00cec9);">{attr['hot_level']}</span>
                <span class="price-tag" style="background:linear-gradient(135deg,#fd79a8,#e84393);">{attr['type']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 地图位置
        st.markdown("<div class='cyber-card'><h4>📍 位置</h4>", unsafe_allow_html=True)
        map_df = pd.DataFrame([{"lat": attr["lat"], "lon": attr["lng"], "name": attr["name"]}])
        st.map(map_df, zoom=10)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 距我多远 + 交通方式
        if "user_lat" in st.session_state and st.session_state.user_lat is not None:
            import math
            R = 6371
            dlat = math.radians(attr["lat"] - st.session_state.user_lat)
            dlng = math.radians(attr["lng"] - st.session_state.user_lng)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(st.session_state.user_lat)) * math.cos(math.radians(attr["lat"])) * math.sin(dlng/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            dist_km = round(R * c, 1)
            
            if dist_km < 3:
                transport_opt = "🚶 步行可达（约" + str(int(dist_km/0.08)) + "分钟）"
            elif dist_km < 20:
                time_drive = int(dist_km / 0.6)
                time_bus = int(dist_km / 0.3)
                transport_opt = f"🚗 驾车约{time_drive}分钟 | 🚌 公交约{time_bus}分钟"
            elif dist_km < 50:
                time_drive = int(dist_km / 0.7)
                transport_opt = f"🚗 驾车约{time_drive}分钟 | 🚌 建议先乘公交后打车"
            else:
                time_drive = int(dist_km / 0.8)
                transport_opt = f"🚗 驾车约{time_drive}分钟 | 🚄 建议乘高铁到最近站点"
            
            st.markdown(f"""
            <div class="cyber-card">
                <h4>🚗 距您当前位置</h4>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:1.3rem;font-weight:bold;color:#00d4ff;">{dist_km} 公里</span>
                    <span style="font-size:0.9rem;color:rgba(255,255,255,0.7);">{transport_opt}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 附近酒店速览
        nearby_hotels = links[links["attraction"] == selected_attraction].head(5)
        st.markdown("<div class='cyber-card'><h4>🏨 附近推荐酒店</h4>", unsafe_allow_html=True)
        for _, h in nearby_hotels.iterrows():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                <span>{h['hotel']}</span>
                <span style="color:#00d4ff;">¥{int(h['hotel_price'])}  |  ⭐{h['hotel_rating']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def show_hotel_detail_page(selected_hotel):
    """酒店详情页：含价格对比"""
    hotel = hotels[hotels["name"] == selected_hotel]
    if len(hotel) == 0:
        st.warning("未找到该酒店信息")
        return
    hotel = hotel.iloc[0]
    detail = get_hotel_detail(selected_hotel)
    
    st.markdown(f"<h1>🏨 {selected_hotel}</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("评分", f"{'⭐' * int(hotel['rating'])} {hotel['rating']}")
    col2.metric("星级", f"{'★' * hotel['star']}{'☆' * (5-hotel['star'])}")
    col3.metric("参考价格", f"¥{int(hotel['price'])}/晚")
    col4.metric("性价比指数", f"{hotel['cost_performance']:.3f}")
    
    col1, col2 = st.columns([1.5, 2])
    
    with col1:
        st.markdown(f"""
        <div class="cyber-card">
            <h4>📍 位置与交通</h4>
            <p><strong>附近景点：</strong><br>{detail['nearest_attractions']}</p>
            <p><strong>交通提示：</strong><br>{detail['transport_tips']}</p>
        </div>
        <div class="cyber-card">
            <h4>🛋️ 设施服务</h4>
            <p>{detail['facilities']}</p>
        </div>
        <div class="cyber-card">
            <h4>👥 适合人群</h4>
            <p>{detail['good_for']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="cyber-card">
            <h4>💲 价格对比</h4>
            <p style="font-size:0.85rem;color:rgba(255,255,255,0.5);">以下为参考价格，实际价格以当日为准</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 价格对比表
        if detail['room_types'] != "暂无数据":
            rooms = []
            for r in detail['room_types'].split(","):
                parts = r.strip().split("¥")
                if len(parts) == 2:
                    rooms.append({"房型": parts[0].strip(), "价格": int(parts[1])})
            
            if rooms:
                room_df = pd.DataFrame(rooms)
                
                # 横向柱状图
                fig = go.Figure()
                colors = ["#00d4ff", "#667eea", "#764ba2", "#fd79a8"]
                for i, (_, row) in enumerate(room_df.iterrows()):
                    fig.add_trace(go.Bar(
                        x=[row["价格"]], y=[row["房型"]],
                        orientation="h",
                        name=row["房型"],
                        marker_color=colors[i % len(colors)],
                        text=f"¥{row['价格']}",
                        textposition="outside",
                        showlegend=False
                    ))
                fig.update_layout(
                    height=250,
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(title="价格(元)", gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(title="", gridcolor="rgba(255,255,255,0.05)"),
                    font=dict(family="Microsoft YaHei", size=12, color="rgba(255,255,255,0.8)"),
                    margin=dict(l=0, r=40, t=10, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 区域价格对比
        st.markdown(f"""
        <div class="cyber-card">
            <h4>📊 区域价格对比</h4>
        </div>
        """, unsafe_allow_html=True)
        
        district = hotel["district"]
        district_hotels = hotels[hotels["district"] == district].sort_values("price")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=district_hotels["price"], y=district_hotels["name"],
            orientation="h",
            marker_color=["#00d4ff" if n == selected_hotel else "rgba(102,126,234,0.3)" 
                         for n in district_hotels["name"]],
            text=[f"¥{int(p)}" for p in district_hotels["price"]],
            textposition="outside",
            showlegend=False
        ))
        fig.update_layout(
            height=300,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="价格(元)", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="", gridcolor="rgba(255,255,255,0.05)"),
            font=dict(family="Microsoft YaHei", size=12, color="rgba(255,255,255,0.8)"),
            margin=dict(l=0, r=40, t=10, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"📌 高亮为当前所选酒店 · {district}共{len(district_hotels)}家酒店")


# ==================== 页面路由 ====================

if page == "📊 数据总览":
    st.markdown("<h1>📊 温州旅游数据总览</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.5);'>温州 · 一座充满活力的山水之城</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("景点总数", f"{len(attractions)} 个", "18个景区")
    col2.metric("酒店总数", f"{len(hotels)} 家", "覆盖11区县")
    col3.metric("美食推荐", f"{len(food)} 家", "5大菜系")
    col4.metric("推荐路线", f"{len(routes)} 条", "1/2/3日游")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("景点均分", f"{attractions['rating'].mean():.2f}", f"最高{attractions['rating'].max()}")
    col2.metric("酒店均价", f"¥{hotels['price'].mean():.0f}", f"最高性价比{hotels['cost_performance'].max():.3f}")
    col3.metric("本月旅游指数", f"{weather[weather['month']==datetime.now().month]['tourism_index'].values[0]}", "100满分")
    col4.metric("今日天气", f"{today_weather.get('temp','N/A')}°C", today_weather.get('condition','N/A'))
    
    st.markdown("<h2 style='margin-top:1.5rem;'>🌤️ 今日温州</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    for c, (label, val) in zip([col1,col2,col3,col4], [
        ("天气状况", today_weather.get('condition','N/A')),
        ("温度", f"{today_weather.get('temp','N/A')}°C"),
        ("体感温度", f"{today_weather.get('feels_like','N/A')}°C"),
        ("湿度", f"{today_weather.get('humidity','N/A')}%")
    ]):
        c.markdown(f"""
        <div class='cyber-card' style='text-align:center;'>
            <div style='font-size:0.8rem;color:rgba(255,255,255,0.5);'>{label}</div>
            <div style='font-size:1.5rem;font-weight:bold;color:#00d4ff;'>{val}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='margin-top:1.5rem;'>🗺️ 温州景点地图</h2>", unsafe_allow_html=True)
    map_data = attractions[["lat", "lng"]].rename(columns={"lng": "lon"})
    st.map(map_data, zoom=7.5, use_container_width=True, height=500)
    st.caption("💡 圆点位置=景点 · 通过缩放查看更多细节")

elif page == "🌤️ 今日出行指南":
    st.markdown("<h1>🌤️ 今日出行指南</h1>", unsafe_allow_html=True)
    st.info(f"📅 {datetime.now().strftime('%Y年%m月%d日 %A')}")
    
    # 天气大卡片
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown(f"""
        <div class='cyber-card' style='text-align:center;padding:2rem;background:linear-gradient(135deg,rgba(0,119,255,0.15),rgba(102,126,234,0.15));'>
            <div style='font-size:4rem;'>{'☀️' if '晴' in today_weather.get('condition','') or 'Clear' in today_weather.get('condition','') else '🌧️' if '雨' in today_weather.get('condition','') or 'rain' in today_weather.get('condition','') else '⛅'}</div>
            <div style='font-size:2.5rem;font-weight:bold;color:#00d4ff;text-shadow:0 0 20px rgba(0,212,255,0.3);'>{today_weather.get('temp','N/A')}°C</div>
            <div style='font-size:1rem;color:rgba(255,255,255,0.7);'>{today_weather.get('condition','N/A')}</div>
            <div style='font-size:0.8rem;color:rgba(255,255,255,0.4);margin-top:0.5rem;'>
                体感{today_weather.get('feels_like','N/A')}°C · 湿度{today_weather.get('humidity','N/A')}% · 风速{today_weather.get('wind_speed','N/A')}km/h
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        condition = today_weather.get("condition", "")
        is_rain = any(k in condition for k in ["rain", "雨", "shower", "drizzle"])
        is_cloudy = any(k in condition for k in ["cloud", "云", "overcast", "阴"])
        outdoor = "⚠️ 不适宜" if is_rain else "✅ 适宜"
        advice = "🌧️ 今日有雨，建议游览室内景点（江心屿、刘伯温故里、泰顺廊桥、温州博物馆）" if is_rain else "☀️ 晴好天气！推荐前往自然风光景点（雁荡山、楠溪江、大罗山）"
        
        st.markdown(f"""
        <div class='cyber-card' style='height:100%;'>
            <h4 style='margin-top:0;'>🎯 今日出行建议</h4>
            <p style='font-size:1.05rem;line-height:1.8;'>{advice}</p>
            <div style='margin-top:1rem;'>
                <span style='background:rgba(0,212,255,0.15);padding:0.3rem 0.8rem;border-radius:1rem;margin-right:0.5rem;font-size:0.85rem;'>
                    户外活动: {outdoor}
                </span>
                <span style='background:rgba(255,255,255,0.05);padding:0.3rem 0.8rem;border-radius:1rem;font-size:0.85rem;'>
                    室内活动: 均可
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='margin-top:1rem;'>🚶 景点拥挤度 · 今日实时</h2>", unsafe_allow_html=True)
    congested = get_today_congestion()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4 style='color:#ff6b6b;'>🔴 建议避开</h4>", unsafe_allow_html=True)
        crowded = congested[congested["congestion_score"] >= 0.5].head(6)
        for _, r in crowded.iterrows():
            st.markdown(f"""
            <div class='cyber-card' style='padding:0.6rem 1rem;border-left:3px solid #ff6b6b;'>
                <strong>{r['congestion_label']}</strong> {r['name']}
                <span style='float:right;color:rgba(255,255,255,0.5);font-size:0.85rem;'>⭐{r['rating']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h4 style='color:#00d4ff;'>🟢 推荐前往</h4>", unsafe_allow_html=True)
        comfy = congested[congested["congestion_score"] < 0.5].head(6)
        for _, r in comfy.iterrows():
            st.markdown(f"""
            <div class='cyber-card' style='padding:0.6rem 1rem;border-left:3px solid #00d4ff;'>
                <strong>{r['congestion_label']}</strong> {r['name']}
                <span style='float:right;color:rgba(255,255,255,0.5);font-size:0.85rem;'>⭐{r['rating']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='margin-top:1rem;'>🏨 今日高性价比酒店 TOP 8</h2>", unsafe_allow_html=True)
    hotels_today = get_today_hotel_prices().head(8)
    cols = st.columns(4)
    for i, (_, r) in enumerate(hotels_today.iterrows()):
        with cols[i % 4]:
            st.markdown(f"""
            <div class='cyber-card' style='text-align:center;padding:1rem;'>
                <div style='font-size:0.85rem;color:#00d4ff;font-weight:bold;'>{r['name'][:8]}</div>
                <div style='font-size:0.75rem;color:rgba(255,255,255,0.4);'>{r['district']}</div>
                <div style='font-size:1.3rem;font-weight:bold;color:#ff6b6b;margin:0.3rem 0;'>¥{r['today_price']}</div>
                <div style='font-size:0.8rem;'>⭐{r['rating']} · 性价比{r['today_cost_performance']:.3f}</div>
            </div>
            """, unsafe_allow_html=True)

elif page == "🤖 智能行程规划":
    st.markdown("<h1>🤖 智能行程规划</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.5);'>根据你的预算、天数和偏好，智能规划最优温州旅行方案</p>", unsafe_allow_html=True)
    
    # 输入面板
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        plan_days = st.slider("📅 旅行天数", 1, 7, 2)
    with col2:
        plan_budget = st.slider("💰 总预算(元)", 500, 5000, 1500, 100)
    with col3:
        plan_month = st.selectbox("📆 出行月份", 
            ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"],
            index=datetime.now().month - 1)
    with col4:
        plan_style = st.selectbox("🚶 旅行风格", ["休闲", "正常", "深度"])
    
    plan_interests = st.multiselect(
        "🎯 兴趣偏好（可多选）",
        ["自然风光", "历史文化", "美食探店", "摄影采风", "亲子出游", "小众清静", "海岛度假"],
        default=["自然风光", "摄影采风"]
    )
    
    interest_map = {
        "自然风光": "自然", "历史文化": "文化", "美食探店": "美食",
        "摄影采风": "摄影", "亲子出游": "亲子", "小众清静": "小众", "海岛度假": "海岛"
    }
    interests_list = [interest_map[i] for i in plan_interests]
    month_num = int(plan_month.replace("月",""))
    
    if st.button("🚀 一键生成行程", use_container_width=True):
        with st.spinner("🤖 正在智能规划最优行程..."):
            plans, cost, text, scored = plan_trip(
                days=plan_days, budget=plan_budget,
                interests=interests_list, travel_style=plan_style,
                month=month_num
            )
        
        if len(plans) == 0:
            st.error("⚠️ 当前条件下无法生成行程，请尝试增加预算或减少天数")
        else:
            st.session_state["plans"] = plans
            st.session_state["cost"] = cost
            st.session_state["text"] = text
            st.session_state["scored"] = scored
            st.balloons()
    
    if "plans" in st.session_state:
        plans = st.session_state["plans"]
        cost = st.session_state["cost"]
        text = st.session_state["text"]
        scored = st.session_state["scored"]
        
        total = sum(cost.values())
        
        # 费用概览
        st.markdown("<h2>💰 费用概览</h2>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("预估总花费", f"¥{total:,}", f"预算¥{plan_budget}")
        col2.metric("门票费用", f"¥{cost['门票']:,}")
        col3.metric("住宿费用", f"¥{cost['住宿']:,}")
        col4.metric("餐饮+交通", f"¥{cost['餐饮']+cost['交通']:,}")
        
        # 费用占比图
        cost_df = pd.DataFrame({
            "类别": list(cost.keys()),
            "金额": list(cost.values())
        })
        fig = px.pie(cost_df, values="金额", names="类别",
                     title="费用占比", hole=0.4,
                     color_discrete_map={
                         "门票": "#00d4ff", "住宿": "#667eea",
                         "餐饮": "#2ecc71", "交通": "#f39c12"
                     })
        fig = dark_fig(fig, 300)
        st.plotly_chart(fig, use_container_width=True)
        
        # 每日行程
        st.markdown("<h2>📅 每日行程</h2>", unsafe_allow_html=True)
        day_tabs = st.tabs([f"第{p['day']}天" for p in plans])
        
        for idx, day in enumerate(plans):
            with day_tabs[idx]:
                st.markdown(f"""
                <div class="cyber-card" style="margin-bottom:1rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <h4 style="margin:0;color:#00d4ff;">📅 第{day['day']}天 · 约{day['total_hours']}小时</h4>
                        <span style="background:rgba(0,212,255,0.15);padding:0.2rem 0.6rem;border-radius:1rem;font-size:0.85rem;">{plan_style}型</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 景点
                for i, attr in enumerate(day["attractions"], 1):
                    ticket = "免费" if attr["ticket_price"] == 0 else f"¥{int(attr['ticket_price'])}"
                    st.markdown(f"""
                    <div style="display:flex;align-items:stretch;margin:0.5rem 0;gap:0;">
                        <div style="min-width:36px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:8px 0 0 8px;display:flex;align-items:center;justify-content:center;font-weight:bold;color:white;">{i}</div>
                        <div style="flex:1;background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;padding:0.6rem 1rem;border:1px solid rgba(255,255,255,0.05);">
                            <div style="display:flex;justify-content:space-between;">
                                <strong style="color:#00d4ff;">{attr['name']}</strong>
                                <span style="font-size:0.85rem;color:rgba(255,255,255,0.5);">{attr['district']}</span>
                            </div>
                            <div style="font-size:0.85rem;color:rgba(255,255,255,0.6);margin-top:0.2rem;">
                                {'⭐'*int(attr['rating'])} {attr['rating']} | 🎫 {ticket} | ⏱ {attr['visit_hours']}h
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 酒店
                h = day.get("hotel")
                if h and not isinstance(h, float) and h is not None:
                    st.markdown(f"""
                    <div style="background:rgba(102,126,234,0.08);border:1px solid rgba(102,126,234,0.2);border-radius:8px;padding:0.6rem 1rem;margin:0.5rem 0;">
                        <span style="font-size:0.85rem;">🏨 <strong>{h.get('name','')}</strong></span>
                        <span style="float:right;font-size:0.85rem;">{'★'*int(h.get('star',3))} · ¥{int(h.get('price',0))}/晚 · ⭐{h.get('rating',0)}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 美食
                foods = day.get("food", [])
                if foods:
                    f_text = " | ".join([f"🍜 {f.get('name','')}(¥{int(f.get('avg_price',0))})" for f in foods if isinstance(f, dict)])
                    st.markdown(f"""
                    <div style="background:rgba(46,204,113,0.08);border:1px solid rgba(46,204,113,0.2);border-radius:8px;padding:0.6rem 1rem;margin:0.5rem 0;font-size:0.85rem;">
                        {f_text}
                    </div>
                    """, unsafe_allow_html=True)
        
        # 景点匹配分排行
        st.markdown("<h2>🏆 景点匹配度排行</h2>", unsafe_allow_html=True)
        selected_names = set()
        for day in plans:
            for attr in day["attractions"]:
                selected_names.add(attr["name"])
        
        top15 = scored.head(15).copy()
        top15["is_selected"] = top15["name"].apply(lambda x: "已选" if x in selected_names else "")
        fig = px.bar(top15.sort_values("match_score", ascending=True), 
                     x="match_score", y="name", orientation="h",
                     color="is_selected",
                     color_discrete_map={"已选": "#00d4ff", "": "rgba(102,126,234,0.3)"},
                     text="match_score",
                     labels={"match_score": "匹配分", "name": "景点", "is_selected": "状态"},
                     title="景点匹配分数排行（蓝色=已选入行程）")
        fig = dark_fig(fig, 400)
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        
        # 行程地图
        st.markdown("<h2>🗺️ 行程路线地图</h2>", unsafe_allow_html=True)
        map_points = []
        for day in plans:
            for attr in day["attractions"]:
                map_points.append({
                    "lat": attr["lat"], "lon": attr["lng"],
                    "name": f"[第{day['day']}天] {attr['name']}"
                })
        if map_points:
            map_df = pd.DataFrame(map_points)
            map_df = map_df.rename(columns={"lon": "lon"})
            st.map(map_df.rename(columns={"lon": "lon"}), zoom=8, use_container_width=True, height=400)
        
        # 淡旺季对比
        st.markdown("<h2>📊 淡旺季价格对比</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            <div class="cyber-card" style="text-align:center;">
                <h4 style="color:#00d4ff;">🏖️ 旺季（7-8月/国庆）</h4>
                <div style="font-size:1.8rem;font-weight:bold;color:#ff6b6b;">¥{:,}</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.5);">酒店上浮~20% · 门票全价</div>
            </div>
            """.format(int(total * 1.15)), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="cyber-card" style="text-align:center;">
                <h4 style="color:#2ecc71;">❄️ 淡季（11-2月除春节）</h4>
                <div style="font-size:1.8rem;font-weight:bold;color:#2ecc71;">¥{:,}</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.5);">酒店下浮~15% · 部分门票优惠</div>
            </div>
            """.format(int(total * 0.85)), unsafe_allow_html=True)
        
        # 对比柱状图
        seasons_df = pd.DataFrame({
            "季节": ["旺季(7-8月)", "平季", "淡季(11-2月)"],
            "预估花费": [int(total * 1.15), total, int(total * 0.85)]
        })
        fig = px.bar(seasons_df, x="季节", y="预估花费", 
                     color="季节", text="预估花费",
                     color_discrete_map={
                         "旺季(7-8月)": "#ff6b6b", "平季": "#667eea", "淡季(11-2月)": "#2ecc71"
                     },
                     title="不同季节价格对比")
        fig = dark_fig(fig, 350)
        fig.update_traces(texttemplate="¥%{text:,d}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
        
        # 导出
        st.markdown("<h2>📄 导出行程</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📋 复制行程文本"):
                st.info("✅ 行程已复制到剪贴板！请使用 Ctrl+V 粘贴")
                st.code(text, language="text")
        with col2:
            st.download_button(
                label="📥 下载行程(.txt)",
                data=text.encode("utf-8-sig"),
                file_name=f"温州行程规划_{plan_days}天.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    else:
        st.markdown("""
        <div class="cyber-card" style="text-align:center;padding:3rem;">
            <div style="font-size:4rem;margin-bottom:1rem;">🤖</div>
            <h3 style="color:rgba(255,255,255,0.6);">设置参数后点击「一键生成行程」</h3>
            <p style="color:rgba(255,255,255,0.4);">我将根据你的预算、天数和兴趣偏好<br>智能规划最优的温州旅行方案</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "🏞️ 景点探索":
    st.markdown("<h1>🏞️ 景点探索</h1>", unsafe_allow_html=True)
    
    # 用户定位
    import streamlit.components.v1 as components
    if "user_lat" not in st.session_state:
        st.session_state.user_lat = None
        st.session_state.user_lng = None
        st.session_state.location_set = False
    
    geo_html = """
    <div id="geo-status" style="text-align:center;padding:0.5rem;font-size:0.9rem;color:rgba(255,255,255,0.6);">
        📡 正在获取您的位置...
    </div>
    <script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(pos) {
                const lat = pos.coords.latitude.toFixed(6);
                const lng = pos.coords.longitude.toFixed(6);
                document.getElementById('geo-status').innerHTML = 
                    '📍 已定位: ' + lat + ', ' + lng;
                // 通过隐藏input传递给Streamlit
                var input = document.createElement('input');
                input.type = 'hidden';
                input.id = 'geo-lat';
                input.value = lat;
                document.body.appendChild(input);
                var input2 = document.createElement('input');
                input2.type = 'hidden';
                input2.id = 'geo-lng';
                input2.value = lng;
                document.body.appendChild(input2);
                // 触发Streamlit事件
                var evt = new CustomEvent('geo-ready', {detail: {lat: lat, lng: lng}});
                window.dispatchEvent(evt);
            },
            function(err) {
                document.getElementById('geo-status').innerHTML = 
                    '⚠️ 位置获取失败: ' + err.message + '（默认使用温州市中心）';
            },
            {timeout: 10000, enableHighAccuracy: false}
        );
    } else {
        document.getElementById('geo-status').innerHTML = '⚠️ 浏览器不支持定位';
    }
    </script>
    """
    components.html(geo_html, height=60)
    
    # 手动输入位置（备选）
    with st.expander("📍 手动设置位置"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            manual_lat = st.number_input("纬度", value=28.0, format="%.4f", step=0.01)
        with col2:
            manual_lng = st.number_input("经度", value=120.7, format="%.4f", step=0.01)
        with col3:
            if st.button("设置定位"):
                st.session_state.user_lat = manual_lat
                st.session_state.user_lng = manual_lng
                st.session_state.location_set = True
                st.rerun()
    
    if st.session_state.user_lat is None:
        st.session_state.user_lat = 28.0  # 温州市中心默认
        st.session_state.user_lng = 120.7
    
    # 选择景点
    st.markdown("<h3>选择景点查看详情</h3>", unsafe_allow_html=True)
    cols = st.columns([2, 1, 1, 1])
    with cols[0]:
        selected = st.selectbox("", attractions["name"].tolist(), label_visibility="collapsed")
    with cols[1]:
        filtered_types = st.multiselect("类型", attractions["type"].unique(), default=[])
    with cols[2]:
        filtered_districts = st.multiselect("区域", attractions["district"].unique(), default=[])
    with cols[3]:
        show_all = st.button("🏔️ 查看详情")
    
    if show_all or selected:
        if filtered_types:
            filtered_attrs = attractions[attractions["type"].isin(filtered_types)]
        else:
            filtered_attrs = attractions
        if filtered_districts:
            filtered_attrs = filtered_attrs[filtered_attrs["district"].isin(filtered_districts)]
        
        if selected in filtered_attrs["name"].values:
            show_detail_page(selected)
        else:
            if selected:
                st.warning(f"当前筛选条件下未包含'{selected}'，请调整筛选条件")
    
    # 景点总览图表
    st.markdown("<hr style='border-color:rgba(102,126,234,0.2);'>", unsafe_allow_html=True)
    st.markdown("<h2>📊 景点总览分析</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["评分排行", "热度排行", "最佳月份"])
    
    with tab1:
        fig = create_attraction_rating_chart(attractions)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = create_hotness_chart(attractions)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = create_monthly_recommend_heatmap(attractions)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("💡 绿色=该月推荐 · 春秋季(3-5月,9-11月)是温州旅游黄金季节")

elif page == "🏨 酒店性价比":
    st.markdown("<h1>🏨 酒店性价比分析</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3>选择酒店查看价格对比</h3>", unsafe_allow_html=True)
    cols = st.columns([2, 1, 1])
    with cols[0]:
        hotel_selected = st.selectbox("", hotels["name"].tolist(), label_visibility="collapsed")
    with cols[1]:
        hotel_district_filter = st.multiselect("区域", hotels["district"].unique(), default=[])
    with cols[2]:
        show_hotel = st.button("🏨 查看详情")
    
    if hotel_district_filter:
        filtered_hotels = hotels[hotels["district"].isin(hotel_district_filter)]
    else:
        filtered_hotels = hotels
    
    if hotel_selected and (show_hotel or hotel_selected in filtered_hotels["name"].values):
        show_hotel_detail_page(hotel_selected)
    
    st.markdown("<hr style='border-color:rgba(102,126,234,0.2);'>", unsafe_allow_html=True)
    st.markdown("<h2>📊 酒店数据总览</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💎 性价比排行", "📈 价格分析", "🏙️ 区域对比"])
    with tab1:
        fig = create_cost_performance_chart(hotels)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_hotel_scatter(hotels)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_hotel_price_distribution(hotels)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_hotel_district_price(hotels)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_star_comparison(hotels)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)

elif page == "🔗 游住联动推荐":
    st.markdown("<h1>🔗 景点-酒店联动推荐</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.5);'>选择想去的目的地，智能推荐附近高性价比酒店</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        sel_attr = st.selectbox("🏞️ 选择景点", attractions["name"].tolist())
    with col2:
        budget = st.slider("💵 预算上限(元/晚)", 100, 800, 400, 50)
    with col3:
        min_rating = st.slider("⭐ 最低评分", 3.0, 5.0, 3.5, 0.1)
    
    # 景点信息卡片
    attr_info = attractions[attractions["name"] == sel_attr].iloc[0]
    detail = get_attraction_detail(sel_attr)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        <div class='cyber-card'>
            <h4 style='margin-top:0;'>{attr_info['type'][:2]} {sel_attr}</h4>
            <p>📌 {attr_info['district']} · {attr_info['type']}</p>
            <p>⭐ {attr_info['rating']} · 💬 {attr_info['reviews']:,d}条评论</p>
            <p>🎫 {'免费' if attr_info['ticket_price']==0 else f'¥{int(attr_info["ticket_price"])}'}</p>
            <p>📖 {detail['highlights_desc'][:100]}...</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h4>🏨 附近推荐酒店</h4>", unsafe_allow_html=True)
        nearby = links[links["attraction"] == sel_attr].copy()
        nearby = nearby.merge(hotels[["name","star","cost_performance","price"]], left_on="hotel", right_on="name", suffixes=("","_h"))
        nearby = nearby[(nearby["hotel_price"] <= budget) & (nearby["hotel_rating"] >= min_rating)]
        nearby = nearby.sort_values("recommend_score", ascending=False)
        
        if len(nearby) == 0:
            st.warning("当前条件无匹配，建议放宽")
            nearby = links[links["attraction"] == sel_attr].sort_values("recommend_score", ascending=False).head(3)
            nearby = nearby.merge(hotels[["name","star","cost_performance","price"]], left_on="hotel", right_on="name", suffixes=("","_h"))
        
        for i, (_, r) in enumerate(nearby.head(6).iterrows()):
            st.markdown(f"""
            <div class='cyber-card' style='padding:0.7rem 1rem;border-left:3px solid {"#00d4ff" if i<2 else "rgba(255,255,255,0.1)"};'>
                <div style='display:flex;justify-content:space-between;'>
                    <span style='font-weight:bold;'>{r['hotel']}</span>
                    <span style='color:#ff6b6b;font-weight:bold;'>¥{int(r['hotel_price'])}</span>
                </div>
                <div style='font-size:0.85rem;color:rgba(255,255,255,0.5);margin-top:0.2rem;'>
                    ⭐{r['hotel_rating']} · 📏{r['distance_km']}km · 💎性价比{r.get('cost_performance',0):.3f}
                    <span style='float:right;color:#00d4ff;'>🏆 推荐{r['recommend_score']:.1f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color:rgba(102,126,234,0.2);'>", unsafe_allow_html=True)
    st.markdown("<h2>🏆 区域综合性价比</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig = create_district_comprehensive(district_summary)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = create_district_radar(district_summary)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

elif page == "🗺️ 路线规划":
    st.markdown("<h1>🗺️ 旅游路线规划</h1>", unsafe_allow_html=True)
    
    # 天气联动推荐
    condition = today_weather.get("condition", "")
    month = datetime.now().month
    is_rain = any(k in condition for k in ["rain", "雨", "shower", "drizzle"])
    is_hot = today_weather.get("temp", 20) >= 30
    is_cold = today_weather.get("temp", 15) <= 8
    is_clear = any(k in condition for k in ["Clear", "晴", "Sunny", "sunny"])
    
    if is_rain:
        weather_route = "🌧️ 今日有雨 · 推荐室内文化路线"
        weather_route_desc = "江心屿、刘伯温故里、泰顺廊桥、温州博物馆"
    elif is_hot:
        weather_route = "☀️ 今日高温 · 推荐避暑清凉路线"
        weather_route_desc = "百丈漈、楠溪江漂流、洞头列岛、大罗山"
    elif is_cold:
        weather_route = "❄️ 今日较冷 · 推荐温泉暖身路线"
        weather_route_desc = "泰顺温泉、文成山珍、刘伯温故里"
    elif is_clear:
        weather_route = "☀️ 今日晴好 · 推荐户外风光路线"
        weather_route_desc = "雁荡山、楠溪江、大罗山、泽雅"
    else:
        weather_route = "⛅ 今日天气尚可 · 推荐综合路线"
        weather_route_desc = "雁荡山、江心屿、南麂列岛、温州乐园"
    
    st.markdown(f"""
    <div class="cyber-card" style="background:linear-gradient(135deg,rgba(0,119,255,0.12),rgba(102,126,234,0.12));
                border-left:4px solid #00d4ff;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <h4 style="margin:0;color:#00d4ff;">🎯 {weather_route}</h4>
                <p style="margin:0.3rem 0 0 0;font-size:0.9rem;color:rgba(255,255,255,0.7);">{weather_route_desc}</p>
            </div>
            <div style="font-size:2rem;">{'🌧️' if is_rain else '☀️' if is_clear else '⛅'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🗺️ 路线推荐", "📋 路线详情"])
    with tab1:
        days = st.radio("选择天数", [1, 2, 3], format_func=lambda x: f"{x} 天游", horizontal=True)
        filtered = routes[routes["days"] == days]
        
        if len(filtered) > 0:
            route_name = st.selectbox("选择路线", filtered["name"].tolist())
            r = filtered[filtered["name"] == route_name].iloc[0]
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"""
                <div class='cyber-card'>
                    <h3 style='margin-top:0;color:#00d4ff;'>{r['name']}</h3>
                    <p><strong>📅 天数：</strong>{r['days']}天</p>
                    <p><strong>🏞️ 途经：</strong>{r['attractions']}</p>
                    <p><strong>✨ 特色：</strong>{r['highlights']}</p>
                    <p><strong>💰 预算：</strong><span class='price-tag'>{r['budget']}</span></p>
                    <p><strong>🌤️ 最佳季节：</strong>{r['best_season']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # 拥挤度检查
                congested = get_today_congestion()
                route_attrs = r["attractions"].split(", ")
                st.markdown("<div class='cyber-card'><h4>📡 今日拥挤度</h4>", unsafe_allow_html=True)
                for a_name in route_attrs:
                    match = congested[congested["name"].str.contains(a_name[:2])]
                    if len(match) > 0:
                        cr = match.iloc[0]
                        st.markdown(f"""
                        <div style='padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.05);'>
                            {cr['name']}: <strong>{cr['congestion_label']}</strong>
                            <span style='float:right;font-size:0.85rem;color:rgba(255,255,255,0.4);'>{cr['congestion_tip']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        fig = create_route_detail_table(routes)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        # 预算推荐
        st.markdown("<h3>💰 预算推荐方案</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        for c, (title, price, desc, color) in zip(
            [col1, col2, col3],
            [
                ("🌱 经济型", "300-500元/人", "市区文化一日游\n免费景点+经济酒店", "#00b894"),
                ("👍 舒适型", "500-1000元/人", "雁荡山或楠溪江\n2日游+中档酒店", "#00d4ff"),
                ("🌟 豪华型", "1000-2000元/人", "温州全景3日游\n高端酒店+全景点", "#764ba2")
            ]
        ):
            c.markdown(f"""
            <div class='cyber-card' style='text-align:center;border-top:3px solid {color};'>
                <div style='font-size:1.3rem;font-weight:bold;color:{color};'>{title}</div>
                <div style='font-size:0.9rem;margin:0.5rem 0;color:rgba(255,255,255,0.6);'>{price}</div>
                <div style='font-size:0.85rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

elif page == "📅 最佳旅行时间":
    st.markdown("<h1>📅 最佳旅行时间</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🌡️ 气候分析", "🌸 四季推荐", "🌤️ 天气影响"])
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = create_monthly_weather(weather)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("<div class='cyber-card'><h4>🏆 最佳月份TOP</h4>", unsafe_allow_html=True)
            ws = weather.sort_values("tourism_index", ascending=False).head(6)
            for _, w in ws.iterrows():
                bar_w = int(w["tourism_index"] * 0.8)
                st.markdown(f"""
                <div style='margin:0.4rem 0;display:flex;align-items:center;'>
                    <span style='width:2.5rem;font-size:0.85rem;'>{int(w['month'])}月</span>
                    <div style='flex:1;height:1.2rem;background:rgba(255,255,255,0.05);border-radius:0.6rem;overflow:hidden;'>
                        <div style='width:{bar_w}%;height:100%;background:linear-gradient(90deg,#00d4ff,#667eea);border-radius:0.6rem;'></div>
                    </div>
                    <span style='width:2rem;text-align:right;font-size:0.85rem;color:#00d4ff;'>{w['tourism_index']}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        fig = create_season_recommendation()
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns([1, 1])
        with col1:
            fig = create_weather_impact_chart(weather)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            months_cn = ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
            sel_m = st.selectbox("选择月份查看推荐景点", months_cn)
            idx = months_cn.index(sel_m) + 1
            m_data = weather[weather["month"] == idx].iloc[0]
            
            st.markdown(f"""
            <div class='cyber-card'>
                <h4 style='margin-top:0;'>{sel_m} 旅游指南</h4>
                <p>🌡️ 平均温度: {m_data['avg_temp']}°C</p>
                <p>🌤️ 概况: {m_data['condition']}</p>
                <p>🌧️ 降雨: {m_data['rain_days']}天</p>
                <p>📊 指数: {'⭐' * int(m_data['tourism_index']/20)} {m_data['tourism_index']}/100</p>
            </div>
            """, unsafe_allow_html=True)
            
            best_m = attractions[attractions["best_months"].str.contains(str(idx))]
            if len(best_m) > 0:
                st.markdown("<div class='cyber-card'><h4>🏞️ 本月推荐</h4>", unsafe_allow_html=True)
                for _, a in best_m.iterrows():
                    st.markdown(f"- **{a['name']}** ({a['district']}) {'⭐'*int(a['rating'])}")
                st.markdown("</div>", unsafe_allow_html=True)

elif page == "🍜 美食推荐":
    st.markdown("<h1>🍜 美食推荐</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏆 评分排行", "📊 类型分布", "💰 价格分析"])
    with tab1:
        fig = create_food_chart(food)
        fig = dark_fig(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class='cyber-card'>
            <h4 style='margin-top:0;'>🍴 温州特色美食推荐</h4>
            <p>🥟 <strong>灯盏糕</strong> — 温州传统小吃，外酥里嫩，¥8/个</p>
            <p>🐟 <strong>温州鱼圆</strong> — 鱼肉制成，弹滑鲜美，¥18/碗</p>
            <p>🦆 <strong>温州鸭舌</strong> — 温州名产，酱香浓郁，¥28/份</p>
            <p>🥟 <strong>长人馄饨</strong> — 百年老字号，¥20/碗</p>
            <p>🫓 <strong>永嘉麦饼</strong> — 永嘉特产，¥12/个</p>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_food_type_chart(food)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            dc = food["district"].value_counts().reset_index()
            dc.columns = ["district", "count"]
            fig = px.bar(dc, x="district", y="count", color="count",
                        color_continuous_scale="OrRd",
                        title="各区域美食分布",
                        labels={"district":"区域","count":"数量"})
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_food_price_chart(food)
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            bins = [0, 20, 50, 100, 200]
            labels = ["便宜(0-20)", "平价(20-50)", "中档(50-100)", "高档(100+)"]
            food["price_range"] = pd.cut(food["avg_price"], bins=bins, labels=labels)
            pc = food["price_range"].value_counts().reset_index()
            pc.columns = ["price_range", "count"]
            fig = px.pie(pc, values="count", names="price_range",
                        title="价格区间分布",
                        color_discrete_sequence=["#00b894","#00d4ff","#667eea","#764ba2"])
            fig = dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
