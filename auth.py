import streamlit as st

USERS = {
    "admin":   {"password": "greenipath2025", "role": "Администратор", "name": "Admin"},
    "manager": {"password": "carbon2025",     "role": "Менеджер",      "name": "Project Manager"},
    "analyst": {"password": "bi2025",         "role": "Аналитик",      "name": "Analyst"},
}

def login_page():
    st.markdown("""
    <style>
    .stApp { background-color: #1A3D2B; }
    .block-container { 
        max-width: 420px; 
        margin: 0 auto; 
        padding-top: 8vh;
    }
    .login-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 40px 36px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
    }
    .login-logo {
        font-size: 22px;
        font-weight: 700;
        color: #1A3D2B;
        letter-spacing: 0.02em;
        margin-bottom: 4px;
    }
    .login-sub {
        font-size: 12px;
        color: #6B7280;
        letter-spacing: 0.08em;
        margin-bottom: 28px;
    }
    .login-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 20px;
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
    section[data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-logo">GreenIPath</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">CARBON BI SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Вход в систему</div>', unsafe_allow_html=True)

    username = st.text_input("Логин", placeholder="Введите логин", key="login_user")
    password = st.text_input("Пароль", type="password", placeholder="Введите пароль", key="login_pass")

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

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-top:20px;font-size:11px;color:rgba(255,255,255,0.4);">
      GreenIPath Carbon BI · Конфиденциально
    </div>
    """, unsafe_allow_html=True)


def check_auth():
    """Вызывается в начале каждой страницы — проверяет авторизацию"""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        login_page()
        st.stop()


def render_user_info():
    """Показывает имя пользователя и кнопку выхода в сайдбаре"""
    with st.sidebar:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.08);border-radius:6px;
             padding:10px 12px;margin-bottom:12px;">
          <div style="font-size:11px;color:#A7C4A0;margin-bottom:2px;">ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ</div>
          <div style="font-size:13px;font-weight:600;color:#FFFFFF;">
            {st.session_state.get('display_name','—')}
          </div>
          <div style="font-size:11px;color:#A7C4A0;">
            {st.session_state.get('role','—')}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Выйти из системы", use_container_width=True):
            st.session_state.clear()
            st.rerun()
