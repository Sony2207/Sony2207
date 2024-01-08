
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import requests
import plotly.express as px
import random
import time
 
# API-Informationen für TheMovieDB
api_key = '20f06120887f0b5a9124cb4f2713a9a7'
base_url = 'https://api.themoviedb.org/3'
 
# MySQL-Verbindungsinformationen
host = 'localhost'
user = 'root'
password = '12345'
database = 'movies_metadata'
 
# Verbindung zur MySQL-Datenbank herstellen
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
 
# Laden der Daten aus der MySQL-Datenbank
def load_data():
    query = "SELECT * FROM movies_metadata"
    df = pd.read_sql(query, con=engine)
    return df
 
# Funktion zur Abfrage von Filminformationen von TheMovieDB-API
def get_movie_poster(movie_title):
    search_url = f"{base_url}/search/movie"
    params = {'api_key': api_key, 'query': movie_title}
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        results = response.json()['results']
        if results:
            return results[0]['poster_path']
    return None
# Seite 1: Liste der 10 meistgeschauten Filme mit Bildverknüpfungen von TheMovieDB
def page_top_movies(df):
    st.title("Top 10 Meistgeschauten Filme")
    top_movies = df.nlargest(10, 'vote_count')[['original_title', 'vote_count', 'popularity']]
 
    # Erstellen von zwei Spalten
    col1, col2 = st.columns(2)
    films_shown = 0
 
    for index, movie in enumerate(top_movies.iterrows()):
        movie_data = movie[1]
        poster_path = get_movie_poster(movie_data['original_title'])
 
        # Wechsel zwischen den zwei Spalten
        col = col1 if films_shown % 2 == 0 else col2
        with col:
            st.write(f"**{movie_data['original_title']}**")
            st.write(f"Votes: {movie_data['vote_count']} - Popularity: {movie_data['popularity']}")
            if poster_path:
                st.image(f"https://image.tmdb.org/t/p/w500/{poster_path}", use_column_width=True)
            else:
                st.write("Bild nicht verfügbar")
       
        films_shown += 1
# Seite 2: Slider für Budget der 20 erfolgreichsten Filme
def page_budget_slider(df):
    st.title("Slider für Budget der 20 Erfolgreichsten Filme")
    top_20_movies = df.nlargest(20, 'revenue')
    top_20_movies['budget'] = top_20_movies['budget'].astype(float)
 
    budget_range = st.slider("Budget-Bereich auswählen", float(top_20_movies['budget'].min()), float(top_20_movies['budget'].max()), (float(top_20_movies['budget'].min()), float(top_20_movies['budget'].max())))
   
    fig = px.scatter(top_20_movies[(top_20_movies['budget'] >= budget_range[0]) & (top_20_movies['budget'] <= budget_range[1])],
                     x='original_title', y='budget', size='revenue', color='revenue',
                     title='Budget der Top 20 Filme')
 
    st.plotly_chart(fig)
 
# Seite 3: Die 3 erfolgreichsten Filme nach Genres
# Liste der zu entfernenden Strings aus den Genres
remove_strings = [
    'id', 'name Aniplex', 'name BROSTA TV', 'name Carousel Productions',
    'name Mardock Scramble Production Committee', 'name Odyssey Media',
    'name Pulser Productions', 'name Rogue State', 'name Telescene Film Group Productions',
    'name The Cartel', 'name Vision View Entertainment'
]
 
# Seite 3: Die 3 erfolgreichsten Filme nach Genres
remove_strings = [
    'id', 'name Aniplex', 'name BROSTA TV', 'name Carousel Productions',
    'name Mardock Scramble Production Committee', 'name Odyssey Media',
    'name Pulser Productions', 'name Rogue State', 'name Telescene Film Group Productions',
    'name The Cartel', 'name Vision View Entertainment'
]
 

# Seite 3: Die 3 erfolgreichsten Filme nach Genres
def page_top_genres(df):
    st.title("Die 3 Erfolgreichsten Filme nach Genres")
 
    # Bereinigen der Genres und Entfernen unnötiger Zeichen
    df['clean_genres'] = df['genres'].str.replace('[^a-zA-Z, ]', '', regex=True).apply(lambda x: x.split(', ') if isinstance(x, str) else [])
 
    # Erzeugen einer eindeutigen Liste aller Genres
    unique_genres = sorted(set([genre.strip() for sublist in df['clean_genres'] for genre in sublist if genre]))
 
    for genre in unique_genres:
        st.subheader(f"Top 3 Filme im Genre: {genre}")
        genre_df = df[df['clean_genres'].apply(lambda genres: genre in genres)].nlargest(3, 'revenue')
       
        # Anzeigen der Filme in zwei Zeilen für gleiche Höhe der Bilder
        col1, col2 = st.columns(2)
        for index, movie in enumerate(genre_df.iterrows()):
            movie_data = movie[1]
            poster_path = get_movie_poster(movie_data['original_title'])
            # Wechsel zwischen den zwei Spalten
            col = col1 if index % 2 == 0 else col2
            with col:
                st.write(f"**{movie_data['original_title']}**")
                st.write(f"Einnahmen: {movie_data['revenue']}$")
                if poster_path:
                    st.image(f"https://image.tmdb.org/t/p/w500/{poster_path}", use_column_width=True)
                else:
                    st.write("Bild nicht verfügbar")
# Seite 4: Informationen zu den Sprachen der Filme
def page_languages(df):
    st.title("Sprachen der Filme")
 
    # Berechnung der zehn häufigsten Sprachen
    language_count = df['original_language'].value_counts().nlargest(10)
 
    # Erstellung einer Tabelle mit Sprachen und Anzahl der Filme
    language_table = pd.DataFrame({
        'Sprache': language_count.index,
        'Anzahl der Filme': language_count.values
    })
 
    # Anzeigen der Tabelle
    st.table(language_table)
# Seite 5: Filmroulette
def page_movie_roulette(df):
    st.title("Filmroulette")
    language_map = {
        'en': 'Englisch',
        'es': 'Spanisch',
        'fr': 'Französisch',
        'de': 'Deutsch',
        # Fügen Sie hier weitere Übersetzungen hinzu
    }
 
    # Übersetze Sprachcodes in den Filmdaten
    df['original_language'] = df['original_language'].map(language_map).fillna(df['original_language'])
 
    # Bereinigung und Aufteilung der Genres für die Auswahl
    df['clean_genres'] = df['genres'].str.replace('[^a-zA-Z,name,id ]', '', regex=True).apply(lambda x: x.split(', ') if isinstance(x, str) else [])
    unique_genres = sorted(set([genre.strip() for sublist in df['clean_genres'] for genre in sublist if genre]))
 
    selected_genre = st.selectbox("Wähle ein Genre:", ['Alle'] + unique_genres)
 
    if st.button("Film vorschlagen"):
        # Filtern nach gewähltem Genre, falls nicht 'Alle' ausgewählt ist
        if selected_genre != 'Alle':
            filtered_df = df[df['clean_genres'].apply(lambda genres: selected_genre in genres)]
        else:
            filtered_df = df
 
        # Zufällige Auswahl eines Films
        random_movie = filtered_df.sample(1).iloc[0]
        movie_title = random_movie['original_title']
        movie_tagline = random_movie.get('tagline', 'Keine Tagline verfügbar')
 
        # Roulette-Animation
        for _ in range(5):
            random_temp_movie = filtered_df.sample(1).iloc[0]
            st.write("⏳ Roulette dreht sich... Auswahl: " + random_temp_movie['original_title'])
            time.sleep(1)
        st.write("🎬 Film ausgewählt: " + movie_title)
        st.write("📜 Tagline: " + movie_tagline)
 
        # Anzeigen des Posters
        poster_path = get_movie_poster(movie_title)
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w500/{poster_path}", use_column_width=True)
        else:
            st.write("Bild nicht verfügbar")
 
# Hauptfunktion für das Benutzerinterface
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Gehe zu", ['Top Filme', 'Budget Slider', 'Top Genres', 'Sprachen', 'Filmroulette'])
 
    # Laden der Daten beim Start
    df = load_data()
 
    # Anzeige entsprechender Seite basierend auf Benutzerwahl
    if page == 'Top Filme':
        page_top_movies(df)
    elif page == 'Budget Slider':
        page_budget_slider(df)
    elif page == 'Top Genres':
        page_top_genres(df)
    elif page == 'Sprachen':
        page_languages(df)
    elif page == 'Filmroulette':
        page_movie_roulette(df)
 
# Streamlit-Anwendung starten
if __name__ == '__main__':
    main()