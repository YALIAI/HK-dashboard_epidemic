import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 设置matplotlib支持中文
try:
    plt.rcParams['font.sans-serif'] = ['Heiti TC']
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print('警告：未能设置中文字体，坐标轴可能显示为方块。', e)

# 读取数据
file_path = '香港各区疫情数据_20250322.xlsx'
df = pd.read_excel(file_path)

# 确保报告日期为日期类型
if '报告日期' in df.columns:
    df['报告日期'] = pd.to_datetime(df['报告日期'])

# 计算每日新增和累计确诊数据
if {'报告日期', '新增确诊', '累计确诊', '新增康复', '累计康复', '新增死亡', '累计死亡'}.issubset(df.columns):
    daily_summary = df.groupby('报告日期').agg({
        '新增确诊': 'sum',
        '累计确诊': 'max',
        '新增康复': 'sum',
        '累计康复': 'max',
        '新增死亡': 'sum',
        '累计死亡': 'max'
    }).reset_index()
    daily_summary = daily_summary.sort_values('报告日期')
    daily_summary['7日移动平均_新增确诊'] = daily_summary['新增确诊'].rolling(window=7, min_periods=1).mean().round(2)
    daily_summary['活跃病例'] = daily_summary['累计确诊'] - daily_summary['累计康复'] - daily_summary['累计死亡']

    # 绘制每日新增与累计确诊曲线
    plt.figure(figsize=(15, 8))
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    ax1.bar(daily_summary['报告日期'], daily_summary['新增确诊'], alpha=0.7, color='skyblue', label='每日新增确诊')
    ax1.plot(daily_summary['报告日期'], daily_summary['7日移动平均_新增确诊'], color='blue', linewidth=2, label='7日移动平均')
    ax1.set_ylabel('每日新增确诊数', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax2.plot(daily_summary['报告日期'], daily_summary['累计确诊'], color='red', linewidth=2, label='累计确诊')
    ax2.set_ylabel('累计确诊数', fontsize=12)
    plt.title('香港疫情每日新增与累计确诊数据', fontsize=16)
    plt.xlabel('日期', fontsize=12)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('每日确诊数据统计图.png', dpi=300)
    print('每日确诊数据统计图.png 已保存')

    # 绘制活跃病例趋势
    plt.figure(figsize=(15, 8))
    plt.plot(daily_summary['报告日期'], daily_summary['活跃病例'], color='orange', linewidth=2)
    plt.title('香港疫情活跃病例数据', fontsize=16)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('活跃病例数', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('活跃病例数据统计图.png', dpi=300)
    print('活跃病例数据统计图.png 已保存')

# 各地区累计确诊对比
if {'报告日期', '地区名称', '累计确诊', '人口'}.issubset(df.columns):
    last_date = df['报告日期'].max()
    last_day_data = df[df['报告日期'] == last_date]
    region_summary = last_day_data.groupby('地区名称').agg({
        '累计确诊': 'max',
        '人口': 'first'
    }).reset_index()
    region_summary = region_summary.sort_values('累计确诊', ascending=False)
    plt.figure(figsize=(14, 10))
    bars = plt.barh(region_summary['地区名称'], region_summary['累计确诊'], color='steelblue')
    plt.title('香港各地区累计确诊病例对比', fontsize=16)
    plt.xlabel('累计确诊病例数', fontsize=12)
    plt.ylabel('地区', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 5, bar.get_y() + bar.get_height()/2, f'{int(width):,}', va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig('各地区确诊病例对比图.png', dpi=300)
    print('各地区确诊病例对比图.png 已保存') 