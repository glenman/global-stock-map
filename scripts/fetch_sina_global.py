#!/usr/bin/env python3
"""从新浪财经获取全球股票指数"""
import subprocess, json, re, os

update_time = os.popen("TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S'").read().strip()

# 新浪财经全球指数配置
sina_indices = {
    # 北美洲
    "int_dji": {"name": "道琼斯", "region": "美国", "area": "北美洲", "currency": "USD"},
    "int_nasdaq": {"name": "纳斯达克", "region": "美国", "area": "北美洲", "currency": "USD"},
    "int_sp500": {"name": "标普500", "region": "美国", "area": "北美洲", "currency": "USD"},
    # 欧洲
    "int_ftse": {"name": "富时100", "region": "英国", "area": "欧洲", "currency": "GBP"},
    # 亚洲
    "int_nikkei": {"name": "日经225", "region": "日本", "area": "亚洲", "currency": "JPY"},
    "rt_hkHSI": {"name": "恒生指数", "region": "香港", "area": "亚洲", "currency": "HKD"},
    # 中国大陆
    "sh000001": {"name": "上证指数", "region": "中国", "area": "亚洲", "currency": "CNY"},
    "sz399001": {"name": "深证成指", "region": "中国", "area": "亚洲", "currency": "CNY"},
    "sh000300": {"name": "沪深300", "region": "中国", "area": "亚洲", "currency": "CNY"},
    "sh000016": {"name": "上证50", "region": "中国", "area": "亚洲", "currency": "CNY"},
    "sz399006": {"name": "创业板指", "region": "中国", "area": "亚洲", "currency": "CNY"},
}

indices = []

try:
    codes = ",".join(sina_indices.keys())
    raw = subprocess.check_output([
        "curl", "-s", "--max-time", "10",
        "-H", "Referer: https://finance.sina.com.cn",
        f"https://hq.sinajs.cn/list={codes}"
    ]).decode("gbk", errors="ignore")

    for code, meta in sina_indices.items():
        pattern = rf'hq_str_{code}="([^"]*)"'
        m = re.search(pattern, raw)
        if not m or not m.group(1):
            print(f"[新浪] 跳过 {meta['name']}: 无数据")
            continue

        fields = m.group(1).split(",")
        try:
            # 新浪格式:
            # 标准格式: 名称,当前价,涨跌点数,涨跌幅%
            # rt_格式: 代码,名称,当前价,昨收,最高,最低,开盘,涨跌点数,涨跌幅%
            # 中国股票格式: 名称,开盘,昨收,当前,最高,最低,...
            
            if code.startswith("rt_"):
                # rt_ 格式 (如 rt_hkHSI)
                if len(fields) >= 3 and fields[2]:
                    current = float(fields[2])
                    change_pct = float(fields[8]) if len(fields) > 8 and fields[8] else 0
                    indices.append({
                        "id": code,
                        "name": meta["name"],
                        "region": meta["region"],
                        "area": meta["area"],
                        "value": current,
                        "change": change_pct,
                        "currency": meta["currency"]
                    })
                    print(f"[新浪] {meta['name']}: {current:.2f} ({change_pct:+.2f}%)")
            
            elif code.startswith("sh") or code.startswith("sz"):
                # 中国股票指数格式: 名称,开盘,昨收,当前,最高,最低,...
                if len(fields) >= 4 and fields[2] and fields[3]:
                    current = float(fields[3])
                    prev_close = float(fields[2])
                    if prev_close > 0:
                        change_pct = ((current - prev_close) / prev_close) * 100
                    else:
                        change_pct = 0
                    indices.append({
                        "id": code,
                        "name": meta["name"],
                        "region": meta["region"],
                        "area": meta["area"],
                        "value": current,
                        "change": round(change_pct, 2),
                        "currency": meta["currency"]
                    })
                    print(f"[新浪] {meta['name']}: {current:.2f} ({change_pct:+.2f}%)")
            
            else:
                # 标准格式 (如 int_dji, int_nasdaq)
                if len(fields) >= 4 and fields[1]:
                    current = float(fields[1])
                    change_pct = float(fields[3]) if fields[3] else 0
                    indices.append({
                        "id": code,
                        "name": meta["name"],
                        "region": meta["region"],
                        "area": meta["area"],
                        "value": current,
                        "change": change_pct,
                        "currency": meta["currency"]
                    })
                    print(f"[新浪] {meta['name']}: {current:.2f} ({change_pct:+.2f}%)")
        except Exception as e:
            print(f"[新浪] {meta['name']}: 解析错误 {e}")
except Exception as e:
    print(f"[新浪] 获取失败: {e}")

output = {"update_time": update_time, "indices": indices, "count": len(indices)}
os.makedirs("data", exist_ok=True)
with open("data/indices.json", "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n=== 股票指数数据完成: {len(indices)} 个 ===")
