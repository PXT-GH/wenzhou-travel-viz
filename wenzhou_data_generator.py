"""
温州旅游数据采集与生成模块
功能：生成温州旅游基础数据集（景点、酒店、美食、交通）
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def generate_attractions():
    """生成温州景点数据"""
    attractions = [
        # name, district, type, rating, reviews, ticket_price, visit_hours, lat, lng, description, best_months
        ["雁荡山", "乐清市", "自然风光", 4.7, 85000, 200, 4.0, 28.371, 121.148, "国家5A级景区，'东南第一山'，以奇峰怪石、飞瀑流泉闻名", "4,5,6,7,8,9,10"],
        ["江心屿", "鹿城区", "历史人文", 4.5, 42000, 30, 2.5, 28.020, 120.642, "中国四大名屿之一，历代文人墨客留下众多诗篇", "3,4,5,9,10,11"],
        ["楠溪江", "永嘉县", "自然风光", 4.6, 56000, 50, 5.0, 28.307, 120.693, "国家4A级景区，以水秀、岩奇、瀑多、村古闻名", "5,6,7,8,9,10"],
        ["洞头列岛", "洞头区", "海岛风光", 4.4, 28000, 100, 6.0, 27.837, 121.154, "国家4A级景区，由302个岛屿组成，'百岛之县'", "6,7,8,9,10"],
        ["南麂列岛", "平阳县", "海岛风光", 4.6, 18000, 150, 6.0, 27.471, 121.044, "国家级海洋自然保护区，贝藻类王国", "6,7,8,9"],
        ["百丈漈", "文成县", "自然风光", 4.5, 35000, 65, 3.5, 27.786, 119.951, "中华第一高瀑，三级瀑布总落差353米", "5,6,7,8,9"],
        ["刘伯温故里", "文成县", "历史人文", 4.3, 22000, 50, 2.0, 27.790, 120.056, "明朝开国元勋刘伯温故居，文化底蕴深厚", "3,4,5,9,10,11"],
        ["温州乐园", "瓯海区", "主题乐园", 4.3, 65000, 130, 5.0, 27.970, 120.646, "浙南地区最大主题乐园，适合亲子游玩", "4,5,6,7,8,9,10"],
        ["泽雅风景区", "瓯海区", "自然风光", 4.2, 15000, 30, 3.0, 28.031, 120.537, "以瀑布、碧潭、古桥著称的山水胜地", "5,6,7,8,9"],
        ["泰顺廊桥", "泰顺县", "历史人文", 4.5, 12000, 40, 2.0, 27.558, 119.716, "中国廊桥之乡，现存古廊桥33座", "3,4,5,9,10,11"],
        ["渔寮风景区", "苍南县", "沙滩海岸", 4.3, 20000, 40, 4.0, 27.225, 120.529, "浙南黄金海岸，沙滩长2000米", "6,7,8,9,10"],
        ["碗窑古村", "苍南县", "古镇村落", 4.2, 10000, 30, 2.0, 27.332, 120.407, "清代古村落，保存完整的古窑址和古民居", "3,4,5,9,10,11"],
        ["中雁荡山", "乐清市", "自然风光", 4.3, 8000, 30, 3.5, 28.182, 120.896, "雁荡山支脉，以玉甑峰为核心", "4,5,6,7,8,9,10"],
        ["瑞安古城", "瑞安市", "历史人文", 4.0, 6000, 0, 2.0, 27.788, 120.648, "千年古县，历史文化名城", "3,4,5,9,10,11"],
        ["大罗山", "瓯海区", "自然风光", 4.4, 25000, 0, 4.0, 27.919, 120.716, "温州城市后花园，登山观景好去处", "4,5,6,7,8,9,10,11"],
        ["仙岩风景区", "瓯海区", "自然风光", 4.1, 12000, 35, 2.5, 27.881, 120.671, "朱自清《绿》的创作地，以梅雨潭闻名", "4,5,6,7,8,9"],
        ["铜铃山", "文成县", "自然风光", 4.3, 8000, 70, 3.0, 27.876, 119.887, "国家森林公园，壶穴奇观", "5,6,7,8,9"],
        ["望海楼", "洞头区", "历史人文", 4.2, 15000, 50, 1.5, 27.851, 121.148, "洞头标志性建筑，登楼可观百岛全景", "3,4,5,9,10,11"],
    ]
    columns = ["name", "district", "type", "rating", "reviews", "ticket_price", "visit_hours", "lat", "lng", "description", "best_months"]
    df = pd.DataFrame(attractions, columns=columns)
    df["best_months_list"] = df["best_months"].str.split(",")
    df["id"] = range(1, len(df) + 1)
    return df

def generate_hotels():
    """生成温州酒店数据"""
    districts = ["鹿城区", "瓯海区", "龙湾区", "乐清市", "瑞安市", "永嘉县", "洞头区", "文成县", "苍南县", "泰顺县", "平阳县"]
    hotels = []
    hotel_names = {
        "鹿城区": [("温州万豪酒店", 5, 680), ("温州国际大酒店", 4, 420), ("温州华侨饭店", 4, 380), ("温州开元名都大酒店", 5, 550), ("温州亚金大酒店", 3, 260), ("温州顺锦国际商务酒店", 4, 350), ("温州半岛酒店", 4, 320)],
        "瓯海区": [("温州中瑞大酒店", 4, 380), ("温州梦江酒店", 3, 250), ("温州和晟温德姆酒店", 5, 520), ("温州君廷酒店", 4, 350), ("温州阿外楼度假酒店", 4, 400)],
        "龙湾区": [("温州空港万豪酒店", 5, 580), ("温州滨海大酒店", 4, 320), ("温州瑞达洲际酒店", 4, 380), ("温州龙湾国际机场宾馆", 3, 200)],
        "乐清市": [("雁荡山芙蓉宾馆", 3, 220), ("雁荡山云台山居", 4, 380), ("乐清金鼎大酒店", 4, 350), ("雁荡山雁山宾馆", 3, 180), ("乐清天豪君澜大酒店", 5, 480)],
        "瑞安市": [("瑞安时代开元名都大酒店", 5, 450), ("瑞安国际大酒店", 4, 320), ("瑞安瑞立大酒店", 3, 200), ("瑞安华侨饭店", 3, 180)],
        "永嘉县": [("楠溪江悦庭楠舍", 4, 420), ("楠溪江耕读小院", 3, 280), ("永嘉裕锦大酒店", 4, 350), ("楠溪江四季驿站", 3, 180)],
        "洞头区": [("洞头金海岸开元名都度假酒店", 5, 550), ("洞头罗马酒店", 3, 250), ("洞头海景度假公寓", 3, 200), ("洞头海上人家", 4, 380)],
        "文成县": [("文成国际大酒店", 4, 300), ("文成天鹅堡度假酒店", 4, 380), ("文成隐山居", 3, 220)],
        "苍南县": [("苍南万顺大酒店", 4, 320), ("苍南国际大酒店", 4, 280), ("苍南渔寮海景酒店", 3, 200)],
        "泰顺县": [("泰顺香洲国际大酒店", 4, 330), ("泰顺亿联开元名都大酒店", 5, 480), ("泰顺山里人家民宿", 3, 180)],
        "平阳县": [("平阳国际大酒店", 4, 300), ("平阳南麂岛海景酒店", 3, 350), ("平阳海港宾馆", 3, 180)],
    }
    np.random.seed(42)
    hid = 1
    for district, hotels_list in hotel_names.items():
        base_reviews = np.random.randint(2000, 12000)
        for name, star, base_price in hotels_list:
            rating = round(np.random.uniform(3.5, 4.8), 1)
            reviews = int(base_reviews * np.random.uniform(0.3, 1.5))
            price = int(base_price * np.random.uniform(0.85, 1.15))
            lat_offset = np.random.uniform(-0.05, 0.05)
            lng_offset = np.random.uniform(-0.05, 0.05)
            if district == "鹿城区":
                lat, lng = 28.010 + lat_offset, 120.650 + lng_offset
            elif district == "瓯海区":
                lat, lng = 27.970 + lat_offset, 120.630 + lng_offset
            elif district == "龙湾区":
                lat, lng = 27.920 + lat_offset, 120.810 + lng_offset
            elif district == "乐清市":
                lat, lng = 28.130 + lat_offset, 120.960 + lng_offset
            elif district == "瑞安市":
                lat, lng = 27.780 + lat_offset, 120.650 + lng_offset
            elif district == "永嘉县":
                lat, lng = 28.150 + lat_offset, 120.690 + lng_offset
            elif district == "洞头区":
                lat, lng = 27.840 + lat_offset, 121.150 + lng_offset
            elif district == "文成县":
                lat, lng = 27.790 + lat_offset, 120.090 + lng_offset
            elif district == "苍南县":
                lat, lng = 27.520 + lat_offset, 120.430 + lng_offset
            elif district == "泰顺县":
                lat, lng = 27.560 + lat_offset, 119.720 + lng_offset
            elif district == "平阳县":
                lat, lng = 27.670 + lat_offset, 120.560 + lng_offset
            cost_performance = round(rating / price * 50, 2)
            hotels.append([name, district, star, rating, reviews, price, cost_performance, lat, lng])
            hid += 1
    columns = ["name", "district", "star", "rating", "reviews", "price", "cost_performance", "lat", "lng"]
    df = pd.DataFrame(hotels, columns=columns)
    df["id"] = range(1, len(df) + 1)
    return df

def generate_food():
    """生成温州美食数据"""
    food_data = [
        ["老温州馄饨铺", "鹿城区", "小吃快餐", 4.6, 4200, 25],
        ["长人馄饨", "鹿城区", "小吃快餐", 4.5, 3800, 20],
        ["温州大酒家", "鹿城区", "瓯菜", 4.3, 5600, 80],
        ["阿外楼海鲜", "鹿城区", "海鲜", 4.5, 7200, 120],
        ["瓯菜馆", "鹿城区", "瓯菜", 4.4, 4800, 90],
        ["正阁海鲜", "鹿城区", "海鲜", 4.3, 3500, 110],
        ["天一角", "鹿城区", "小吃快餐", 4.2, 2800, 35],
        ["五马街老锅贴", "鹿城区", "小吃快餐", 4.4, 3200, 15],
        ["永嘉麦饼店", "鹿城区", "小吃快餐", 4.3, 2500, 12],
        ["温州海鲜大排档", "瓯海区", "海鲜", 4.2, 3800, 85],
        ["瓯海人家", "瓯海区", "瓯菜", 4.1, 2200, 65],
        ["雁荡山珍馆", "乐清市", "农家菜", 4.4, 1800, 75],
        ["雁荡特色菜馆", "乐清市", "农家菜", 4.2, 1500, 60],
        ["楠溪江鱼庄", "永嘉县", "农家菜", 4.5, 2800, 70],
        ["永嘉田鱼馆", "永嘉县", "农家菜", 4.3, 2000, 55],
        ["洞头海鲜城", "洞头区", "海鲜", 4.4, 3500, 100],
        ["洞头渔家乐", "洞头区", "海鲜", 4.2, 2400, 80],
        ["文成山珍馆", "文成县", "农家菜", 4.1, 1200, 60],
        ["泰顺农家宴", "泰顺县", "农家菜", 4.0, 800, 50],
        ["苍南海鲜楼", "苍南县", "海鲜", 4.2, 1800, 75],
        ["瑞安老字号", "瑞安市", "瓯菜", 4.3, 2200, 60],
        ["平阳黄牛骨馆", "平阳县", "小吃快餐", 4.1, 1500, 35],
        ["灯盏糕老店", "鹿城区", "小吃快餐", 4.5, 4500, 8],
        ["温州鱼圆店", "鹿城区", "小吃快餐", 4.4, 5100, 18],
        ["鸭舌大王", "鹿城区", "小吃快餐", 4.3, 3800, 28],
    ]
    columns = ["name", "district", "cuisine_type", "rating", "reviews", "avg_price"]
    df = pd.DataFrame(food_data, columns=columns)
    df["id"] = range(1, len(df) + 1)
    return df

def generate_transport():
    """生成景点间交通数据"""
    attractions = generate_attractions()
    transport_data = []
    n = len(attractions)
    np.random.seed(42)
    for i in range(n):
        for j in range(i+1, n):
            a1 = attractions.iloc[i]
            a2 = attractions.iloc[j]
            dist_km = np.random.uniform(10, 120)
            drive_min = int(dist_km * np.random.uniform(1.0, 1.8))
            has_bus = np.random.choice([True, False], p=[0.7, 0.3])
            bus_min = int(drive_min * np.random.uniform(1.5, 3.0)) if has_bus else None
            has_subway = np.random.choice([True, False], p=[0.2, 0.8])
            note = ""
            if a1["district"] == a2["district"]:
                dist_km = np.random.uniform(5, 40)
                drive_min = int(dist_km * np.random.uniform(0.8, 1.5))
            if "雁荡" in a1["name"] and "雁荡" in a2["name"]:
                note = "同属雁荡山景区，建议联游"
            if "洞头" in a1["name"] and "望海" in a2["name"]:
                note = "同在洞头岛，可步行到达"
            if "楠溪" in a1["name"] or "楠溪" in a2["name"]:
                if "雁荡" in a1["name"] or "雁荡" in a2["name"]:
                    note = "楠溪江-雁荡山经典线路，建议安排一日游"
            transport_data.append([
                a1["name"], a2["name"],
                round(dist_km, 1), drive_min,
                "有" if has_bus else "无",
                f"{bus_min}分钟" if bus_min else "—",
                "有" if has_subway else "无",
                note
            ])
    columns = ["from_attraction", "to_attraction", "distance_km", "drive_min", "has_bus", "bus_time", "has_subway", "note"]
    df = pd.DataFrame(transport_data, columns=columns)
    return df

def generate_attraction_hotel_link(attractions_df, hotels_df):
    """生成景点-酒店关联表"""
    links = []
    np.random.seed(42)
    for _, attr in attractions_df.iterrows():
        nearby = hotels_df[hotels_df["district"] == attr["district"]].copy()
        if len(nearby) == 0:
            nearby = hotels_df.sample(min(3, len(hotels_df)))
        for _, hotel in nearby.iterrows():
            dist = np.random.uniform(0.5, 8.0)
            score = round(hotel["rating"] / (dist + 0.5) * 10, 2)
            links.append([
                attr["name"], hotel["name"], attr["district"],
                round(dist, 1), hotel["price"], hotel["rating"],
                hotel["cost_performance"], score
            ])
    columns = ["attraction", "hotel", "district", "distance_km", "hotel_price", "hotel_rating", "cost_performance", "recommend_score"]
    df = pd.DataFrame(links, columns=columns)
    return df

def generate_weather_patterns():
    """生成温州各月份气候数据"""
    months = range(1, 13)
    weather_data = []
    for m in months:
        if m in [12, 1, 2]:
            avg_temp = np.random.uniform(5, 12)
            condition = "寒冷"
        elif m in [3, 4]:
            avg_temp = np.random.uniform(10, 18)
            condition = "温和"
        elif m in [5, 6]:
            avg_temp = np.random.uniform(20, 28)
            condition = "温暖多雨"
        elif m in [7, 8]:
            avg_temp = np.random.uniform(28, 35)
            condition = "炎热"
        elif m in [9, 10]:
            avg_temp = np.random.uniform(18, 28)
            condition = "凉爽"
        else:
            avg_temp = np.random.uniform(12, 20)
            condition = "温和"
        rain_days = {"寒冷": 10, "温和": 14, "温暖多雨": 18, "炎热": 12, "凉爽": 10, "温和": 12}
        tourism_index = {"寒冷": 50, "温和": 80, "温暖多雨": 65, "炎热": 70, "凉爽": 90}
        weather_data.append([m, round(avg_temp, 1), condition, rain_days.get(condition, 12), tourism_index.get(condition, 70)])
    columns = ["month", "avg_temp", "condition", "rain_days", "tourism_index"]
    df = pd.DataFrame(weather_data, columns=columns)
    return df

def save_all_data():
    """生成并保存所有数据"""
    os.makedirs(os.path.join(DATA_DIR, "raw"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "processed"), exist_ok=True)
    
    print("=" * 50)
    print("温州旅游数据生成")
    print("=" * 50)
    
    # 生成景点数据
    attractions = generate_attractions()
    attractions.to_csv(os.path.join(DATA_DIR, "raw", "attractions_raw.csv"), index=False, encoding="utf-8-sig")
    print(f"[OK] 景点数据: {len(attractions)} 个景点")
    
    # 生成酒店数据
    hotels = generate_hotels()
    hotels.to_csv(os.path.join(DATA_DIR, "raw", "hotels_raw.csv"), index=False, encoding="utf-8-sig")
    print(f"[OK] 酒店数据: {len(hotels)} 家酒店")
    
    # 生成美食数据
    food = generate_food()
    food.to_csv(os.path.join(DATA_DIR, "raw", "food_raw.csv"), index=False, encoding="utf-8-sig")
    print(f"[OK] 美食数据: {len(food)} 家店铺")
    
    # 生成交通数据
    transport = generate_transport()
    transport.to_csv(os.path.join(DATA_DIR, "raw", "transport_raw.csv"), index=False, encoding="utf-8-sig")
    print(f"[OK] 交通数据: {len(transport)} 条路线")
    
    # 生成景点-酒店关联
    links = generate_attraction_hotel_link(attractions, hotels)
    links.to_csv(os.path.join(DATA_DIR, "raw", "attraction_hotel_link_raw.csv"), index=False, encoding="utf-8-sig")
    print(f"[OK] 景点-酒店关联: {len(links)} 条关联")
    
    # 生成气候数据
    weather = generate_weather_patterns()
    weather.to_csv(os.path.join(DATA_DIR, "raw", "weather_patterns.csv"), index=False, encoding="utf-8-sig")
    print(f"[OK] 气候模式数据: 12 个月份")
    
    print(f"\n[INFO] 所有原始数据已保存至: {os.path.join(DATA_DIR, 'raw')}")
    return attractions, hotels, food, transport, links, weather

if __name__ == "__main__":
    save_all_data()
