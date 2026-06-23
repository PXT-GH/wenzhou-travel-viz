"""
数据分析与可视化模块
功能：7大分析主题的图表生成
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def load_data():
    """加载预处理数据"""
    attractions = pd.read_csv(os.path.join(PROCESSED_DIR, "attractions_processed.csv"), encoding="utf-8-sig")
    hotels = pd.read_csv(os.path.join(PROCESSED_DIR, "hotels_processed.csv"), encoding="utf-8-sig")
    food = pd.read_csv(os.path.join(PROCESSED_DIR, "food_processed.csv"), encoding="utf-8-sig")
    transport = pd.read_csv(os.path.join(PROCESSED_DIR, "transport_processed.csv"), encoding="utf-8-sig")
    links = pd.read_csv(os.path.join(PROCESSED_DIR, "links_processed.csv"), encoding="utf-8-sig")
    weather = pd.read_csv(os.path.join(PROCESSED_DIR, "weather_processed.csv"), encoding="utf-8-sig")
    district_summary = pd.read_csv(os.path.join(PROCESSED_DIR, "district_summary.csv"), encoding="utf-8-sig")
    routes = pd.read_csv(os.path.join(PROCESSED_DIR, "routes.csv"), encoding="utf-8-sig")
    return attractions, hotels, food, transport, links, weather, district_summary, routes


# ========== 1. 景点综合分析 ==========

def create_attraction_rating_chart(attractions):
    """景点评分排行"""
    df = attractions.sort_values("rating", ascending=False).head(15)
    fig = px.bar(df, x="rating", y="name", orientation="h",
                 color="rating", color_continuous_scale="RdYlGn",
                 text="rating",
                 labels={"rating": "评分", "name": "景点", "type": "类型"},
                 title="温州景点评分排行")
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        template="plotly_white", height=500,
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[3.8, 5.0]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13)
    )
    return fig

def create_attraction_type_chart(attractions):
    """景点类型分布"""
    type_counts = attractions["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    colors = {"自然风光": "#2ecc71", "历史人文": "#3498db", "海岛风光": "#1abc9c",
              "主题乐园": "#e74c3c", "沙滩海岸": "#f39c12", "古镇村落": "#9b59b6"}
    fig = px.pie(type_counts, values="count", names="type",
                 title="温州景点类型分布",
                 color="type", color_discrete_map=colors)
    fig.update_layout(
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13)
    )
    fig.update_traces(textinfo="label+percent", pull=[0.05, 0.05, 0.05, 0, 0, 0])
    return fig

def create_attraction_price_distribution(attractions):
    """门票价格分布"""
    fig = px.histogram(attractions, x="ticket_price", nbins=12,
                       color="type",
                       labels={"ticket_price": "门票价格(元)", "count": "景点数", "type": "类型"},
                       title="温州景点门票价格分布",
                       barmode="overlay", opacity=0.7)
    fig.update_layout(
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_monthly_recommend_heatmap(attractions):
    """各景点最佳月份热力图"""
    months = ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
    heat_data = []
    for _, row in attractions.iterrows():
        best = [int(m) for m in str(row["best_months"]).split(",")]
        row_data = [1 if m in best else 0 for m in range(1, 13)]
        heat_data.append(row_data)
    
    fig = go.Figure(data=go.Heatmap(
        z=heat_data,
        x=months,
        y=attractions["name"],
        colorscale=[[0, "#f0f0f0"], [1, "#2ecc71"]],
        showscale=False,
        hovertemplate="景点: %{y}<br>月份: %{x}<br>推荐: %{customdata}<extra></extra>",
        customdata=[["✓ 推荐" if v else "" for v in row] for row in heat_data]
    ))
    fig.update_layout(
        title="各景点最佳游览月份",
        template="plotly_white", height=500,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=12),
        xaxis=dict(side="bottom")
    )
    return fig

def create_hotness_chart(attractions):
    """景点热度排行榜"""
    df = attractions.sort_values("reviews", ascending=True).head(15)
    fig = px.bar(df, x="reviews", y="name", orientation="h",
                 color="hot_level", 
                 color_discrete_map={
                     "🔥 热门": "#e74c3c", "⭐ 较热": "#f39c12",
                     "👍 一般": "#3498db", "🌱 小众": "#95a5a6"
                 },
                 text="reviews",
                 labels={"reviews": "评论数", "name": "景点", "hot_level": "热度"},
                 title="温州景点热度排行")
    fig.update_traces(texttemplate="%{text:,d}", textposition="outside")
    fig.update_layout(
        template="plotly_white", height=500,
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_attraction_map(attractions):
    """景点地图分布 — 使用白名单底图"""
    fig = px.scatter_mapbox(attractions, lat="lat", lon="lng",
                            size="reviews", color="rating",
                            hover_name="name", hover_data={
                                "rating":":.1f", "reviews":",d",
                                "ticket_price":"元", "type":True, "district":True
                            },
                            color_continuous_scale="RdYlGn",
                            size_max=25, zoom=7.5,
                            labels={"rating":"评分", "reviews":"评论数"},
                            title="温州景点地图分布")
    fig.update_layout(
        mapbox_style="carto-positron",
        height=550, margin={"r":0,"t":30,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=12)
    )
    return fig


# ========== 2. 酒店性价比分析 ==========

def create_hotel_price_distribution(hotels):
    """酒店价格分布"""
    fig = px.histogram(hotels, x="price", nbins=15,
                       color="star",
                       labels={"price": "价格(元)", "count": "酒店数", "star": "星级"},
                       title="温州酒店价格分布",
                       barmode="overlay", opacity=0.6)
    fig.update_layout(
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_cost_performance_chart(hotels):
    """性价比排行"""
    df = hotels.sort_values("cost_performance", ascending=True).head(20)
    fig = px.bar(df, x="cost_performance", y="name", orientation="h",
                 color="cost_performance", color_continuous_scale="Blues",
                 text="cost_performance",
                 hover_data={"star": True, "price": True, "rating": True},
                 labels={"cost_performance": "性价比指数", "name": "酒店", "price": "价格"},
                 title="温州酒店性价比排行 Top 20")
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(
        template="plotly_white", height=550,
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=12),
        xaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_hotel_scatter(hotels):
    """价格-评分气泡图"""
    fig = px.scatter(hotels, x="price", y="rating",
                     size="reviews", color="district",
                     hover_name="name",
                     hover_data={"star": True, "cost_performance": ":.3f", "reviews": ",d"},
                     labels={"price": "价格(元)", "rating": "评分",
                             "district": "区域", "reviews": "评论数"},
                     title="温州酒店价格-评分分析",
                     size_max=30, opacity=0.7)
    fig.update_layout(
        template="plotly_white", height=450,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_hotel_district_price(hotels):
    """各区域酒店均价对比"""
    district_avg = hotels.groupby("district", observed=True).agg(
        avg_price=("price", "mean"),
        avg_rating=("rating", "mean"),
        count=("name", "count")
    ).reset_index()
    fig = px.bar(district_avg, x="district", y="avg_price",
                 color="avg_rating", color_continuous_scale="RdYlGn",
                 text="avg_price",
                 hover_data={"count": True, "avg_rating": ":.2f"},
                 labels={"district": "区域", "avg_price": "平均价格(元)",
                         "avg_rating": "平均评分", "count": "酒店数"},
                 title="温州各区域酒店均价对比")
    fig.update_traces(texttemplate="%{text:.0f}元", textposition="outside")
    fig.update_layout(
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_star_comparison(hotels):
    """各星级性价比对比"""
    star_stats = hotels.groupby("star").agg(
        avg_price=("price", "mean"),
        avg_rating=("rating", "mean"),
        avg_cp=("cost_performance", "mean"),
        count=("name", "count")
    ).reset_index()
    star_stats["star_label"] = star_stats["star"].apply(lambda x: "★" * x + "☆" * (5 - x))
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=["各星级均价", "各星级性价比"])
    fig.add_trace(
        go.Bar(x=star_stats["star_label"], y=star_stats["avg_price"],
               marker_color=px.colors.sequential.Blues[2::2],
               text=star_stats["avg_price"].round(0).astype(int),
               textposition="outside", showlegend=False),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=star_stats["star_label"], y=star_stats["avg_cp"],
               marker_color=px.colors.sequential.Greens[2::2],
               text=star_stats["avg_cp"].round(3),
               textposition="outside", showlegend=False),
        row=1, col=2
    )
    fig.update_layout(
        title="各星级酒店价格与性价比对比",
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13)
    )
    return fig


# ========== 3. 景点-酒店联动分析 ==========

def create_attraction_hotel_link(links):
    """景点-酒店联动排行"""
    # 每个景点推荐评分最高的酒店
    top_links = links.loc[links.groupby("attraction")["recommend_score"].idxmax()].head(18)
    top_links = top_links.sort_values("recommend_score", ascending=True)
    
    fig = px.bar(top_links, x="recommend_score", y="attraction", orientation="h",
                 color="recommend_score", color_continuous_scale="Viridis",
                 text="recommend_score",
                 hover_data={"hotel": True, "distance_km": ":.1f", "hotel_price": True, "hotel_rating": True},
                 labels={"recommend_score": "推荐指数", "attraction": "景点",
                         "hotel": "推荐酒店", "distance_km": "距离(km)"},
                 title="各景点最佳推荐酒店")
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        template="plotly_white", height=550,
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=12),
        xaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_link_scatter(links):
    """景点-酒店推荐关系散点图"""
    fig = px.scatter(links, x="hotel_price", y="recommend_score",
                     color="district", size="hotel_rating",
                     hover_name="attraction",
                     hover_data={"hotel": True, "distance_km": ":.1f", "cost_performance": ":.3f"},
                     labels={"hotel_price": "酒店价格(元)", "recommend_score": "推荐指数",
                             "district": "区域", "hotel_rating": "酒店评分"},
                     title="景点-酒店推荐关系分析",
                     size_max=20, opacity=0.6)
    fig.update_layout(
        template="plotly_white", height=450,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig


# ========== 4. 综合性价比排行 ==========

def create_district_comprehensive(district_summary):
    """区域综合性价比排名"""
    df = district_summary.sort_values("total_score", ascending=True)
    fig = px.bar(df, x="total_score", y="district", orientation="h",
                 color="total_score", color_continuous_scale="RdYlGn",
                 text="total_score",
                 hover_data={
                     "avg_attraction_rating": ":.2f", "avg_hotel_price": ":.0f",
                     "avg_cost_performance": ":.4f", "attraction_count": True, "hotel_count": True
                 },
                 labels={"total_score": "综合评分", "district": "区域",
                         "avg_attraction_rating": "景点均分", "avg_hotel_price": "酒店均价"},
                 title="温州各区域综合性价比排行")
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(
        template="plotly_white", height=450,
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_district_radar(district_summary):
    """区域性价比雷达图"""
    top5 = district_summary.head(5)
    categories = ["景点均分", "酒店均价(反向)", "性价比指数", "景点数", "酒店数"]
    
    fig = go.Figure()
    colors = px.colors.qualitative.Set1[:5]
    for i, (_, row) in enumerate(top5.iterrows()):
        values = [
            row["avg_attraction_rating"] / 5 * 100,
            (1 - row["avg_hotel_price"] / 800) * 100,
            row["avg_cost_performance"] * 30 * 100,
            min(row["attraction_count"] / 5 * 100, 100),
            min(row["hotel_count"] / 8 * 100, 100)
        ]
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            name=row["district"],
            fill="toself",
            line_color=colors[i],
            opacity=0.6
        ))
    fig.update_layout(
        title="Top 5 区域综合性价比雷达图",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template="plotly_white", height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=12)
    )
    return fig


# ========== 5. 推荐路线规划 ==========

def create_route_timeline(routes):
    """路线推荐概览"""
    # 按天数分组
    routes_by_day = {}
    for d in [1, 2, 3]:
        rs = routes[routes["days"] == d]
        routes_by_day[d] = rs
    
    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=["一日游推荐", "两日游推荐", "三日游推荐"],
                        specs=[[{"type": "domain"}, {"type": "domain"}, {"type": "domain"}]])
    
    for idx, d in enumerate([1, 2, 3], 1):
        rs = routes_by_day[d]
        fig.add_trace(
            go.Pie(labels=rs["name"], values=[1]*len(rs),
                   textinfo="label", hole=0.4,
                   marker=dict(colors=px.colors.qualitative.Set2[:len(rs)])),
            row=1, col=idx
        )
    
    fig.update_layout(
        title="温州旅游推荐路线概览",
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=11)
    )
    return fig

def create_route_detail_table(routes):
    """路线详情表格"""
    fig = go.Figure(data=[go.Table(
        header=dict(values=["路线名称", "天数", "途经景点", "特色亮点", "预算", "最佳季节"],
                    fill_color="#1a1f4e", font=dict(color="#00d4ff", size=13, family="Microsoft YaHei"),
                    align="center", height=35, line_color="rgba(102,126,234,0.3)"),
        cells=dict(values=[
            routes["name"], routes["days"].astype(str) + "天",
            routes["attractions"], routes["highlights"],
            routes["budget"], routes["best_season"]
        ], fill_color=[["rgba(20,25,60,0.8)"]*len(routes), ["rgba(30,35,70,0.8)"]*len(routes)],
           align="center", font=dict(color="#e0e0f0", size=12, family="Microsoft YaHei"), height=35,
           line_color="rgba(102,126,234,0.15)")
    )])
    fig.update_layout(
        title="推荐路线详情",
        title_font_color="#e0e0f0",
        height=350, margin={"t":40,"b":0},
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


# ========== 6. 最佳旅行时间 ==========

def create_monthly_weather(weather):
    """各月天气与旅游指数"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=weather["month"], y=weather["rain_days"],
               name="降雨天数", marker_color="#3498db", opacity=0.6),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=weather["month"], y=weather["avg_temp"], name="平均温度(°C)",
                   mode="lines+markers", line=dict(color="#e74c3c", width=3),
                   marker=dict(size=10)),
        secondary_y=True
    )
    fig.add_trace(
        go.Scatter(x=weather["month"], y=weather["tourism_index"], name="旅游指数",
                   mode="lines+markers", line=dict(color="#2ecc71", width=3, dash="dot"),
                   marker=dict(size=10)),
        secondary_y=True
    )
    fig.update_layout(
        title="温州各月气候与旅游适宜度",
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis=dict(dtick=1, title="月份"),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="天数 / 指数", secondary_y=False)
    fig.update_yaxes(title_text="温度(°C)", secondary_y=True)
    return fig

def create_season_recommendation():
    """四季推荐"""
    seasons = [
        {"season": "🌸 春季 (3-5月)", "temp": "15-25°C", "features": "春暖花开，气温宜人",
         "attractions": "江心屿、楠溪江、雁荡山、泰顺廊桥、泽雅",
         "tips": "适合户外踏青，建议携带薄外套"},
        {"season": "☀️ 夏季 (6-8月)", "temp": "25-35°C", "features": "炎热多雨，海岛旺季",
         "attractions": "洞头列岛、南麂列岛、渔寮、楠溪江漂流、百丈漈",
         "tips": "注意防暑防晒，海岛游最佳时节"},
        {"season": "🍂 秋季 (9-11月)", "temp": "15-28°C", "features": "秋高气爽，最适合旅游",
         "attractions": "雁荡山、楠溪江、大罗山、文成、泰顺",
         "tips": "全年最佳旅游季节，建议错峰出行"},
        {"season": "❄️ 冬季 (12-2月)", "temp": "5-12°C", "features": "温和少雨，温泉好时节",
         "attractions": "江心屿、泰顺廊桥、刘伯温故里、温州市区",
         "tips": "可体验温州温泉，景区人少清静"}
    ]
    df = pd.DataFrame(seasons)
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=["季节", "温度", "特点", "推荐景点", "出行建议"],
                    fill_color="#1a1f4e", 
                    font=dict(color="#00d4ff", size=13, family="Microsoft YaHei"),
                    align="center", height=38, line_color="rgba(102,126,234,0.3)"),
        cells=dict(values=[df["season"], df["temp"], df["features"],
                           df["attractions"], df["tips"]],
                   fill_color=[["rgba(20,25,60,0.9)"]*4, ["rgba(30,35,70,0.9)"]*4],
                   font=dict(color="#e0e0f0", size=12, family="Microsoft YaHei"),
                   align="center", height=38, line_color="rgba(102,126,234,0.15)")
    )])
    fig.update_layout(
        title="温州四季旅游推荐",
        title_font=dict(color="#e0e0f0", size=16),
        height=320, margin={"t":40,"b":0,"l":0,"r":0},
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


# ========== 7. 美食分析 ==========

def create_food_chart(food):
    """美食评分排行"""
    df = food.sort_values("rating", ascending=True).head(15)
    fig = px.bar(df, x="rating", y="name", orientation="h",
                 color="rating", color_continuous_scale="RdYlGn",
                 text="rating",
                 hover_data={"cuisine_type": True, "avg_price": True},
                 labels={"rating": "评分", "name": "店铺", "cuisine_type": "类型",
                         "avg_price": "人均价格"},
                 title="温州美食评分排行 Top 15")
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        template="plotly_white", height=500,
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=12),
        xaxis=dict(range=[3.8, 5.0]),
        xaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig

def create_food_type_chart(food):
    """美食类型分布"""
    type_counts = food["cuisine_type"].value_counts().reset_index()
    type_counts.columns = ["cuisine_type", "count"]
    colors = {"小吃快餐": "#f39c12", "瓯菜": "#3498db", "海鲜": "#1abc9c",
              "农家菜": "#2ecc71"}
    fig = px.pie(type_counts, values="count", names="cuisine_type",
                 title="温州美食类型分布",
                 color="cuisine_type", color_discrete_map=colors)
    fig.update_layout(
        template="plotly_white", height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13)
    )
    fig.update_traces(textinfo="label+percent", pull=[0.05, 0.05, 0.05, 0.05])
    return fig

def create_food_price_chart(food):
    """美食价格-评分分析"""
    fig = px.scatter(food, x="avg_price", y="rating",
                     size="reviews", color="cuisine_type",
                     hover_name="name",
                     labels={"avg_price": "人均价格(元)", "rating": "评分",
                             "cuisine_type": "类型", "reviews": "评论数"},
                     title="温州美食价格-评分分析",
                     size_max=25, opacity=0.7)
    fig.update_layout(
        template="plotly_white", height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig


# ========== 天气影响分析 ==========

def create_weather_impact_chart(weather):
    """天气状况与旅游指数关系（按月份）"""
    fig = px.line(weather, x="month", y="tourism_index",
                  text="condition",
                  markers=True,
                  labels={"month": "月份", "tourism_index": "旅游指数",
                          "condition": "天气状况"},
                  title="温州各月旅游指数变化")
    fig.update_traces(line=dict(color="#2ecc71", width=3), marker=dict(size=10, color="#2ecc71"))
    fig.update_layout(
        template="plotly_white", height=350,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Microsoft YaHei, sans-serif", size=13),
        xaxis=dict(dtick=1),
        xaxis_gridcolor="rgba(200,200,200,0.3)", yaxis_gridcolor="rgba(200,200,200,0.3)"
    )
    return fig


def generate_all_charts():
    """生成所有图表并保存HTML"""
    attractions, hotels, food, transport, links, weather, district_summary, routes = load_data()
    
    charts = {}
    
    # 景点分析
    charts["attraction_rating"] = create_attraction_rating_chart(attractions)
    charts["attraction_type"] = create_attraction_type_chart(attractions)
    charts["attraction_price"] = create_attraction_price_distribution(attractions)
    charts["attraction_monthly"] = create_monthly_recommend_heatmap(attractions)
    charts["attraction_hotness"] = create_hotness_chart(attractions)
    charts["attraction_map"] = create_attraction_map(attractions)
    
    # 酒店分析
    charts["hotel_price_dist"] = create_hotel_price_distribution(hotels)
    charts["hotel_cp"] = create_cost_performance_chart(hotels)
    charts["hotel_scatter"] = create_hotel_scatter(hotels)
    charts["hotel_district"] = create_hotel_district_price(hotels)
    charts["hotel_star"] = create_star_comparison(hotels)
    
    # 联动分析
    charts["link_bar"] = create_attraction_hotel_link(links)
    charts["link_scatter"] = create_link_scatter(links)
    
    # 综合性价比
    charts["district_comprehensive"] = create_district_comprehensive(district_summary)
    charts["district_radar"] = create_district_radar(district_summary)
    
    # 路线
    charts["route_timeline"] = create_route_timeline(routes)
    charts["route_detail"] = create_route_detail_table(routes)
    
    # 时间
    charts["monthly_weather"] = create_monthly_weather(weather)
    charts["season_table"] = create_season_recommendation()
    
    # 美食
    charts["food_rating"] = create_food_chart(food)
    charts["food_type"] = create_food_type_chart(food)
    charts["food_scatter"] = create_food_price_chart(food)
    
    # 天气影响
    charts["weather_impact"] = create_weather_impact_chart(weather)
    
    # 保存
    out_dir = os.path.join(DATA_DIR, "charts")
    os.makedirs(out_dir, exist_ok=True)
    for name, fig in charts.items():
        fig.write_html(os.path.join(out_dir, f"{name}.html"))
    
    print(f"[OK] 已生成 {len(charts)} 个图表")
    return charts


if __name__ == "__main__":
    generate_all_charts()
