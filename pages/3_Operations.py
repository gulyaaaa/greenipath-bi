import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import sys, os
from datetime import date

sys.path.append(os.path.expanduser("~/greenipath-bi"))
from ui import apply_styles, render_sidebar, page_header, kpi_card

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../greenipath.db")

def get_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Операционный контроль · GreenIPath",
                   page_icon=None, layout="wide", initial_sidebar_state="expanded")
apply_styles()
render_sidebar()
page_header("Операционный контроль",
            "Дедлайны верификаций · Статусы периодов · Предупреждения",
            f"Сегодня: {date.today().strftime('%d.%m.%Y')}")

periods_df = get_data("""
    SELECT dp.period_id, dp.project_id, dp.period_number,
           dp.period_start, dp.period_end, dp.status,
           p.project_name, p.project_type, p.standard, p.country
    FROM dim_period dp JOIN dim_project p ON dp.project_id=p.project_id
    ORDER BY dp.period_end DESC
""")
today = date.today()
periods_df["period_end_date"] = pd.to_datetime(periods_df["period_end"]).dt.date
periods_df["days_to_end"] = (periods_df["period_end_date"]-today).apply(lambda x: x.days)

verified   = len(periods_df[periods_df["status"]=="Верифицирован"])
in_process = len(periods_df[periods_df["status"]=="В процессе"])
on_verif   = len(periods_df[periods_df["status"]=="На верификации"])
monitoring = len(periods_df[periods_df["status"]=="Мониторинг"])
expiring   = len(periods_df[(periods_df["days_to_end"]>=0)&(periods_df["days_to_end"]<=90)])

st.markdown("<br>", unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
for col,label,value,sub,cls in [
    (c1,"Верифицировано",    str(verified),   "периодов успешно",""),
    (c2,"В процессе",        str(in_process), "активных периодов",""),
    (c3,"На верификации",    str(on_verif),   "ожидают решения","kpi-card-warn"),
    (c4,"Мониторинг",        str(monitoring), "сбор данных","kpi-card-blue"),
    (c5,"Дедлайн до 90 дней",str(expiring),  "требуют внимания","kpi-card-red"),
]:
    with col:
        st.markdown(kpi_card(label,value,sub,cls), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Предупреждения и алерты</div>', unsafe_allow_html=True)

shown = False
for _, row in periods_df.iterrows():
    if row["status"]=="На верификации":
        st.markdown(f"""
        <div style="background:#FFFBEB;border:1px solid #FDE68A;border-left:3px solid #D97706;
             border-radius:6px;padding:12px 16px;margin-bottom:8px;">
          <div style="font-size:13px;font-weight:600;color:#92400E;">
            {row['project_name']} — Период {row['period_number']} ожидает верификации
          </div>
          <div style="font-size:11px;color:#B45309;margin-top:3px;">
            Конец периода: {row['period_end']} · Статус: {row['status']}
          </div>
        </div>""", unsafe_allow_html=True)
        shown = True
    elif row["status"]=="Мониторинг":
        st.markdown(f"""
        <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-left:3px solid #2563EB;
             border-radius:6px;padding:12px 16px;margin-bottom:8px;">
          <div style="font-size:13px;font-weight:600;color:#1E40AF;">
            {row['project_name']} — Период {row['period_number']} в стадии мониторинга
          </div>
          <div style="font-size:11px;color:#1D4ED8;margin-top:3px;">
            Конец периода: {row['period_end']} · Необходимо подготовить мониторинговый отчёт
          </div>
        </div>""", unsafe_allow_html=True)
        shown = True
    elif row["status"]=="В процессе" and 0<=row["days_to_end"]<=60:
        st.markdown(f"""
        <div style="background:#FEF2F2;border:1px solid #FECACA;border-left:3px solid #DC2626;
             border-radius:6px;padding:12px 16px;margin-bottom:8px;">
          <div style="font-size:13px;font-weight:600;color:#991B1B;">
            {row['project_name']} — Период {row['period_number']} заканчивается через {row['days_to_end']} дней
          </div>
          <div style="font-size:11px;color:#B91C1C;margin-top:3px;">
            Конец периода: {row['period_end']} · Подготовить данные для верификатора
          </div>
        </div>""", unsafe_allow_html=True)
        shown = True

if not shown:
    st.markdown("""
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-left:3px solid #059669;
         border-radius:6px;padding:12px 16px;">
      <div style="font-size:13px;font-weight:600;color:#065F46;">
        Все периоды в норме — критических дедлайнов нет
      </div>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

col_l,col_r = st.columns([1,1], gap="medium")
with col_l:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Распределение периодов по статусам</div>', unsafe_allow_html=True)
    sc = periods_df["status"].value_counts().reset_index()
    sc.columns = ["Статус","Количество"]
    fig = px.pie(sc, values="Количество", names="Статус",
        color="Статус",
        color_discrete_map={"Верифицирован":"#059669","В процессе":"#2563EB",
                            "На верификации":"#D97706","Мониторинг":"#6D28D9"},
        template="plotly_white")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="#FFFFFF", showlegend=False,
        font=dict(family="Inter, Arial, sans-serif", size=12))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Ближайшие дедлайны</div>', unsafe_allow_html=True)
    upcoming = periods_df[periods_df["days_to_end"]>=-30].sort_values("days_to_end").head(8)
    for _, row in upcoming.iterrows():
        days = row["days_to_end"]
        color = "#DC2626" if days<=30 else "#D97706" if days<=90 else "#059669"
        days_text = f"просрочен на {abs(days)} дн." if days<0 else f"через {days} дн."
        st.markdown(f"""
        <div class="row-item">
          <div>
            <div style="font-size:13px;font-weight:600;color:#111827;">{row['project_name']}</div>
            <div style="font-size:11px;color:#6B7280;margin-top:2px;">
              Период {row['period_number']} · {row['status']} · до {row['period_end']}
            </div>
          </div>
          <div style="font-size:12px;font-weight:600;color:{color};white-space:nowrap;margin-left:12px;">
            {days_text}
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Все периоды мониторинга</div>', unsafe_allow_html=True)
display_df = periods_df[["project_name","period_number","period_start","period_end","status"]].copy()
display_df.columns = ["Проект","Период","Начало","Конец","Статус"]
st.dataframe(display_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)
