import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.expanduser("~/greenipath-bi"))
from ui import apply_styles, render_sidebar, page_header, kpi_card

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../greenipath.db")

def get_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Финансовая аналитика · GreenIPath",
                   page_icon=None, layout="wide", initial_sidebar_state="expanded")
apply_styles()
render_sidebar()
page_header("Финансовая аналитика",
            "Выручка по проектам · Динамика цен CO₂ · Реализованные и нереализованные единицы")

fin_df = get_data("""
    SELECT fi.*, p.project_name, p.project_type, p.standard,
           dp.period_number, dp.period_start
    FROM fact_credits_issued fi
    JOIN dim_project p ON fi.project_id=p.project_id
    JOIN dim_period dp ON fi.period_id=dp.period_id
    ORDER BY fi.issuance_date
""")
fin_df["year"] = pd.to_datetime(fin_df["issuance_date"]).dt.year
fin_df["margin"] = fin_df["avg_price_usd"] - fin_df["cost_per_credit_usd"]

total_rev    = fin_df["revenue_usd"].sum()
total_issued = fin_df["issued_credits"].sum()
total_sold   = fin_df["sold_credits"].sum()
unsold       = total_issued - total_sold
avg_price    = fin_df["avg_price_usd"].mean()
potential    = unsold * avg_price
best_margin  = fin_df.loc[fin_df["margin"].idxmax(),"project_name"].split("—")[0].strip()

st.markdown("<br>", unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
for col,label,value,sub in [
    (c1,"Суммарная выручка",      f"${total_rev/1000000:.2f}M",  "от реализации единиц"),
    (c2,"Средняя цена CO₂",       f"${avg_price:.2f}/т",         "по всем стандартам"),
    (c3,"Реализовано единиц",     f"{total_sold/1000:.0f}K т",   "верифицированных"),
    (c4,"Нереализованный запас",  f"{unsold/1000:.0f}K т CO₂",   f"потенциал ~${potential/1000000:.1f}M"),
    (c5,"Наибольшая маржа",       best_margin,                   "по спреду цена−себест."),
]:
    with col:
        st.markdown(kpi_card(label,value,sub), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col_l,col_r = st.columns([1,1], gap="medium")

with col_l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Выручка по годам и проектам, USD</div>', unsafe_allow_html=True)
    year_df = fin_df.groupby(["year","project_name"])["revenue_usd"].sum().reset_index()
    fig = px.bar(year_df, x="year", y="revenue_usd", color="project_name",
        color_discrete_sequence=["#1A3D2B","#2563EB","#B45309","#6D28D9","#6B7280"],
        labels={"year":"Год","revenue_usd":"Выручка (USD)","project_name":"Проект"},
        template="plotly_white")
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        legend=dict(font=dict(size=10), title=""))
    fig.update_xaxes(gridcolor="#F3F4F6", dtick=1)
    fig.update_yaxes(gridcolor="#F3F4F6", tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Динамика средней цены CO₂ по стандартам, USD/т</div>', unsafe_allow_html=True)
    price_df = fin_df.groupby(["year","standard"])["avg_price_usd"].mean().reset_index()
    fig2 = px.line(price_df, x="year", y="avg_price_usd", color="standard", markers=True,
        color_discrete_map={"Verra VCS":"#1A3D2B","Gold Standard":"#B45309","Plan Vivo":"#6D28D9"},
        labels={"year":"Год","avg_price_usd":"Цена (USD/т)","standard":"Стандарт"},
        template="plotly_white")
    fig2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        legend=dict(font=dict(size=10), title="Стандарт"))
    fig2.update_xaxes(gridcolor="#F3F4F6", dtick=1)
    fig2.update_yaxes(gridcolor="#F3F4F6")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col_l2,col_r2 = st.columns([1,1], gap="medium")

with col_l2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Структура выпущенных единиц по проектам</div>', unsafe_allow_html=True)
    struct_df = fin_df.groupby("project_name").agg(
        sold=("sold_credits","sum"), buffer=("buffer_credits","sum"),
        issued=("issued_credits","sum")).reset_index()
    struct_df["unsold"] = (struct_df["issued"]-struct_df["sold"]-struct_df["buffer"]).clip(lower=0)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Реализовано", x=struct_df["project_name"],
        y=struct_df["sold"], marker_color="#1A3D2B"))
    fig3.add_trace(go.Bar(name="Буферный резерв", x=struct_df["project_name"],
        y=struct_df["buffer"], marker_color="#A7C4A0"))
    fig3.add_trace(go.Bar(name="Нереализовано", x=struct_df["project_name"],
        y=struct_df["unsold"], marker_color="#FCA5A5"))
    fig3.update_layout(barmode="stack", template="plotly_white", height=300,
        margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)))
    fig3.update_xaxes(gridcolor="#F3F4F6", tickangle=-10)
    fig3.update_yaxes(gridcolor="#F3F4F6")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Маржа по проектам, USD/т CO₂</div>', unsafe_allow_html=True)
    margin_df = fin_df.groupby("project_name").agg(
        avg_price=("avg_price_usd","mean"), avg_cost=("cost_per_credit_usd","mean")).reset_index()
    margin_df["margin"] = (margin_df["avg_price"]-margin_df["avg_cost"]).round(2)
    margin_df["margin_pct"] = (margin_df["margin"]/margin_df["avg_price"]*100).round(1)
    margin_df = margin_df.sort_values("margin", ascending=False)
    for _, row in margin_df.iterrows():
        color = "#059669" if row["margin"]>4 else "#D97706"
        bar_w = min(int(row["margin"]/8*100),100)
        st.markdown(f"""
        <div class="row-item">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:600;color:#111827;">{row['project_name']}</div>
            <div style="font-size:11px;color:#6B7280;margin-top:2px;">
              Цена: ${row['avg_price']:.2f} · Себест.: ${row['avg_cost']:.2f}
            </div>
            <div style="margin-top:5px;background:#F3F4F6;border-radius:2px;height:4px;">
              <div style="background:{color};width:{bar_w}%;height:4px;border-radius:2px;"></div>
            </div>
          </div>
          <div style="margin-left:16px;text-align:right;">
            <div style="font-size:16px;font-weight:700;color:{color};">${row['margin']:.2f}</div>
            <div style="font-size:11px;color:#9CA3AF;">{row['margin_pct']}% маржа</div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Детализация транзакций выпуска и реализации</div>', unsafe_allow_html=True)
table_df = fin_df[["project_name","registry","issuance_date","issued_credits","sold_credits","avg_price_usd","revenue_usd"]].copy()
table_df.columns = ["Проект","Реестр","Дата выпуска","Выпущено (т CO₂)","Реализовано (т CO₂)","Цена (USD/т)","Выручка (USD)"]
st.dataframe(table_df, use_container_width=True, hide_index=True,
    column_config={
        "Выпущено (т CO₂)":    st.column_config.NumberColumn(format="%,.0f"),
        "Реализовано (т CO₂)": st.column_config.NumberColumn(format="%,.0f"),
        "Цена (USD/т)":        st.column_config.NumberColumn(format="$%.2f"),
        "Выручка (USD)":       st.column_config.NumberColumn(format="$%,.0f"),
    })
st.markdown('</div>', unsafe_allow_html=True)
