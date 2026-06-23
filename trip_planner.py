"""
智能行程规划引擎
功能：根据预算、天数、偏好自动规划温州旅游行程
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def load_planner_data():
    """加载规划所需数据"""
    attractions = pd.read_csv(os.path.join(PROCESSED_DIR, "attractions_processed.csv"), encoding="utf-8-sig")
    hotels = pd.read_csv(os.path.join(PROCESSED_DIR, "hotels_processed.csv"), encoding="utf-8-sig")
    food = pd.read_csv(os.path.join(PROCESSED_DIR, "food_processed.csv"), encoding="utf-8-sig")
    transport = pd.read_csv(os.path.join(PROCESSED_DIR, "transport_processed.csv"), encoding="utf-8-sig")
    links = pd.read_csv(os.path.join(PROCESSED_DIR, "links_processed.csv"), encoding="utf-8-sig")
    weather = pd.read_csv(os.path.join(PROCESSED_DIR, "weather_processed.csv"), encoding="utf-8-sig")
    return attractions, hotels, food, transport, links, weather


def score_attraction(attr, interests, month, travel_style):
    """
    计算景点匹配分数 (0-100)
    """
    score = 0
    
    # 评分基础分 (0-30)
    score += attr["rating"] / 5 * 30
    
    # 兴趣匹配 (0-30)
    type_keywords = {
        "自然风光": ["自然", "户外", "摄影", "登山", "徒步", "风景"],
        "历史人文": ["文化", "历史", "古迹", "博物馆", "人文", "古村"],
        "海岛风光": ["海岛", "沙滩", "海景", "游泳", "水上", "度假"],
        "主题乐园": ["亲子", "游乐", "刺激", "家庭", "娱乐", "孩子"],
        "沙滩海岸": ["沙滩", "海景", "休闲", "度假", "海边"],
        "古镇村落": ["古村", "摄影", "文化", "田园", "乡村", "宁静"]
    }
    type_name = attr["type"]
    if type_name in type_keywords:
        kw = type_keywords[type_name]
        match_count = sum(1 for word in kw if word in interests)
        score += match_count / max(len(kw), 1) * 30
    
    # 季节匹配 (0-25)
    best_months = str(attr["best_months"])
    month_strs = best_months.replace(",", " ").split()
    if str(month) in month_strs:
        score += 25
    else:
        score += 8
    
    # 热度调整 (0-15)
    hot_level = str(attr["hot_level"])
    if "热门" in hot_level:
        if "小众" in interests or "清静" in interests:
            score += 3  # 怕拥挤的人减分
        else:
            score += 15
    elif "较热" in hot_level:
        score += 10
    elif "小众" in hot_level:
        if "小众" in interests or "清静" in interests:
            score += 15
        else:
            score += 8
    else:
        score += 8
    
    # 游玩强度匹配
    visit_hours = attr["visit_hours"]
    if travel_style == "休闲":
        if visit_hours <= 2.5:
            score += 5
        elif visit_hours > 4:
            score -= 5
    elif travel_style == "深度":
        if visit_hours >= 3:
            score += 5
        else:
            score += 2
    
    return max(0, min(100, round(score, 1)))


def select_attractions(attractions, interests, month, days, travel_style):
    """
    根据偏好和天数筛选最优景点组合
    返回 (scored_df, day_plans)
    """
    scored = attractions.copy()
    scored["match_score"] = scored.apply(
        lambda r: score_attraction(r, interests, month, travel_style),
        axis=1
    )
    scored = scored.sort_values("match_score", ascending=False).reset_index(drop=True)
    
    hours_per_day = {"休闲": 4, "正常": 6, "紧凑": 8, "深度": 5}
    max_hours = hours_per_day.get(travel_style, 6)
    
    selected_names = set()
    day_plans = []
    
    for day in range(days):
        day_hours = 0
        day_attrs = []
        
        for _, row in scored.iterrows():
            if row["name"] in selected_names:
                continue
            if day_hours + row["visit_hours"] > max_hours:
                continue
            
            # 同一天最多选3个景点
            if len(day_attrs) >= 3:
                break
            
            # 优先同区域，避免跨区
            if len(day_attrs) == 0:
                day_attrs.append(row)
                day_hours += row["visit_hours"]
                selected_names.add(row["name"])
            else:
                # 第二个景点尽量同区
                last_district = day_attrs[-1]["district"]
                if row["district"] == last_district or len(day_attrs) < 2:
                    day_attrs.append(row)
                    day_hours += row["visit_hours"]
                    selected_names.add(row["name"])
        
        if day_attrs:
            day_plans.append({
                "day": day + 1,
                "attractions": day_attrs,
                "total_hours": round(day_hours, 1)
            })
    
    return scored, day_plans


def find_hotels_for_route(day_plans, hotels, links, budget_per_day):
    """为每日行程推荐附近酒店"""
    for day in day_plans:
        attr_names = [a["name"] for a in day["attractions"]]
        nearby = links[links["attraction"].isin(attr_names)]
        
        if len(nearby) == 0:
            day["hotel"] = None
            continue
        
        nearby = nearby.merge(hotels, left_on="hotel", right_on="name", suffixes=("_link", ""))
        hotel_budget = budget_per_day * 0.55
        budget_hotels = nearby[nearby["price"] <= hotel_budget]
        
        if len(budget_hotels) > 0:
            best = budget_hotels.sort_values("cost_performance", ascending=False).iloc[0]
            day["hotel"] = best.to_dict()
        else:
            cheapest = nearby.sort_values("price").iloc[0].to_dict()
            day["hotel"] = cheapest
    
    return day_plans


def find_food_for_route(day_plans, food, budget_per_day):
    """为每日推荐餐饮"""
    for day in day_plans:
        food_budget = budget_per_day * 0.2
        suitable = food[food["avg_price"] * 2 <= food_budget]
        if len(suitable) > 0:
            day["food"] = suitable.sort_values("rating", ascending=False).head(2).to_dict("records")
        else:
            day["food"] = food.sort_values("avg_price").head(2).to_dict("records")
    return day_plans


def calculate_total_cost(day_plans, budget_per_day):
    """计算总花费"""
    total = {"门票": 0, "住宿": 0, "餐饮": 0, "交通": 150}
    
    for day in day_plans:
        for attr in day["attractions"]:
            total["门票"] += attr["ticket_price"]
        
        if day.get("hotel") and not isinstance(day["hotel"], float) and day["hotel"] is not None:
            total["住宿"] += day["hotel"].get("price", 0)
        
        if day.get("food") and isinstance(day["food"], list):
            for f in day["food"]:
                if isinstance(f, dict):
                    total["餐饮"] += f.get("avg_price", 30)
    
    total["住宿"] = int(total["住宿"])
    total["门票"] = int(total["门票"])
    total["餐饮"] = int(total["餐饮"])
    total["交通"] = max(150, len(day_plans) * 50)
    return total


def format_itinerary(day_plans, total_cost, budget, days, interests_str, travel_style, month):
    """格式化行程文本"""
    month_names = ["", "1月", "2月", "3月", "4月", "5月", "6月",
                   "7月", "8月", "9月", "10月", "11月", "12月"]
    lines = []
    lines.append("=" * 55)
    lines.append("  🏯 温州智能行程规划")
    lines.append(f"  {days}天 · 预算¥{budget} · {travel_style}型 · {month_names[month]}")
    lines.append("=" * 55)
    lines.append("")
    
    grand_total = sum(total_cost.values())
    lines.append(f"💰 预估总花费: ¥{grand_total:,}")
    lines.append(f"   门票: ¥{total_cost['门票']:,}  |  住宿: ¥{total_cost['住宿']:,}")
    lines.append(f"   餐饮: ¥{total_cost['餐饮']:,}  |  交通: ¥{total_cost['交通']:,}")
    lines.append("")
    
    for day in day_plans:
        lines.append(f"─── 📅 第{day['day']}天 (约{day['total_hours']}小时) ───")
        for i, attr in enumerate(day["attractions"], 1):
            ticket = "免费" if attr["ticket_price"] == 0 else f"¥{int(attr['ticket_price'])}"
            lines.append(f"  {i}. {attr['name']}")
            lines.append(f"     {'⭐'*int(attr['rating'])} {attr['rating']} | 🎫 {ticket} | ⏱ {attr['visit_hours']}h")
        lines.append("")
        
        h = day.get("hotel")
        if h and not isinstance(h, float) and h is not None:
            lines.append(f"  🏨 {h.get('name','')}")
            lines.append(f"     {'★'*int(h.get('star',3))} | ¥{int(h.get('price',0))}/晚 | ⭐{h.get('rating',0)}")
        lines.append("")
        
        foods = day.get("food", [])
        if foods:
            f_names = "、".join([f.get("name","") for f in foods if isinstance(f, dict)])
            lines.append(f"  🍜 {f_names}")
        lines.append("")
    
    lines.append("=" * 55)
    lines.append("  💡 出行建议")
    lines.append("=" * 55)
    lines.append("  • 提前3-7天预订酒店，旺季建议更早")
    lines.append("  • 温州多雨，随身携带雨具")
    lines.append("  • 部分景区支持网上购票，可享优惠")
    lines.append("  • 推荐使用「温州智旅」App获取实时导览")
    
    return "\n".join(lines)


def plan_trip(days=2, budget=1500, interests=None, travel_style="正常", month=None):
    """
    智能行程规划主函数
    
    参数:
        days: 旅行天数 (1-7)
        budget: 总预算(元)
        interests: 兴趣列表 ["自然", "文化", "美食", "摄影", ...]
        travel_style: "休闲"/"正常"/"深度"
        month: 出行月份 1-12
    
    返回:
        (day_plans, total_cost, itinerary_text, scored_df)
    """
    if interests is None:
        interests = ["自然", "文化", "摄影"]
    if month is None:
        month = datetime.now().month
    
    attractions, hotels, food, transport, links, weather = load_planner_data()
    budget_per_day = budget / max(days, 1)
    
    scored_attrs, day_plans = select_attractions(attractions, interests, month, days, travel_style)
    
    if len(day_plans) == 0:
        return [], {}, "⚠️ 当前条件下无法生成行程，请调整参数。", scored_attrs
    
    day_plans = find_hotels_for_route(day_plans, hotels, links, budget_per_day)
    day_plans = find_food_for_route(day_plans, food, budget_per_day)
    total_cost = calculate_total_cost(day_plans, budget_per_day)
    
    interests_str = "、".join(interests)
    itinerary_text = format_itinerary(day_plans, total_cost, budget, days, interests_str, travel_style, month)
    
    return day_plans, total_cost, itinerary_text, scored_attrs


if __name__ == "__main__":
    plans, cost, text, scored = plan_trip(days=3, budget=2000, 
                                          interests=["自然", "摄影", "美食"], 
                                          travel_style="正常")
    print(text)
    print(f"\n总花费: ¥{sum(cost.values()):,}")
