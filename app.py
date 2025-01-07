import streamlit as st
import pandas as pd
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Titre de l'application
st.title("Surveillance des Effets Secondaires du Venetoclax")

# Description
st.markdown(
    """
    Cette application permet de surveiller les effets secondaires liés au traitement par Venetoclax.
    Veuillez entrer les résultats des paramètres cliniques et biologiques pour chaque jour.
    """
)

# Collecte des données utilisateur
st.sidebar.header("Entrée des paramètres")
data = {
    "Jour": st.sidebar.number_input("Jour", min_value=1, max_value=30, step=1),
    "Température (°C)": st.sidebar.number_input("Température (°C)", min_value=30.0, max_value=42.0, step=0.1),
    "Tension artérielle systolique": st.sidebar.number_input("Tension systolique (mmHg)", min_value=50, max_value=200, step=1),
    "Tension artérielle diastolique": st.sidebar.number_input("Tension diastolique (mmHg)", min_value=30, max_value=130, step=1),
    "Potassium (K+)": st.sidebar.number_input("Potassium (K+, mmol/L)", min_value=1.0, max_value=10.0, step=0.1),
    "Calcium (Ca++)": st.sidebar.number_input("Calcium (Ca++, mmol/L)", min_value=0.5, max_value=5.0, step=0.1),
    "Phosphore (P)": st.sidebar.number_input("Phosphore (P, mmol/L)", min_value=0.5, max_value=5.0, step=0.1),
    "Créatinine": st.sidebar.number_input("Créatinine (µmol/L)", min_value=10, max_value=1000, step=1),
    "Diurèse": st.sidebar.number_input("Diurèse (mL/24h)", min_value=0, max_value=5000, step=10)
}

# Bouton pour enregistrer les données
if st.sidebar.button("Enregistrer les données"):
    try:
        # Chargement des données dans un DataFrame
        if "surveillance_data" not in st.session_state:
            st.session_state["surveillance_data"] = pd.DataFrame(columns=data.keys())
        df = st.session_state["surveillance_data"]
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        st.session_state["surveillance_data"] = df
        st.success("Les données ont été enregistrées avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement des données : {e}")

# Affichage des données enregistrées
if "surveillance_data" in st.session_state:
    st.subheader("Historique des données enregistrées")
    st.dataframe(st.session_state["surveillance_data"])

# Fonction pour générer un PDF
def generate_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport de Surveillance", ln=True, align='C')
    pdf.ln(10)

    for i, row in dataframe.iterrows():
        pdf.cell(0, 10, txt=f"Jour {row['Jour']} :", ln=True)
        for col in dataframe.columns:
            if col != "Jour":
                pdf.cell(0, 10, txt=f"  {col}: {row[col]}", ln=True)
        pdf.ln(5)

    file_path = "rapport_surveillance.pdf"
    pdf.output(file_path)
    return file_path

# Bouton pour générer le PDF
if st.button("Générer le PDF"):
    if "surveillance_data" in st.session_state:
        file_path = generate_pdf(st.session_state["surveillance_data"])
        st.success(f"PDF généré avec succès : {file_path}")
        with open(file_path, "rb") as pdf_file:
            st.download_button(
                label="Télécharger le PDF",
                data=pdf_file,
                file_name="rapport_surveillance.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Aucune donnée disponible pour générer le PDF.")

# Fonction pour envoyer un email avec pièce jointe
def send_email_with_attachment(recipient_email, subject, body, file_path):
    sender_email = "your_email@example.com"  # Remplacez par votre email
    sender_password = "your_password"  # Remplacez par votre mot de passe

    # Création de l'email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Ajout du fichier PDF
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

    # Envoi de l'email
    try:
        server = smtplib.SMTP('smtp.example.com', 587)  # Remplacez par votre serveur SMTP
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False, str(e)

# Bouton pour envoyer le PDF par email
recipient_email = st.text_input("Email du destinataire")
if st.button("Envoyer par email"):
    if "surveillance_data" in st.session_state:
        file_path = generate_pdf(st.session_state["surveillance_data"])
        success, error_message = send_email_with_attachment(
            recipient_email,
            "Rapport de Surveillance",
            "Veuillez trouver ci-joint le rapport de surveillance.",
            file_path
        )
        if success:
            st.success("Email envoyé avec succès !")
        else:
            st.error(f"Erreur lors de l'envoi de l'email : {error_message}")
    else:
        st.error("Aucune donnée disponible pour envoyer le PDF.")
