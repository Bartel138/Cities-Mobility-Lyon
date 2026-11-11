import streamlit as st

# 1. Configuration de la page (titre de l'onglet, icône, largeur)
st.set_page_config(
    page_title="Cities Mobility - Lyon",
    page_icon="🚗",
    layout="wide"
)

# 2. Titre principal et sous-titre
st.title("🚗 Cities Mobility - Lyon")
st.markdown("### Analyse Spatiale, Accessibilité et Prédiction de l'Autopartage")
st.divider()

# 3. Organisation en deux colonnes
col1, col2 = st.columns([2, 1])

with col1:
    st.write("""
    **Bienvenue sur le tableau de bord de mobilité de la Métropole de Lyon.**
    
    Cette application a été développée pour répondre à un défi de taille : **Où implanter les nouvelles stations d'autopartage (Citiz) pour maximiser l'impact ?**
    
    Elle s'appuie sur un pipeline de données complet (Architecture Medallion) :
    *   🥉 **Couche Bronze** : Ingestion des données brutes (TCL, Vélo'v, Filosofi, SIRENE, etc.).
    *   🥈 **Couche Silver** : Nettoyage, filtrage spatial et standardisation des 18 sources de données.
    *   🥇 **Couche Gold** : Création d'indicateurs métiers et modélisation par Machine Learning (Random Forest).
    
    👈 **Utilisez le menu de gauche** pour naviguer entre les Statistiques de la ville et le Simulateur de Prédictions.
    """)

with col2:
    st.info("💡 **Note technique**")
    st.write("""
    *   **Grille d'analyse** : Carreaux de 200m x 200m (INSEE).
    *   **Périmètre** : Métropole de Lyon (4 334 carreaux).
    *   **Modèle ML** : Random Forest (32% de précision sur le Blind Test).
    """)

st.divider()

# 4. Section des limites (Transparence)
st.subheader("⚠️ Limites et Transparence")
st.markdown("""
Ce modèle est un outil d'aide à la décision, il ne remplace pas une étude terrain. 
*   **Données financières** : Les coûts (CAPEX/OPEX) sont des hypothèses, les comptes réels de Citiz n'étant pas publics.
*   **Concurrence** : L'application ne modélise pas la concurrence directe (Uber, taxis, autres opérateurs).
*   **Fréquences de transport** : Le réseau TCL est évalué par sa densité spatiale, sans intégrer les horaires (GTFS).
""")
