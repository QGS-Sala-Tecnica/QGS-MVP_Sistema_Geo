import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from zipfile import ZipFile
import tempfile
import requests
import os

st.set_page_config(layout="wide")
st.title("QGS WebCity")
st.markdown("**Projeto piloto: Nova Conquista**")
st.success("MVP iniciado com sucesso.")

st.subheader("Visualização das Camadas Vetoriais")

# LINKS diretos para os arquivos ZIP no Google Drive
links = {
    "Quadras": "https://drive.google.com/uc?export=download&id=1hSIIBeFZm15r3JEg46FlAB7ZcZbzAZNg",
    "Lotes": "https://drive.google.com/uc?export=download&id=1rA9BDRLM2hBHHkmQeVTvZcu4FvVeNYHm"
}

}

def baixar_e_ler_shapefile_zip(link):
    response = requests.get(link)
    if response.status_code != 200:
        st.error("Erro ao baixar arquivo")
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "arquivo.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        for file in os.listdir(tmpdir):
            if file.endswith(".shp"):
                shp_path = os.path.join(tmpdir, file)
                return gpd.read_file(shp_path)
    return None

# Baixar e carregar as camadas
quadras = baixar_e_ler_shapefile_zip(links["Quadras"])
lotes = baixar_e_ler_shapefile_zip(links["Lotes"])

# Criar mapa
if quadras is not None and lotes is not None:
    center = quadras.geometry.centroid.iloc[0].coords[0][::-1]
    m = folium.Map(location=center, zoom_start=17, tiles="cartodbpositron")

    # Adiciona Quadras (contorno vermelho)
    folium.GeoJson(
        quadras,
        name="Quadras",
        style_function=lambda x: {
            'color': 'red',
            'weight': 2,
            'fillOpacity': 0
        },
        tooltip=folium.GeoJsonTooltip(fields=quadras.columns.tolist())
    ).add_to(m)

    # Adiciona Lotes (contorno azul escuro)
    folium.GeoJson(
        lotes,
        name="Lotes",
        style_function=lambda x: {
            'color': 'darkblue',
            'weight': 1.5,
            'fillOpacity': 0
        },
        tooltip=folium.GeoJsonTooltip(fields=lotes.columns.tolist())
    ).add_to(m)

    folium.LayerControl().add_to(m)
    folium_static(m)
else:
    st.error("Falha ao carregar uma ou mais camadas.")
