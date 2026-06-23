"""
实时数据引擎
功能：天气API获取 + 实时拥挤度计算 + 实时酒店价格浮动
"""
import pandas as pd
import numpy as np
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def get_weather_from_api():
    """
    尝试从免费天气API获取温州今日天气
    使用 wttr.in（无需API Key）作为默认源
    失败时返回模拟数据
    """
    try:
        url = "https://wttr.in/Wenzhou?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
        current = data["current_condition"][0]
        weather = {
            "temp": int(current["temp_C"]),
            "condition": current["weatherDesc"][0]["value"],
            "humidity": int(current["humidity"]),
            "wind_speed": int(current["windspeedKmph"]),
            "feels_like": int(current["FeelsLikeC"]),
            "visibility": current["visibility"],
            "pressure": current["pressure"],
            "source": "wttr.in (实时)"
        }
        return weather
    except Exception as e:
        print(f"[WARN] 天气API获取失败: {e}，使用模拟数据")
        return get_simulated_weather()


def get_simulated_weather():
    """模拟今日天气数据（API不可用时的备选）"""
    today = datetime.now()
    month = today.month
    
    if month in [12, 1, 2]:
        temp = np.random.randint(3, 14)
        conditions = ["晴", "多云", "阴", "小雨"]
        probs = [0.3, 0.35, 0.2, 0.15]
    elif month in [3, 4]:
        temp = np.random.randint(10, 22)
        conditions = ["晴", "多云", "阴", "小雨", "中雨"]
        probs = [0.2, 0.3, 0.2, 0.2, 0.1]
    elif month in [5, 6]:
        temp = np.random.randint(20, 30)
        conditions = ["多云", "阴", "小雨", "中雨", "阵雨"]
        probs = [0.2, 0.2, 0.25, 0.15, 0.2]
    elif month in [7, 8]:
        temp = np.random.randint(27, 37)
        conditions = ["晴", "多云", "阴", "阵雨", "雷阵雨"]
        probs = [0.3, 0.3, 0.15, 0.15, 0.1]
    elif month in [9, 10]:
        temp = np.random.randint(18, 28)
        conditions = ["晴", "多云", "阴", "小雨"]
        probs = [0.3, 0.35, 0.2, 0.15]
    else:
        temp = np.random.randint(12, 22)
        conditions = ["晴", "多云", "阴", "小雨"]
        probs = [0.25, 0.3, 0.25, 0.2]
    
    condition = np.random.choice(conditions, p=probs)
    
    weather = {
        "temp": temp,
        "condition": condition,
        "humidity": np.random.randint(50, 95),
        "wind_speed": np.random.randint(5, 30),
        "feels_like": temp + np.random.randint(-3, 3),
        "source": "模拟数据（基于季节规律）"
    }
    return weather


def compute_congestion(attractions_df, weather, today=None):
    """
    计算各景点今日拥挤度
    影响因素：景点热度（评论数）、天气、是否周末/节假日、季节
    """
    if today is None:
        today = datetime.now()
    
    df = attractions_df.copy()
    
    # 基础拥挤度：基于评论数归一化
    max_reviews = df["reviews"].max()
    df["base_congestion"] = df["reviews"] / max_reviews
    
    # 天气惩罚因子
    condition = weather.get("condition", "晴")
    weather_penalty = {
        "晴": 1.0, "多云": 0.95, "阴": 0.85,
        "小雨": 0.7, "中雨": 0.5, "大雨": 0.3,
        "阵雨": 0.65, "雷阵雨": 0.25, "暴雨": 0.1,
        "雪": 0.2, "雾": 0.4
    }
    weather_factor = 0.5  # 天气差的景点人少
    for key, val in weather_penalty.items():
        if key in condition:
            weather_factor = val
            break
    
    # 周末/节假日加成
    weekday = today.weekday()
    is_weekend = weekday >= 5
    weekend_factor = 1.3 if is_weekend else 1.0
    
    # 季节加成
    month = today.month
    if month in [4, 5, 6, 7, 8, 9, 10]:
        season_factor = 1.2
    else:
        season_factor = 0.7
    
    # 综合拥挤度计算
    df["congestion_score"] = df["base_congestion"] * weekend_factor * season_factor * (1.5 - weather_factor * 0.5)
    df["congestion_score"] = df["congestion_score"].clip(0, 1)
    
    # 拥挤度分级
    def congestion_label(score):
        if score >= 0.8:
            return "🔴 爆满", "建议改日前往，人流量极大"
        elif score >= 0.6:
            return "🟠 拥挤", "人流量较大，建议早去"
        elif score >= 0.4:
            return "🟡 适中", "适合游览，体验良好"
        elif score >= 0.2:
            return "🟢 舒适", "人少清静，游览体验佳"
        else:
            return "🔵 冷清", "游客稀少，可独享风景"
    
    df[["congestion_label", "congestion_tip"]] = df["congestion_score"].apply(
        lambda x: pd.Series(congestion_label(x))
    )
    
    # 今日推荐指数
    df["today_recommend"] = (1 - df["congestion_score"]) * 0.5 + (df["rating"] / 5) * 0.5
    
    return df.sort_values("congestion_score", ascending=False)


def compute_hotel_prices(hotels_df, weather, today=None):
    """
    计算今日酒店实时价格与性价比
    影响因素：基础价格、是否周末、季节性、天气
    """
    if today is None:
        today = datetime.now()
    
    df = hotels_df.copy()
    
    weekday = today.weekday()
    is_weekend = weekday >= 5
    month = today.month
    
    # 周末价格上浮
    weekend_price_factor = 1.15 if is_weekend else 1.0
    
    # 旺季价格上浮
    if month in [4, 5, 6, 7, 8, 9, 10]:
        season_price_factor = 1.1
    else:
        season_price_factor = 0.9
    
    # 天气影响（恶劣天气价格略降）
    condition = weather.get("condition", "晴")
    bad_weather = any(k in condition for k in ["雨", "雪", "雾", "阴"])
    weather_price_factor = 0.95 if bad_weather else 1.0
    
    # 实时价格计算
    df["today_price"] = (df["price"] * weekend_price_factor * season_price_factor * weather_price_factor).round(0).astype(int)
    
    # 今日性价比
    df["today_cost_performance"] = (df["rating"] / df["today_price"] * 50).round(4)
    
    # 性价比等级
    def cp_level(cp):
        if cp >= 0.8:
            return "超高性价比"
        elif cp >= 0.5:
            return "高性价比"
        elif cp >= 0.3:
            return "性价比一般"
        else:
            return "性价比偏低"
    df["today_cp_level"] = df["today_cost_performance"].apply(cp_level)
    
    # 今日特价标签
    df["is_today_deal"] = df["today_price"] < df["price"] * 0.95
    
    # 今日推荐分
    df["today_score"] = (df["today_cost_performance"] * 0.5 + df["rating"] / 5 * 0.5)
    
    return df.sort_values("today_score", ascending=False)


def build_real_time_report(today=None):
    """生成完整实时报告"""
    if today is None:
        today = datetime.now()
    
    print(f"\n{'='*50}")
    print(f"  温州旅游实时数据报告")
    print(f"  生成时间: {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"  星期: {'周末' if today.weekday() >= 5 else '工作日'}")
    print(f"{'='*50}")
    
    # 获取天气
    weather = get_weather_from_api()
    print(f"\n[天气] 来源: {weather.get('source', '模拟')}")
    print(f"  今日温州天气: {weather.get('condition', 'N/A')}")
    print(f"  温度: {weather.get('temp', 'N/A')}°C")
    print(f"  体感温度: {weather.get('feels_like', 'N/A')}°C")
    print(f"  湿度: {weather.get('humidity', 'N/A')}%")
    print(f"  风速: {weather.get('wind_speed', 'N/A')} km/h")
    
    # 加载景点和酒店数据
    attractions = pd.read_csv(os.path.join(PROCESSED_DIR, "attractions_processed.csv"), encoding="utf-8-sig")
    hotels = pd.read_csv(os.path.join(PROCESSED_DIR, "hotels_processed.csv"), encoding="utf-8-sig")
    
    # 计算拥挤度
    congested = compute_congestion(attractions, weather, today)
    print(f"\n[景点拥挤度排行]")
    for _, row in congested.head(5).iterrows():
        print(f"  {row['congestion_label']} - {row['name']} (评分:{row['rating']})")
    print(f"  ... 共 {len(congested)} 个景点")
    
    # 计算酒店价格
    hotels_today = compute_hotel_prices(hotels, weather, today)
    print(f"\n[今日酒店性价比排行 TOP 5]")
    for _, row in hotels_today.head(5).iterrows():
        print(f"  {row['name']} - {row['star']}星 - 今日价:{row['today_price']}元 - 性价比:{row['today_cost_performance']:.3f}")
    
    return weather, congested, hotels_today


def get_weather():
    """对外接口：获取天气"""
    return get_weather_from_api()

def get_congestion(attractions_df):
    """对外接口：获取拥挤度"""
    weather = get_weather()
    return compute_congestion(attractions_df, weather)

def get_hotel_prices(hotels_df):
    """对外接口：获取酒店实时价格"""
    weather = get_weather()
    return compute_hotel_prices(hotels_df, weather)


if __name__ == "__main__":
    weather, congested, hotels_today = build_real_time_report()
