import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import time

sys.path.append(os.path.expanduser("~/greenipath-bi"))
from realtime import (
    init_realtime_tables, seed_initial_data, fetch_co2_price,
    simulate_monitoring_reading, get_latest_co2_price,
    get_latest_monitoring_stream, get_stream_stats
)

DB_PATH = os.path.expanduser("~/greenipath-bi/greenipath.db")

st.set_page_config(
    page_title="Real-Time · GreenIPath",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp { background-color: #F7F8FA; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.page-header {
    background: #FFFFFF; border-radius: 12px;
    padding: 20px 28px; border: 1px solid #E8ECF0; margin-bottom: 20px;
}
.section-card {
    background: #FFFFFF; border-radius: 12px;
    padding: 24px; border: 1px solid #E8ECF0; margin-bottom: 16px;
}
.section-title {
    font-size: 15px; font-weight: 600; color: #111827;
    margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #F3F4F6;
}
.kpi-card {
    background: #FFFFFF; border-radius: 12px;
    padding: 20px 24px; border: 1px solid #E8ECF0;
    border-left: 4px solid #1F5C3E;
}
.kpi-label { font-size: 12px; color: #6B7280; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #111827; }
.kpi-sub   { font-size: 12px; color: #059669; margin-top: 4px; }
.live-dot {
    display: inline-block; width: 8px; height: 8px;
    background: #059669; border-radius: 50%;
    animation: pulse 1.5s infinite;
    margin-right: 6px;
}
@keyframes pulse {
    0%   { opacity: 1; }
    50%  { opacity: 0.3; }
    100% { opacity: 1; }
}
.stream-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0; border-bottom: 1px solid #F3F4F6; font-size: 13px;
}
.stream-row:last-child { border-bottom: none; }
.badge-norm { background:#D1FAE5;color:#065F46;padding:2px 8px;
    border-radius:12px;font-size:11px;font-weight:600; }
.badge-warn { background:#FEF3C7;color:#92400E;padding:2px 8px;
    border-radius:12px;font-size:11px;font-weight:600; }
.badge-anom { background:#FEE2E2;color:#991B1B;padding:2px 8px;
    border-radius:12px;font-size:11px;font-weight:600; }
section[data-testid="stSidebar"] { background: #1F5C3E; }
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌿 GreenIPath")
    st.markdown("---")
    st.markdown("**Навигация**")
    st.page_link("Home.py",                  label="📊 Портфельный обзор")
    st.page_link("pages/1_CO2_Monitor.py",   label="🌱 Мониторинг CO₂")
    st.page_link("pages/2_Investments.py",   label="💰 Инвестиции и ROI")
    st.page_link("pages/3_Operations.py",    label="📋 Операционный контроль")
    st.page_link("pages/4_Finance.py",       label="📈 Финансовая аналитика")
    st.page_link("pages/5_AI_Analyst.py",    label="🤖 AI-аналитик")
    st.page_link("pages/6_RealTime.py",      label="⚡ Real-Time данные")
    st.markdown("---")
    st.markdown("**Обновлено:** сегодня")

# Инициализация
init_realtime_tables()
seed_initial_data()

# Шапка
st.markdown("""
<div class="page-header">
  <div>
    <div style="font-size:22px;font-weight:700;color:#1F5C3E;">
      <span class="live-dot"></span>⚡ Real-Time мониторинг
    </div>
    <div style="font-size:13px;color:#6B7280;margin-top:2px;">
      Живые цены углеродного рынка · Поток данных с проектов · Автообновление
    </div>
  </div>
  <div style="font-size:11px;color:#9CA3AF;text-align:right;">
    Источник цен: Yahoo Finance / KRBN ETF<br>
    Мониторинг: симуляция IoT-потока
  </div>
</div>
""", unsafe_allow_html=True)

# Контроль обновления
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 4])
with col_ctrl1:
    if st.button("🔄 Обновить данные", type="primary", use_container_width=True):
        fetch_co2_price()
        simulate_monitoring_reading()
        simulate_monitoring_reading()
        simulate_monitoring_reading()
        st.rerun()
with col_ctrl2:
    auto_refresh = st.toggle("Авто-обновление", value=False)

if auto_refresh:
    st.info("Автообновление включено — страница обновляется каждые 30 секунд")
    time.sleep(30)
    fetch_co2_price()
    simulate_monitoring_reading()
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# KPI реального времени
price_df = get_latest_co2_price()
stream_df = get_latest_monitoring_stream(50)
stats_df  = get_stream_stats()

if not price_df.empty:
    last_price  = price_df.iloc[-1]["price_eur"]
    last_change = price_df.iloc[-1]["change_pct"]
else:
    last_price, last_change = 24.50, 0.0

total_readings = len(stream_df) if not stream_df.empty else 0
anomalies = len(stream_df[stream_df["status"] == "Отклонение"]) if not stream_df.empty else 0
normal_pct = round((len(stream_df[stream_df["status"] == "Норма"]) / total_readings * 100), 1) if total_readings > 0 else 0

c1, c2, c3, c4 = st.columns(4)
price_color = "#1F5C3E" if last_change >= 0 else "#DC2626"
change_arrow = "↑" if last_change >= 0 else "↓"

with c1:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:{price_color};">
      <div class="kpi-label">Цена CO₂ · Live</div>
      <div class="kpi-value" style="color:{price_color};">${last_price:.2f}</div>
      <div class="kpi-sub" style="color:{price_color};">
        {change_arrow} {abs(last_change):.2f}% · KRBN ETF
      </div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Измерений получено</div>
      <div class="kpi-value">{total_readings}</div>
      <div class="kpi-sub">из потока мониторинга</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">В норме</div>
      <div class="kpi-value">{normal_pct}%</div>
      <div class="kpi-sub">показателей в допуске</div>
    </div>""", unsafe_allow_html=True)
with c4:
    anom_color = "#DC2626" if anomalies > 0 else "#059669"
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:{anom_color};">
      <div class="kpi-label">Отклонений</div>
      <div class="kpi-value" style="color:{anom_color};">{anomalies}</div>
      <div class="kpi-sub">требуют проверки</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Строка 1: График цены CO₂ + Поток измерений
col_l, col_r = st.columns([1, 1], gap="medium")

with col_l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Динамика цены CO₂ · Live (KRBN ETF, USD)</div>',
                unsafe_allow_html=True)

    if not price_df.empty:
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(
            x=price_df["timestamp"], y=price_df["price_eur"],
            mode="lines+markers", name="Цена CO₂",
            line=dict(color="#1F5C3E", width=2),
            marker=dict(size=4),
            fill="tozeroy", fillcolor="rgba(31,92,62,0.08)"
        ))
        fig_price.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(family="Inter, sans-serif", size=11),
            showlegend=False, yaxis_title="USD",
            xaxis_title=""
        )
        fig_price.update_xaxes(gridcolor="#F3F4F6")
        fig_price.update_yaxes(gridcolor="#F3F4F6")
        st.plotly_chart(fig_price, use_container_width=True)
        st.caption(f"Источник: Yahoo Finance · KRBN (KraneShares Global Carbon ETF) · "
                   f"Последнее обновление: {price_df.iloc[-1]['timestamp'].strftime('%H:%M:%S')}")
    else:
        st.info("Нажмите 'Обновить данные' для загрузки цен")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📡 Последние измерения с проектов</div>',
                unsafe_allow_html=True)

    if not stream_df.empty:
        for _, row in stream_df.head(10).iterrows():
            badge_class = {
                "Норма": "badge-norm",
                "Внимание": "badge-warn",
                "Отклонение": "badge-anom"
            }.get(row["status"], "badge-norm")

            ts = row["timestamp"].strftime("%H:%M:%S")
            st.markdown(f"""
            <div class="stream-row">
              <div>
                <div style="font-weight:600;color:#111827;">{row['project_name']}</div>
                <div style="font-size:11px;color:#6B7280;">{row['indicator']} · {ts}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-weight:600;">{row['value']} {row['unit']}</div>
                <span class="{badge_class}">{row['status']}</span>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Нажмите 'Обновить данные' для получения измерений")
    st.markdown('</div>', unsafe_allow_html=True)

# Строка 2: Статистика по проектам + Распределение статусов
if not stats_df.empty:
    col_l2, col_r2 = st.columns([1, 1], gap="medium")

    with col_l2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Измерений по проектам за последний час</div>',
                    unsafe_allow_html=True)
        fig_stats = px.bar(
            stats_df, x="project_name", y="readings",
            color_discrete_sequence=["#1F5C3E"],
            template="plotly_white",
            labels={"project_name": "", "readings": "Кол-во измерений"}
        )
        fig_stats.update_layout(
            height=260, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(family="Inter, sans-serif", size=11)
        )
        fig_stats.update_xaxes(gridcolor="#F3F4F6", tickangle=-10)
        fig_stats.update_yaxes(gridcolor="#F3F4F6")
        st.plotly_chart(fig_stats, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Распределение статусов измерений</div>',
                    unsafe_allow_html=True)
        if not stream_df.empty:
            status_counts = stream_df["status"].value_counts().reset_index()
            status_counts.columns = ["Статус", "Количество"]
            fig_status = px.pie(
                status_counts, values="Количество", names="Статус",
                color="Статус",
                color_discrete_map={
                    "Норма": "#059669",
                    "Внимание": "#F59E0B",
                    "Отклонение": "#DC2626"
                },
                template="plotly_white"
            )
            fig_status.update_traces(textposition="inside", textinfo="percent+label")
            fig_status.update_layout(
                height=260, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="#FFFFFF", showlegend=False,
                font=dict(family="Inter, sans-serif", size=12)
            )
            st.plotly_chart(fig_status, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
