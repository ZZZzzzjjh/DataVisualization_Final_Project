from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd


APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / ".env"
DEFAULT_API_BASE = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"


def _read_env_file() -> dict[str, str]:
    if not ENV_FILE.exists():
        return {}

    values: dict[str, str] = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _env_value(name: str, default: str = "") -> str:
    return os.environ.get(name) or _read_env_file().get(name, default)


def has_ai_config() -> bool:
    return bool(_env_value("DEEPSEEK_API_KEY") or _env_value("OPENAI_API_KEY"))


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _top_label(df: pd.DataFrame, group_col: str) -> tuple[str, float]:
    if df.empty:
        return "暂无", 0.0
    grouped = df.groupby(group_col)["Total Revenue"].sum().sort_values(ascending=False)
    if grouped.empty:
        return "暂无", 0.0
    return str(grouped.index[0]), float(grouped.iloc[0])


def build_local_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    if df.empty:
        return [{"title": "当前筛选无数据", "body": "请调整筛选条件后再查看智能洞察。", "accent": "muted"}]

    total_revenue = float(df["Total Revenue"].sum())
    transactions = len(df)
    units = int(df["Units Sold"].sum())
    avg_order = float(df["Total Revenue"].mean())
    top_category, top_category_revenue = _top_label(df, "Product Category")
    top_region, top_region_revenue = _top_label(df, "Region")
    top_payment, top_payment_revenue = _top_label(df, "Payment Method")

    monthly = df.groupby("Month")["Total Revenue"].sum().sort_index()
    if len(monthly) >= 2 and monthly.iloc[-2] != 0:
        change = (monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]
        trend_text = f"最近月份销售额较前一月变化 {change:+.1%}，需要结合促销、品类结构和地区贡献判断趋势是否可持续。"
    else:
        trend_text = "当前月份跨度不足，建议结合更多时间样本继续观察趋势稳定性。"

    category_share = top_category_revenue / total_revenue if total_revenue else 0
    region_share = top_region_revenue / total_revenue if total_revenue else 0
    payment_share = top_payment_revenue / total_revenue if total_revenue else 0

    return [
        {
            "title": "核心规模",
            "body": f"筛选后共有 {transactions:,} 笔交易、{units:,} 件销量，销售额为 {_money(total_revenue)}，平均单笔销售额为 {_money(avg_order)}。",
            "accent": "blue",
        },
        {
            "title": "主力品类",
            "body": f"{top_category} 是当前销售额最高的品类，贡献 {_money(top_category_revenue)}，占总销售额 {category_share:.1%}。",
            "accent": "teal",
        },
        {
            "title": "区域与支付",
            "body": f"{top_region} 是领先地区，占比 {region_share:.1%}；{top_payment} 是主要支付方式，占比 {payment_share:.1%}。",
            "accent": "orange",
        },
        {
            "title": "趋势提醒",
            "body": trend_text,
            "accent": "purple",
        },
    ]


def build_ai_context(df: pd.DataFrame, focus: str = "") -> str:
    if df.empty:
        return "当前筛选结果为空。"

    total_revenue = float(df["Total Revenue"].sum())
    summary = {
        "交易量": len(df),
        "总销量": int(df["Units Sold"].sum()),
        "销售额": round(total_revenue, 2),
        "平均单笔销售额": round(float(df["Total Revenue"].mean()), 2),
        "日期范围": f"{df['DateOnly'].min().date()} 至 {df['DateOnly'].max().date()}",
    }

    def top_table(group_cols: str | list[str], limit: int = 6) -> list[dict[str, object]]:
        grouped = (
            df.groupby(group_cols, as_index=False)
            .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
            .sort_values("销售额", ascending=False)
            .head(limit)
        )
        if total_revenue:
            grouped["销售额占比"] = grouped["销售额"] / total_revenue
        return grouped.round({"销售额": 2, "销售额占比": 4}).to_dict("records")

    context = {
        "用户关注点": focus or "请综合分析整体表现、结构特征、风险点和行动建议。",
        "总体指标": summary,
        "品类排行": top_table("Product Category"),
        "地区排行": top_table("Region"),
        "支付方式排行": top_table("Payment Method"),
        "价格带排行": top_table("PriceBand"),
        "地区支付交叉Top": top_table(["Region", "Payment Method"], limit=8),
    }
    return json.dumps(context, ensure_ascii=False, indent=2)


def generate_ai_insight(df: pd.DataFrame, focus: str = "") -> str:
    api_key = _env_value("DEEPSEEK_API_KEY") or _env_value("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("未在 .env 或环境变量中找到 DEEPSEEK_API_KEY / OPENAI_API_KEY。")

    api_base = _env_value("DEEPSEEK_API_BASE", DEFAULT_API_BASE)
    model = _env_value("DEEPSEEK_MODEL", DEFAULT_MODEL)
    prompt = build_ai_context(df, focus)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一名电商数据分析师。请用中文输出，结论要基于用户提供的数据摘要，不要编造外部事实。",
            },
            {
                "role": "user",
                "content": (
                    "请根据以下电商销售数据生成仪表盘AI洞察。输出格式："
                    "1. 关键结论；2. 异常或风险；3. 可执行建议。每部分用短句，避免空泛。\n\n"
                    f"{prompt}"
                ),
            },
        ],
        "temperature": 0.35,
        "max_tokens": 900,
        "stream": False,
    }
    request = urllib.request.Request(
        api_base,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"AI接口请求失败：HTTP {exc.code} {detail[:240]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"AI接口连接失败：{exc.reason}") from exc

    try:
        return result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("AI接口返回格式异常，请检查模型或接口地址配置。") from exc
