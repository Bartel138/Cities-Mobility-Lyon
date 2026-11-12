Claude
Oui, j’ai plusieurs idées. Voici d’abord ce qui rend le rendu peu pro, d’après ta capture et ton code.

Ce qui ne va pas
Le fond OpenStreetMap est trop chargé. Routes, zones et noms de lieux se battent avec tes points, qui sont en couleurs pastel.
Pas de hiérarchie. Les arrêts TCL (rouge) sont les plus nombreux et noient le reste. Tes Citiz, qui sont le sujet du projet, sont des points comme les autres.
Couleurs par défaut de Folium (blue, green, red, purple), sans palette pensée.
Pas de légende. On ne comprend les couleurs qu’en ouvrant le menu des calques.
Les popups affichent des identifiants techniques (transport_commun, recharge_ve).
Trois st.divider(), quatre KPI par défaut, filtre sur une demi-largeur, bouton « Deploy » visible.
Mes idées, par effort croissant
Facile (une soirée) :

Fond gris clair pour que les points ressortent.
Palette cohérente et rayon selon l’importance : gris discret et petit pour les TCL, bleu vif et gros pour Citiz.
Un calque par type, avec le nombre dans le nom du calque, et des libellés français dans les infobulles.
Les vraies couleurs des lignes TCL (la colonne couleur_hex existe dans tes données de lignes) à la place du violet, orange, gris.
Thème Streamlit dans .streamlit/config.toml (couleur principale, police), et masquer le bouton « Deploy ».
Moyen :

Légende sous forme de pastilles colorées à côté des filtres.
KPI alignés sur la légende (même couleur que les points), avec les chiffres de population desservie quand tu les auras.
Pied de page « Sources et fraîcheur » : les dates d’ingestion que tu as ajoutées dans le Bronze, c’est un argument de sérieux.
Plus ambitieux (utile pour le sujet) :

Cercles de 400 m autour d’un point cliqué, pour montrer visuellement la zone à 5 minutes à pied.
Couche de densité de population (carroyage) en dessous des points.
pydeck (déjà intégré à Streamlit) si Folium devient lent : il gère mieux plus de 10 000 points. Moins de contrôle sur les popups.
Première étape à tester
Elle regroupe les trois premiers points (fond, couleurs, un calque par type). Je l’ai testée sur des données synthétiques, pas sur ton CSV. Dans ton code, remplace la carte (section 4, de m = folium.Map(...) jusqu’à fg_points.add_to(m)) par :

python
LIBELLES = {'transport_commun': "Arrêt TCL", 'parking': "Parking", 'recharge_ve': "Borne de recharge",
            'velo_partage': "Station Vélo'v", 'trottinette_partage': "Trottinette Dott",
            'autopartage': "Station Citiz"}
# (couleur, rayon) : du plus discret (très nombreux) au plus important
STYLE = {'transport_commun': ('#9CA3AF', 3), 'parking': ('#6B7280', 4), 'recharge_ve': ('#14B8A6', 4),
         'velo_partage': ('#16A34A', 5), 'trottinette_partage': ('#F59E0B', 5),
         'autopartage': ('#2563EB', 7)}

m = folium.Map(location=[45.7640, 4.8357], zoom_start=12, control_scale=True, attr="Esri",
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}")

# (garde ici ton bloc A : les trois FeatureGroup de lignes et tracer_lignes)

for type_service, (couleur, rayon) in STYLE.items():
    sous = df_filtre_kpi[df_filtre_kpi['type_service'] == type_service]
    if sous.empty:
        continue
    fg = folium.FeatureGroup(name=f"{LIBELLES[type_service]} ({len(sous):,})".replace(",", " "))
    for r in sous.itertuples():
        if pd.notna(r.lat) and pd.notna(r.lon):
            folium.CircleMarker(location=[r.lat, r.lon], radius=rayon, color="white", weight=1,
                                fill=True, fill_color=couleur, fill_opacity=0.9,
                                tooltip=f"{LIBELLES[type_service]} · {r.nom}").add_to(fg)
    fg.add_to(m)
Points à noter :

N’utilise pas tiles="CartoDB positron" : avec la version de Folium que j’ai testée, il demande maintenant une clé d’API. Le fond Esri, lui, n’en demande pas (c’est celui de tes notebooks).
Je suppose que type_service contient bien les six valeurs de ton dictionnaire couleurs. Un type absent du STYLE ne sera pas affiché.
J’ai remplacé les popups par des tooltip, plus légers. Sur mon jeu synthétique de 5 600 points, la carte pèse 4 Mo ; avec tes ~13 000 points elle sera plus lourde, ce qui te dira si on doit passer à des clusters ou à pydeck.
Teste-la et envoie-moi une capture : on affinera la palette d’après le rendu réel, puis on passera au thème et à la légende.


import streamlit as st import pandas as pd import folium from streamlit_folium import st_folium import json import os # Configuration de la page (pleine largeur) st.set_page_config(page_title="Cartographie - Lyon", page_icon="🗺️", layout="wide") st.title("🗺️ Cartographie Interactive") s

pasted

ce code est juste pas pro, et presque ridiccule,  les lignes de tram ou bus ou metro ne sont pas tracé,  tres pauvre pas visuellement attirante, que peut-on faire pour rendre cette carte et cette première page pro, on peutt tou changer si tu veux là, ça va pas d'autre ont un rendu bien plus professionnele et bien plus intercatif et agreable là, j'ai l'imoression c'est une page de 2000

Cartographie
PY
Continuer

J’ai refait la page cartographie en entier et ajouté un fichier de thème. Je l’ai testée sans interface graphique, avec des données fabriquées (mêmes noms de colonnes que ton code), mais je n’ai pas vu le rendu à l’écran.

Installation
Remplace ta page par cartographie.py (dans pages/).
Ajoute config.toml dans un dossier .streamlit/ à la racine de l’app. Il donne un thème clair, une couleur principale bleue, et masque la barre Deploy.
Les lignes qui ne s’affichaient pas
Ton ancien code les ignorait en silence : except: pass cachait toute erreur de lecture. Je n’ai pas tes fichiers lignes_*.csv, donc je ne connais pas la vraie cause. Les trois pistes les plus probables sont une géométrie stockée comme dictionnaire Python (apostrophes) au lieu de JSON, une géométrie en WKT, ou un type LineString au lieu de MultiLineString. La nouvelle page lit les trois formats.

Elle a aussi un panneau « Qualité des données affichées » en bas de page. Il dit, pour le métro, le tram et le bus, combien de lignes sont dans le fichier, combien sont tracées, combien sont illisibles, et affiche le début de la géométrie. Si tes lignes ne s’affichent toujours pas, copie-moi ce tableau.

Ce qui change
Fond de carte clair, sombre ou satellite, à choisir dans le menu.
Hiérarchie visuelle : les arrêts TCL sont petits et gris, Citiz est gros et bleu vif.
Légende flottante sur la carte, et filtres avec pastilles de couleur et effectifs.
Cartes de chiffres à la place des st.metric : points affichés, stations Citiz, habitants, lignes tracées.
Accessibilité à 400 m : tu cliques sur la carte, un cercle apparaît, et un panneau donne le nombre de points de mobilité par type dans le cercle, les habitants à moins de 400 m (estimés avec les centres des carreaux) et la station Citiz la plus proche. C’est l’objectif 1 du sujet, en interactif.
Population : couche de densité, ou profils K-Means dessinés en carreaux (un seul calque, beaucoup plus léger que tes 13 000 cercles).
Les tracés utilisent la colonne couleur_hex si elle existe dans tes CSV de lignes, sinon des couleurs par défaut.
L’ancien menu de calques de Folium est supprimé, car la barre latérale suffit.
Ce que j’ai vérifié
Le script s’exécute sans erreur avec tous les filtres activés : bus, TCL, parkings, K-Means, densité, ZFE, fond sombre.
Les trois formats de géométrie sont lus ; une ligne illisible et une ligne en Lambert-93 (mètres) sont comptées à part, sans faire planter la page.
Le clic, le cercle de 400 m, le panneau et le bouton « Effacer » fonctionnent, sans boucle de rafraîchissement.
Poids de la carte avec les données fabriquées : 0,1 Mo par défaut, 1,8 Mo avec 9 000 arrêts TCL, 2,6 Mo avec les profils K-Means.
Ce que je n’ai pas pu vérifier
Le rendu visuel réel : j’ai testé sans navigateur. Les fonds Esri « sombre » et « satellite » n’ont pas pu être chargés d’ici, seul le fond clair est celui que tu utilisais déjà.
Tes vrais CSV. Mon code suppose les colonnes de ton ancien code : type_service, source, nom, lat, lon ; ind, lat, lon, cluster_kmeans, dans_zfe. Un type_service inconnu s’affiche comme « Autre ».
La compatibilité avec ta version de Streamlit. J’ai testé avec la 1.67 et streamlit-folium 0.27.4. Si ton Streamlit est ancien, st.rerun() demande au moins la 1.27.
Les noms des profils K-Means : ils s’affichent « Profil 0 » à « Profil 4 », faute de libellés dans ton fichier.
Envoie-moi une capture du rendu, avec le tableau de qualité des données s’il y a un problème de lignes : on affinera les couleurs et la mise en page d’après ce que tu vois.

Cartographie
PY
Config
TOML
la carte n'a rien de pro, tu ondonnds cityz avec tout les auto partage,  / les filtres sot pas moderne, la carte n'est pas modere, o a pas de heatmap par rapport à un densité de trasport par exemple, les lignes de ream, bus, lettro ne sont pas traces et visible sur la map, .... c'est grave, je note 3/10 pour cette mpa,  utilise la cahrte grphique de cityz,  / la crte doit s'inittialiser sur la frace etière et ous permetre de visueliser directement que c'est sur lyon que il y'a l'etude,  la crte à l'air, simplement de basse qualité, ...3/10.

Je note tes points, ils sont justes : la page ne tenait pas ses promesses. Avant de réécrire, je cherche la charte graphique de Citiz, et je vérifie si je peux tester le rendu dans un vrai navigateur ici, ce que je n’avais pas fait.

Continuer

2 fichiers lus
Ce n’est pas un bug de la carte : mon test a cliqué sur le lien « Leaflet » du bas de page à cause d’un mauvais décalage. Je refais le clic au centre de la carte.

Exécuté 10 commandes, 3 fichiers lus, fichiers partagés
Tes critiques étaient justes : la version précédente restait une carte Folium rechargée à chaque clic, que je n’avais jamais vue s’afficher. J’ai tout repris avec une vraie carte interactive (Leaflet), cette fois testée dans un navigateur (Firefox sans interface) avec des données fabriquées : captures, vrais clics de souris, boutons, et la page Streamlit complète.

Tes points, un par un
Citiz confondu avec l’autopartage. Les calques se font maintenant par opérateur, d’après ta colonne source : Citiz, Leo&Go, Vélo’v, Dott, arrêts TCL, parkings, bornes de recharge. Le tableau « Qualité des données affichées » (en bas de page) montre la répartition opérateur / source / type_service. Si la source de Leo&Go contient un autre nom que leo, il apparaîtra comme « Autre » : dis-le-moi.
Filtres pas modernes. Panneau flottant avec interrupteurs, sélecteurs en pastilles, fond de carte clair / sombre / satellite / plan, et légende dynamique. Tout se règle dans la carte, sans recharger la page.
Pas de heatmap. Trois cartes thermiques : Population, Arrêts TCL et Offre partagée, avec un curseur d’intensité. Un mode Profils K-Means dessine les carreaux de 200 m.
Lignes non tracées. Je ne connais pas la vraie cause dans tes CSV (je ne les ai pas). La page lit maintenant quatre formats de géométrie (JSON, dictionnaire Python, WKT, affichage numpy) et, si le CSV reste illisible, recharge les lignes en direct depuis le flux TCL (la même requête que ton notebook). Si tout échoue, le calque affiche « données non lues » au lieu de disparaître en silence.
Départ sur la France entière. La carte s’ouvre sur la France, avec Lyon signalé par un repère animé et le contour de la zone d’étude. Le bouton « Explorer Lyon » (ou un clic sur le repère) zoome, et les données apparaissent à partir du niveau de zoom 9.
Charte Citiz. Je n’ai pas pu récupérer la charte officielle (aucun kit de marque accessible). La seule information sourcée que j’ai trouvée : les voitures sont blanches avec un logo vert. J’ai donc mis un vert approché (
#1FA463) pour l’accent, les cartes de chiffres et les stations Citiz. Il est dans un seul endroit du code, le dictionnaire CHARTE en haut du fichier : donne-moi le code couleur exact et la typographie du kit Citiz, ou remplace-le toi-même.
J’ai gardé et amélioré le clic d’accessibilité à 400 m : la carte zoome sur le cercle, et le panneau donne le nombre de points par opérateur, les habitants à proximité, le profil du quartier et la station Citiz la plus proche.

Installation
Remplace ta page par cartographie.py et ajoute config.toml dans .streamlit/. La page n’a plus besoin de streamlit-folium. Le navigateur doit avoir accès à Internet (la bibliothèque de carte et les fonds Esri viennent de CDN).

Ce que je n’ai pas pu vérifier
Les fonds de carte : mon environnement n’a pas accès aux serveurs de tuiles. Sur mes captures la carte est donc grise, avec tes points par-dessus. Le rendu avec les fonds est à vérifier chez toi.
Tes vraies données : j’ai testé avec des nuages de points fabriqués autour de Lyon, au même format de colonnes que ton ancien code.
Le chargement en direct des lignes TCL : testé avec un faux serveur, pas avec le vrai.
La vitesse avec tes ~13 000 points, tes carreaux et les lignes de bus : sur mes données la page pèse environ 0,7 Mo.
Ta version de Streamlit (j’ai testé avec la 1.67).
Ce que je te demande
Envoie-moi une capture de la page chez toi, le tableau « Qualité des données affichées », et le code couleur exact de Citiz. S’il y a encore un défaut de rendu, je corrigerai à partir de ce que tu vois.

Cartographie
PY
Config
TOML



Claude est une IA et peut commettre des erreurs. Veuillez vérifier les réponses.
Cartographie · PY
import ast
import json
import math
import os
import re
 
import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
 
st.set_page_config(page_title="Offre de mobilité · Lyon", page_icon="🗺️", layout="wide",
                   initial_sidebar_state="collapsed")
 
# =====================================================================
# 0. CHARTE GRAPHIQUE (à ajuster ici, en un seul endroit)
# =====================================================================
# Citiz : voitures blanches avec un logo vert. Le vert ci-dessous est une APPROXIMATION :
# remplace-le par le code exact de la charte Citiz (kit de marque fourni par Citiz).
CHARTE = {"accent": "#1FA463", "accent_sombre": "#168650", "accent_doux": "#E6F5EC"}
 
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data")
CENTRE_LYON = [45.7640, 4.8357]
HAUTEUR_CARTE = 780
 
# (clé, motif sur « source type_service », libellé, groupe, couleur, rayon, affiché par défaut)
OPERATEURS = [
    ("citiz", r"citiz", "Citiz", "Autopartage", CHARTE["accent"], 9, True),
    ("leogo", r"leo", "Leo&Go", "Autopartage", "#7C3AED", 6, True),
    ("velov", r"v[ée]lo", "Vélo'v", "Vélos et trottinettes", "#2563EB", 6, True),
    ("dott", r"dott|trottinette", "Dott", "Vélos et trottinettes", "#F59E0B", 5, False),
    ("tcl", r"tcl|transport_commun", "Arrêts TCL", "Transport en commun", "#64748B", 3.5, False),
    ("parking", r"parking", "Parkings", "Équipements", "#334155", 5, False),
    ("irve", r"irve|recharge", "Bornes de recharge", "Équipements", "#0EA5E9", 4, False),
]
GROUPE_PAR_TYPE = {"autopartage": "Autopartage", "velo_partage": "Vélos et trottinettes",
                   "trottinette_partage": "Vélos et trottinettes", "transport_commun": "Transport en commun"}
 
# clé -> (libellé, couleur par défaut, épaisseur, opacité, affiché par défaut, fichier CSV, couche WFS)
WFS_SYTRAL = "https://data.grandlyon.com/geoserver/sytral/ows"
RESEAU = {
    "metro": ("Métro et funiculaire", "#7C3AED", 5, 0.95, True, "lignes_metro.csv", "sytral:tcl_sytral.tcllignemf_2_0_0"),
    "tram": ("Tramway", "#EA580C", 4, 0.9, True, "lignes_tram.csv", "sytral:tcl_sytral.tcllignetram_2_0_0"),
    "bus": ("Bus", "#94A3B8", 1.6, 0.65, False, "lignes_bus.csv", "sytral:tcl_sytral.tcllignebus_2_0_0"),
}
MODELE = r'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--accent:__ACCENT__;--accent-dark:__ACCENT_DARK__;--accent-soft:__ACCENT_SOFT__;--ink:#0F172A;--muted:#64748B;--line:rgba(15,23,42,.09)}
*{box-sizing:border-box}
html,body{height:100%;margin:0;font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:var(--ink);background:#E5E7EB;overflow:hidden}
#map{position:absolute;inset:0;background:#E8ECF0;cursor:grab}
.card{background:rgba(255,255,255,.95);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 30px rgba(15,23,42,.15)}
#left,#right{position:absolute;top:14px;bottom:14px;z-index:1100;display:flex;flex-direction:column;gap:10px;pointer-events:none}
#left{left:14px;width:292px}
#right{right:14px;width:292px;align-items:flex-end}
#left>*,#right>*{pointer-events:auto}
#brand{display:flex;align-items:center;gap:12px;padding:12px 14px}
#brand .mark{width:38px;height:38px;border-radius:11px;background:var(--accent);display:grid;place-items:center;color:#fff;font-weight:700;font-size:18px;flex:none}
#brand .t{font-weight:700;font-size:14.5px;letter-spacing:-.01em;line-height:1.2}
#brand .s{font-size:11.5px;color:var(--muted);margin-top:2px}
.btn{border:0;background:var(--accent);color:#fff;font:600 12px 'Inter',sans-serif;padding:8px 12px;border-radius:10px;cursor:pointer;white-space:nowrap;transition:background .15s}
.btn:hover{background:var(--accent-dark)}
#brand .btn{margin-left:auto}
#panel{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden}
#panel .ph{display:flex;align-items:center;justify-content:space-between;padding:13px 16px 8px;font-weight:700;font-size:13px;cursor:pointer;user-select:none}
#panel .ph span{font-size:11px;color:var(--muted);font-weight:500}
#pbody{overflow-y:auto;padding:0 8px 10px 8px}
#panel.collapsed #pbody{display:none}
.sec{font-size:10.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);font-weight:700;margin:12px 8px 4px}
.row{display:flex;align-items:center;gap:10px;padding:7px 8px;border-radius:10px;cursor:pointer;font-size:13px}
.row:hover{background:#F1F5F9}
.row .chip{width:12px;height:12px;border-radius:50%;flex:none;border:2px solid #fff;box-shadow:0 0 0 1px rgba(15,23,42,.18)}
.row .chip.ln{width:18px;height:5px;border-radius:3px;border:0;box-shadow:none}
.row .lbl{flex:1;font-weight:500}
.row .lbl em{font-style:normal;color:var(--muted);font-weight:400;margin-left:6px;font-size:12px}
.row.off .lbl{color:#94A3B8}
.sw{position:relative;width:34px;height:20px;flex:none}
.sw input{position:absolute;opacity:0;width:0;height:0}
.sw span{position:absolute;inset:0;background:#CBD5E1;border-radius:20px;transition:.18s}
.sw span:before{content:"";position:absolute;width:16px;height:16px;left:2px;top:2px;background:#fff;border-radius:50%;transition:.18s;box-shadow:0 1px 3px rgba(0,0,0,.3)}
.sw input:checked+span{background:var(--accent)}
.sw input:checked+span:before{transform:translateX(14px)}
.sw input:disabled+span{opacity:.4}
.seg{display:flex;background:#EEF2F6;border-radius:11px;padding:3px;gap:2px}
.seg button{flex:1;border:0;background:transparent;font:600 11.5px 'Inter',sans-serif;color:#475569;padding:7px 6px;border-radius:9px;cursor:pointer;transition:.15s;white-space:nowrap}
.seg button.on{background:#fff;color:var(--ink);box-shadow:0 1px 3px rgba(15,23,42,.18)}
.seg button:disabled{opacity:.4;cursor:not-allowed}
#heatseg{margin:2px 8px 4px;flex-wrap:wrap}
#heatseg button{flex:1 1 45%}
.rng{display:flex;align-items:center;gap:10px;margin:6px 10px 2px;font-size:12px;color:var(--muted)}
.rng input{flex:1;accent-color:var(--accent)}
#bases{padding:4px;width:auto}
#bases .seg{background:transparent;padding:0}
#analyse{width:292px;padding:16px 16px 14px;overflow-y:auto;max-height:calc(100% - 70px)}
#analyse.hidden{display:none}
#analyse h4{margin:0;font-size:14px;font-weight:700;display:flex;justify-content:space-between;align-items:center}
#analyse .x{border:0;background:#F1F5F9;border-radius:8px;width:26px;height:26px;cursor:pointer;color:#475569;font-size:14px}
#analyse .sub{font-size:12px;color:var(--muted);margin:2px 0 8px}
.ar{display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid #F1F5F9;font-size:13px}
.ar.z{color:#A3AEBD}
.ar .l{display:flex;align-items:center;gap:8px}
.ar .c{width:10px;height:10px;border-radius:50%;flex:none}
.ar b{font-weight:700}
.big{font-size:26px;font-weight:700;letter-spacing:-.02em;line-height:1.1}
.mut{font-size:11.5px;color:var(--muted)}
.blk{margin-top:12px}
#legend{padding:12px 14px;font-size:12px}
#legend .lt{font-size:10.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);font-weight:700;margin-bottom:6px}
#legend .lg{display:flex;align-items:center;gap:8px;margin:3px 0}
#legend i{display:inline-block;flex:none}
#legend i.dt{width:10px;height:10px;border-radius:50%;box-shadow:0 0 0 1.5px #fff,0 0 0 2.5px rgba(15,23,42,.15)}
#legend i.ln{width:18px;height:4px;border-radius:2px}
#legend i.sq{width:12px;height:12px;border-radius:3px}
#legend i.gr{width:70px;height:8px;border-radius:4px;background:linear-gradient(90deg,#BFDBFE,#60A5FA,#F59E0B,#DC2626)}
#hint{position:absolute;left:50%;bottom:18px;transform:translateX(-50%);z-index:1100;padding:9px 16px;font-size:12.5px;font-weight:500;border-radius:999px;pointer-events:none;white-space:nowrap}
#hint b{color:var(--accent-dark)}
.leaflet-control-zoom{border:0!important;box-shadow:0 6px 18px rgba(15,23,42,.18)!important;border-radius:12px!important;overflow:hidden}
.leaflet-control-zoom a{width:34px!important;height:34px!important;line-height:34px!important;color:#334155!important}
.leaflet-control-attribution{font-size:10px!important;background:rgba(255,255,255,.8)!important;border-radius:8px 0 0 0}
.leaflet-bottom.leaflet-right{margin-right:0}
.tt{border:0;border-radius:10px;box-shadow:0 6px 20px rgba(15,23,42,.22);font:500 12px 'Inter',sans-serif;padding:7px 10px;color:var(--ink)}
.tt:before{display:none}
.lyon-pin{position:relative;width:0;height:0}
.lyon-pin .ring{position:absolute;left:-16px;top:-16px;width:32px;height:32px;border-radius:50%;background:var(--accent);opacity:.25;animation:pulse 2s ease-out infinite}
.lyon-pin .dot{position:absolute;left:-6px;top:-6px;width:12px;height:12px;border-radius:50%;background:var(--accent);border:2.5px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.35)}
.lyon-pin .lab{position:absolute;left:14px;top:-22px;background:#fff;border-radius:10px;padding:6px 10px;box-shadow:0 6px 18px rgba(15,23,42,.25);white-space:nowrap;font:700 13px 'Inter',sans-serif;cursor:pointer;line-height:1.2}
.lyon-pin .lab small{display:block;font-weight:500;font-size:10.5px;color:var(--muted)}
@keyframes pulse{0%{transform:scale(.6);opacity:.45}100%{transform:scale(2.6);opacity:0}}
@media (max-width:820px){#left{width:240px}#right{width:240px}#analyse{width:240px}}
</style>
</head>
<body>
<div id="map"></div>
<div id="left">
  <div id="brand" class="card">
    <div class="mark">L</div>
    <div><div class="t">Offre de mobilité</div><div class="s">Métropole de Lyon · zone d'étude</div></div>
    <button id="btnLyon" class="btn">Explorer Lyon</button>
  </div>
  <div id="panel" class="card">
    <div class="ph" id="phead">Couches <span id="chev">Réduire</span></div>
    <div id="pbody"></div>
  </div>
  <div id="legend" class="card"></div>
</div>
<div id="right">
  <div id="bases" class="card"><div class="seg" id="baseseg"></div></div>
  <div id="analyse" class="card hidden"></div>
</div>
<div id="hint" class="card"></div>
 
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<script>
(function(){
"use strict";
window.__errs = [];
window.addEventListener('error', function(e){ window.__errs.push(String(e.message)); });
 
var D = __DATA__;
var R = 400, MINZ = 9;
var FRANCE = [[41.0,-5.6],[51.3,9.9]];
var fmt = function(n){ return Math.round(n).toLocaleString('fr-FR'); };
var esc = function(s){ return String(s==null?'':s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); };
var $ = function(id){ return document.getElementById(id); };
 
var map = L.map('map', {zoomControl:false, minZoom:5, maxZoom:19, zoomSnap:1, worldCopyJump:false});
L.control.zoom({position:'bottomright'}).addTo(map);
L.control.scale({position:'bottomright', imperial:false}).addTo(map);
map.fitBounds(FRANCE, {padding:[0,0]});
 
/* ---------- fonds de carte ---------- */
var ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/';
var BASES = {
  clair: L.tileLayer(ESRI+'Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {maxNativeZoom:16, maxZoom:19, attribution:'Esri, HERE, Garmin'}),
  sombre: L.tileLayer(ESRI+'Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {maxNativeZoom:16, maxZoom:19, attribution:'Esri, HERE, Garmin'}),
  satellite: L.tileLayer(ESRI+'World_Imagery/MapServer/tile/{z}/{y}/{x}', {maxZoom:19, attribution:'Esri, Maxar, Earthstar'}),
  plan: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19, attribution:'&copy; OpenStreetMap'})
};
var BASE_LABELS = {clair:'Clair', sombre:'Sombre', satellite:'Satellite', plan:'Plan'};
var state = {base:'clair', on:{}, heat:'aucune', km:false, zfe:false, circle:null, pin:null};
function setBase(k){
  Object.keys(BASES).forEach(function(b){ if(map.hasLayer(BASES[b])) map.removeLayer(BASES[b]); });
  BASES[k].addTo(map); state.base = k;
  [].forEach.call($('baseseg').children, function(b){ b.classList.toggle('on', b.dataset.b===k); });
}
Object.keys(BASE_LABELS).forEach(function(k){
  var b = document.createElement('button'); b.textContent = BASE_LABELS[k]; b.dataset.b = k;
  b.onclick = function(){ setBase(k); }; $('baseseg').appendChild(b);
});
 
/* ---------- panes et rendus canvas ---------- */
map.createPane('km').style.zIndex = 405;
map.createPane('reseau').style.zIndex = 420;
map.createPane('points').style.zIndex = 430;
map.createPane('analyse').style.zIndex = 450;
var rKm = L.canvas({pane:'km', padding:0.3});
var rReseau = L.canvas({pane:'reseau', padding:0.3});
var rPoints = L.canvas({pane:'points', padding:0.3});
 
/* ---------- couches de l'offre ---------- */
var ITEMS = [];
var PT = {lat:[], lon:[], op:[], n:0};
D.offre.forEach(function(o){
  var g = L.layerGroup(), ms = [];
  o.pts.forEach(function(p){
    PT.lat.push(p[0]); PT.lon.push(p[1]); PT.op.push(o.id);
    var m = L.circleMarker([p[0],p[1]], {renderer:rPoints, radius:o.radius*0.6, color:'#fff', weight:1.2, fillColor:o.color, fillOpacity:.95});
    m.on('mouseover', function(){
      if(!this.getTooltip()){ this.bindTooltip('<b>'+esc(o.label)+'</b><br>'+esc(p[2]||'Sans nom'), {direction:'top', offset:[0,-5], className:'tt'}); this.openTooltip(); }
    });
    g.addLayer(m); ms.push(m);
  });
  ITEMS.push({id:o.id, label:o.label, group:o.group, color:o.color, count:o.pts.length, on:o.on, layer:g, markers:ms, base:o.radius, kind:'pt', pts:o.pts});
});
PT.n = PT.lat.length;
 
/* ---------- réseau de transport ---------- */
D.reseau.forEach(function(r){
  if(!r.gj){ ITEMS.push({id:r.id, label:r.label, group:r.group, color:r.color, count:0, on:false, layer:null, kind:'ln', missing:true}); return; }
  var layer = L.geoJSON(r.gj, {
    renderer:rReseau,
    style:function(f){ return {color:(f.properties&&f.properties.c)||r.color, weight:r.weight, opacity:r.opacity, lineJoin:'round', lineCap:'round'}; },
    onEachFeature:function(f,l){ if(f.properties && f.properties.n){ l.bindTooltip(esc(r.label)+' '+esc(f.properties.n), {sticky:true, className:'tt'}); } }
  });
  var seen = {}, cols = [];
  r.gj.features.forEach(function(f){ var c = (f.properties && f.properties.c) || r.color; if(!seen[c]){ seen[c]=1; cols.push(c); } });
  ITEMS.push({id:r.id, label:r.label, group:r.group, color:r.color, colors:cols.slice(0,5), count:r.gj.features.length, on:r.on, layer:layer, kind:'ln'});
});
ITEMS.forEach(function(it){ state.on[it.id] = !!it.on; });
 
/* ---------- population : carreaux ---------- */
var HAS_POP = !!(D.pop && D.pop.c && D.pop.c.length);
function carreaux(){ return !HAS_POP ? [] : (state.zfe ? D.pop.c.filter(function(c){ return c[4]===1; }) : D.pop.c); }
var heatLayer = null, kmLayer = null;
var HEAT_DEFS = {
  pop: {label:'Population', pts:function(){ var p99 = D.pop.p99||1; return carreaux().filter(function(c){return c[2]>0;}).map(function(c){ return [c[0],c[1],Math.min(c[2]/p99,1)]; }); }, radius:14},
  tcl: {label:'Arrêts TCL', pts:function(){ return pointsOf(function(it){ return it.group==='Transport en commun'; }); }, radius:16},
  partage: {label:'Offre partagée', pts:function(){ return pointsOf(function(it){ return it.group==='Autopartage' || it.group==='Vélos et trottinettes'; }); }, radius:20}
};
function pointsOf(f){ var out=[]; ITEMS.forEach(function(it){ if(it.kind==='pt' && f(it)){ it.pts.forEach(function(p){ out.push([p[0],p[1],1]); }); } }); return out; }
function autoMax(pts, radiusPx){
  /* densité "forte" observée : 90e centile du poids cumulé dans le rayon de chauffe (à zoom 12) */
  var n = pts.length; if(!n) return 1;
  var metres = radiusPx*38.2*Math.cos(LYON_LAT*Math.PI/180), r2 = metres*metres;
  var kx = 111320*Math.cos(LYON_LAT*Math.PI/180), ky = 111320, step = Math.max(1, Math.floor(n/300)), vals = [];
  for(var i=0;i<n;i+=step){ var a=pts[i], s=0; for(var j=0;j<n;j++){ var b=pts[j], dx=(b[1]-a[1])*kx, dy=(b[0]-a[0])*ky; if(dx*dx+dy*dy<=r2) s+=b[2]; } vals.push(s); }
  vals.sort(function(x,y){ return x-y; });
  return Math.max(vals[Math.floor(vals.length*0.9)]||1, 1);
}
var LYON_LAT = D.lyon[0], heatBase = 1;
function setHeat(mode){
  state.heat = mode;
  if(heatLayer){ map.removeLayer(heatLayer); heatLayer=null; }
  [].forEach.call($('heatseg').children, function(b){ b.classList.toggle('on', b.dataset.h===mode); });
  $('heatrng').style.display = (mode==='aucune') ? 'none' : 'flex';
  if(mode!=='aucune' && L.heatLayer && HEAT_DEFS[mode]){
    var pts = HEAT_DEFS[mode].pts();
    heatBase = Math.max(autoMax(pts, HEAT_DEFS[mode].radius) * 0.12, 0.3);
    heatLayer = L.heatLayer(pts, {radius:HEAT_DEFS[mode].radius, blur:20, maxZoom:15, minOpacity:.03,
      max: heatBase/parseFloat($('heatint').value), gradient:{0.2:'#BFDBFE',0.45:'#60A5FA',0.7:'#F59E0B',1:'#DC2626'}});
  }
  sync();
}
function setKm(on){
  state.km = on;
  if(kmLayer){ map.removeLayer(kmLayer); kmLayer=null; }
  if(on && D.pop.profils && D.pop.profils.length){
    kmLayer = L.layerGroup();
    carreaux().forEach(function(c){
      if(c[3] < 0) return;
      var dlat = 100/111320, dlon = 100/(111320*Math.cos(c[0]*Math.PI/180));
      L.rectangle([[c[0]-dlat, c[1]-dlon],[c[0]+dlat, c[1]+dlon]], {renderer:rKm, stroke:false, fillColor:D.pop.profils[c[3]%D.pop.profils.length].color, fillOpacity:.5, interactive:false}).addTo(kmLayer);
    });
  }
  sync();
}
 
/* ---------- synchronisation couches / zoom ---------- */
function sync(){
  var show = map.getZoom() >= MINZ;
  ITEMS.forEach(function(it){
    if(!it.layer) return;
    var want = show && state.on[it.id];
    if(want && !map.hasLayer(it.layer)) it.layer.addTo(map);
    if(!want && map.hasLayer(it.layer)) map.removeLayer(it.layer);
  });
  [heatLayer, kmLayer].forEach(function(l){ if(!l) return; if(show && !map.hasLayer(l)) l.addTo(map); if(!show && map.hasLayer(l)) map.removeLayer(l); });
  var s = map.getZoom()<10 ? .6 : map.getZoom()<12 ? .8 : map.getZoom()<14 ? 1 : 1.25;
  ITEMS.forEach(function(it){ if(it.markers) it.markers.forEach(function(m){ m.setRadius(it.base*s); }); });
  $('btnLyon').textContent = show ? 'Vue France' : 'Explorer Lyon';
  legend(); hint();
}
 
/* ---------- panneau de couches ---------- */
var GROUPS = ['Autopartage','Vélos et trottinettes','Transport en commun','Équipements'];
function lineBg(it){ var c = it.colors && it.colors.length ? it.colors : [it.color]; return c.length===1 ? c[0] : 'linear-gradient(90deg,'+c.join(',')+')'; }
function row(it){
  var off = it.missing ? ' off' : '';
  var c = it.kind==='ln' ? '<span class="chip ln" style="background:'+lineBg(it)+'"></span>' : '<span class="chip" style="background:'+it.color+'"></span>';
  var cnt = it.missing ? '<em>données non lues</em>' : '<em>'+fmt(it.count)+'</em>';
  return '<label class="row'+off+'">'+c+'<span class="lbl">'+esc(it.label)+cnt+'</span><span class="sw"><input type="checkbox" data-id="'+it.id+'" '+(state.on[it.id]?'checked':'')+(it.missing?' disabled':'')+'><span></span></span></label>';
}
function buildPanel(){
  var h = '';
  h += '<div class="sec">Carte thermique</div><div class="seg" id="heatseg"><button data-h="aucune" class="on">Aucune</button>'
     + (HAS_POP ? '<button data-h="pop">Population</button>' : '')
     + '<button data-h="tcl">Arrêts TCL</button><button data-h="partage">Offre partagée</button></div>'
     + '<div class="rng" id="heatrng" style="display:none"><span>Intensité</span><input type="range" id="heatint" min="0.4" max="3" step="0.1" value="1"></div>';
  GROUPS.forEach(function(g){
    var its = ITEMS.filter(function(i){ return i.group===g; });
    if(!its.length) return;
    h += '<div class="sec">'+g+'</div>' + its.map(row).join('');
  });
  if(HAS_POP){
    h += '<div class="sec">Quartiers</div>';
    h += '<label class="row"><span class="chip" style="background:#7C3AED"></span><span class="lbl">Profils K-Means (carreaux 200 m)</span><span class="sw"><input type="checkbox" id="kmchk"'+((D.pop.profils&&D.pop.profils.length)?'':' disabled')+'><span></span></span></label>';
    h += '<label class="row"><span class="chip" style="background:#0EA5E9"></span><span class="lbl">Limiter à la ZFE</span><span class="sw"><input type="checkbox" id="zfechk"'+(D.pop.hasZfe?'':' disabled')+'><span></span></span></label>';
  }
  $('pbody').innerHTML = h;
  [].forEach.call($('pbody').querySelectorAll('input[data-id]'), function(inp){
    inp.onchange = function(){ state.on[inp.dataset.id] = inp.checked; sync(); };
  });
  [].forEach.call($('heatseg').children, function(b){ b.onclick = function(){ setHeat(b.dataset.h); }; });
  $('heatint').oninput = function(){ if(heatLayer) heatLayer.setOptions({max: heatBase/parseFloat(this.value)}); };
  if($('kmchk')) $('kmchk').onchange = function(){ setKm(this.checked); };
  if($('zfechk')) $('zfechk').onchange = function(){ state.zfe = this.checked; setHeat(state.heat); setKm(state.km); };
}
$('phead').onclick = function(){ var p=$('panel'); p.classList.toggle('collapsed'); $('chev').textContent = p.classList.contains('collapsed') ? 'Développer' : 'Réduire'; };
 
/* ---------- légende et aide ---------- */
function legend(){
  var h = '<div class="lt">Légende</div>', n = 0;
  if(map.getZoom() >= MINZ){
    ITEMS.forEach(function(it){
      if(!it.layer || !state.on[it.id]) return;
      h += '<div class="lg"><i class="'+(it.kind==='ln'?'ln':'dt')+'" style="background:'+(it.kind==='ln'?lineBg(it):it.color)+'"></i>'+esc(it.label)+'</div>'; n++;
    });
    if(state.heat!=='aucune'){ h += '<div class="lg"><i class="gr"></i>Densité · '+HEAT_DEFS[state.heat].label+'</div>'; n++; }
    if(state.km && D.pop.profils){ D.pop.profils.forEach(function(p){ h += '<div class="lg"><i class="sq" style="background:'+p.color+';opacity:.7"></i>'+esc(p.label)+'</div>'; n++; }); }
  }
  if(!n) h += '<div class="mut">Aucune couche affichée</div>';
  $('legend').innerHTML = h;
}
function hint(){
  $('hint').innerHTML = map.getZoom() < MINZ
    ? 'Étude centrée sur <b>Lyon</b> · cliquez sur le repère ou sur « Explorer Lyon »'
    : (state.circle ? 'Cliquez ailleurs pour analyser un autre point' : 'Cliquez sur la carte pour analyser l\'accès à pied · <b>400 m</b>');
}
 
/* ---------- zone d'étude et repère Lyon ---------- */
var zone = L.polygon(D.zone, {color:D.accent, weight:2, fillColor:D.accent, fillOpacity:.14, dashArray:'6 5', interactive:false}).addTo(map);
var pinIcon = L.divIcon({className:'', html:'<div class="lyon-pin"><div class="ring"></div><div class="dot"></div><div class="lab">Lyon<small>zone d\'étude</small></div></div>', iconSize:[0,0]});
var lyonPin = L.marker(D.lyon, {icon:pinIcon, keyboard:false}).addTo(map);
function exploreLyon(){ map.flyToBounds(zone.getBounds(), {padding:[40,40], duration:1.3}); }
function showFrance(){ map.flyToBounds(FRANCE, {duration:1.3}); }
lyonPin.on('click', exploreLyon);
$('btnLyon').onclick = function(){ if(map.getZoom() >= MINZ) showFrance(); else exploreLyon(); };
map.on('zoomend', function(){ sync(); lyonPin.setOpacity(map.getZoom() >= 12 ? 0 : 1); zone.setStyle({fillOpacity: map.getZoom() >= MINZ ? .04 : .18}); });
 
/* ---------- analyse d'accessibilité (clic) ---------- */
function closeAnalyse(){
  if(state.circle){ map.removeLayer(state.circle); state.circle=null; }
  if(state.pin){ map.removeLayer(state.pin); state.pin=null; }
  $('analyse').classList.add('hidden'); hint();
}
function analyse(ll){
  var lat0 = ll.lat, lon0 = ll.lng, kx = 111320*Math.cos(lat0*Math.PI/180), ky = 111320, r2 = R*R, counts = {}, i, dx, dy;
  for(i=0;i<PT.n;i++){ dx=(PT.lon[i]-lon0)*kx; dy=(PT.lat[i]-lat0)*ky; if(dx*dx+dy*dy<=r2){ counts[PT.op[i]]=(counts[PT.op[i]]||0)+1; } }
  var pop = 0, bestD = 1e9, prof = null;
  if(HAS_POP){ D.pop.c.forEach(function(c){ dx=(c[1]-lon0)*kx; dy=(c[0]-lat0)*ky; var d2=dx*dx+dy*dy; if(d2<=r2) pop+=c[2]; if(d2<bestD){ bestD=d2; prof=c; } }); }
  var citiz = null, cd = 1e9;
  ITEMS.forEach(function(it){ if(it.id==='citiz'){ it.pts.forEach(function(p){ dx=(p[1]-lon0)*kx; dy=(p[0]-lat0)*ky; var d=Math.sqrt(dx*dx+dy*dy); if(d<cd){ cd=d; citiz=p; } }); } });
  var rows = '', modes = 0, total = 0;
  GROUPS.forEach(function(g){
    ITEMS.filter(function(it){ return it.kind==='pt' && it.group===g; }).forEach(function(it){
      var n = counts[it.id]||0; total += n; if(n>0 && g!=='Équipements') modes++;
      rows += '<div class="ar'+(n?'':' z')+'"><span class="l"><span class="c" style="background:'+it.color+'"></span>'+esc(it.label)+'</span><b>'+n+'</b></div>';
    });
  });
  var h = '<h4>Accès à pied · '+R+' m<button class="x" id="xclose">✕</button></h4>'
        + '<div class="sub">'+total+' point(s) de mobilité · '+modes+' type(s) de service accessibles</div>' + rows;
  if(HAS_POP){
    h += '<div class="blk"><div class="mut">Habitants à moins de '+R+' m</div><div class="big">'+fmt(pop)+'</div><div class="mut">estimé d\'après les centres des carreaux de 200 m</div></div>';
    if(prof && bestD <= 200*200 && prof[3] >= 0 && D.pop.profils && D.pop.profils.length){
      h += '<div class="blk"><div class="mut">Profil du quartier</div><div><b>'+esc(D.pop.profils[prof[3]%D.pop.profils.length].label)+'</b></div></div>';
    }
  }
  if(citiz){ h += '<div class="blk"><div class="mut">Station Citiz la plus proche</div><div><b>'+fmt(cd)+' m</b> · '+esc(citiz[2]||'sans nom')+'</div></div>'; }
  $('analyse').innerHTML = h; $('analyse').classList.remove('hidden');
  $('xclose').onclick = closeAnalyse;
  if(state.circle) map.removeLayer(state.circle); if(state.pin) map.removeLayer(state.pin);
  state.circle = L.featureGroup([
    L.circle(ll, {radius:R, stroke:false, fillColor:'#FFFFFF', fillOpacity:.28, interactive:false}),
    L.circle(ll, {pane:'analyse', radius:R, color:'#0F172A', weight:2.5, dashArray:'7 6', fill:false, interactive:false})
  ]).addTo(map);
  state.pin = L.circleMarker(ll, {pane:'analyse', radius:6, color:'#fff', weight:2.5, fillColor:'#0F172A', fillOpacity:1, interactive:false}).addTo(map);
  if(map.getZoom() < 14){ map.flyToBounds(state.circle.getBounds(), {padding:[150,150], maxZoom:16, duration:.7}); }
  hint();
}
map.on('click', function(e){ if(map.getZoom() >= MINZ) analyse(e.latlng); });
 
/* ---------- démarrage ---------- */
buildPanel(); setBase('clair'); legend(); hint(); sync();
window.__api = {map:map, analyse:analyse, exploreLyon:exploreLyon, setHeat:setHeat, setKm:setKm, setBase:setBase, state:state, ITEMS:ITEMS, closeAnalyse:closeAnalyse};
})();
</script>
</body>
</html>
'''
PALETTE_PROFILS = ["#2563EB", "#DC2626", "#16A34A", "#F59E0B", "#7C3AED", "#0891B2", "#DB2777", "#65A30D"]
 
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 0.6rem; max-width: 1700px; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
.titre {{ font-size: 1.55rem; font-weight: 700; color: #0F172A; margin: 0; letter-spacing: -0.015em; }}
.titre span {{ color: {CHARTE['accent']}; }}
.sous-titre {{ color: #64748B; font-size: .92rem; margin: 2px 0 12px 0; }}
.kpi {{ background: #fff; border: 1px solid #E5E7EB; border-left: 4px solid {CHARTE['accent']}; border-radius: 12px;
        padding: 12px 16px; box-shadow: 0 1px 2px rgba(16,24,40,.05); }}
.kpi .label {{ font-size: .7rem; color: #64748B; text-transform: uppercase; letter-spacing: .07em; font-weight: 600; }}
.kpi .value {{ font-size: 1.6rem; font-weight: 700; color: #0F172A; line-height: 1.25; }}
.kpi .sub {{ font-size: .78rem; color: #64748B; }}
</style>
""",
    unsafe_allow_html=True,
)
 
 
# =====================================================================
# 1. LECTURE DES DONNÉES
# =====================================================================
def date_fichier(nom_fichier):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    return os.path.getmtime(chemin) if os.path.exists(chemin) else 0
 
 
@st.cache_data(show_spinner="Chargement des données…")
def _lire_csv(nom_fichier, _date):
    chemin = os.path.join(DATA_DIR, nom_fichier)
    if not os.path.exists(chemin):
        return None
    return pd.read_csv(chemin, on_bad_lines="skip")
 
 
def charger(nom_fichier):
    return _lire_csv(nom_fichier, date_fichier(nom_fichier))
 
 
def coordonnees_valides(df):
    df = df.copy()
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    return df[df["lat"].notna() & df["lon"].notna() & ((df["lat"] != 0) | (df["lon"] != 0))]
 
 
def milliers(n):
    return f"{int(round(n)):,}".replace(",", " ")
 
 
df_offre = charger("offres_de_mobilite.csv")
if df_offre is None or df_offre.empty or not {"lat", "lon", "type_service"} <= set(df_offre.columns):
    st.error("Fichier `Data/offres_de_mobilite.csv` introuvable ou sans colonnes `lat`, `lon`, `type_service`.")
    st.stop()
df_offre = coordonnees_valides(df_offre)
for colonne in ("nom", "source"):
    if colonne not in df_offre.columns:
        df_offre[colonne] = ""
df_offre["nom"] = df_offre["nom"].fillna("").astype(str)
df_offre["source"] = df_offre["source"].fillna("").astype(str)
df_offre["type_service"] = df_offre["type_service"].fillna("").astype(str)
 
df_ind = charger("indicateurs_avec_clusters.csv")
if df_ind is not None and {"lat", "lon", "ind"} <= set(df_ind.columns):
    df_ind = coordonnees_valides(df_ind)
    df_ind["ind"] = pd.to_numeric(df_ind["ind"], errors="coerce").fillna(0)
else:
    df_ind = None
 
 
# =====================================================================
# 2. OPÉRATEURS : un calque par opérateur (Citiz ≠ tout l'autopartage)
# =====================================================================
def attribuer_operateurs(df):
    texte = (df["source"] + " " + df["type_service"]).str.lower()
    cle = pd.Series("", index=df.index)
    for k, motif, *_ in OPERATEURS:
        libre = cle == ""
        cle[libre & texte.str.contains(motif, regex=True)] = k
    reste = cle == ""
    cle[reste] = "autre_" + df.loc[reste, "source"].where(df.loc[reste, "source"] != "", df.loc[reste, "type_service"]) \
        .str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    return cle
 
 
df_offre["operateur"] = attribuer_operateurs(df_offre)
 
 
def definitions_offre(df):
    defs = []
    connus = {k: (lib, grp, coul, ray, defaut) for k, _, lib, grp, coul, ray, defaut in OPERATEURS}
    for k in df["operateur"].unique():
        if k in connus:
            defs.append((k,) + connus[k])
        else:
            sous = df[df["operateur"] == k].iloc[0]
            defs.append((k, (sous["source"] or sous["type_service"] or "Autre").capitalize(),
                         GROUPE_PAR_TYPE.get(sous["type_service"], "Équipements"), "#94A3B8", 4, False))
    ordre = [o[0] for o in OPERATEURS]
    return sorted(defs, key=lambda d: ordre.index(d[0]) if d[0] in ordre else 99)
 
 
# =====================================================================
# 3. LIGNES DE TRANSPORT : CSV d'abord, WFS TCL en secours
# =====================================================================
NOMBRE = r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"
PAIRE = rf"\[\s*{NOMBRE}\s*,\s*{NOMBRE}\s*\]"
GROUPE_PAIRES = re.compile(rf"\[\s*{PAIRE}(?:\s*,\s*{PAIRE})+\s*,?\s*\]")
 
 
def _lignes_wkt(texte):
    lignes = []
    for morceau in re.findall(r"\(([^()]+)\)", texte[texte.index("("):]):
        points = []
        for paire in morceau.split(","):
            xy = paire.split()
            if len(xy) >= 2:
                try:
                    points.append([float(xy[0]), float(xy[1])])
                except ValueError:
                    continue
        if len(points) >= 2:
            lignes.append(points)
    return lignes
 
 
def _lignes_regex(texte):
    """Dernier recours : repère les suites de paires [lon, lat], y compris dans un affichage numpy."""
    texte = re.sub(r"array\(", "", texte)
    texte = re.sub(r",\s*dtype=\w+\)", "", texte).replace(")", "")
    return [[[float(a), float(b)] for a, b in re.findall(rf"({NOMBRE})\s*,\s*({NOMBRE})", g)]
            for g in GROUPE_PAIRES.findall(texte)]
 
 
def lignes_depuis_geometrie(valeur):
    """Liste de lignes [[lon, lat], ...] depuis du JSON, un dict Python, du WKT ou un affichage numpy."""
    if valeur is None or (isinstance(valeur, float) and np.isnan(valeur)):
        return []
    geom = valeur if isinstance(valeur, dict) else None
    if geom is None and isinstance(valeur, str):
        texte = valeur.strip()
        if texte.upper().startswith(("LINESTRING", "MULTILINESTRING")):
            return _lignes_wkt(texte)
        if texte and texte[0] in "{[":
            try:
                geom = json.loads(texte)
            except ValueError:
                try:
                    geom = ast.literal_eval(texte)
                except (ValueError, SyntaxError):
                    return _lignes_regex(texte)
    if not isinstance(geom, dict):
        return []
    coordonnees = geom.get("coordinates")
    if coordonnees is None:
        return []
    coordonnees = np.asarray(coordonnees, dtype=object).tolist() if not isinstance(coordonnees, list) else coordonnees
    if geom.get("type") == "LineString":
        return [coordonnees]
    if geom.get("type") == "MultiLineString":
        return list(coordonnees)
    return []
 
 
def construire_geojson(elements, pas=1):
    """elements : (géométrie, nom, couleur ou None). Renvoie un GeoJSON léger et des statistiques."""
    stats = {"lignes_fichier": len(elements), "tracees": 0, "illisibles": 0, "hors_degres": 0, "exemple": ""}
    features = []
    for geometrie, nom, couleur in elements:
        if not stats["exemple"] and geometrie is not None and not (isinstance(geometrie, float) and np.isnan(geometrie)):
            stats["exemple"] = str(geometrie)[:140]
        lignes = lignes_depuis_geometrie(geometrie)
        if not lignes:
            stats["illisibles"] += 1
            continue
        valides = []
        for ligne in lignes:
            try:
                points = [[round(float(p[0]), 5), round(float(p[1]), 5)] for p in ligne]
            except (TypeError, ValueError, IndexError):
                continue
            if len(points) >= 2 and abs(points[0][0]) <= 180 and abs(points[0][1]) <= 90:
                if pas > 1 and len(points) > 4:
                    points = points[::pas] + ([points[-1]] if (len(points) - 1) % pas else [])
                valides.append(points)
            else:
                stats["hors_degres"] += 1
        if valides:
            propriete = {"n": nom or ""}
            if couleur:
                propriete["c"] = couleur
            features.append({"type": "Feature", "properties": propriete,
                             "geometry": {"type": "MultiLineString", "coordinates": valides}})
    stats["tracees"] = len(features)
    return ({"type": "FeatureCollection", "features": features} if features else None), stats
 
 
def couleur_valide(brut):
    brut = str(brut).strip().lstrip("#")
    return "#" + brut if re.fullmatch(r"[0-9A-Fa-f]{6}", brut) else None
 
 
NOMS_COLONNE_NOM = ("ligne", "nom_ligne", "nom_trace", "code_ligne", "nom")
NOMS_COLONNE_COULEUR = ("couleur_hex", "couleur")
 
 
def elements_depuis_csv(df):
    if df is None or df.empty:
        return [], ""
    col_geo = next((c for c in ("geometry", "geom", "geometrie", "the_geom", "geometry_raw", "wkt", "shape") if c in df.columns), None)
    col_geo = col_geo or next((c for c in df.columns if "geom" in c.lower()), None)
    if col_geo is None:
        return [], f"aucune colonne de géométrie (colonnes : {', '.join(map(str, df.columns))})"
    col_nom = next((c for c in NOMS_COLONNE_NOM if c in df.columns), None)
    col_coul = next((c for c in NOMS_COLONNE_COULEUR if c in df.columns), None)
    elements = []
    for _, ligne in df.iterrows():
        nom = "" if not col_nom or pd.isna(ligne[col_nom]) else str(ligne[col_nom])
        elements.append((ligne[col_geo], nom, couleur_valide(ligne[col_coul]) if col_coul else None))
    return elements, ""
 
 
@st.cache_data(ttl=86400, show_spinner=False)
def elements_depuis_wfs(typename):
    """Même requête que le notebook d'ingestion (flux TCL, lecture directe)."""
    params = {"SERVICE": "WFS", "VERSION": "2.0.0", "request": "GetFeature", "typename": typename,
              "outputFormat": "application/json", "SRSNAME": "EPSG:4171", "sortby": "gid", "count": 5000}
    try:
        reponse = requests.get(WFS_SYTRAL, params=params, timeout=(10, 60))
        reponse.raise_for_status()
        features = reponse.json().get("features", [])
    except Exception as erreur:  # réseau indisponible, serveur lent, etc.
        return [], f"{type(erreur).__name__}"
    elements = []
    for f in features:
        props = f.get("properties") or {}
        nom = next((str(props[c]) for c in NOMS_COLONNE_NOM if props.get(c)), "")
        coul = next((couleur_valide(props[c]) for c in NOMS_COLONNE_COULEUR if props.get(c)), None)
        elements.append((f.get("geometry"), nom, coul))
    return elements, ""
 
 
@st.cache_data(show_spinner="Chargement du réseau…")
def reseau(cle, _date):
    libelle, _, _, _, _, fichier, typename = RESEAU[cle]
    pas = 3 if cle == "bus" else 1
    elements, remarque = elements_depuis_csv(charger(fichier))
    geojson, stats = construire_geojson(elements, pas)
    stats.update(source="CSV (" + fichier + ")", remarque=remarque)
    if geojson is None:
        elements, erreur = elements_depuis_wfs(typename)
        geojson_wfs, stats_wfs = construire_geojson(elements, pas)
        if geojson_wfs is not None:
            geojson, stats = geojson_wfs, {**stats_wfs, "source": "WFS TCL en direct (CSV illisible)", "remarque": remarque}
        else:
            stats["remarque"] = (remarque + " " if remarque else "") + (f"WFS indisponible ({erreur})" if erreur else "WFS sans résultat")
    return geojson, stats
 
 
# =====================================================================
# 4. DONNÉES DE LA CARTE
# =====================================================================
def enveloppe_convexe(points):
    points = sorted(set(points))
    if len(points) <= 2:
        return points
 
    def croix(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
 
    bas, haut = [], []
    for p in points:
        while len(bas) >= 2 and croix(bas[-2], bas[-1], p) <= 0:
            bas.pop()
        bas.append(p)
    for p in reversed(points):
        while len(haut) >= 2 and croix(haut[-2], haut[-1], p) <= 0:
            haut.pop()
        haut.append(p)
    return bas[:-1] + haut[:-1]
 
 
def zone_etude():
    """Contour de la zone d'étude : enveloppe des carreaux (sinon des points d'offre) autour de Lyon."""
    source = df_ind if df_ind is not None and len(df_ind) > 50 else df_offre
    lat, lon = source["lat"].to_numpy(), source["lon"].to_numpy()
    km_lat, km_lon = 111.32, 111.32 * math.cos(math.radians(CENTRE_LYON[0]))
    proche = np.hypot((lat - CENTRE_LYON[0]) * km_lat, (lon - CENTRE_LYON[1]) * km_lon) <= 45
    lat, lon = lat[proche], lon[proche]
    if len(lat) < 3:
        return [[CENTRE_LYON[0] - .1, CENTRE_LYON[1] - .15], [CENTRE_LYON[0] - .1, CENTRE_LYON[1] + .15],
                [CENTRE_LYON[0] + .1, CENTRE_LYON[1] + .15], [CENTRE_LYON[0] + .1, CENTRE_LYON[1] - .15]]
    marge_lat, marge_lon = 150 / 111320, 150 / (111320 * math.cos(math.radians(CENTRE_LYON[0])))
    coins = [(x + dx, y + dy) for x, y in zip(lon.round(4), lat.round(4))
             for dx, dy in ((-marge_lon, -marge_lat), (marge_lon, -marge_lat), (marge_lon, marge_lat), (-marge_lon, marge_lat))]
    return [[round(y, 5), round(x, 5)] for x, y in enveloppe_convexe(coins)]
 
 
def donnees_population():
    if df_ind is None:
        return None
    d = df_ind
    clusters = {}
    if "cluster_kmeans" in d.columns:
        valeurs = sorted(pd.to_numeric(d["cluster_kmeans"], errors="coerce").dropna().unique().tolist())
        clusters = {v: i for i, v in enumerate(valeurs)}
    profils = [{"label": f"Profil {int(v)}", "color": PALETTE_PROFILS[i % len(PALETTE_PROFILS)]} for v, i in clusters.items()]
    cl = pd.to_numeric(d["cluster_kmeans"], errors="coerce").map(clusters).fillna(-1).astype(int) if clusters else pd.Series(-1, index=d.index)
    zfe = (pd.to_numeric(d["dans_zfe"], errors="coerce").fillna(0).astype(int) if "dans_zfe" in d.columns else pd.Series(0, index=d.index))
    lignes = [[round(a, 5), round(b, 5), int(round(c)), int(k), int(z)]
              for a, b, c, k, z in zip(d["lat"], d["lon"], d["ind"], cl, zfe)]
    positifs = d.loc[d["ind"] > 0, "ind"]
    return {"c": lignes, "profils": profils, "hasZfe": "dans_zfe" in d.columns,
            "p99": float(positifs.quantile(0.99)) if len(positifs) else 1.0}
 
 
def construire_donnees():
    offre = []
    for cle, libelle, groupe, couleur, rayon, defaut in definitions_offre(df_offre):
        sous = df_offre[df_offre["operateur"] == cle]
        offre.append({"id": cle, "label": libelle, "group": groupe, "color": couleur, "radius": rayon, "on": defaut,
                      "pts": [[round(a, 5), round(b, 5), n[:60]] for a, b, n in zip(sous["lat"], sous["lon"], sous["nom"])]})
    lignes, stats = [], {}
    for cle, (libelle, couleur, poids, opacite, defaut, *_r) in RESEAU.items():
        geojson, stats[cle] = reseau(cle, date_fichier(RESEAU[cle][5]))
        lignes.append({"id": cle, "label": libelle, "group": "Transport en commun", "color": couleur,
                       "weight": poids, "opacity": opacite, "on": defaut, "gj": geojson})
    return {"accent": CHARTE["accent"], "lyon": CENTRE_LYON, "zone": zone_etude(), "offre": offre,
            "reseau": lignes, "pop": donnees_population() or {"c": [], "profils": [], "hasZfe": False, "p99": 1}}, stats
 
 
@st.cache_data(show_spinner="Préparation de la carte…")
def html_carte(_dates):
    donnees, stats = construire_donnees()
    charge = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    charge = charge.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    html = (MODELE.replace("__ACCENT_DARK__", CHARTE["accent_sombre"]).replace("__ACCENT_SOFT__", CHARTE["accent_doux"])
            .replace("__ACCENT__", CHARTE["accent"]).replace("__DATA__", charge))
    return html, stats
 
 
# =====================================================================
# 5. PAGE
# =====================================================================
st.markdown("<p class='titre'>Offre de mobilité · <span>Métropole de Lyon</span></p>"
            "<p class='sous-titre'>Autopartage, vélos, transports en commun et densité de population, avec analyse d'accessibilité à pied.</p>",
            unsafe_allow_html=True)
 
dates = tuple(date_fichier(f) for f in ["offres_de_mobilite.csv", "indicateurs_avec_clusters.csv"] + [v[5] for v in RESEAU.values()])
html, stats_reseau = html_carte(dates)
comptes = df_offre["operateur"].value_counts().to_dict()
nb_lignes = sum(s["tracees"] for s in stats_reseau.values())
 
 
def carte_kpi(colonne, label, valeur, sous=""):
    colonne.markdown(f"<div class='kpi'><div class='label'>{label}</div><div class='value'>{valeur}</div>"
                     f"<div class='sub'>{sous}</div></div>", unsafe_allow_html=True)
 
 
k1, k2, k3, k4 = st.columns(4)
carte_kpi(k1, "Stations Citiz", milliers(comptes.get("citiz", 0)), "réseau d'autopartage coopératif")
carte_kpi(k2, "Autres points de mobilité", milliers(len(df_offre) - comptes.get("citiz", 0)), "Leo&Go, Vélo'v, Dott, TCL…")
carte_kpi(k3, "Habitants (carreaux 200 m)", milliers(df_ind["ind"].sum()) if df_ind is not None else "n/d", "zone d'étude")
carte_kpi(k4, "Tronçons de lignes tracés", milliers(nb_lignes), "métro, tramway, bus")
st.write("")
 
components.html(html, height=HAUTEUR_CARTE, scrolling=False)
 
with st.expander("Qualité des données affichées"):
    st.caption("Si un élément manque sur la carte, ce tableau dit si la source a été lue et pourquoi.")
    st.dataframe(pd.DataFrame([
        {"Réseau": RESEAU[k][0], "Source utilisée": stats_reseau[k].get("source", ""), "Lignes lues": stats_reseau[k]["lignes_fichier"],
         "Tracées": stats_reseau[k]["tracees"], "Illisibles": stats_reseau[k]["illisibles"],
         "Hors degrés (CRS ?)": stats_reseau[k]["hors_degres"], "Remarque": stats_reseau[k].get("remarque", ""),
         "Début de la géométrie": stats_reseau[k]["exemple"]} for k in RESEAU]), hide_index=True)
    croise = (df_offre.groupby(["operateur", "source", "type_service"]).size().reset_index(name="points")
              .sort_values("points", ascending=False))
    st.caption("Répartition des points par opérateur détecté, selon les colonnes `source` et `type_service` :")
    st.dataframe(croise, hide_index=True)
 
st.caption("Sources : Métropole de Lyon (TCL), flux GBFS (Citiz, Vélo'v, Dott, Leo&Go), INSEE Filosofi (carroyage 200 m). "
           "L'accès à 400 m est une distance à vol d'oiseau, pas un temps de marche réel.")
 
















