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
        max-width: 400px !important;
        margin: 0 auto !important;
        padding-top: 12vh !important;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }

    .stTextInput input {
        background: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        color: #111827 !important;
    }
    .stTextInput input:focus {
        border-color: #6FCF97 !important;
        box-shadow: 0 0 0 2px rgba(111,207,151,0.2) !important;
    }
    .stTextInput label {
        color: #FFFFFF !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
    }
    .stButton > button {
        background: #6FCF97 !important;
        color: #0F2419 !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 10px !important;
        margin-top: 8px !important;
    }
    .stButton > button:hover {
        background: #57B97E !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Логотип
    st.markdown("""
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-size:26px;font-weight:700;color:#FFFFFF;letter-spacing:0.02em;">
        GreenIPath
      </div>
      <div style="font-size:11px;color:#6FCF97;letter-spacing:0.14em;margin-top:4px;">
        CARBON BI SYSTEM
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Карточка формы
    st.markdown("""
    <div style="background:#FFFFFF;border-radius:10px;padding:32px 28px;
                box-shadow:0 8px 32px rgba(0,0,0,0.25);">
      <div style="font-size:18px;font-weight:700;color:#111827;margin-bottom:4px;">
        Вход в систему
      </div>
      <div style="font-size:13px;color:#6B7280;margin-bottom:24px;">
        Введите учётные данные для доступа
      </div>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("ЛОГИН", placeholder="Введите логин", key="login_user")
    password = st.text_input("ПАРОЛЬ", type="password", placeholder="Введите пароль", key="login_pass")

    if st.button("Войти", type="primary", use_container_width=True):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"]      = username
            st.session_state["role"]          = USERS[username]["role"]
            st.session_state["display_name"]  = USERS[username]["name"]
            st.rerun()
        else:
            st.error("Неверный логин или пароль")

    st.markdown("""
    <div style="text-align:center;margin-top:24px;font-size:11px;color:rgba(255,255,255,0.35);">
      © 2025 GreenIPath · Конфиденциально
    </div>
    """, unsafe_allow_html=True)


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
