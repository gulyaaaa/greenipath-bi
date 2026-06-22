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

st.set_page_config(page_title="Инвестиции и ROI · GreenIPath",
                   page_icon=None, layout="wide", initial_sidebar_state="expanded")
apply_styles()
render_sidebar()
page_header("Инвестиции и ROI",
            "Эффективность вложений · Маржинальность проектов · Окупаемость и прогноз")

roi_df = get_data("""
    SELECT p.project_name, p.project_type, p.investment_usd, p.credit_period_years,
           SUM(fi.revenue_usd) as total_revenue,
           AVG(fi.avg_price_usd) as avg_price,
           AVG(fi.cost_per_credit_usd) as avg_cost,
           ROUND((SUM(fi.revenue_usd)-p.investment_usd)/p.investment_usd*100,1) as roi_pct,
           ROUND(p.investment_usd/(SUM(fi.revenue_usd)/COUNT(DISTINCT fi.period_id)),1) as payback_years
    FROM fact_credits_issued fi
    JOIN dim_project p ON fi.project_id=p.project_id
    GROUP BY p.project_id ORDER BY roi_pct DESC
""")

total_invested = roi_df["investment_usd"].sum()
total_revenue  = roi_df["total_revenue"].sum()
portfolio_roi  = round((total_revenue-total_invested)/total_invested*100,1)
avg_margin     = round((roi_df["avg_price"]-roi_df["avg_cost"]).mean(),2)
best_project   = roi_df.iloc[0]["project_name"].split("—")[0].strip()

st.markdown("<br>", unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
for col,label,value,sub,cls in [
    (c1,"Всего инвестировано",  f"${total_invested/1000000:.1f}M","в портфель проектов",""),
    (c2,"Суммарная выручка",    f"${total_revenue/1000000:.1f}M", "от реализации единиц",""),
    (c3,"ROI портфеля",         f"{portfolio_roi}%",              "чистая доходность",""),
    (c4,"Средняя маржа",        f"${avg_margin:.2f}/т CO₂",       "цена продажи − затраты",""),
    (c5,"Лучший проект",        best_project,                     "по доходности",""),
]:
    with col:
        st.markdown(kpi_card(label,value,sub,cls), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col_l,col_r = st.columns([1,1], gap="medium")

with col_l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ROI по проектам, %</div>', unsafe_allow_html=True)
    colors = ["#059669" if x>50 else "#D97706" if x>0 else "#DC2626" for x in roi_df["roi_pct"]]
    fig = go.Figure(go.Bar(x=roi_df["project_name"], y=roi_df["roi_pct"],
        marker_color=colors, text=[f"{v}%" for v in roi_df["roi_pct"]], textposition="outside"))
    fig.add_hline(y=0, line_dash="dash", line_color="#9CA3AF", line_width=1)
    fig.update_layout(template="plotly_white", height=300,
        margin=dict(l=0,r=0,t=20,b=0), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        yaxis_title="ROI (%)", showlegend=False)
    fig.update_xaxes(gridcolor="#F3F4F6", tickangle=-15)
    fig.update_yaxes(gridcolor="#F3F4F6")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Себестоимость vs Цена продажи, USD/т CO₂</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Себестоимость", x=roi_df["project_name"],
        y=roi_df["avg_cost"], marker_color="#FCA5A5"))
    fig2.add_trace(go.Bar(name="Цена продажи", x=roi_df["project_name"],
        y=roi_df["avg_price"], marker_color="#1A3D2B"))
    fig2.update_layout(barmode="group", template="plotly_white", height=300,
        margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
        yaxis_title="USD/т CO₂")
    fig2.update_xaxes(gridcolor="#F3F4F6", tickangle=-15)
    fig2.update_yaxes(gridcolor="#F3F4F6")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col_l2,col_r2 = st.columns([1,1], gap="medium")

with col_l2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Инвестиции vs Выручка, USD</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Инвестиции", x=roi_df["project_name"],
        y=roi_df["investment_usd"], marker_color="#E2E5EA",
        marker_line_color="#9CA3AF", marker_line_width=1))
    fig3.add_trace(go.Bar(name="Выручка", x=roi_df["project_name"],
        y=roi_df["total_revenue"], marker_color="#1A3D2B"))
    fig3.update_layout(barmode="group", template="plotly_white", height=280,
        margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)))
    fig3.update_xaxes(gridcolor="#F3F4F6", tickangle=-15)
    fig3.update_yaxes(gridcolor="#F3F4F6", tickformat="$,.0f")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Срок окупаемости и жизненный цикл</div>', unsafe_allow_html=True)
    for _, row in roi_df.iterrows():
        payback = row["payback_years"]
        period  = row["credit_period_years"]
        pct     = min(100, int(payback/period*100))
        color   = "#059669" if payback < period*0.4 else "#D97706"
        st.markdown(f"""
        <div class="row-item">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:600;color:#111827;">{row['project_name']}</div>
            <div style="font-size:11px;color:#6B7280;margin-top:2px;">
              Срок окупаемости: <b style="color:{color};">{payback:.1f} лет</b> из {period} лет
            </div>
            <div style="margin-top:5px;background:#F3F4F6;border-radius:2px;height:4px;">
              <div style="background:{color};width:{pct}%;height:4px;border-radius:2px;"></div>
            </div>
          </div>
          <div style="margin-left:16px;font-size:16px;font-weight:700;color:{color};min-width:54px;text-align:right;">
            {payback:.1f} лет
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Детализация инвестиционных показателей</div>', unsafe_allow_html=True)
table_df = roi_df[["project_name","investment_usd","total_revenue","avg_cost","avg_price","roi_pct","payback_years"]].copy()
table_df.columns = ["Проект","Инвестиции (USD)","Выручка (USD)","Себестоимость (USD/т)","Цена продажи (USD/т)","ROI (%)","Окупаемость (лет)"]
st.dataframe(table_df, use_container_width=True, hide_index=True,
    column_config={
        "Инвестиции (USD)":      st.column_config.NumberColumn(format="$%,.0f"),
        "Выручка (USD)":         st.column_config.NumberColumn(format="$%,.0f"),
        "Себестоимость (USD/т)": st.column_config.NumberColumn(format="$%.2f"),
        "Цена продажи (USD/т)":  st.column_config.NumberColumn(format="$%.2f"),
        "ROI (%)":               st.column_config.NumberColumn(format="%.1f%%"),
        "Окупаемость (лет)":     st.column_config.NumberColumn(format="%.1f"),
    })
st.markdown('</div>', unsafe_allow_html=True)
