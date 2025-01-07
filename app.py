import streamlit as st
import pandas as pd

# Titre de l'application
st.title("Surveillance des Effets Secondaires du Venetoclax")

# Description
st.markdown(
    """
    Cette application permet de surveiller les effets secondaires liés au traitement par Venetoclax.
    Veuillez entrer les résultats des paramètres cliniques et biologiques pour chaque jour.
    """
)

# Initialisation des seuils critiques
seuils = {
    "Température (°C)": [36.0, 38.0],
    "Tension artérielle systolique": [90, 140],
    "Tension artérielle diastolique": [60, 90],
    "Potassium (K+)": [3.5, 5.0],
    "Calcium (Ca++)": [2.2, 2.6],
    "Phosphore (P)": [0.8, 1.5],
    "Créatinine": [50, 110],  # Valeurs en µmol/L
    "Diurèse": [800, 2000]  # Valeurs en mL/24h
}

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

# Analyse des données
if "surveillance_data" in st.session_state:
    st.subheader("Analyse des effets secondaires")
    df = st.session_state["surveillance_data"]

    def detect_anomalies(row):
        anomalies = []
        for param, (min_val, max_val) in seuils.items():
            # Vérifier que la colonne existe dans le DataFrame
            if param in row:
                if row[param] < min_val or row[param] > max_val:
                    anomalies.append(param)
        return anomalies

    df["Anomalies"] = df.apply(detect_anomalies, axis=1)
    st.write("Liste des anomalies détectées :")
    st.dataframe(df[["Jour", "Anomalies"]])

    # Alertes si des anomalies critiques sont détectées
    anomalies_detectees = df["Anomalies"].explode().dropna().unique()
    if len(anomalies_detectees) > 0:
        st.error(f"Paramètres critiques détectés : {', '.join(anomalies_detectees)}. Veuillez consulter un médecin.")
    else:
        st.success("Aucune anomalie critique détectée.")
