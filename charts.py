from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PRIMARY = "#2563EB"
SECONDARY = "#0F766E"
ACCENT = "#F59E0B"
PURPLE = "#7C3AED"
ROSE = "#E11D48"
COLOR_SEQ = [PRIMARY, SECONDARY, ACCENT, PURPLE, ROSE, "#16A34A", "#0891B2", "#64748B"]
COLOR_SCALE = ["#BFDBFE", "#93C5FD", "#60A5FA", "#2563EB", "#0EA5E9", "#0F766E"]
BLUE_SEQ = ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#0EA5E9", "#38BDF8", "#7DD3FC", "#BAE6FD"]
BAR_SCALE = ["#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6", "#2563EB", "#0F766E"]
HEATMAP_SCALE = "YlOrRd"
TEMPLATE = "plotly_white"


def empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template=TEMPLATE,
        height=340,
        annotations=[dict(text="暂无数据", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#64748B"))],
    )
    return fig


def apply_layout(fig: go.Figure, title: str, height: int = 370) -> go.Figure:
    fig.update_layout(
        title=title,
        template=TEMPLATE,
        height=height,
        margin=dict(l=64, r=58, t=62, b=62),
        colorway=COLOR_SEQ,
        legend_title_text="",
        font=dict(family="Microsoft YaHei, Arial", size=13),
        title_font=dict(size=17, color="#0F172A"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )
    fig.update_xaxes(automargin=True, title_standoff=10, gridcolor="#E2E8F0", zerolinecolor="#CBD5E1")
    fig.update_yaxes(automargin=True, title_standoff=10, gridcolor="#E2E8F0", zerolinecolor="#CBD5E1")
    return fig


def place_bottom_legend(fig: go.Figure, bottom: int = 96, font_size: int = 11) -> go.Figure:
    fig.update_layout(
        margin=dict(l=64, r=70, t=62, b=bottom),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(size=font_size),
        ),
    )
    return fig


def apply_doughnut_layout(fig: go.Figure, title: str, height: int = 430) -> go.Figure:
    fig = apply_layout(fig, title, height)
    fig.update_layout(
        margin=dict(l=28, r=28, t=58, b=92),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
    )
    return fig


def monthly_sales_line(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("月度销售趋势")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data["Month"], y=data["交易量"], name="交易量", marker_color="#BFDBFE", yaxis="y2", opacity=0.42))
    fig.add_trace(
        go.Scatter(
            x=data["Month"],
            y=data["销售额"],
            mode="lines+markers",
            name="销售额",
            line=dict(color=PRIMARY, width=4),
            marker=dict(size=8, color=PRIMARY, line=dict(color="#FFFFFF", width=1.5)),
        )
    )
    fig.update_layout(
        xaxis=dict(title="月份"),
        yaxis=dict(title="销售额", tickprefix="$"),
        yaxis2=dict(title="交易量", overlaying="y", side="right", showgrid=False, title_standoff=14),
        hovermode="x unified",
    )
    fig = apply_layout(fig, "月度销售趋势", 420)
    return place_bottom_legend(fig, bottom=86)


def monthly_category_area(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("月度品类销售结构")
    fig = px.area(
        data,
        x="Month",
        y="销售额",
        color="Product Category",
        color_discrete_sequence=COLOR_SEQ,
        hover_data={"交易量": ":,", "销量": ":,", "销售额": ":$,.2f"},
    )
    fig.update_yaxes(title="销售额", tickprefix="$")
    fig.update_xaxes(title="月份")
    return apply_layout(fig, "月度品类销售结构", 420)


def daily_sales_line(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("日度销售额变化")
    fig = px.line(data, x="DateOnly", y="销售额", markers=False, color_discrete_sequence=[SECONDARY])
    fig.update_traces(fill="tozeroy", fillcolor="rgba(15, 118, 110, 0.13)")
    fig.update_yaxes(title="销售额", tickprefix="$")
    fig.update_xaxes(title="日期")
    return apply_layout(fig, "日度销售额变化", 350)


def weekday_bar(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("星期销售分布")
    fig = px.bar(
        data,
        x="Weekday",
        y="销售额",
        color="销售额",
        color_continuous_scale=BAR_SCALE,
        hover_data={"交易量": ":,", "销量": ":,", "销售额": ":$,.2f"},
    )
    fig.update_coloraxes(showscale=False)
    fig.update_yaxes(title="销售额", tickprefix="$")
    fig.update_xaxes(title="星期")
    return apply_layout(fig, "星期销售分布", 350)


def category_bar(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("商品类别销售额排行")
    ordered = data.sort_values("销售额", ascending=True)
    fig = px.bar(
        ordered,
        x="销售额",
        y="Product Category",
        orientation="h",
        color="销售额",
        color_continuous_scale=BAR_SCALE,
        hover_data={"交易量": ":,", "销量": ":,", "销售额": ":$,.2f", "销售额占比": ":.2%"},
    )
    fig.update_coloraxes(showscale=False)
    fig.update_xaxes(title="销售额", tickprefix="$")
    fig.update_yaxes(title="商品类别")
    return apply_layout(fig, "商品类别销售额排行", max(380, min(560, 46 * len(ordered) + 110)))


def category_share_doughnut(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("商品类别销售额占比")
    fig = px.pie(data, values="销售额", names="Product Category", hole=0.56, color_discrete_sequence=BLUE_SEQ)
    fig.update_traces(
        marker=dict(colors=BLUE_SEQ),
        textposition="inside",
        texttemplate="%{percent:.0%}",
        insidetextorientation="radial",
        hovertemplate="%{label}<br>销售额：$%{value:,.2f}<br>占比：%{percent}<extra></extra>",
    )
    return apply_doughnut_layout(fig, "商品类别销售额占比")


def category_waterfall(data: pd.DataFrame, top_n: int = 6) -> go.Figure:
    if data.empty:
        return empty_figure("品类销售额贡献瀑布图")
    ordered = data.sort_values("销售额", ascending=False)
    top = ordered.head(top_n).copy()
    other_value = ordered.iloc[top_n:]["销售额"].sum()
    x = top["Product Category"].tolist()
    y = top["销售额"].tolist()
    if other_value > 0:
        x.append("其他品类")
        y.append(other_value)
    x.append("销售总额")
    y.append(sum(y))
    measure = ["relative"] * (len(x) - 1) + ["total"]

    fig = go.Figure(
        go.Waterfall(
            x=x,
            y=y,
            measure=measure,
            connector={"line": {"color": "#CBD5E1"}},
            increasing={"marker": {"color": SECONDARY}},
            totals={"marker": {"color": PRIMARY}},
            hovertemplate="%{x}<br>销售额：$%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_yaxes(title="销售额", tickprefix="$")
    fig.update_xaxes(title="商品类别", tickangle=-25)
    return apply_layout(fig, "品类销售额贡献瀑布图", 420)


def category_price_scatter(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("品类销量与销售额关系")
    fig = px.scatter(
        data,
        x="销量",
        y="销售额",
        size="平均单价",
        color="Product Category",
        color_discrete_sequence=COLOR_SEQ,
        hover_data={"交易量": ":,", "商品数": ":,", "平均单价": ":$,.2f", "销售额": ":$,.2f"},
    )
    fig.update_traces(marker=dict(line=dict(color="#FFFFFF", width=1.2)))
    fig.update_xaxes(title="销量")
    fig.update_yaxes(title="销售额", tickprefix="$")
    fig = apply_layout(fig, "品类销量与销售额关系", 470)
    return place_bottom_legend(fig, bottom=110, font_size=10)


def product_treemap(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("商品销售层级树图")
    fig = px.treemap(
        data,
        path=["Product Category", "Product Name"],
        values="销售额",
        color="平均单价",
        color_continuous_scale=COLOR_SCALE,
        hover_data={"交易量": ":,", "销量": ":,", "平均单价": ":$,.2f", "销售额": ":$,.2f"},
    )
    fig.update_traces(
        textinfo="label",
        textfont=dict(size=11),
        hovertemplate="%{label}<br>销售额：$%{value:,.2f}<br>平均单价：$%{color:,.2f}<extra></extra>",
    )
    fig.update_layout(uniformtext=dict(minsize=10, mode="hide"))
    return apply_layout(fig, "商品销售层级树图", 560)


def product_bar(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("商品销售额排行")
    ordered = data.sort_values("销售额", ascending=True)
    fig = px.bar(
        ordered,
        x="销售额",
        y="Product Name",
        orientation="h",
        color="Product Category",
        color_discrete_sequence=COLOR_SEQ,
        hover_data={"Product Category": True, "销量": ":,", "平均单价": ":$,.2f", "销售额": ":$,.2f"},
    )
    fig.update_xaxes(title="销售额", tickprefix="$")
    fig.update_yaxes(title="商品名称")
    return apply_layout(fig, "商品销售额排行", max(420, min(720, 34 * len(ordered) + 120)))


def price_band_bar(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("价格带销售贡献")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data["PriceBand"], y=data["销售额"], name="销售额", marker_color="#FDE68A", opacity=0.62))
    fig.add_trace(
        go.Scatter(
            x=data["PriceBand"],
            y=data["销量"],
            mode="lines+markers",
            name="销量",
            yaxis="y2",
            line=dict(color=PURPLE, width=4),
            marker=dict(size=8, color=PURPLE, line=dict(color="#FFFFFF", width=1.5)),
        )
    )
    fig.update_layout(
        xaxis=dict(title="价格带"),
        yaxis=dict(title="销售额", tickprefix="$"),
        yaxis2=dict(title="销量", overlaying="y", side="right", showgrid=False, title_standoff=14),
        hovermode="x unified",
    )
    fig = apply_layout(fig, "价格带销售贡献", 420)
    return place_bottom_legend(fig, bottom=86)


def region_price_heatmap(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("地区与价格带销售热力图")
    matrix = data.pivot_table(index="Region", columns="PriceBand", values="销售额", aggfunc="sum", fill_value=0)
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=[str(col) for col in matrix.columns],
            y=matrix.index,
            colorscale=HEATMAP_SCALE,
            hovertemplate="地区：%{y}<br>价格带：%{x}<br>销售额：$%{z:,.2f}<extra></extra>",
            colorbar=dict(title=dict(text="销售额", side="top"), thickness=14, len=0.78),
        )
    )
    fig.update_xaxes(title="价格带")
    fig.update_yaxes(title="地区")
    fig = apply_layout(fig, "地区与价格带销售热力图", 440)
    fig.update_layout(margin=dict(l=64, r=92, t=62, b=70))
    return fig


def price_band_doughnut(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("价格带销售额占比")
    fig = px.pie(data, values="销售额", names="PriceBand", hole=0.56, color_discrete_sequence=BLUE_SEQ)
    fig.update_traces(
        marker=dict(colors=BLUE_SEQ),
        textposition="inside",
        texttemplate="%{percent:.0%}",
        insidetextorientation="radial",
        hovertemplate="%{label}<br>销售额：$%{value:,.2f}<br>占比：%{percent}<extra></extra>",
    )
    return apply_doughnut_layout(fig, "价格带销售额占比")


def region_bar(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("地区销售额对比")
    ordered = data.sort_values("销售额", ascending=True)
    fig = px.bar(
        ordered,
        x="销售额",
        y="Region",
        orientation="h",
        color="销售额",
        color_continuous_scale=BAR_SCALE,
        hover_data={"交易量": ":,", "销量": ":,", "平均单笔销售额": ":$,.2f", "销售额": ":$,.2f"},
    )
    fig.update_coloraxes(showscale=False)
    fig.update_xaxes(title="销售额", tickprefix="$")
    fig.update_yaxes(title="地区")
    return apply_layout(fig, "地区销售额对比", 360)


def payment_doughnut(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("支付方式销售额占比")
    fig = px.pie(data, values="销售额", names="Payment Method", hole=0.56, color_discrete_sequence=BLUE_SEQ)
    fig.update_traces(
        marker=dict(colors=BLUE_SEQ),
        textposition="inside",
        texttemplate="%{percent:.0%}",
        insidetextorientation="radial",
        hovertemplate="%{label}<br>销售额：$%{value:,.2f}<br>占比：%{percent}<extra></extra>",
    )
    return apply_doughnut_layout(fig, "支付方式销售额占比")


def region_payment_sunburst(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("地区支付方式层级占比")
    fig = px.sunburst(
        data,
        path=["Region", "Payment Method"],
        values="销售额",
        color="销售额",
        color_continuous_scale=COLOR_SCALE,
        hover_data={"交易量": ":,", "销量": ":,", "销售额": ":$,.2f"},
    )
    return apply_layout(fig, "地区支付方式层级占比", 430)


def region_payment_bar(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("地区与支付方式交叉销售额")
    fig = px.bar(
        data,
        x="Region",
        y="销售额",
        color="Payment Method",
        barmode="group",
        color_discrete_sequence=COLOR_SEQ,
        hover_data={"交易量": ":,", "销量": ":,", "销售额": ":$,.2f"},
    )
    fig.update_yaxes(title="销售额", tickprefix="$")
    fig.update_xaxes(title="地区")
    fig = apply_layout(fig, "地区与支付方式交叉销售额", 470)
    return place_bottom_legend(fig, bottom=102, font_size=11)


def category_region_heatmap(data: pd.DataFrame) -> go.Figure:
    if data.empty:
        return empty_figure("品类与地区销售热力图")
    matrix = data.pivot_table(index="Product Category", columns="Region", values="销售额", aggfunc="sum", fill_value=0)
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=matrix.index,
            colorscale=HEATMAP_SCALE,
            hovertemplate="品类：%{y}<br>地区：%{x}<br>销售额：$%{z:,.2f}<extra></extra>",
            colorbar=dict(title=dict(text="销售额", side="top"), thickness=14, len=0.78),
        )
    )
    fig.update_xaxes(title="地区")
    fig.update_yaxes(title="商品类别")
    fig = apply_layout(fig, "品类与地区销售热力图", max(440, min(660, 42 * len(matrix.index) + 140)))
    fig.update_layout(margin=dict(l=84, r=92, t=62, b=70))
    return fig
