import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import webbrowser
from datetime import datetime
import random

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'f66c2d6e2c0c41ceae76e7b8dd41664c'
SPOTIPY_CLIENT_SECRET = '3323dddfec1446b0bb8bf6c6453d2f6e'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Spotify API setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-library-read playlist-modify-public user-top-read"))

# Function to get user's top tracks
def get_top_tracks():
    results = sp.current_user_top_tracks(limit=50)
    return [track['name'] for track in results['items']]

# Function to recommend tracks based on mood
def recommend_tracks(mood):
    all_tracks = get_top_tracks()
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(all_tracks)
    indices = np.argsort(vectorizer.idf_)[::-1]
    features = vectorizer.get_feature_names_out()
    top_keywords = [features[i] for i in indices[:50]]  # Increase the number of keywords

    # Add mood-based variability
    mood_keywords = {
        "😊 Happy": ["joy", "happy", "upbeat", "dance", "party"],
        "😢 Sad": ["sad", "melancholy", "downbeat", "blue", "heartbreak"],
        "💪 Energetic": ["energetic", "powerful", "intense", "workout", "pump"],
        "😌 Calm": ["calm", "relaxing", "soothing", "chill", "peaceful"]
    }

    selected_keywords = top_keywords + mood_keywords.get(mood, [])
    random.shuffle(selected_keywords)  # Shuffle the keywords to introduce variability

    # Search for tracks based on keywords
    recommended_tracks = []
    for keyword in selected_keywords[:20]:  # Use a larger subset of keywords
        results = sp.search(q=keyword, type='track', limit=1)
        if results['tracks']['items']:
            track_id = results['tracks']['items'][0]['id']
            if track_id not in recommended_tracks:  # Avoid duplicates
                recommended_tracks.append(track_id)
        if len(recommended_tracks) >= 10:  # Limit to 10 tracks
            break

    return recommended_tracks

# Function to create a playlist
def create_playlist(name, tracks):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, name)
    sp.playlist_add_items(playlist['id'], tracks)
    return playlist['external_urls']['spotify']

# GUI setup
def create_gui():
    def on_submit():
        mood = mood_combobox.get()
        if not mood:
            messagebox.showerror("Error", "Please select your mood")
            return
        recommended_tracks = recommend_tracks(mood)
        playlist_name = f"{mood} Playlist - {datetime.now().strftime('%Y-%m-%d')}"
        playlist_url = create_playlist(playlist_name, recommended_tracks)
        messagebox.showinfo("Success", "Playlist created successfully")
        webbrowser.open(playlist_url)

    root = ThemedTk(theme="equilux")
    root.title("AI-Based Music Recommendation")
    root.configure(bg='#2e2e2e')

    style = ttk.Style()
    style.configure('TLabel', background='#2e2e2e', foreground='#ffffff')
    style.configure('TCombobox', fieldbackground='#2e2e2e', background='#2e2e2e', foreground='#ffffff')
    style.configure('TButton', background='#2e2e2e', foreground='#ffffff')

    ttk.Label(root, text="Select your mood:").pack(pady=10)
    mood_combobox = ttk.Combobox(root, values=["😊 Happy", "😢 Sad", "💪 Energetic", "😌 Calm"], style='TCombobox')
    mood_combobox.pack(pady=10)

    submit_button = ttk.Button(root, text="Create Playlist", command=on_submit, style='TButton')
    submit_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()