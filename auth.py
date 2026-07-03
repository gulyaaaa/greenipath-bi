import streamlit as st

USERS = {
    "admin":   {"password": "greenipath2025", "role": "Администратор", "name": "Admin"},
    "manager": {"password": "carbon2025",     "role": "Менеджер",      "name": "Project Manager"},
    "analyst": {"password": "bi2025",         "role": "Аналитик",      "name": "Analyst"},
}

def login_page():
    st.markdown("""
    <style>
    .stApp { background-color: #0F2419; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* Скрыть сайдбар и хедер */
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }

    /* Сетка: левая панель + правая форма */
    .login-wrapper {
        display: flex;
        min-height: 100vh;
        width: 100%;
    }

    /* Левая панель — брендинг */
    .login-left {
        flex: 1.1;
        background: linear-gradient(160deg, #1A3D2B 0%, #0F2419 60%, #0A1A10 100%);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 52px 56px;
        position: relative;
        overflow: hidden;
    }
    .login-left::before {
        content: '';
        position: absolute;
        top: -120px; right: -120px;
        width: 420px; height: 420px;
        border-radius: 50%;
        background: rgba(255,255,255,0.03);
    }
    .login-left::after {
        content: '';
        position: absolute;
        bottom: -80px; left: -80px;
        width: 300px; height: 300px;
        border-radius: 50%;
        background: rgba(255,255,255,0.02);
    }
    .brand-logo {
        font-size: 26px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: 0.02em;
    }
    .brand-tag {
        font-size: 11px;
        color: #6FCF97;
        letter-spacing: 0.14em;
        margin-top: 4px;
        font-weight: 500;
    }
    .brand-headline {
        font-size: 36px;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.25;
        letter-spacing: -0.02em;
        margin-bottom: 16px;
    }
    .brand-sub {
        font-size: 15px;
        color: rgba(255,255,255,0.5);
        line-height: 1.65;
        max-width: 360px;
    }
    .brand-stats {
        display: flex;
        gap: 32px;
        margin-top: 40px;
    }
    .stat-item { }
    .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #6FCF97;
        letter-spacing: -0.02em;
    }
    .stat-label {
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        margin-top: 2px;
        letter-spacing: 0.04em;
    }
    .brand-footer {
        font-size: 11px;
        color: rgba(255,255,255,0.25);
    }

    /* Правая панель — форма */
    .login-right {
        flex: 0.9;
        background: #F7F8FA;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 48px 40px;
    }
    .login-form-box {
        width: 100%;
        max-width: 360px;
    }
    .form-title {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 6px;
        letter-spacing: -0.01em;
    }
    .form-sub {
        font-size: 13px;
        color: #6B7280;
        margin-bottom: 32px;
    }
    .form-label {
        font-size: 12px;
        font-weight: 600;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .login-error {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 3px solid #DC2626;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        color: #991B1B;
        margin-top: 12px;
    }
    .form-hint {
        font-size: 11px;
        color: #9CA3AF;
        margin-top: 20px;
        text-align: center;
        line-height: 1.6;
    }

    /* Streamlit input styling */
    .stTextInput input {
        border: 1.5px solid #E2E5EA !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        background: #FFFFFF !important;
        color: #111827 !important;
    }
    .stTextInput input:focus {
        border-color: #1A3D2B !important;
        box-shadow: 0 0 0 3px rgba(26,61,43,0.08) !important;
    }
    .stButton button {
        background: #1A3D2B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 11px !important;
        letter-spacing: 0.02em !important;
        transition: background 0.2s !important;
    }
    .stButton button:hover {
        background: #2D6A4F !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

    # Левая панель
    st.markdown("""
    <div class="login-left">
      <div>
        <div class="brand-logo">GreenIPath</div>
        <div class="brand-tag">CARBON BI SYSTEM</div>
      </div>
      <div>
        <div class="brand-headline">Мониторинг<br>углеродных<br>проектов</div>
        <div class="brand-sub">
          Единая аналитическая платформа для управления
          портфелем углеродных активов, оценки инвестиционной
          эффективности и мониторинга CO₂ в реальном времени.
        </div>
        <div class="brand-stats">
          <div class="stat-item">
            <div class="stat-value">5</div>
            <div class="stat-label">ПРОЕКТОВ</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">$10.5M</div>
            <div class="stat-label">ВЫРУЧКА</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">1.7M</div>
            <div class="stat-label">ТОНН CO₂</div>
          </div>
        </div>
      </div>
      <div class="brand-footer">
        © 2025 GreenIPath · Конфиденциально
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Правая панель — форма через Streamlit
    with st.container():
        col_pad1, col_form, col_pad2 = st.columns([1, 2, 1])
        with col_form:
            st.markdown('<div class="form-title">Вход в систему</div>', unsafe_allow_html=True)
            st.markdown('<div class="form-sub">Введите учётные данные для доступа к платформе</div>',
                        unsafe_allow_html=True)

            username = st.text_input("Логин", placeholder="Введите логин", key="login_user",
                                     label_visibility="collapsed")
            st.markdown('<div class="form-label">Логин</div>', unsafe_allow_html=True)

            password = st.text_input("Пароль", type="password", placeholder="Введите пароль",
                                     key="login_pass", label_visibility="collapsed")
            st.markdown('<div class="form-label">Пароль</div>', unsafe_allow_html=True)

            if st.button("Войти", type="primary", use_container_width=True):
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["username"]      = username
                    st.session_state["role"]          = USERS[username]["role"]
                    st.session_state["display_name"]  = USERS[username]["name"]
                    st.rerun()
                else:
                    st.markdown('<div class="login-error">Неверный логин или пароль</div>',
                                unsafe_allow_html=True)

            st.markdown("""
            <div class="form-hint">
              Доступ только для авторизованных сотрудников GreenIPath.<br>
              По вопросам доступа обратитесь к администратору.
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def check_auth():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        login_page()
        st.stop()


def render_user_info():
    with st.sidebar:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.08);border-radius:6px;
             padding:10px 12px;margin-bottom:12px;">
          <div style="font-size:10px;color:#A7C4A0;letter-spacing:0.08em;margin-bottom:3px;">
            ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ
          </div>
          <div style="font-size:13px;font-weight:600;color:#FFFFFF;">
            {st.session_state.get('display_name','—')}
          </div>
          <div style="font-size:11px;color:#A7C4A0;">
            {st.session_state.get('role','—')}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Выйти", use_container_width=True):
            st.session_state.clear()
            st.rerun()
