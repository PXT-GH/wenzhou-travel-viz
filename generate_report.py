"""
报告文档生成器
生成温州旅游数据可视化分析报告.docx
"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_report():
    doc = Document()
    
    # ====== 标题页 ======
    doc.add_paragraph()
    doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("温州旅游行业数据可视化分析")
    run.font.size = Pt(26)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1a, 0x1a, 0x2e)
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("——基于Streamlit的交互式数据可视化大作业")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x66, 0x7e, 0xea)
    
    doc.add_paragraph()
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info.add_run("数据可视化课程\n温州大学\n2026年6月")
    run.font.size = Pt(12)
    
    doc.add_page_break()
    
    # ====== 目录 ======
    doc.add_heading("目录", level=1)
    toc_items = [
        "一、选题背景",
        "二、数据来源与说明",
        "三、数据预处理与特征工程",
        "四、可视化分析",
        "    4.1 景点综合分析",
        "    4.2 酒店性价比分析",
        "    4.3 景点-酒店联动分析",
        "    4.4 综合性价比排行",
        "    4.5 旅游路线规划",
        "    4.6 最佳旅行时间分析",
        "    4.7 美食推荐分析",
        "五、实时数据模块",
        "六、技术实现",
        "七、总结与展望"
    ]
    for item in toc_items:
        p = doc.add_paragraph(item)
        p.paragraph_format.space_after = Pt(2)
    
    doc.add_page_break()
    
    # ====== 一、选题背景 ======
    doc.add_heading("一、选题背景", level=1)
    doc.add_paragraph(
        "温州位于浙江省东南部，是一座拥有丰富旅游资源的城市。"
        "雁荡山、楠溪江、江心屿等知名景点每年吸引大量游客。"
        "然而，旅游者往往面临信息分散、决策困难的问题："
        "何时去最好？哪些景点性价比高？如何规划路线？酒店怎么选？"
    )
    doc.add_paragraph(
        "本作品旨在通过数据可视化的方式，对温州旅游行业的多维度数据进行分析，"
        "帮助用户直观了解温州旅游景点的评分分布、酒店性价比、最佳游览时间、"
        "推荐路线等信息，并为用户提供实时的出行建议。"
    )
    
    # ====== 二、数据来源 ======
    doc.add_heading("二、数据来源与说明", level=1)
    doc.add_paragraph(
        "本作品数据来源包括："
    )
    doc.add_paragraph("1. 景点数据：温州18个主要景点的名称、区域、类型、评分、评论数、门票价格等信息", style='List Bullet')
    doc.add_paragraph("2. 酒店数据：温州45家酒店的名称、区域、星级、评分、价格等信息", style='List Bullet')
    doc.add_paragraph("3. 美食数据：温州25家特色美食店铺的信息", style='List Bullet')
    doc.add_paragraph("4. 交通数据：各景点间的距离与交通方式", style='List Bullet')
    doc.add_paragraph("5. 天气数据：温州各月份气候模式及实时天气API", style='List Bullet')
    
    doc.add_paragraph(
        "实时天气数据通过 wttr.in 免费天气API获取，"
        "景点拥挤度和酒店实时价格基于基础数据与实时因子（天气、季节、节假日）模拟计算。"
    )
    
    # 数据表格
    doc.add_heading("2.1 景点数据概览", level=2)
    table = doc.add_table(rows=7, cols=6)
    table.style = 'Light Grid Accent 1'
    headers = ["景点名称", "区域", "类型", "评分", "门票(元)", "评论数"]
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    
    data_rows = [
        ["雁荡山", "乐清市", "自然风光", "4.7", "200", "85,000"],
        ["江心屿", "鹿城区", "历史人文", "4.5", "30", "42,000"],
        ["楠溪江", "永嘉县", "自然风光", "4.6", "50", "56,000"],
        ["洞头列岛", "洞头区", "海岛风光", "4.4", "100", "28,000"],
        ["百丈漈", "文成县", "自然风光", "4.5", "65", "35,000"],
        ["温州乐园", "瓯海区", "主题乐园", "4.3", "130", "65,000"],
    ]
    for i, row in enumerate(data_rows):
        for j, val in enumerate(row):
            table.rows[i+1].cells[j].text = val
    
    doc.add_paragraph()
    doc.add_heading("2.2 数据字段说明", level=2)
    fields = [
        ("景点数据", "name, district, type, rating, reviews, ticket_price, visit_hours, best_months, lat, lng"),
        ("酒店数据", "name, district, star, rating, reviews, price, cost_performance, lat, lng"),
        ("美食数据", "name, district, cuisine_type, rating, reviews, avg_price"),
        ("交通数据", "from_attraction, to_attraction, distance_km, drive_min, has_bus"),
    ]
    for title, fields_str in fields:
        p = doc.add_paragraph()
        run = p.add_run(f"{title}：")
        run.bold = True
        p.add_run(fields_str)
    
    doc.add_page_break()
    
    # ====== 三、数据预处理与特征工程 ======
    doc.add_heading("三、数据预处理与特征工程", level=1)
    doc.add_paragraph(
        "数据预处理是分析的基础，主要包括以下步骤："
    )
    doc.add_heading("3.1 数据清洗", level=2)
    doc.add_paragraph("• 缺失值检查与处理", style='List Bullet')
    doc.add_paragraph("• 重复数据删除", style='List Bullet')
    doc.add_paragraph("• 数据类型统一（时间格式、数值格式）", style='List Bullet')
    
    doc.add_heading("3.2 特征工程", level=2)
    doc.add_paragraph("• 价格分档：将景点门票和酒店价格分为多个档位（免费/低价/中价/高价）", style='List Bullet')
    doc.add_paragraph("• 热度等级：基于评论数将景点分为热门/较热/一般/小众四个等级", style='List Bullet')
    doc.add_paragraph("• 性价比指数：核心指标 = 评分 / 价格 × 50，用于衡量酒店的性价比", style='List Bullet')
    doc.add_paragraph("• 最佳月份解析：将每个景点的最佳游览月份列表进行结构化解析", style='List Bullet')
    doc.add_paragraph("• 景点-酒店关联：通过区域匹配构建景点-酒店关联表，计算推荐指数", style='List Bullet')
    doc.add_paragraph("• 区域综合评分：综合景点评分、酒店性价比、价格水平计算各区域得分", style='List Bullet')
    
    # ====== 四、可视化分析 ======
    doc.add_heading("四、可视化分析", level=1)
    
    # 4.1 景点 
    doc.add_heading("4.1 景点综合分析", level=2)
    doc.add_paragraph(
        "对温州18个主要景点进行多维度分析，包括评分排行、类型分布、价格分布、热度排行和最佳游览月份。"
    )
    doc.add_paragraph(
        "• 评分排行：雁荡山(4.7)、楠溪江(4.6)、南麂列岛(4.6)位居前三，自然风光类景点整体评分较高。"
    )
    doc.add_paragraph(
        "• 类型分布：自然风光类景点占比最高，其次是历史人文类，体现了温州山水人文并重的旅游资源特色。"
    )
    doc.add_paragraph(
        "• 最佳月份热力图：春秋季(3-5月,9-11月)是绝大多数景点推荐游览的季节，"
        "夏季(6-8月)则是海岛类景点(洞头列岛、南麂列岛、渔寮风景区)的最佳时机。"
    )
    doc.add_paragraph(
        "• 免费景点：大罗山、瑞安古城为免费景点，适合预算有限的游客。"
    )
    
    # 4.2 酒店
    doc.add_heading("4.2 酒店性价比分析", level=2)
    doc.add_paragraph(
        "对温州45家酒店进行性价比分析，核心指标为性价比指数(评分/价格×50)。"
    )
    doc.add_paragraph(
        "• 性价比最高的是经济型酒店（3星级），其性价比指数远超高端酒店，"
        "适合预算有限的游客。"
    )
    doc.add_paragraph(
        "• 各区域酒店均价差异明显：鹿城区（市区）均价最高（约400-600元），"
        "泰顺县、平阳县等远郊区域均价较低（约200-300元）。"
    )
    doc.add_paragraph(
        "• 价格-评分散点图显示，中档酒店（300-500元）在评分和价格之间取得了较好的平衡，"
        "是大多数游客的最佳选择。"
    )
    
    # 4.3 联动
    doc.add_heading("4.3 景点-酒店联动分析", level=2)
    doc.add_paragraph(
        "这是本作品的核心创新点之一。通过构建景点-酒店关联表，"
        "为每个景点推荐附近性价比最高的酒店。"
    )
    doc.add_paragraph(
        "• 推荐指数 = 酒店评分 / (距离 + 0.5) × 10，综合考虑评分和距离因素。"
    )
    doc.add_paragraph(
        "• 用户选择景点后，系统自动展示附近酒店列表，并可按预算和评分筛选。"
    )
    doc.add_paragraph(
        "• 联动分析帮助用户一站式规划'游玩+住宿'方案，极大提升决策效率。"
    )
    
    # 4.4 综合性价比
    doc.add_heading("4.4 综合性价比排行", level=2)
    doc.add_paragraph(
        "对各区域的综合性价比进行量化评估，综合得分 = 景点均分×0.4 + 性价比指数×0.3 + 价格优势×0.3。"
    )
    doc.add_paragraph(
        "• 鹿城区凭借丰富的景点和酒店选择、便利的交通位居综合性价比榜首。"
    )
    doc.add_paragraph(
        "• 永嘉县（楠溪江）以自然风光和高性价比酒店位列第二。"
    )
    doc.add_paragraph(
        "• 瓯海区因靠近市区且房价适中，综合评分列第三。"
    )
    
    # 4.5 路线
    doc.add_heading("4.5 旅游路线规划", level=2)
    doc.add_paragraph(
        "基于景点间的距离和类型搭配，设计了7条经典旅游路线，覆盖1/2/3日游。"
    )
    doc.add_paragraph("一日游推荐：", style='List Bullet')
    doc.add_paragraph("  • 雁荡山精华一日游：感受'东南第一山'的壮丽", style='List Bullet')
    doc.add_paragraph("  • 温州市区文化一日游：江心屿+五马街", style='List Bullet')
    doc.add_paragraph("  • 楠溪江山水一日游：竹筏漂流+古村落", style='List Bullet')
    doc.add_paragraph("两日游推荐：", style='List Bullet')
    doc.add_paragraph("  • 雁荡山-楠溪江两日游：最经典的自然风光组合", style='List Bullet')
    doc.add_paragraph("  • 洞头海岛两日游：吃海鲜、看海景", style='List Bullet')
    doc.add_paragraph("三日游推荐：", style='List Bullet')
    doc.add_paragraph("  • 温州全景三日游：全面感受温州山水人文", style='List Bullet')
    doc.add_paragraph("  • 温州南部深度三日游：文成-泰顺-苍南", style='List Bullet')
    
    # 4.6 时间
    doc.add_heading("4.6 最佳旅行时间分析", level=2)
    doc.add_paragraph(
        "温州属亚热带季风气候，四季分明，全年皆可旅游，但不同季节各有特色。"
    )
    doc.add_paragraph(
        "• 春季(3-5月)：气温15-25°C，春暖花开，适合户外踏青。推荐：江心屿、楠溪江、泽雅。"
    )
    doc.add_paragraph(
        "• 夏季(6-8月)：气温25-35°C，炎热多雨，但海岛风光最佳。推荐：洞头列岛、南麂列岛、渔寮。"
    )
    doc.add_paragraph(
        "• 秋季(9-11月)：气温15-28°C，秋高气爽，全年最佳旅游季节。推荐：雁荡山、楠溪江、大罗山。"
    )
    doc.add_paragraph(
        "• 冬季(12-2月)：气温5-12°C，温和少雨，适合文化类旅游。推荐：江心屿、泰顺廊桥、刘伯温故里。"
    )
    
    # 4.7 美食
    doc.add_heading("4.7 美食推荐分析", level=2)
    doc.add_paragraph(
        "温州美食以小吃快餐和海鲜为主，代表美食包括馄饨、灯盏糕、鱼圆、鸭舌等。"
    )
    doc.add_paragraph(
        "• 评分最高的美食店铺集中在鹿城区（市区），尤其是老字号小吃店。"
    )
    doc.add_paragraph(
        "• 海鲜类美食价格较高（人均80-120元），小吃类价格亲民（人均8-30元）。"
    )
    doc.add_paragraph(
        "• 瓯菜作为温州地方菜系，在大酒家和特色餐馆中可以品尝到正宗风味。"
    )
    
    doc.add_page_break()
    
    # ====== 五、实时数据模块 ======
    doc.add_heading("五、实时数据模块", level=1)
    doc.add_paragraph(
        "实时数据模块是本作品的亮点功能，通过整合天气API和动态算法，为用户提供今日出行指南。"
    )
    
    doc.add_heading("5.1 实时天气", level=2)
    doc.add_paragraph(
        "通过 wttr.in 免费天气API获取温州当日实时天气数据，包括温度、天气状况、湿度、风速等信息。"
        "API获取失败时自动使用基于季节规律的模拟数据作为备选。"
    )
    
    doc.add_heading("5.2 景点拥挤度实时计算", level=2)
    doc.add_paragraph("拥挤度计算公式：")
    doc.add_paragraph("  拥挤度 = 基础热度 × 周末系数 × 季节系数 × 天气系数")
    doc.add_paragraph(
        "• 基础热度：基于评论数归一化"
    )
    doc.add_paragraph(
        "• 周末系数：周末×1.3，工作日×1.0"
    )
    doc.add_paragraph(
        "• 季节系数：旺季×1.2，淡季×0.7"
    )
    doc.add_paragraph(
        "• 天气系数：晴天×1.0，雨天×0.3-0.7"
    )
    doc.add_paragraph(
        "根据计算结果，将景点拥挤度分为爆满(≥0.8)、拥挤(≥0.6)、适中(≥0.4)、舒适(≥0.2)、冷清五个等级，"
        "并给出相应的出行建议。"
    )
    
    doc.add_heading("5.3 酒店实时价格", level=2)
    doc.add_paragraph(
        "酒店实时价格基于基础价格，考虑周末浮动、季节浮动和天气影响动态调整。"
        "同时计算今日性价比指数，为用户推荐今日高性价比酒店。"
    )
    
    doc.add_page_break()
    
    # ====== 六、技术实现 ======
    doc.add_heading("六、技术实现", level=1)
    doc.add_paragraph("本作品采用以下技术栈实现：")
    
    tech_items = [
        ("Python", "数据处理与后端逻辑"),
        ("Streamlit", "交互式Web应用框架"),
        ("Pandas & NumPy", "数据处理与分析"),
        ("Plotly", "交互式可视化图表"),
        ("wttr.in API", "实时天气数据"),
    ]
    for tech, desc in tech_items:
        p = doc.add_paragraph()
        run = p.add_run(f"{tech}：")
        run.bold = True
        p.add_run(desc)
    
    doc.add_heading("6.1 项目结构", level=2)
    doc.add_paragraph("""
    wenzhou_data_generator.py  — 数据生成脚本
    data_preprocess.py          — 数据预处理模块
    analysis.py                 — 分析与可视化模块（23个图表）
    realtime_engine.py          — 实时数据引擎（天气API+拥挤度+价格）
    app.py                      — Streamlit主应用（7个页面）
    data/
    ├── raw/                    — 原始数据
    └── processed/              — 预处理后数据
    output/                     — 输出报告
    """)
    
    doc.add_heading("6.2 可视化页面结构", level=2)
    pages = [
        "📊 数据总览 — 全局指标展示 + 今日天气速览",
        "🌤️ 今日出行指南 — 实时天气 + 拥挤度排行 + 酒店推荐",
        "🏞️ 景点深度分析 — 评分/类型/热度/最佳月份",
        "🏨 酒店性价比 — 性价比排行 + 价格分析 + 区域对比",
        "🔗 游住联动推荐 — 景点选酒店 + 区域性价比排行",
        "🗺️ 路线规划 — 1/2/3日游推荐 + 预算方案",
        "📅 最佳旅行时间 — 气候分析 + 四季推荐",
        "🍜 美食推荐 — 评分排行 + 类型分布 + 价格分析",
    ]
    for p in pages:
        doc.add_paragraph(p, style='List Bullet')
    
    doc.add_page_break()
    
    # ====== 七、总结 ======
    doc.add_heading("七、总结与展望", level=1)
    doc.add_heading("7.1 作品总结", level=2)
    doc.add_paragraph(
        "本作品以温州旅游行业数据为核心，通过Python数据分析和Streamlit交互式可视化技术，"
        "构建了一个包含7大主题模块的综合性数据可视化平台。"
    )
    doc.add_paragraph("主要成果：", style='List Bullet')
    doc.add_paragraph("• 收集并整理了温州18个景点、45家酒店、25家美食店铺的多维度数据", style='List Bullet')
    doc.add_paragraph("• 设计了性价比指数、拥挤度算法、推荐指数等多个创新特征", style='List Bullet')
    doc.add_paragraph("• 生成了23个交互式Plotly可视化图表", style='List Bullet')
    doc.add_paragraph("• 构建了景点-酒店联动推荐和路线规划功能", style='List Bullet')
    doc.add_paragraph("• 集成了实时天气API，实现今日出行指南功能", style='List Bullet')
    doc.add_paragraph("• 使用Streamlit构建了7个页面的交互式Web应用", style='List Bullet')
    
    doc.add_heading("7.2 不足与展望", level=2)
    doc.add_paragraph(
        "• 数据来源以构建和模拟为主，未来可接入真实OTA平台API获取更准确的实时数据"
    )
    doc.add_paragraph(
        "• 拥挤度算法可进一步优化，引入历史客流数据和预测模型"
    )
    doc.add_paragraph(
        "• 路线规划可加入更多约束条件（如交通时间、用餐时间等），实现更精准的行程安排"
    )
    doc.add_paragraph(
        "• 可增加用户反馈和评论分析，通过NLP技术分析游客评价情感"
    )
    doc.add_paragraph(
        "• 可扩展至浙江省其他城市，构建更大的旅游数据可视化平台"
    )
    
    # 保存
    output_path = os.path.join(OUTPUT_DIR, "温州旅游数据可视化分析报告.docx")
    doc.save(output_path)
    print(f"[OK] 报告已生成: {output_path}")
    return output_path

if __name__ == "__main__":
    create_report()
