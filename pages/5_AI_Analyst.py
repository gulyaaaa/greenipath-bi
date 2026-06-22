import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from openai import OpenAI
import sys, os, re

sys.path.append(os.path.expanduser("~/greenipath-bi"))
from ui import apply_styles, render_sidebar, page_header

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../greenipath.db")

def run_query_safe(sql):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

st.set_page_config(page_title="AI-аналитик · GreenIPath",
                   page_icon=None, layout="wide", initial_sidebar_state="expanded")
apply_styles()
render_sidebar()
page_header("AI-аналитик",
            "Аналитические запросы на русском языке — система автоматически строит SQL и возвращает результат",
            "Powered by DeepSeek · Natural Language to SQL")

st.markdown("""
<style>
.chat-user {
    background:#EFF6FF;border-radius:6px 6px 2px 6px;
    padding:12px 16px;margin:8px 0;font-size:13px;color:#1E40AF;text-align:right;
}
.chat-ai {
    background:#F0FDF4;border-radius:6px 6px 6px 2px;
    padding:12px 16px;margin:8px 0;font-size:13px;color:#065F46;line-height:1.6;
}
.ai-error {
    background:#FEF2F2;border:1px solid #FECACA;border-left:3px solid #DC2626;
    border-radius:6px;padding:14px;font-size:13px;color:#991B1B;margin-top:8px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.15);margin:8px 0;"></div>',
                unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;color:#A7C4A0;letter-spacing:0.1em;margin-bottom:8px;">НАСТРОЙКИ AI</div>',
                unsafe_allow_html=True)
    api_key = st.text_input("DeepSeek API Key", type="password",
                             placeholder="sk-...",
                             help="Получить на platform.deepseek.com")

DB_SCHEMA = """
База данных SQLite. Таблицы:
dim_project: project_id, project_name, project_code, country, region,
             project_type, standard, status, start_date, credit_period_years, investment_usd
dim_period: period_id, project_id, period_number, period_start, period_end, status
fact_carbon_calc: calc_id, project_id, period_id, gross_reduction_tco2, leakage_tco2,
                  net_reduction_tco2, buffer_tco2, eligible_credits_tco2
fact_credits_issued: issuance_id, project_id, period_id, registry, issued_credits,
                     sold_credits, buffer_credits, avg_price_usd, revenue_usd,
                     issuance_date, cost_per_credit_usd
Страны проектов: Камерун, Казахстан, Индонезия, Индия, Бразилия
Стандарты: 'Verra VCS', 'Gold Standard', 'Plan Vivo'
"""

SYSTEM_PROMPT = f"""Ты аналитик BI-системы GreenIPath Carbon BI.
{DB_SCHEMA}
Правила:
1. Аналитический вопрос — напиши SQL для SQLite в тегах <SQL>...</SQL>
2. После тегов — краткое объяснение на русском (2-3 предложения)
3. Общий вопрос — просто ответь текстом
4. Только SELECT, только таблицы из схемы выше
"""

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Примеры запросов</div>', unsafe_allow_html=True)
examples = [
    "Суммарная выручка по каждому проекту",
    "Какой проект выпустил больше всего единиц?",
    "Сравни ROI всех проектов",
    "Динамика цены CO₂ по годам",
    "Проекты с наибольшим буферным резервом",
    "Объём продаж по каждому стандарту",
    "Проекты с наибольшими утечками",
    "Суммарная выручка по годам",
]
cols = st.columns(4)
for i, ex in enumerate(examples):
    with cols[i % 4]:
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state["ai_q"] = ex
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Задайте вопрос</div>', unsafe_allow_html=True)
question = st.text_input("Вопрос", value=st.session_state.get("ai_q",""),
    placeholder="Например: Топ-3 проекта по выручке за все периоды",
    label_visibility="collapsed")
cb1, cb2, _ = st.columns([1,1,4])
with cb1:
    ask = st.button("Выполнить запрос", type="primary", use_container_width=True)
with cb2:
    if st.button("Очистить историю", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if ask and question:
    if not api_key:
        st.markdown('<div class="ai-error">Введите DeepSeek API ключ в левой панели</div>',
                    unsafe_allow_html=True)
    else:
        with st.spinner("Анализируем запрос..."):
            try:
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                resp = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role":"system","content":SYSTEM_PROMPT},
                        {"role":"user","content":question}
                    ],
                    temperature=0.1, max_tokens=1000
                )
                ai_text = resp.choices[0].message.content
                sql_match   = re.search(r'<SQL>(.*?)</SQL>', ai_text, re.DOTALL)
                explanation = re.sub(r'<SQL>.*?</SQL>', '', ai_text, flags=re.DOTALL).strip()
                result = {"question":question,"explanation":explanation,
                          "sql":None,"df":None,"error":None}
                if sql_match:
                    sql = sql_match.group(1).strip()
                    result["sql"] = sql
                    df, err = run_query_safe(sql)
                    if err:
                        result["error"] = err
                    else:
                        result["df"] = df
                st.session_state["chat_history"].append(result)
                st.session_state["ai_q"] = ""
                st.rerun()
            except Exception as e:
                st.markdown(f'<div class="ai-error">Ошибка подключения: {str(e)}</div>',
                            unsafe_allow_html=True)

if st.session_state["chat_history"]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">История запросов</div>', unsafe_allow_html=True)
    for item in reversed(st.session_state["chat_history"]):
        st.markdown(f'<div class="chat-user">{item["question"]}</div>', unsafe_allow_html=True)
        if item["explanation"]:
            st.markdown(f'<div class="chat-ai">{item["explanation"]}</div>', unsafe_allow_html=True)
        if item["sql"]:
            with st.expander("SQL запрос"):
                st.code(item["sql"], language="sql")
        if item["error"]:
            st.markdown(f'<div class="ai-error">{item["error"]}</div>', unsafe_allow_html=True)
        elif item["df"] is not None and not item["df"].empty:
            df = item["df"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            num_cols = df.select_dtypes(include="number").columns.tolist()
            str_cols = df.select_dtypes(include="object").columns.tolist()
            if len(num_cols) >= 1 and len(str_cols) >= 1:
                try:
                    fig = px.bar(df, x=str_cols[0], y=num_cols[0],
                        color_discrete_sequence=["#1A3D2B"], template="plotly_white")
                    fig.update_layout(height=300, margin=dict(l=0,r=0,t=20,b=0),
                        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                        font=dict(family="Inter, Arial, sans-serif", size=11))
                    fig.update_xaxes(gridcolor="#F3F4F6", tickangle=-15)
                    fig.update_yaxes(gridcolor="#F3F4F6")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass
        st.divider()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="section-card" style="text-align:center;padding:48px 24px;">
      <div style="font-size:15px;font-weight:600;color:#374151;margin-bottom:8px;">
        AI-аналитик готов к работе
      </div>
      <div style="font-size:13px;color:#6B7280;">
        Введите DeepSeek API ключ в левой панели,<br>
        затем выберите пример или введите собственный вопрос
      </div>
    </div>
    """, unsafe_allow_html=True)
