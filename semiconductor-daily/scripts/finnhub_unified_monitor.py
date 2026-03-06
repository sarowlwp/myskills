#!/usr/bin/env python3
"""
Finnhub 统一金融监控脚本
整合：股价 + SEC 文件
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("需要安装 requests: pip install requests")
    exit(1)

# 配置
API_KEY = "d6gfqj1r01quah09d3d0d6gfqj1r01quah09d3dg"
BASE_URL = "https://finnhub.io/api/v1"
SKILL_ROOT = Path(__file__).parent.parent
STATE_PATH = SKILL_ROOT / 'state.json'

# 监控配置 - 严格限制时间范围
WATCHLIST = {
    'tickers': ['INTC', 'NVDA', 'AMD', 'TSM'],
    'price_alert_threshold': 3.0,  # ±3% 预警
    'sec_forms': ['10-K', '10-Q', '8-K', '4', '13F-HR'],  # 关注的 SEC 文件类型
    'sec_lookback_days': 7,  # 只查看本周内的 SEC 文件
}

def finnhub_request(endpoint, params=None):
    """发送 Finnhub API 请求"""
    url = f"{BASE_URL}{endpoint}"
    params = params or {}
    params['token'] = API_KEY
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ API Error {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def get_stock_quote(symbol):
    """获取股票实时报价"""
    data = finnhub_request('/quote', {'symbol': symbol})
    if data:
        return {
            'symbol': symbol,
            'current': data.get('c'),
            'change': data.get('d'),
            'change_percent': data.get('dp'),
            'high': data.get('h'),
            'low': data.get('l'),
            'open': data.get('o'),
            'previous_close': data.get('pc'),
            'timestamp': datetime.now().isoformat()
        }
    return None

def get_sec_filings(symbol, from_date=None, to_date=None):
    """获取 SEC 文件 - 只获取当日/当周的文件"""
    now = datetime.now()
    
    if not from_date:
        # 只获取本周一的文件（当周）
        monday = now - timedelta(days=now.weekday())
        from_date = monday.strftime('%Y-%m-%d')
    if not to_date:
        to_date = now.strftime('%Y-%m-%d')
    
    data = finnhub_request('/stock/filings', {
        'symbol': symbol,
        'from': from_date,
        'to': to_date
    })
    
    if data:
        # 只返回关注的文件类型，并且只返回本周内的文件
        today_str = now.strftime('%Y-%m-%d')
        this_week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
        
        filtered = []
        for f in data:
            if f.get('form') not in WATCHLIST['sec_forms']:
                continue
            
            filed_date = f.get('filedDate', '')
            # 只保留本周内的文件
            if filed_date >= this_week_start:
                filtered.append(f)
        
        return filtered
    return []

def is_filing_today(filed_date_str):
    """检查文件是否是今天的"""
    today = datetime.now().strftime('%Y-%m-%d')
    return filed_date_str == today

def load_state():
    """加载状态"""
    try:
        with open(STATE_PATH, 'r') as f:
            return json.load(f)
    except:
        return {
            'seen_filings': {},
            'seeded': False,
            'last_run': None
        }

def save_state(state):
    """保存状态"""
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def main():
    """主函数"""
    state = load_state()
    is_first_run = not state.get('seeded', False)
    
    print("=" * 60)
    print(f"📊 Finnhub 金融监控 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 1. 股价监控
    print("\n💰 股价监控:")
    print("-" * 60)
    
    price_alerts = []
    all_quotes = {}
    
    for ticker in WATCHLIST['tickers']:
        quote = get_stock_quote(ticker)
        if quote:
            all_quotes[ticker] = quote
            change_pct = quote.get('change_percent', 0) or 0
            emoji = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➖"
            
            print(f"{emoji} {ticker}: ${quote['current']:.2f} ({change_pct:+.2f}%)")
            
            # 检查预警
            if abs(change_pct) >= WATCHLIST['price_alert_threshold']:
                price_alerts.append({
                    'ticker': ticker,
                    'price': quote['current'],
                    'change_pct': change_pct,
                    'direction': '上涨' if change_pct > 0 else '下跌'
                })
        else:
            print(f"❌ {ticker}: 获取失败")
    
    # 2. SEC 文件监控
    print("\n📄 SEC 文件监控:")
    print("-" * 60)
    
    new_filings = []
    
    for ticker in WATCHLIST['tickers']:
        if is_first_run:
            print(f"  🆕 {ticker}: 首次运行，正在 seed...")
        else:
            print(f"  📊 {ticker}: 检查新文件...")
        
        filings = get_sec_filings(ticker)
        
        for filing in filings:
            access_num = filing.get('accessNumber')
            filed_date = filing.get('filedDate', '')
            
            if not access_num:
                continue
            
            # 严格检查：只处理本周内的文件
            this_week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
            if filed_date < this_week_start:
                continue  # 跳过旧文件
            
            if access_num in state['seen_filings']:
                continue
            
            filing_info = {
                'ticker': ticker,
                'form': filing.get('form'),
                'filed_date': filed_date,
                'accepted_date': filing.get('acceptedDate'),
                'filing_url': filing.get('filingUrl'),
                'report_url': filing.get('reportUrl'),
            }
            
            if is_first_run:
                print(f"     💾 SEED: {ticker} {filing_info['form']} ({filing_info['filed_date']})")
            else:
                print(f"     🔔 NEW: {ticker} {filing_info['form']} ({filing_info['filed_date']})")
                new_filings.append(filing_info)
            
            state['seen_filings'][access_num] = {
                **filing_info,
                'detected_at': datetime.now().isoformat()
            }
    
    # 更新状态
    state['seeded'] = True
    state['last_run'] = datetime.now().isoformat()
    save_state(state)
    
    # 3. 输出汇总
    print("\n" + "=" * 60)
    print("📋 监控汇总:")
    print("-" * 60)
    
    if price_alerts:
        print(f"\n🚨 股价预警 ({len(price_alerts)} 只):")
        for alert in price_alerts:
            print(f"   {alert['ticker']}: {alert['direction']} {abs(alert['change_pct']):.2f}%")
    else:
        print("\n✅ 股价无异常")
    
    if new_filings:
        print(f"\n🚨 新 SEC 文件 ({len(new_filings)} 个):")
        for f in new_filings[:5]:  # 只显示前5个
            print(f"   {f['ticker']} - {f['form']} ({f['filed_date']})")
        if len(new_filings) > 5:
            print(f"   ... 还有 {len(new_filings) - 5} 个")
    else:
        print("\n✅ 无新 SEC 文件")
    
    print("\n" + "=" * 60)
    
    # 4. 输出 JSON 供外部处理
    output = {
        'timestamp': datetime.now().isoformat(),
        'quotes': all_quotes,
        'price_alerts': price_alerts,
        'new_filings': new_filings,
    }
    
    print("\n📤 JSON_OUTPUT_START")
    print(json.dumps(output, indent=2, default=str))
    print("📤 JSON_OUTPUT_END")
    
    # 返回退出码
    if price_alerts or new_filings:
        sys.exit(2)  # 有预警
    else:
        sys.exit(0)  # 正常

if __name__ == '__main__':
    main()
