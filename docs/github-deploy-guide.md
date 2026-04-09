# GitHub 部署、运行与 Action 配置指南

## 📦 仓库信息

- **仓库**: https://github.com/glenman/global-stock-map
- **访问地址**: https://glenman.github.io/global-stock-map
- **分支**: main
- **部署方式**: GitHub Pages（从main分支根目录部署）

---

## 🚀 如何发布到 GitHub

### 首次设置

```bash
# 1. 克隆仓库（如果还没有）
git clone https://github.com/glenman/global-stock-map.git
cd global-stock-map

# 2. 创建 data 目录（存放自动生成的数据）
mkdir -p data

# 3. 提交初始代码
git add .
git commit -m "init: global stock map"
git push origin main
```

### 日常更新流程

```bash
# 修改代码后
git add .
git commit -m "描述修改内容"
git push origin main
```

GitHub Pages 会在 push 后自动部署（通常1-2分钟生效）。

---

## ⚙️ GitHub Pages 配置

1. 进入仓库 → **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` / `/ (root)`
4. 点击 **Save**

部署成功后访问 `https://<username>.github.io/global-stock-map/`

---

## 🤖 GitHub Actions 自动数据更新

### Action 配置文件

**文件位置**: `.github/workflows/update-data.yml`

### 触发方式

```yaml
on:
  schedule:
    - cron: '*/30 * * * *'    # 每30分钟自动运行
  workflow_dispatch:            # 支持手动触发
```

### 运行流程

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Action (ubuntu-latest)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: Checkout 代码                                  │
│     ↓                                                   │
│  Step 2: 获取全球股票指数                               │
│     ├─ 遍历35+个Yahoo Finance指数                       │
│     ├─ 通过 allorigins.win 代理（解决CORS）             │
│     ├─ parse_yahoo.py 解析JSON → 提取收盘价+涨跌幅     │
│     └─ 生成 data/indices.json                          │
│     ↓                                                   │
│  Step 3: 获取贵金属行情                                │
│     ├─ 新浪财经: 伦敦金/银、纽约期金/银                 │
│     ├─ 东方财富: 沪金/沪银主连                          │
│     └─ 生成 data/metals.json                           │
│     ↓                                                   │
│  Step 4: Git Commit & Push                              │
│     ├─ git add data/indices.json data/metals.json       │
│     ├─ git commit -m "data: update YYYY-MM-DD HH:MM"   │
│     └─ git push → 触发 GitHub Pages 重新部署            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 手动触发 Action

1. 进入仓库 → **Actions** 标签页
2. 左侧选择 **"Update Stock & Metals Data"**
3. 点击 **"Run workflow"** → **"Run workflow"** 按钮
4. 等待运行完成（通常2-3分钟）

### 查看运行日志

1. 进入仓库 → **Actions** 标签页
2. 点击最近的运行记录
3. 展开 "Fetch Stock Indices" / "Fetch Precious Metals" 查看详细日志

---

## 🔧 Action 配置详解

### Yahoo Finance 数据获取

```bash
# 通过 allorigins 代理访问 Yahoo Finance（解决CORS和IP限制）
url="https://api.allorigins.win/raw?url=https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=2d"

# 解析返回的JSON，提取最近两天收盘价
echo "$response" | python3 scripts/parse_yahoo.py
# 输出格式: "当前价|涨跌幅"
```

**支持的指数**: 标普500、道琼斯、纳斯达克、日经225、德国DAX等35+个

### 新浪财经数据获取（贵金属）

```bash
# 请求贵金属数据（需带Referer）
curl -s -H "Referer: https://finance.sina.com.cn" \
  "https://hq.sinajs.cn/list=hf_XAU,hf_XAG,hf_GC,hf_SI"
```

**支持**: 伦敦金/银、纽约期金/银（4个品种）

### 东方财富数据获取（国内期货）

```bash
curl -s "https://push2.eastmoney.com/api/qt/stock/get?ut=...&secid=113.aum&fields=f43,f44,f45,f46,f57,f58,f170"
```

**支持**: 沪金主连、沪银主连（2个品种）

---

## ⚠️ 已知限制与解决方案

### 1. Yahoo Finance 对 GitHub Actions IP 限流

**现象**: 中国相关指数（上证、深证、恒生）频繁获取失败

**解决方案**: 改用新浪财经API获取中国指数
- 参考文档: `memory/china-stock-api-solution.md`
- API: `https://hq.sinajs.cn/list=sh000001,sz399001,hkHSI`
- 需要 Header: `Referer: https://finance.sina.com.cn`
- 返回编码: GBK

**实施方法**: 修改 `update-data.yml`，在获取 Yahoo 数据之前先从新浪获取中国指数，写入 indices.json

### 2. allorigins.win 代理不稳定

**现象**: 偶尔出现代理超时

**备选方案**:
- 使用 `corsproxy.io`
- 使用自建代理
- 直接请求（GitHub Actions 有时可以直连）

### 3. 数据更新延迟

- Action 每30分钟运行一次
- 每次运行约2-3分钟
- 实际数据延迟约30-35分钟

---

## 📝 如何修改 Action

### 修改更新频率

编辑 `.github/workflows/update-data.yml`:

```yaml
on:
  schedule:
    - cron: '0 */1 * * *'    # 每1小时
    - cron: '*/15 * * * *'   # 每15分钟
    - cron: '0 9,15,21 * * *' # 每天9:00、15:00、21:00（北京时间）
```

### 添加新指数

在 `update-data.yml` 的 `YAHOO_INDICES` 数组中添加:

```bash
"^NEW_INDEX|指数名称|国家|区域|货币"
```

### 添加新贵金属品种

编辑 `scripts/fetch_metals.py`，在 `metal_config` 或 `em_items` 中添加配置。

---

## 🔐 权限配置

Action 需要 `contents: write` 权限来提交数据:

```yaml
permissions:
  contents: write
```

**无需额外配置** — 此权限已在 workflow 文件中声明，GitHub 默认允许。

如果 push 失败，检查:
1. 仓库 Settings → Actions → General → Workflow permissions
2. 确保选择了 **"Read and write permissions"**

---

*小龙虾 🦞 - 2026-04-09*
