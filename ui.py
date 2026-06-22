import streamlit as st

def render_sidebar():
    """Единый сайдбар для всех страниц системы"""
    with st.sidebar:
        # Логотип
        st.markdown("""
        <div style="padding: 8px 0 16px 0;">
          <div style="font-size:18px;font-weight:700;color:#FFFFFF;letter-spacing:0.02em;">
            GreenIPath
          </div>
          <div style="font-size:11px;color:#A7C4A0;margin-top:2px;letter-spacing:0.05em;">
            CARBON BI SYSTEM
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.15);margin-bottom:16px;"></div>',
                    unsafe_allow_html=True)

        # Навигация
        st.markdown('<div style="font-size:10px;color:#A7C4A0;letter-spacing:0.1em;margin-bottom:8px;">НАВИГАЦИЯ</div>',
                    unsafe_allow_html=True)

        pages = [
            ("Home.py",                  "Портфельный обзор"),
            ("pages/1_CO2_Monitor.py",   "Мониторинг CO₂"),
            ("pages/2_Investments.py",   "Инвестиции и ROI"),
            ("pages/3_Operations.py",    "Операционный контроль"),
            ("pages/4_Finance.py",       "Финансовая аналитика"),
            ("pages/5_AI_Analyst.py",    "AI-аналитик"),
            ("pages/6_RealTime.py",      "Данные в реальном времени"),
        ]

        for path, label in pages:
            st.page_link(path, label=label)

        st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.15);margin:16px 0;"></div>',
                    unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:11px;color:#A7C4A0;line-height:1.8;">
          Обновлено: сегодня<br>
          Проектов в портфеле: 5<br>
          <span style="color:#6FCF97;">● Система активна</span>
        </div>
        """, unsafe_allow_html=True)


def apply_styles():
    """Единые стили для всех страниц"""
    st.markdown("""
    <style>
    /* Основной фон */
    .stApp { background-color: #F4F5F7; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Сайдбар */
    section[data-testid="stSidebar"] {
        background: #1A3D2B;
        border-right: 1px solid #153324;
    }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] a {
        color: #D4EAD0 !important;
        font-size: 13px !important;
        padding: 6px 0 !important;
        display: block;
        text-decoration: none;
        border-radius: 4px;
    }
    section[data-testid="stSidebar"] a:hover {
        color: #FFFFFF !important;
        background: rgba(255,255,255,0.08);
        padding-left: 6px !important;
    }

    /* Шапка страницы */
    .page-header {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 18px 24px;
        border: 1px solid #E2E5EA;
        margin-bottom: 20px;
        border-left: 3px solid #1A3D2B;
    }
    .page-header-title {
        font-size: 20px;
        font-weight: 600;
        color: #1A3D2B;
        letter-spacing: -0.01em;
    }
    .page-header-sub {
        font-size: 12px;
        color: #6B7280;
        margin-top: 3px;
    }

    /* Карточки секций */
    .section-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 20px 24px;
        border: 1px solid #E2E5EA;
        margin-bottom: 16px;
    }
    .section-title {
        font-size: 13px;
        font-weight: 600;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid #F3F4F6;
    }

    /* KPI карточки */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 18px 20px;
        border: 1px solid #E2E5EA;
        border-top: 3px solid #1A3D2B;
    }
    .kpi-card-warn { border-top-color: #D97706; }
    .kpi-card-red  { border-top-color: #DC2626; }
    .kpi-card-blue { border-top-color: #2563EB; }
    .kpi-label {
        font-size: 11px;
        color: #6B7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        font-size: 11px;
        color: #059669;
        margin-top: 5px;
        font-weight: 500;
    }
    .kpi-sub-warn { font-size:11px; color:#D97706; margin-top:5px; font-weight:500; }
    .kpi-sub-muted { font-size:11px; color:#9CA3AF; margin-top:5px; }

    /* Таблицы */
    .row-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #F3F4F6;
    }
    .row-item:last-child { border-bottom: none; }

    /* Бейджи статусов — без эмодзи, деловой стиль */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .badge-green  { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .badge-yellow { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    .badge-blue   { background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
    .badge-gray   { background: #F9FAFB; color: #4B5563; border: 1px solid #E5E7EB; }
    .badge-red    { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }

    /* Скрыть стандартный заголовок Streamlit */
    header[data-testid="stHeader"] { background: transparent; }
    </style>
    """, unsafe_allow_html=True)


def page_header(title, subtitle, right_text=""):
    """Стандартная шапка страницы"""
    st.markdown(f"""
    <div class="page-header">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div class="page-header-title">{title}</div>
          <div class="page-header-sub">{subtitle}</div>
        </div>
        <div style="font-size:11px;color:#9CA3AF;text-align:right;">{right_text}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, sub, card_class=""):
    """Стандартная KPI карточка"""
    sub_class = "kpi-sub-warn" if card_class == "kpi-card-warn" else \
                "kpi-sub-muted" if card_class == "kpi-card-red" else "kpi-sub"
    return f"""
    <div class="kpi-card {card_class}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="{sub_class}">{sub}</div>
    </div>"""
