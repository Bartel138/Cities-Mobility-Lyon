import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
import os

# Configuration de la page
st.set_page_config(page_title="Cartographie - Lyon", page_icon="🗺️", layout="wide")

st.title("🗺️ Cartographie de l'Offre de Mobilité")
st.write("Visualisez l'ensemble du réseau (Points et Lignes) et filtrez par type de transport.")

# =====================================================================
# 1. CHARGEMENT DES DONNÉES
# =====================================================================
@st.cache_data
def load_data():
    # On trouve le dossier où se trouve ce script (App/pages)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # On remonte d'un niveau (vers App/) et on entre dans Data/
    data_path = os.path.join(current_dir, "..", "Data")
    
    try:
        # 🛡️ CORRECTIF : on_bad_lines='skip' ignore les lignes avec des virgules en trop
        df_offre = pd.read_csv(os.path.join(data_path, "offres_de_mobilite.csv"), on_bad_lines='skip')
        df_metro = pd.read_csv(os.path.join(data_path, "lignes_metro.csv"), on_bad_lines='skip')
        df_tram = pd.read_csv(os.path.join(data_path, "lignes_tram.csv"), on_bad_lines='skip')
        df_bus = pd.read_csv(os.path.join(data_path, "lignes_bus.csv"), on_bad_lines='skip')
        return df_offre, df_metro, df_tram, df_bus
    except Exception as e:
        st.error(f"⚠️ Erreur de chargement. Détail : {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_offre, df_metro, df_tram, df_bus = load_data()

if not df_offre.empty:
    # =====================================================================
    # 2. INDICATEURS (KPIs)
    # =====================================================================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Points", f"{len(df_offre):,}")
    
    # Comptage par source (avec gestion des majuscules/minuscules)
    nb_tcl = len(df_offre[df_offre['source'].str.lower() == 'tcl'])
    nb_velo = len(df_offre[df_offre['source'].str.lower() == 'velo'])
    nb_citiz = len(df_offre[df_offre['source'].str.lower() == 'citiz'])
    
    col2.metric("Arrêts TCL", f"{nb_tcl:,}")
    col3.metric("Stations Vélo'v", f"{nb_velo:,}")
    col4.metric("Stations Citiz", f"{nb_citiz:,}")
    
    st.divider()

    # =====================================================================
    # 3. FILTRES (Barre latérale)
    # =====================================================================
    st.sidebar.header("Filtres de la carte")
    
    # Liste des types de services disponibles
    types_dispos = df_offre['type_service'].unique().tolist()
    
    # Par défaut, on coche tout
    type_transport = st.sidebar.multiselect(
        "Types de transport à afficher",
        options=types_dispos,
        default=types_dispos
    )

    # =====================================================================
    # 4. LA CARTE FOLIUM
    # =====================================================================
    m = folium.Map(location=[45.7640, 4.8357], zoom_start=12, tiles="CartoDB positron")

    # --- A. Les tracés de lignes (Bus, Tram, Métro) ---
    fg_metro = folium.FeatureGroup(name="🚇 Lignes Métro", show=True)
    fg_tram = folium.FeatureGroup(name="🚋 Lignes Tram", show=True)
    fg_bus = folium.FeatureGroup(name="🚌 Lignes Bus", show=False)

    # Fonction pour décoder le JSON et tracer les lignes
    def tracer_lignes(df, feature_group, couleur):
        for _, row in df.iterrows():
            geom_str = row.get('geometry')
            if pd.isna(geom_str): continue
            try:
                # On lit le texte JSON exporté de Spark
                geom = json.loads(geom_str) if isinstance(geom_str, str) else geom_str
                if geom.get('type') == 'MultiLineString':
                    for line in geom['coordinates']:
                        # Inversion [lon, lat] en [lat, lon] pour Folium
                        folium.PolyLine([[pt[1], pt[0]] for pt in line], color=couleur, weight=3, opacity=0.7).add_to(feature_group)
            except Exception:
                pass

    tracer_lignes(df_metro, fg_metro, "#8e44ad") # Violet
    tracer_lignes(df_tram, fg_tram, "#e67e22")   # Orange
    tracer_lignes(df_bus, fg_bus, "#95a5a6")     # Gris

    fg_metro.add_to(m)
    fg_tram.add_to(m)
    fg_bus.add_to(m)

    # --- B. Les points (Offre) ---
    fg_points = folium.FeatureGroup(name="📍 Arrêts & Stations")
    
    # Dictionnaire des couleurs par type
    couleurs = {
        'autopartage': 'blue',
        'velo_partage': 'green',
        'transport_commun': 'red',
        'trottinette_partage': 'purple',
        'parking': 'darkblue',
        'recharge_ve': 'darkgreen'
    }

    # On filtre selon ce que l'utilisateur a coché
    df_filtre = df_offre[df_offre['type_service'].isin(type_transport)]

    for _, row in df_filtre.iterrows():
        if pd.notna(row['lat']) and pd.notna(row['lon']):
            couleur = couleurs.get(row['type_service'], 'gray')
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=4,
                color=couleur,
                fill=True,
                fill_opacity=0.8,
                popup=f"<b>{row['type_service']}</b><br>{row['nom']}"
            ).add_to(fg_points)
            
    fg_points.add_to(m)

    # Ajout du menu des calques en haut à droite
    folium.LayerControl().add_to(m)

    # Affichage
    st.subheader("Carte Interactive")
    folium_static(m, width=1200, height=600)