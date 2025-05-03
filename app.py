import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Autenticação via Streamlit Secrets ---
secret_json = st.secrets["gcp_service_account"]["credentials"]
creds_dict = json.loads(secret_json)

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
gc = gspread.authorize(creds)

SPREADSHEET_ID = "1iPouPzef7W-kw-2EIsDMq7K6g9A70dz-lwp2A0GU2lU"
sh = gc.open_by_key(SPREADSHEET_ID)

st.title("Questionário Diário de Prontidão para Treino")

# Captura nome e confirmação
name = st.text_input("Nome completo:")
confirm = st.checkbox(f"Confirmo que meu nome está correto: {name}")
email = st.text_input("E-mail:")

if confirm and email:
    st.write("### Responda cada item de 0 a 2 pontos:")
    questions = {
        "Sono": "Como foi seu sono na última noite?",
        "Dor Muscular": "Qual seu nível de dor muscular/rigidez hoje?",
        "Fadiga": "Qual seu nível de cansaço/fadiga hoje?",
        "Estresse": "Como está seu nível de estresse hoje?",
        "Motivação": "Qual sua motivação para treinar hoje?"
    }
    responses = {}
    for key, text in questions.items():
        responses[key] = st.slider(f"{text} (0–2)", 0, 2, 2)

    # Limiar e recomendação
    score = sum(responses.values())
    if score >= 8:
        recommendation = "Treino normal (100%)."
    elif score >= 6:
        recommendation = "Reduzir ~15% do volume/intensidade."
    elif score >= 4:
        recommendation = "Reduzir ~35% do volume/intensidade."
    else:
        recommendation = "Repouso recomendável."

    if st.button("Enviar respostas"):
        # Monta o registro
        record = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "email": email,
            **responses,
            "score": score,
            "recommendation": recommendation
        }
        # Envia para a aba do usuário (cria se não existir)
        try:
            ws = sh.worksheet(name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=name, rows="1000", cols="20")
            ws.append_row(list(record.keys()))
        ws.append_row(list(record.values()))
        st.success("Dados enviados com sucesso!")

    # Opção de gráfico de evolução
    if st.checkbox("Mostrar gráfico de evolução"):
        period = st.selectbox("Período (dias):", [7, 15, 30])
        rows = sh.worksheet(name).get_all_records()
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp").last(f"{period}D")
        st.line_chart(df["score"])

 },
 "nbformat": 4,
 "nbformat_minor": 5
}
