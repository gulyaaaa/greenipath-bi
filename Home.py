import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.expanduser("~/greenipath-bi"))
from ui import apply_styles, render_sidebar, page_header, kpi_card

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "greenipath.db")

def get_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="GreenIPath Carbon BI", page_icon=None,
                   layout="wide", initial_sidebar_state="expanded")
apply_styles()
render_sidebar()

page_header(
    "Портфельный обзор",
    "GreenIPath Carbon BI — сводные показатели по всем углеродным проектам",
    "По состоянию на 22.06.2026"
)

# KPI
total_co2 = get_data("SELECT SUM(eligible_credits_tco2) as v FROM fact_carbon_calc")["v"][0]
total_rev  = get_data("SELECT SUM(revenue_usd) as v FROM fact_credits_issued")["v"][0]
total_sold = get_data("SELECT SUM(sold_credits) as v FROM fact_credits_issued")["v"][0]
avg_price  = get_data("SELECT AVG(avg_price_usd) as v FROM fact_credits_issued")["v"][0]
active     = get_data("SELECT COUNT(*) as v FROM dim_project WHERE status='Активный'")["v"][0]
attention  = get_data("SELECT COUNT(*) as v FROM dim_period WHERE status IN ('На верификации','Мониторинг')")["v"][0]

c1,c2,c3,c4,c5,c6 = st.columns(6)
cards = [
    (c1, "Выпущено единиц CO₂",       f"{total_co2/1000:.0f}K т",   "совокупно по портфелю",  ""),
    (c2, "Суммарная выручка",          f"${total_rev/1000000:.1f}M", "от реализации единиц",   ""),
    (c3, "Реализовано единиц",         f"{total_sold/1000:.0f}K т",  "верифицированных",       ""),
    (c4, "Средняя цена CO₂",           f"${avg_price:.2f}/т",        "по всем стандартам",     ""),
    (c5, "Активных проектов",          str(int(active)),             "из 5 в портфеле",        ""),
    (c6, "Требуют внимания",           str(int(attention)),          "периодов мониторинга",   "kpi-card-warn"),
]
for col, label, value, sub, cls in cards:
    with col:
        st.markdown(kpi_card(label, value, sub, cls), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Проекты + Выручка
col_l, col_r = st.columns([1,1], gap="medium")

with col_l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Проекты портфеля</div>', unsafe_allow_html=True)

    projects_df = get_data("""
        SELECT project_name, country, project_type, standard, status, investment_usd
        FROM dim_project
    """)
    badge_map = {
        "Активный":       ("badge-green",  "Активный"),
        "На верификации": ("badge-yellow", "Верификация"),
        "Мониторинг":     ("badge-blue",   "Мониторинг"),
        "Разработка":     ("badge-gray",   "Разработка"),
    }
    for _, row in projects_df.iterrows():
        cls, lbl = badge_map.get(row["status"], ("badge-gray", row["status"]))
        st.markdown(f"""
        <div class="row-item">
          <div>
            <div style="font-size:13px;font-weight:600;color:#111827;">{row['project_name']}</div>
            <div style="font-size:11px;color:#6B7280;margin-top:2px;">
              {row['country']} &nbsp;·&nbsp; {row['project_type']} &nbsp;·&nbsp; {row['standard']}
            </div>
          </div>
          <div style="text-align:right;">
            <span class="badge {cls}">{lbl}</span>
            <div style="font-size:11px;color:#9CA3AF;margin-top:3px;">
              Инвестиции: ${row['investment_usd']/1000000:.1f}M
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Выручка по проектам, USD</div>', unsafe_allow_html=True)

    rev_df = get_data("""
        SELECT p.project_name, SUM(fi.revenue_usd) as revenue, p.project_type
        FROM fact_credits_issued fi
        JOIN dim_project p ON fi.project_id = p.project_id
        GROUP BY p.project_id ORDER BY revenue DESC
    """)
    fig = px.bar(rev_df, x="revenue", y="project_name", orientation="h",
        color="project_type",
        color_discrete_map={
            "Лесной":"#1A3D2B","ВИЭ — Ветер":"#2563EB",
            "ВИЭ — Солнце":"#B45309","Торфяники":"#6D28D9","Отходы":"#6B7280"
        },
        labels={"revenue":"Выручка (USD)","project_name":"","project_type":"Тип проекта"},
        template="plotly_white"
    )
    fig.update_layout(height=310, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        legend=dict(font=dict(size=10), title=""))
    fig.update_xaxes(gridcolor="#F3F4F6", tickformat="$,.0f")
    fig.update_yaxes(gridcolor="#F3F4F6")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# CO₂ + ROI
col_l2, col_r2 = st.columns([1,1], gap="medium")

with col_l2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Структура углеродных единиц по проектам</div>', unsafe_allow_html=True)

    co2_df = get_data("""
        SELECT p.project_name,
               SUM(fc.eligible_credits_tco2) as credits,
               SUM(fc.buffer_tco2) as buffer
        FROM fact_carbon_calc fc
        JOIN dim_project p ON fc.project_id = p.project_id
        GROUP BY p.project_id ORDER BY credits DESC
    """)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="К реализации", y=co2_df["project_name"],
        x=co2_df["credits"], orientation="h", marker_color="#1A3D2B"))
    fig2.add_trace(go.Bar(name="Буферный резерв", y=co2_df["project_name"],
        x=co2_df["buffer"], orientation="h", marker_color="#A7C4A0"))
    fig2.update_layout(barmode="stack", template="plotly_white",
        height=270, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)))
    fig2.update_xaxes(gridcolor="#F3F4F6")
    fig2.update_yaxes(gridcolor="#F3F4F6")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Рейтинг проектов по ROI</div>', unsafe_allow_html=True)

    roi_df = get_data("""
        SELECT p.project_name,
               SUM(fi.revenue_usd) as revenue,
               p.investment_usd,
               ROUND((SUM(fi.revenue_usd)-p.investment_usd)/p.investment_usd*100,1) as roi_pct
        FROM fact_credits_issued fi
        JOIN dim_project p ON fi.project_id=p.project_id
        GROUP BY p.project_id ORDER BY roi_pct DESC
    """)
    for _, row in roi_df.iterrows():
        roi = row["roi_pct"]
        color = "#059669" if roi > 50 else "#D97706" if roi > 0 else "#DC2626"
        bar_w = min(int(abs(roi)/2), 100)
        st.markdown(f"""
        <div class="row-item">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:600;color:#111827;">{row['project_name']}</div>
            <div style="font-size:11px;color:#6B7280;margin-top:2px;">
              Выручка ${row['revenue']/1000000:.1f}M &nbsp;·&nbsp; Инвестиции ${row['investment_usd']/1000000:.1f}M
            </div>
            <div style="margin-top:5px;background:#F3F4F6;border-radius:2px;height:4px;">
              <div style="background:{color};width:{bar_w}%;height:4px;border-radius:2px;"></div>
            </div>
          </div>
          <div style="margin-left:16px;font-size:18px;font-weight:700;color:{color};min-width:54px;text-align:right;">
            {roi}%
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
