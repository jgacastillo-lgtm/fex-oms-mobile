import streamlit as st
import requests

# --- CONFIGURACIÓN DE PÁGINA (Modo Móvil) ---
st.set_page_config(page_title="FEX OMS", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    /* Estilos para botones grandes en iPhone */
    div.stButton > button:first-child {
        height: 60px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 FEX Order Management")

# --- CATÁLOGOS (Puedes ajustar estos datos) ---
CASA_BOLSA = {
    "Bx+ (FEX SA)": {"email": "tperez@vepormas.com", "contrato": "6733737"},
    "Bx+ (Polígono)": {"email": "tperez@vepormas.com", "contrato": "6648026"},
    "Punto CB": {"email": "operaciones@puntocb.com", "contrato": "105501"}
}

# --- INTERFAZ DE USUARIO ---
st.subheader("1. Detalles de la Orden")
cb_seleccionada = st.selectbox("🏦 Casa de Bolsa", list(CASA_BOLSA.keys()))

col1, col2 = st.columns(2)
with col1:
    operacion = st.radio("🔄 Operación", ["Compra", "Venta"])
with col2:
    ticker = st.text_input("📈 Ticker / Clave", placeholder="Ej. NVDA, TMF").upper()

titulos = st.number_input("🔢 Cantidad de Títulos", min_value=1, step=1, format="%d")

st.divider()

# --- BOTÓN DE ENVÍO ---
# Pegar aquí la URL que te dio Google Apps Script
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz2hbIqLEkHv3pBuKxLt2MY5SdB9XRDihIzXoeax0cB8ywAnlcMjqA74F23xPumg86F/exec"

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
                # Enviar señal a Google Sheets
                respuesta = requests.post(WEBHOOK_URL, json=datos_orden)
                
                if respuesta.status_code == 200 and "Exito" in respuesta.text:
                    st.success(f"✅ ¡Borrador creado en Gmail para {operacion} {titulos} {ticker}!")
                    st.info("Revisa tu carpeta de 'Borradores' en Gmail. La orden ya está en el Blotter.")
                else:
                    st.error(f"Error al enviar: {respuesta.text}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
