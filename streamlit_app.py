import streamlit as st
import glob
import os
from image_processor import ImageProcessor

image_processor = ImageProcessor()

st.title('Search Images by Text')

n = st.number_input('Select Grid Width', 1, 5, 3)


project_directory = os.getcwd()
folders = [f for f in os.listdir(project_directory) if os.path.isdir(os.path.join(project_directory, f))]
selected_folder = st.selectbox("Seleziona una cartella", folders)

# Mostra la cartella selezionata
st.write("Hai selezionato la cartella:", selected_folder)

process = st.button("Processa le immagini")

# if process:
#     image_processor.set_folder_path(selected_folder)
#     image_processor.process_images()
#     st.write("Immagini processate con successo")

query = st.text_input("Inserisci la query")
search = st.button("Cerca")

if search:
    results = image_processor.query_collection(query, n_results=100)
    
    # Controlla se ci sono risultati
    if not results or not results[0]:
        st.write("Nessun risultato trovato.")
    else:
        st.write(len(results[0]))

        view_images = []
        for image_path in results[0]:
            # Assicurati che image_path sia un dizionario
            if isinstance(image_path, dict) and 'image_paths' in image_path:
                view_images.append(image_path['image_paths'])
            else:
                st.error("Formato di image_path non valido.")

        groups = []
        for i in range(0, len(view_images), n):
            groups.append(view_images[i:i+n])

        cols = st.columns(n)
        for group in groups:
            for idx, image_file in enumerate(group):
                cols[idx % n].image(image_file, use_column_width=True)

