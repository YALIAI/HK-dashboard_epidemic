from flask import Flask, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__, template_folder='templates')
DATA_FILE = os.path.join(os.path.dirname(__file__), '香港各区疫情数据_20250322.xlsx')

def load_data():
    df = pd.read_excel(DATA_FILE)
    if '报告日期' in df.columns:
        df['报告日期'] = pd.to_datetime(df['报告日期'])
    return df

@app.route('/api/summary')
def api_summary():
    df = load_data()
    last_date = df['报告日期'].max()
    last = df[df['报告日期'] == last_date]
    summary = {
        '累计确诊': int(last['累计确诊'].sum()),
        '现存确诊': int(last['现存确诊'].sum()),
        '累计康复': int(last['累计康复'].sum()),
        '累计死亡': int(last['累计死亡'].sum()),
        '发病率': round(last['发病率(每10万人)'].mean(), 2),
        '总人口': int(last['人口'].sum())
    }
    return jsonify(summary)

@app.route('/api/map')
def api_map():
    df = load_data()
    last_date = df['报告日期'].max()
    last = df[df['报告日期'] == last_date]
    result = {
        '地区名称': last['地区名称'].tolist(),
        '累计确诊': last['累计确诊'].tolist(),
        '现存确诊': last['现存确诊'].tolist(),
        '风险等级': last['风险等级'].tolist()
    }
    return jsonify(result)

@app.route('/api/daily')
def api_daily():
    df = load_data()
    daily = df.groupby('报告日期').agg({
        '新增确诊': 'sum',
        '累计确诊': 'sum',
        '现存确诊': 'sum',
        '累计康复': 'sum',
        '累计死亡': 'sum'
    }).reset_index().sort_values('报告日期')
    daily['7日均新增'] = daily['新增确诊'].rolling(window=7, min_periods=1).mean().round(2)
    result = {
        '日期': daily['报告日期'].dt.strftime('%Y-%m-%d').tolist(),
        '新增确诊': daily['新增确诊'].tolist(),
        '累计确诊': daily['累计确诊'].tolist(),
        '现存确诊': daily['现存确诊'].tolist(),
        '累计康复': daily['累计康复'].tolist(),
        '累计死亡': daily['累计死亡'].tolist(),
        '7日均新增': daily['7日均新增'].tolist()
    }
    return jsonify(result)

@app.route('/api/region_bar')
def api_region_bar():
    df = load_data()
    last_date = df['报告日期'].max()
    last = df[df['报告日期'] == last_date]
    region = last[['地区名称', '累计确诊', '现存确诊']].sort_values('累计确诊', ascending=False)
    result = {
        '地区名称': region['地区名称'].tolist(),
        '累计确诊': region['累计确诊'].tolist(),
        '现存确诊': region['现存确诊'].tolist()
    }
    return jsonify(result)

@app.route('/api/trend')
def api_trend():
    df = load_data()
    daily = df.groupby('报告日期').agg({
        '新增确诊': 'sum',
        '累计确诊': 'sum',
        '现存确诊': 'sum',
        '累计康复': 'sum',
        '累计死亡': 'sum'
    }).reset_index().sort_values('报告日期')
    result = {
        '日期': daily['报告日期'].dt.strftime('%Y-%m-%d').tolist(),
        '现存确诊': daily['现存确诊'].tolist(),
        '累计康复': daily['累计康复'].tolist(),
        '累计死亡': daily['累计死亡'].tolist()
    }
    return jsonify(result)

@app.route('/api/risk_board')
def api_risk_board():
    df = load_data()
    last_date = df['报告日期'].max()
    last = df[df['报告日期'] == last_date]
    high_risk = last[last['风险等级'] == '高风险']
    result = {
        '高风险地区': high_risk['地区名称'].tolist(),
        '现存确诊': high_risk['现存确诊'].tolist()
    }
    return jsonify(result)

@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002) 