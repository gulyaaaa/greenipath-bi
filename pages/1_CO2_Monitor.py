import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.expanduser("~/greenipath-bi"))
from ui import apply_styles, render_sidebar, page_header, kpi_card

DB_PATH = os.path.expanduser("~/greenipath-bi/greenipath.db")

def get_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Мониторинг CO₂ · GreenIPath",
                   page_icon=None, layout="wide", initial_sidebar_state="expanded")
apply_styles()
render_sidebar()
page_header("Мониторинг CO₂",
            "Динамика сокращений выбросов · Базовый и проектный сценарий · Структура выпуска единиц")

projects_list = get_data("SELECT project_id, project_name FROM dim_project ORDER BY project_id")
project_options = {"Все проекты": None}
for _, r in projects_list.iterrows():
    project_options[r["project_name"]] = r["project_id"]

selected_label = st.selectbox("Проект", list(project_options.keys()))
selected_id = project_options[selected_label]
where  = f"WHERE fc.project_id = {selected_id}" if selected_id else ""
where2 = f"AND fc.project_id = {selected_id}" if selected_id else ""

total_gross = get_data(f"SELECT SUM(gross_reduction_tco2) as v FROM fact_carbon_calc fc {where}")["v"][0] or 0
total_net   = get_data(f"SELECT SUM(net_reduction_tco2) as v FROM fact_carbon_calc fc {where}")["v"][0] or 0
total_elig  = get_data(f"SELECT SUM(eligible_credits_tco2) as v FROM fact_carbon_calc fc {where}")["v"][0] or 0
total_buf   = get_data(f"SELECT SUM(buffer_tco2) as v FROM fact_carbon_calc fc {where}")["v"][0] or 0
total_leak  = get_data(f"SELECT SUM(leakage_tco2) as v FROM fact_carbon_calc fc {where}")["v"][0] or 0

st.markdown("<br>", unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
for col, label, value, sub in [
    (c1,"Валовое сокращение", f"{total_gross/1000:.0f}K т CO₂","до корректировок"),
    (c2,"Чистое сокращение",  f"{total_net/1000:.0f}K т CO₂",  "после утечек"),
    (c3,"К выпуску единиц",   f"{total_elig/1000:.0f}K т CO₂", "после буфера"),
    (c4,"Буферный резерв",    f"{total_buf/1000:.0f}K т CO₂",  "страховой фонд"),
    (c5,"Утечки",             f"{total_leak/1000:.0f}K т CO₂", "перенос воздействий"),
]:
    with col:
        st.markdown(kpi_card(label, value, sub), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col_l, col_r = st.columns([1,1], gap="medium")

with col_l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Воронка расчёта углеродных единиц</div>', unsafe_allow_html=True)
    fig_f = go.Figure(go.Funnel(
        y=["Валовое сокращение","Чистое (после утечек)","К выпуску (после буфера)"],
        x=[total_gross, total_net, total_elig],
        textinfo="value+percent initial",
        marker=dict(color=["#1A3D2B","#2D6A4F","#A7C4A0"]),
        connector=dict(line=dict(color="#E2E5EA", width=2))
    ))
    fig_f.update_layout(height=280, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=12))
    st.plotly_chart(fig_f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Динамика выпуска единиц по периодам</div>', unsafe_allow_html=True)
    dyn_df = get_data(f"""
        SELECT dp.period_start, p.project_name, fc.eligible_credits_tco2
        FROM fact_carbon_calc fc
        JOIN dim_period dp ON fc.period_id=dp.period_id
        JOIN dim_project p ON fc.project_id=p.project_id
        WHERE 1=1 {where2} ORDER BY dp.period_start
    """)
    if not dyn_df.empty:
        fig_d = px.line(dyn_df, x="period_start", y="eligible_credits_tco2",
            color="project_name", markers=True, template="plotly_white",
            color_discrete_sequence=["#1A3D2B","#2563EB","#B45309","#6D28D9","#6B7280"],
            labels={"period_start":"Период","eligible_credits_tco2":"Единиц к выпуску (т CO₂)","project_name":"Проект"})
        fig_d.update_layout(height=260, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(family="Inter, Arial, sans-serif", size=11),
            legend=dict(font=dict(size=10)))
        fig_d.update_xaxes(gridcolor="#F3F4F6")
        fig_d.update_yaxes(gridcolor="#F3F4F6")
        st.plotly_chart(fig_d, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Базовый сценарий vs Проектный сценарий</div>', unsafe_allow_html=True)
compare_df = get_data(f"""
    SELECT p.project_name,
           SUM(fc.gross_reduction_tco2+fc.net_reduction_tco2) as baseline_est,
           SUM(fc.net_reduction_tco2) as project_actual,
           SUM(fc.leakage_tco2) as leakage,
           SUM(fc.buffer_tco2) as buffer
    FROM fact_carbon_calc fc
    JOIN dim_project p ON fc.project_id=p.project_id
    {'WHERE fc.project_id='+str(selected_id) if selected_id else ''}
    GROUP BY p.project_id ORDER BY project_actual DESC
""")
fig_c = go.Figure()
fig_c.add_trace(go.Bar(name="Базовый сценарий", x=compare_df["project_name"],
    y=compare_df["baseline_est"], marker_color="#E2E5EA",
    marker_line_color="#9CA3AF", marker_line_width=1))
fig_c.add_trace(go.Bar(name="Фактическое сокращение", x=compare_df["project_name"],
    y=compare_df["project_actual"], marker_color="#1A3D2B"))
fig_c.add_trace(go.Bar(name="Утечки", x=compare_df["project_name"],
    y=compare_df["leakage"], marker_color="#FCA5A5"))
fig_c.add_trace(go.Bar(name="Буферный вычет", x=compare_df["project_name"],
    y=compare_df["buffer"], marker_color="#A7C4A0"))
fig_c.update_layout(barmode="group", template="plotly_white",
    height=320, margin=dict(l=0,r=0,t=10,b=0),
    paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
    font=dict(family="Inter, Arial, sans-serif", size=11),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
    yaxis_title="Тонн CO₂")
fig_c.update_xaxes(gridcolor="#F3F4F6")
fig_c.update_yaxes(gridcolor="#F3F4F6")
st.plotly_chart(fig_c, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

periods_df = get_data(f"""
    SELECT p.project_name as Проект, dp.period_number as Период,
           dp.period_start as Начало, dp.period_end as Конец,
           dp.status as Статус,
           ROUND(fc.gross_reduction_tco2) as 'Валовое (т CO₂)',
           ROUND(fc.eligible_credits_tco2) as 'К выпуску (т CO₂)'
    FROM dim_period dp
    JOIN dim_project p ON dp.project_id=p.project_id
    LEFT JOIN fact_carbon_calc fc ON fc.period_id=dp.period_id
    {'WHERE dp.project_id='+str(selected_id) if selected_id else ''}
    ORDER BY dp.period_start DESC
""")
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Периоды мониторинга</div>', unsafe_allow_html=True)
st.dataframe(periods_df, use_container_width=True, hide_index=True,
    column_config={
        "Валовое (т CO₂)": st.column_config.NumberColumn(format="%,.0f"),
        "К выпуску (т CO₂)": st.column_config.NumberColumn(format="%,.0f"),
    })
st.markdown('</div>', unsafe_allow_html=True)
