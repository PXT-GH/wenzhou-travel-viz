"""
数据预处理模块
功能：数据清洗、特征工程、构建分析用数据集
"""
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def load_raw_data():
    """加载原始数据"""
    attractions = pd.read_csv(os.path.join(RAW_DIR, "attractions_raw.csv"), encoding="utf-8-sig")
    hotels = pd.read_csv(os.path.join(RAW_DIR, "hotels_raw.csv"), encoding="utf-8-sig")
    food = pd.read_csv(os.path.join(RAW_DIR, "food_raw.csv"), encoding="utf-8-sig")
    transport = pd.read_csv(os.path.join(RAW_DIR, "transport_raw.csv"), encoding="utf-8-sig")
    links = pd.read_csv(os.path.join(RAW_DIR, "attraction_hotel_link_raw.csv"), encoding="utf-8-sig")
    weather = pd.read_csv(os.path.join(RAW_DIR, "weather_patterns.csv"), encoding="utf-8-sig")
    return attractions, hotels, food, transport, links, weather


def preprocess_attractions(df):
    """景点数据预处理与特征工程"""
    df = df.copy()
    
    # 价格分档
    def price_level(price):
        if price == 0:
            return "免费"
        elif price <= 40:
            return "低价 (0-40元)"
        elif price <= 80:
            return "中价 (41-80元)"
        else:
            return "高价 (80元以上)"
    df["price_level"] = df["ticket_price"].apply(price_level)
    
    # 热度等级（基于评论数）
    def hot_level(reviews):
        if reviews >= 50000:
            return "🔥 热门"
        elif reviews >= 20000:
            return "⭐ 较热"
        elif reviews >= 10000:
            return "👍 一般"
        else:
            return "🌱 小众"
    df["hot_level"] = df["reviews"].apply(hot_level)
    
    # 评分等级
    def rating_level(rating):
        if rating >= 4.5:
            return "极佳 (4.5+)"
        elif rating >= 4.0:
            return "优秀 (4.0-4.4)"
        else:
            return "良好 (4.0以下)"
    df["rating_level"] = df["rating"].apply(rating_level)
    
    # 最佳月份解析
    df["best_months_list"] = df["best_months"].str.split(",")
    df["best_months_count"] = df["best_months_list"].apply(len)
    
    # 区域编码
    district_order = ["鹿城区", "瓯海区", "龙湾区", "乐清市", "瑞安市", 
                      "永嘉县", "洞头区", "文成县", "苍南县", "泰顺县", "平阳县"]
    df["district"] = pd.Categorical(df["district"], categories=district_order, ordered=True)
    
    # 类型编码
    type_order = ["自然风光", "历史人文", "海岛风光", "主题乐园", "沙滩海岸", "古镇村落"]
    df["type"] = pd.Categorical(df["type"], categories=type_order, ordered=True)
    
    return df


def preprocess_hotels(df):
    """酒店数据预处理与特征工程"""
    df = df.copy()
    
    # 价格分档
    def price_level(price):
        if price < 200:
            return "经济 (200元以下)"
        elif price < 350:
            return "舒适 (200-350元)"
        elif price < 500:
            return "中档 (350-500元)"
        else:
            return "高档 (500元以上)"
    df["price_level"] = df["price"].apply(price_level)
    
    # 评分等级
    def rating_level(rating):
        if rating >= 4.5:
            return "极佳 (4.5+)"
        elif rating >= 4.0:
            return "优秀 (4.0-4.4)"
        else:
            return "良好 (4.0以下)"
    df["rating_level"] = df["rating"].apply(rating_level)
    
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
    df["cp_level"] = df["cost_performance"].apply(cp_level)
    
    # 星级命名
    def star_name(s):
        return "★" * s + "☆" * (5 - s)
    df["star_display"] = df["star"].apply(star_name)
    
    # 区域编码
    district_order = ["鹿城区", "瓯海区", "龙湾区", "乐清市", "瑞安市", 
                      "永嘉县", "洞头区", "文成县", "苍南县", "泰顺县", "平阳县"]
    df["district"] = pd.Categorical(df["district"], categories=district_order, ordered=True)
    
    return df


def preprocess_food(df):
    """美食数据预处理"""
    df = df.copy()
    
    # 价格分档
    def price_level(price):
        if price < 20:
            return "便宜 (20元以下)"
        elif price < 50:
            return "平价 (20-50元)"
        elif price < 100:
            return "中档 (50-100元)"
        else:
            return "高档 (100元以上)"
    df["price_level"] = df["avg_price"].apply(price_level)
    
    return df


def build_district_summary(attractions, hotels, food):
    """构建区域综合摘要"""
    summaries = []
    districts = ["鹿城区", "瓯海区", "龙湾区", "乐清市", "瑞安市", 
                 "永嘉县", "洞头区", "文成县", "苍南县", "泰顺县", "平阳县"]
    
    for d in districts:
        a = attractions[attractions["district"] == d]
        h = hotels[hotels["district"] == d]
        f = food[food["district"] == d]
        
        summaries.append({
            "district": d,
            "attraction_count": len(a),
            "avg_attraction_rating": round(a["rating"].mean(), 2) if len(a) > 0 else 0,
            "avg_ticket_price": round(a["ticket_price"].mean(), 1) if len(a) > 0 else 0,
            "hotel_count": len(h),
            "avg_hotel_rating": round(h["rating"].mean(), 2) if len(h) > 0 else 0,
            "avg_hotel_price": round(h["price"].mean(), 1) if len(h) > 0 else 0,
            "avg_cost_performance": round(h["cost_performance"].mean(), 4) if len(h) > 0 else 0,
            "food_count": len(f),
            "total_score": round(a["rating"].mean() * 0.4 + (h["cost_performance"].mean() if len(h) > 0 else 0) * 30 * 0.3 + (1 - h["price"].mean()/800 if len(h) > 0 else 0) * 0.3, 2) if len(a) > 0 and len(h) > 0 else 0
        })
    
    df = pd.DataFrame(summaries)
    df = df.sort_values("total_score", ascending=False).reset_index(drop=True)
    return df


def build_routes(attractions, transport):
    """构建推荐路线"""
    # 按区域分组，推荐经典路线
    routes = []
    
    # 一日游经典路线
    route1 = {
        "name": "雁荡山精华一日游",
        "days": 1,
        "attractions": "雁荡山",
        "description": "游览雁荡山核心景区，感受'东南第一山'的壮丽",
        "highlights": "灵峰、灵岩、大龙湫",
        "budget": "低",
        "best_season": "春秋季"
    }
    
    route2 = {
        "name": "温州市区文化一日游",
        "days": 1,
        "attractions": "江心屿, 五马街, 温州博物馆",
        "description": "感受温州历史文化与城市风情",
        "highlights": "江心屿古建筑群、五马街步行街、博物馆展览",
        "budget": "低",
        "best_season": "全年"
    }
    
    route3 = {
        "name": "楠溪江山水一日游",
        "days": 1,
        "attractions": "楠溪江",
        "description": "楠溪江竹筏漂流+古村落探访",
        "highlights": "竹筏漂流、丽水街、苍坡古村",
        "budget": "中",
        "best_season": "夏秋季"
    }
    
    # 两日游经典路线
    route4 = {
        "name": "雁荡山-楠溪江两日游",
        "days": 2,
        "attractions": "雁荡山, 楠溪江",
        "description": "第一天游览雁荡山，第二天畅游楠溪江",
        "highlights": "雁荡山奇峰+楠溪江竹筏",
        "budget": "中",
        "best_season": "春秋季"
    }
    
    route5 = {
        "name": "洞头海岛两日游",
        "days": 2,
        "attractions": "洞头列岛, 望海楼",
        "description": "海岛度假，吃海鲜、看海景、登望海楼",
        "highlights": "望海楼观景、海滨浴场、海鲜大餐",
        "budget": "中",
        "best_season": "夏季"
    }
    
    # 三日游经典路线
    route6 = {
        "name": "温州全景三日游",
        "days": 3,
        "attractions": "江心屿, 雁荡山, 楠溪江, 洞头列岛",
        "description": "全面感受温州山水之美与人文之韵",
        "highlights": "市区文化+雁荡山水+楠溪漂流+海岛风光",
        "budget": "中高",
        "best_season": "春秋季"
    }
    
    route7 = {
        "name": "温州南部深度三日游",
        "days": 3,
        "attractions": "百丈漈, 刘伯温故里, 泰顺廊桥, 渔寮风景区",
        "description": "文成-泰顺-苍南深度游，领略温州南部自然与人文",
        "highlights": "百丈漈观瀑+刘伯温文化+廊桥之乡+黄金海岸",
        "budget": "中",
        "best_season": "春秋季"
    }
    
    routes = [route1, route2, route3, route4, route5, route6, route7]
    
    # 新增：结合天气的推荐路线
    route8 = {
        "name": "☀️ 晴日推荐·雁荡山登山健行",
        "days": 1,
        "attractions": "雁荡山",
        "description": "晴朗天气最适合登山！雁荡山能见度好，可远眺东海",
        "highlights": "灵峰观景、大龙湫、灵岩飞渡",
        "budget": "中",
        "best_season": "晴好天气优先"
    }
    route9 = {
        "name": "🌧️ 雨日推荐·文化室内之旅",
        "days": 1,
        "attractions": "江心屿, 刘伯温故里, 泰顺廊桥",
        "description": "雨天适合文化遗产类景点，廊桥避雨别有韵味",
        "highlights": "江心寺古建、刘伯温文化、廊桥避雨",
        "budget": "低",
        "best_season": "全年的雨天"
    }
    route10 = {
        "name": "🏖️ 夏日清凉·海岛避暑线",
        "days": 2,
        "attractions": "洞头列岛, 渔寮风景区",
        "description": "炎炎夏日，海岛戏水、吃海鲜，清凉一夏",
        "highlights": "望海楼、大沙岙沙滩、渔寮金沙滩、海鲜大餐",
        "budget": "中",
        "best_season": "6-9月"
    }
    route11 = {
        "name": "🍁 秋日摄影·山水红叶线",
        "days": 2,
        "attractions": "雁荡山, 楠溪江, 大罗山",
        "description": "秋季层林尽染，是最佳摄影季节",
        "highlights": "雁荡秋色、楠溪江晨雾、大罗山日落",
        "budget": "中",
        "best_season": "10-11月"
    }
    route12 = {
        "name": "🌸 春日踏青·乡村赏花线",
        "days": 1,
        "attractions": "楠溪江, 泽雅风景区, 碗窑古村",
        "description": "春暖花开，古村田园风光正好",
        "highlights": "楠溪江竹筏、泽雅瀑布、碗窑制陶体验",
        "budget": "低",
        "best_season": "3-5月"
    }
    route13 = {
        "name": "🎢 亲子欢乐·乐园+自然线",
        "days": 2,
        "attractions": "温州乐园, 大罗山, 温州科技馆",
        "description": "适合带小朋友的亲子路线，玩乐+自然+科普",
        "highlights": "温州乐园游乐项目、大罗山徒步、科技馆体验",
        "budget": "中高",
        "best_season": "4-10月"
    }
    route14 = {
        "name": "♨️ 冬季暖心·温泉古镇线",
        "days": 2,
        "attractions": "泰顺廊桥, 文成百丈漈, 泰顺温泉",
        "description": "寒冬泡温泉、看廊桥、观冬瀑，温暖身心",
        "highlights": "泰顺廊桥雪景、百丈漈冬瀑、温泉泡汤",
        "budget": "中",
        "best_season": "12-2月"
    }
    
    routes = [route1, route2, route3, route4, route5, route6, route7,
              route8, route9, route10, route11, route12, route13, route14]
    return pd.DataFrame(routes)


def main():
    """执行所有预处理"""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    print("=" * 50)
    print("温州旅游数据预处理")
    print("=" * 50)
    
    # 加载原始数据
    attractions, hotels, food, transport, links, weather = load_raw_data()
    print(f"[OK] 加载原始数据完成")
    
    # 预处理各数据集
    attractions_proc = preprocess_attractions(attractions)
    hotels_proc = preprocess_hotels(hotels)
    food_proc = preprocess_food(food)
    
    # 保存预处理数据
    attractions_proc.to_csv(os.path.join(PROCESSED_DIR, "attractions_processed.csv"), index=False, encoding="utf-8-sig")
    hotels_proc.to_csv(os.path.join(PROCESSED_DIR, "hotels_processed.csv"), index=False, encoding="utf-8-sig")
    food_proc.to_csv(os.path.join(PROCESSED_DIR, "food_processed.csv"), index=False, encoding="utf-8-sig")
    transport.to_csv(os.path.join(PROCESSED_DIR, "transport_processed.csv"), index=False, encoding="utf-8-sig")
    links.to_csv(os.path.join(PROCESSED_DIR, "links_processed.csv"), index=False, encoding="utf-8-sig")
    weather.to_csv(os.path.join(PROCESSED_DIR, "weather_processed.csv"), index=False, encoding="utf-8-sig")
    print("[OK] 各数据集预处理完成")
    
    # 构建区域摘要
    district_summary = build_district_summary(attractions_proc, hotels_proc, food_proc)
    district_summary.to_csv(os.path.join(PROCESSED_DIR, "district_summary.csv"), index=False, encoding="utf-8-sig")
    print("[OK] 区域综合摘要构建完成")
    
    # 构建推荐路线
    routes = build_routes(attractions_proc, transport)
    routes.to_csv(os.path.join(PROCESSED_DIR, "routes.csv"), index=False, encoding="utf-8-sig")
    print("[OK] 推荐路线构建完成")
    
    print(f"\n[INFO] 所有预处理数据已保存至: {PROCESSED_DIR}")
    print(f"\n数据概览:")
    print(f"  景点: {len(attractions_proc)} 条")
    print(f"  酒店: {len(hotels_proc)} 条")
    print(f"  美食: {len(food_proc)} 条")
    print(f"  交通: {len(transport)} 条")
    print(f"  景点-酒店关联: {len(links)} 条")
    print(f"  区域综合: {len(district_summary)} 个区域")
    print(f"  推荐路线: {len(routes)} 条")
    
    return attractions_proc, hotels_proc, food_proc, transport, links, weather, district_summary, routes


if __name__ == "__main__":
    main()
