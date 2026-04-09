# 全球股票指数地图 - 项目总览

## 📌 项目简介

一个全球股票指数实时展示页面，覆盖7大洲35+个主要股票指数 + 贵金属行情（黄金/白银），每30分钟自动更新数据，通过GitHub Pages部署。

**在线访问**: https://glenman.github.io/global-stock-map

---

## 🏗️ 项目架构

```
global-stock-map/
├── index.html                    # 前端展示页（纯静态，无框架）
├── data/
│   ├── indices.json              # 股票指数数据（自动生成）
│   └── metals.json               # 贵金属行情数据（自动生成）
├── scripts/
│   ├── parse_yahoo.py            # Yahoo Finance JSON解析器
│   └── fetch_metals.py           # 贵金属数据采集（新浪+东方财富）
├── .github/workflows/
│   ├── update-data.yml           # 主数据更新Action（每30分钟）
│   └── test-simple.yml           # 测试Action（手动触发）
└── docs/                         # 项目文档
    ├── README.md
    ├── project-summary.md        # 本文件
    └── github-deploy-guide.md    # 部署指南
```

---

## 🔧 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | 原生HTML/CSS/JS | 无框架依赖，单文件完成 |
| 数据源 | Yahoo Finance | 全球35+股票指数 |
| 数据源 | 新浪财经 | 贵金属现货+期货 |
| 数据源 | 东方财富 | 国内沪金/沪银期货 |
| 部署 | GitHub Pages | 静态托管，自动部署 |
| CI/CD | GitHub Actions | 每30分钟自动更新数据 |

---

## 📊 数据覆盖

### 股票指数（35+个）

| 区域 | 指数 |
|------|------|
| 🌎 北美洲 | 标普500、道琼斯、纳斯达克、多伦多综指、墨西哥IPC |
| 🌎 南美洲 | 巴西BOVESPA、阿根廷MERVAL |
| 🌍 欧洲 | 富时100、德国DAX、法国CAC40、意大利MIB、西班牙IBEX35、瑞士SMI、荷兰AEX |
| 🌏 亚洲 | 上证、深证、沪深300、上证50、创业板、中小板、日经225、恒生、台湾加权、韩国KOSPI、印度NIFTY50/SENSEX、印尼、泰国、马来西亚、新加坡、菲律宾 |
| 🌏 大洋洲 | 澳洲ASX200、新西兰NZX50 |
| 🌏 中东 | 沙特TASI、以色列TA125 |
| 🌍 非洲 | 南非JSE |

### 贵金属（6个品种）

| 品种 | 数据源 |
|------|--------|
| 伦敦金（现货黄金）| 新浪财经 |
| 伦敦银（现货白银）| 新浪财经 |
| 纽约黄金期货 | 新浪财经 |
| 纽约白银期货 | 新浪财经 |
| 沪金主连 | 东方财富 |
| 沪银主连 | 东方财富 |

---

## 🔄 数据流转

```
GitHub Actions (每30分钟)
    │
    ├─ Yahoo Finance API ──→ parse_yahoo.py ──→ data/indices.json
    │
    ├─ 新浪财经 API ──→ fetch_metals.py ──┐
    │                                       ├─→ data/metals.json
    └─ 东方财富 API ──→ fetch_metals.py ──┘
    │
    └─ git commit & push → GitHub Pages 自动部署
```

---

## 🎨 前端特性

- **实时状态**: 根据交易所交易时间显示"交易中/已收盘"状态
- **夏令时支持**: 自动处理美国/欧洲夏令时切换
- **筛选功能**: 按涨跌筛选、按名称/地区搜索
- **贵金属模块**: 独立展示贵金属实时行情
- **响应式设计**: 适配手机/平板/桌面
- **自动刷新**: 数据每30分钟通过GitHub Action更新

---

## ⚠️ 已知问题与优化方向

### 数据源问题
- **Yahoo Finance对GitHub Actions IP限流** — 中国相关指数（上证、深证、恒生）频繁失败
- **解决方案已记录** — 详见 `memory/china-stock-api-solution.md`，计划改用新浪财经API获取中国指数

### 优化方向
- [ ] 将中国指数数据源从Yahoo切换到新浪财经
- [ ] 添加更多技术指标（K线图、均线）
- [ ] 支持自定义关注列表
- [ ] 添加汇率数据
- [ ] 暗色/亮色主题切换
- [ ] 添加PWA支持

---

*小龙虾 🦞 - 2026-04-09*
