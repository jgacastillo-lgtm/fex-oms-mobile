import streamlit as st
import requests

# --- CONFIGURACIÓN DE PÁGINA (Modo Móvil) ---
st.set_page_config(page_title="FEX OMS", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 60px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE SEGURIDAD (LOGIN) ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["OMS_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Elimina la contraseña de la memoria
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔒 Acceso FEX Trading</h2>", unsafe_allow_html=True)
        st.text_input("Ingresa tu PIN de FEX:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center;'>🔒 Acceso FEX Trading</h2>", unsafe_allow_html=True)
        st.text_input("Ingresa tu PIN de FEX:", type="password", on_change=password_entered, key="password")
        st.error("❌ PIN incorrecto")
        return False
    return True

# --- SI LA CONTRASEÑA ES CORRECTA, MUESTRA LA APP ---
if check_password():
    st.title("📱 FEX Order Management")

    # --- CATÁLOGOS ---
    CASA_BOLSA = {
        "Bx+ (FEX SA)": {"email": "tperez@vepormas.com", "contrato": "6733737"},
        "Bx+ (Polígono)": {"email": "tperez@vepormas.com", "contrato": "6648026"},
        "Punto CB": {"email": "operaciones@puntocb.com", "contrato": "105501"}
    }

    st.subheader("1. Detalles de la Orden")
    cb_seleccionada = st.selectbox("🏦 Casa de Bolsa", list(CASA_BOLSA.keys()))

    col1, col2 = st.columns(2)
    with col1:
        operacion = st.radio("🔄 Operación", ["Compra", "Venta"])
    with col2:
        ticker = st.text_input("📈 Ticker / Clave", placeholder="Ej. NVDA").upper()

    titulos = st.number_input("🔢 Cantidad de Títulos", min_value=1, step=1, format="%d")
    st.divider()

    # --- BOTÓN DE ENVÍO ---
    WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

    if st.button("🚀 GENERAR BORRADOR EN GMAIL", type="primary"):
        if ticker.strip() == "":
            st.error("⚠️ Por favor ingresa un Ticker.")
        else:
            with st.spinner("Conectando con la mesa..."):
                datos_orden = {
                    "tipoOrden": operacion,
                    "clavePizarra": ticker,
                    "cantidad": titulos,
                    "destinatarioPrincipal": CASA_BOLSA[cb_seleccionada]["email"],
                    "numeroContrato": CASA_BOLSA[cb_seleccionada]["contrato"]
                }
                
                try:
                    respuesta = requests.post(WEBHOOK_URL, json=datos_orden)
                    if respuesta.status_code == 200 and "Exito" in respuesta.text:
                        st.success(f"✅ ¡Borrador creado en Gmail para {operacion} {titulos} {ticker}!")
                    else:
                        st.error(f"Error al enviar: {respuesta.text}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
