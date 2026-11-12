import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="Simulateur Budget", page_icon="🎯", layout="wide")

st.title("🎯 Simulateur d'Implantation")
st.write("Entrez votre budget pour découvrir les meilleurs emplacements à ouvrir, classés par notre algorithme d'optimisation spatiale.")

# =====================================================================
# 1. CHARGEMENT DES DONNÉES
# =====================================================================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "..", "Data")
    
    try:
        # On lit la table préparée par Fabric (qui contient le rang et les coûts)
        df = pd.read_csv(os.path.join(data_path, "recommandations_ml.csv"), on_bad_lines='skip')
        return df
    except Exception as e:
        st.error(f"⚠️ Erreur de chargement. Détail : {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # =====================================================================
    # 2. INTERFACE DE SIMULATION (Le Slider)
    # =====================================================================
    st.divider()
    
    # On récupère le coût unitaire directement depuis la table (ex: 25 000 €)
    cout_unitaire = df['cout_station_euros'].iloc[0]
    
    # L'utilisateur choisit son budget
    budget = st.slider(
        "💰 Sélectionnez votre budget d'investissement (€)", 
        min_value=int(cout_unitaire), 
        max_value=1000000, 
        value=100000, 
        step=int(cout_unitaire),
        format="%d €"
    )
    
    # CALCUL ULTRA-SIMPLE : Combien de stations puis-je m'offrir ?
    nb_stations_possibles = int(budget / cout_unitaire)
    
    # ON FILTRE JUSTE LA TABLE : On ne garde que les N premières stations du classement
    df_selection = df[df['rang_optimisation'] <= nb_stations_possibles].copy()
    
    st.divider()

    # =====================================================================
    # 3. AFFICHAGE DES KPIs
    # =====================================================================
    if len(df_selection) == 0:
        st.warning("⚠️ Budget insuffisant pour ouvrir une station.")
    else:
        st.subheader(f"📊 Résultats de la simulation : {nb_stations_possibles} stations ciblées")
        
        col1, col2, col3 = st.columns(3)
        
        # Calculs d'affichage (simples sommes)
        pop_couverte = df_selection['ind'].sum()
        roi_annuel = df_selection['roi_locations_par_an'].iloc[0]
        
        col1.metric("Population couverte", f"{pop_couverte:,.0f} habitants")
        col2.metric("Locations requises / an", f"{roi_annuel * len(df_selection):,} locations")
        col3.metric("Score de confiance moyen", f"{df_selection['proba_citiz_finale'].mean() * 100:.1f}%")
        
        st.divider()

        # =====================================================================
        # 4. LA CARTE FOLIUM
        # =====================================================================
        st.subheader("🗺️ Emplacements recommandés")
        
        m = folium.Map(location=[45.7640, 4.8357], zoom_start=12, tiles="OpenStreetMap")
        
        for _, row in df_selection.iterrows():
            # Couleur selon le score (Rouge = Excellent, Orange = Bon)
            couleur = 'red' if row['proba_citiz_finale'] > 0.8 else 'orange'
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=8,
                color=couleur,
                fill=True,
                fill_opacity=0.9,
                popup=folium.Popup(
                    f"<b>Rang :</b> {row['rang_optimisation']}<br>"
                    f"<b>Population :</b> {row['ind']} hab.<br>"
                    f"<b>Score ML :</b> {row['proba_citiz_finale']:.2f}<br>"
                    f"<b>Dans la ZFE :</b> {'Oui' if row['dans_zfe'] == 1 else 'Non'}",
                    max_width=200
                )
            ).add_to(m)

        st_folium(m, use_container_width=True, height=500)
        
        # =====================================================================
        # 5. TABLEAU DÉTAILLÉ
        # =====================================================================
        with st.expander("Voir le détail des stations sélectionnées"):
            colonnes_affichage = ['rang_optimisation', 'idcar_200m', 'ind', 'dans_zfe', 'proba_citiz_finale']
            st.dataframe(df_selection[colonnes_affichage].sort_values('rang_optimisation'), use_container_width=True)