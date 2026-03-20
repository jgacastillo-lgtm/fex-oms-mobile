import streamlit as st
import requests
import os
import base64

# --- CONFIGURACIÓN DE PÁGINA INSTITUCIONAL ---
# El 'page_icon' configura el favicon y el icono que iOS intentará usar para el home screen
st.set_page_config(page_title="FEX OMS", page_icon="FEXTRADING2.png", layout="centered")

# --- FUNCIÓN PARA CARGAR EL LOGO (REUTILIZADA) ---
def obtener_logo_base64():
    nombre_archivo = "FEXTRADING2.png"
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    return None

# --- ESTILOS CSS PERSONALIZADOS (MODO DARK INSTITUCIONAL) ---
st.markdown("""
    <style>
    /* Estilos para botones grandes y rojos en iPhone */
    div.stButton > button:first-child {
        height: 60px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        background-color: #ff3333; /* Rojo institucional para el botón principal */
        border-color: #ff3333;
    }
    div.stButton > button:first-child:active, div.stButton > button:first-child:focus {
        background-color: #cc0000;
        border-color: #cc0000;
    }
    /* Estilo modo Bloomberg/Trading */
    body {
        background-color: #000000;
        color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE SEGURIDAD (LOGIN) ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["OMS_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Logo centrado en pantalla de Login
        logo_b64 = obtener_logo_base64()
        if logo_b64:
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="data:image/png;base64,{logo_b64}" width="200">
                </div>
                <h2 style='text-align: center; color: #ffb84d;'>🔒 Acceso FEX Trading OMS</h2>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown("<h2 style='text-align: center;'>🔒 Acceso FEX Trading</h2>", unsafe_allow_html=True)
            
        st.text_input("Ingresa tu PIN de FEX:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Ingresa tu PIN de FEX:", type="password", on_change=password_entered, key="password")
        st.error("❌ PIN incorrecto")
        return False
    return True

# --- SI LA CONTRASEÑA ES CORRECTA, MUESTRA LA APP ---
if check_password():
    # Cabecera Institucional
    logo_b64 = obtener_logo_base64()
    if logo_b64:
        # Mostramos el logo centrado en la parte superior
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 25px;">
                <img src="data:image/png;base64,{logo_b64}" width="200">
            </div>
            """,
            unsafe_allow_html=True
        )
        # st.title("📱 Order Management")
    else:
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

    # --- BOTÓN DE ENVÍO SECRETO ---
    WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

    # Botón con tipo primary para que tome el color rojo que configuramos en el CSS
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
