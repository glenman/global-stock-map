#!/usr/bin/env python3
"""获取贵金属数据 (新浪财经 + 东方财富) → data/metals.json"""
import json, re, os, subprocess

update_time = os.popen("TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S'").read().strip()
metals = []

# --- 新浪财经 (主源) ---
metal_config = {
    "hf_XAU": {"name": "伦敦金（现货黄金）", "region": "英国", "currency": "USD", "unit": "美元/盎司"},
    "hf_XAG": {"name": "伦敦银（现货白银）", "region": "英国", "currency": "USD", "unit": "美元/盎司"},
    "hf_GC":  {"name": "纽约黄金期货",       "region": "美国", "currency": "USD", "unit": "美元/盎司"},
    "hf_SI":  {"name": "纽约白银期货",       "region": "美国", "currency": "USD", "unit": "美元/盎司"},
}

try:
    sina_raw = subprocess.check_output([
        "curl", "-s", "--max-time", "15",
        "-H", "Referer: https://finance.sina.com.cn",
        "https://hq.sinajs.cn/list=hf_XAU,hf_XAG,hf_GC,hf_SI"
    ]).decode("gbk", errors="ignore")
except Exception as e:
    print(f"[新浪] 获取失败: {e}")
    sina_raw = ""

for code, meta in metal_config.items():
    pattern = rf'hq_str_{code}="([^"]*)"'
    m = re.search(pattern, sina_raw)
    if not m or not m.group(1):
        print(f"[新浪] 跳过 {meta['name']}: 无数据")
        continue
    fields = m.group(1).split(",")
    try:
        current = float(fields[0])
        prev_close = float(fields[7]) if fields[7] else current
        high = float(fields[4]) if fields[4] else current
        low = float(fields[5]) if fields[5] else current
        trade_time = fields[6]
        trade_date = fields[12]
        change_pct = ((current - prev_close) / prev_close) * 100 if prev_close else 0
        metals.append({
            "id": code, "name": meta["name"], "region": meta["region"], "area": "贵金属",
            "current": round(current, 2), "prev_close": round(prev_close, 2),
            "high": round(high, 2), "low": round(low, 2),
            "change": round(change_pct, 2),
            "currency": meta["currency"], "unit": meta["unit"],
            "trade_time": f"{trade_date} {trade_time}",
            "source": "sina"
        })
        print(f"[新浪] {meta['name']}: {current} ({change_pct:+.2f}%)")
    except Exception as e:
        print(f"[新浪] {meta['name']}: 解析错误 {e}")

# --- 东方财富 (备源: 国内期货) ---
em_items = [
    ("113.aum", "沪金主连", "中国", "CNY", "元/克"),
    ("113.agm", "沪银主连", "中国", "CNY", "元/千克"),
]
for secid, name, region, currency, unit in em_items:
    try:
        resp = subprocess.check_output([
            "curl", "-s", "--max-time", "10",
            f"https://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbbd1d0c&secid={secid}&fields=f43,f44,f45,f46,f57,f58,f170"
        ]).decode()
        d = json.loads(resp)
        data = d.get("data")
        if data and data.get("f43"):
            current_em = data["f43"] / 100
            high_em = data["f44"] / 100 if data.get("f44") else current_em
            low_em = data["f45"] / 100 if data.get("f45") else current_em
            open_em = data["f46"] / 100 if data.get("f46") else current_em
            change_em = data.get("f170", 0) / 100
            metals.append({
                "id": f"em_{secid}", "name": name, "region": region, "area": "贵金属",
                "current": round(current_em, 2), "prev_close": round(open_em, 2),
                "high": round(high_em, 2), "low": round(low_em, 2),
                "change": round(change_em, 2),
                "currency": currency, "unit": unit,
                "trade_time": update_time, "source": "eastmoney"
            })
            print(f"[东方财富] {name}: {current_em} ({change_em:+.2f}%)")
        else:
            print(f"[东方财富] {name}: 无数据")
    except Exception as e:
        print(f"[东方财富] {name}: {e}")

# 输出
output = {"update_time": update_time, "metals": metals}
os.makedirs("data", exist_ok=True)
with open("data/metals.json", "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n=== 贵金属数据完成: {len(metals)} 个品种 ===")
