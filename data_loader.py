from __future__ import annotations

from pathlib import Path

import pandas as pd


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
RAW_CSV = DATA_DIR / "online_sales_data.csv"

WEEKDAY_ORDER = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
PRICE_BAND_ORDER = ["0-50", "50-100", "100-300", "300-500", "500-1000", "1000以上"]
PRICE_BINS = [0, 50, 100, 300, 500, 1000, float("inf")]


def _read_raw_csv() -> pd.DataFrame:
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_CSV}")
    return pd.read_csv(RAW_CSV)


def _clean_text(series: pd.Series, default: str = "未知") -> pd.Series:
    return series.fillna(default).astype(str).str.strip().replace({"": default, "nan": default, "None": default})


def _money(value: float) -> str:
    return f"${value:,.2f}"


def load_sales_data() -> pd.DataFrame:
    raw = _read_raw_csv()
    raw.columns = [c.strip() for c in raw.columns]

    expected_cols = {
        "Transaction ID",
        "Date",
        "Product Category",
        "Product Name",
        "Units Sold",
        "Unit Price",
        "Total Revenue",
        "Region",
        "Payment Method",
    }
    missing = expected_cols.difference(raw.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    df = raw.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Units Sold", "Unit Price", "Total Revenue"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["Transaction ID", "Product Category", "Product Name", "Region", "Payment Method"]:
        df[col] = _clean_text(df[col])

    df = df[
        df["Date"].notna()
        & df["Units Sold"].gt(0)
        & df["Unit Price"].gt(0)
        & df["Total Revenue"].gt(0)
    ].copy()

    df["DateOnly"] = pd.to_datetime(df["Date"].dt.date)
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["WeekdayNum"] = df["Date"].dt.weekday + 1
    df["Weekday"] = df["WeekdayNum"].map(dict(enumerate(WEEKDAY_ORDER, start=1)))
    df["PriceBand"] = pd.cut(
        df["Unit Price"],
        bins=PRICE_BINS,
        labels=PRICE_BAND_ORDER,
        right=False,
        include_lowest=True,
    ).astype(str)
    df["RevenueCheck"] = df["Units Sold"] * df["Unit Price"]
    df["RevenueDiff"] = df["Total Revenue"] - df["RevenueCheck"]

    return df.sort_values(["Date", "Transaction ID"]).reset_index(drop=True)


def filter_sales(
    df: pd.DataFrame,
    date_range: tuple[pd.Timestamp, pd.Timestamp] | None,
    categories: list[str],
    price_bands: list[str],
    regions: list[str],
    payments: list[str],
) -> pd.DataFrame:
    out = df.copy()
    if date_range:
        start, end = date_range
        out = out[(out["DateOnly"] >= start) & (out["DateOnly"] <= end)]
    if categories:
        out = out[out["Product Category"].isin(categories)]
    if price_bands:
        out = out[out["PriceBand"].isin(price_bands)]
    if regions:
        out = out[out["Region"].isin(regions)]
    if payments:
        out = out[out["Payment Method"].isin(payments)]
    return out


def kpi_metrics(df: pd.DataFrame) -> dict[str, str]:
    if df.empty:
        return {"交易量": "0", "总销量": "0", "销售额": "$0.00", "平均单笔销售额": "$0.00", "商品类别": "0"}
    return {
        "交易量": f"{len(df):,}",
        "总销量": f"{int(df['Units Sold'].sum()):,}",
        "销售额": _money(float(df["Total Revenue"].sum())),
        "平均单笔销售额": _money(float(df["Total Revenue"].mean())),
        "商品类别": f"{df['Product Category'].nunique():,}",
    }


def load_summary() -> pd.DataFrame:
    df = load_sales_data()
    return pd.DataFrame(
        [
            ["数据记录数", f"{len(df):,}"],
            ["日期范围", f"{df['DateOnly'].min().date()} 至 {df['DateOnly'].max().date()}"],
            ["商品类别数", df["Product Category"].nunique()],
            ["商品名称数", df["Product Name"].nunique()],
            ["销售地区数", df["Region"].nunique()],
            ["支付方式数", df["Payment Method"].nunique()],
            ["总销量", f"{int(df['Units Sold'].sum()):,}"],
            ["销售总额", _money(float(df["Total Revenue"].sum()))],
            ["平均单笔销售额", _money(float(df["Total Revenue"].mean()))],
            ["数据来源", "Kaggle: Online Sales Dataset - Popular Marketplace Data"],
        ],
        columns=["指标", "数值"],
    )


def load_field_dictionary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Transaction ID", "交易编号", "单笔在线销售交易的唯一标识"],
            ["Date", "交易日期", "订单交易发生日期"],
            ["Product Category", "商品类别", "交易商品所属类别"],
            ["Product Name", "商品名称", "具体售出商品名称"],
            ["Units Sold", "销售数量", "单笔交易售出的商品件数"],
            ["Unit Price", "商品单价", "单件商品销售价格"],
            ["Total Revenue", "销售额", "单笔交易产生的销售收入"],
            ["Region", "销售地区", "交易归属的市场区域"],
            ["Payment Method", "支付方式", "交易使用的支付工具"],
            ["Month/Weekday", "时间衍生字段", "由交易日期提取，用于趋势与周期分析"],
            ["PriceBand", "价格带", "由商品单价分组，用于价格结构分析"],
        ],
        columns=["字段名", "中文含义", "说明"],
    )


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Month", as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
        .sort_values("Month")
    )


def monthly_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Month", "Product Category"], as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
        .sort_values(["Month", "销售额"], ascending=[True, False])
    )


def daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("DateOnly", as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
        .sort_values("DateOnly")
    )


def weekday_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = (
        df.groupby(["WeekdayNum", "Weekday"], as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
        .sort_values("WeekdayNum")
    )
    return data


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = (
        df.groupby("Product Category", as_index=False)
        .agg(
            交易量=("Transaction ID", "count"),
            销量=("Units Sold", "sum"),
            销售额=("Total Revenue", "sum"),
            平均单价=("Unit Price", "mean"),
            商品数=("Product Name", "nunique"),
        )
        .sort_values("销售额", ascending=False)
    )
    total = data["销售额"].sum()
    data["销售额占比"] = data["销售额"] / total if total else 0
    return data


def product_summary(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    return (
        df.groupby(["Product Name", "Product Category"], as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"), 平均单价=("Unit Price", "mean"))
        .sort_values("销售额", ascending=False)
        .head(top_n)
    )


def product_tree_summary(df: pd.DataFrame, top_n: int = 35) -> pd.DataFrame:
    return (
        df.groupby(["Product Category", "Product Name"], as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"), 平均单价=("Unit Price", "mean"))
        .sort_values("销售额", ascending=False)
        .head(top_n)
    )


def price_band_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = (
        df.groupby("PriceBand", as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"), 平均单价=("Unit Price", "mean"))
    )
    data["PriceBand"] = pd.Categorical(data["PriceBand"], categories=PRICE_BAND_ORDER, ordered=True)
    data = data.sort_values("PriceBand").reset_index(drop=True)
    total = data["销售额"].sum()
    data["销售额占比"] = data["销售额"] / total if total else 0
    return data


def region_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Region", as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"), 平均单笔销售额=("Total Revenue", "mean"))
        .sort_values("销售额", ascending=False)
    )


def payment_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Payment Method", as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
        .sort_values("销售额", ascending=False)
    )


def region_payment_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Region", "Payment Method"], as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
        .sort_values(["Region", "销售额"], ascending=[True, False])
    )


def region_price_summary(df: pd.DataFrame) -> pd.DataFrame:
    data = (
        df.groupby(["Region", "PriceBand"], as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
    )
    data["PriceBand"] = pd.Categorical(data["PriceBand"], categories=PRICE_BAND_ORDER, ordered=True)
    return data.sort_values(["Region", "PriceBand"]).reset_index(drop=True)


def category_region_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Product Category", "Region"], as_index=False)
        .agg(交易量=("Transaction ID", "count"), 销量=("Units Sold", "sum"), 销售额=("Total Revenue", "sum"))
        .sort_values(["Product Category", "销售额"], ascending=[True, False])
    )
