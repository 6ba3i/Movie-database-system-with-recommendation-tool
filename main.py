import os
import ssl
import json
import requests
import urllib3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from firebase_service import *  # Ensure firebase_service.py is up-to-date
from werkzeug.utils import secure_filename
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# Disable SSL warnings (for development only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = "5c70ea5bcb6eefaff9f3ea7ef026dbe2"

# ------------------------------
# Custom TLS Adapter to enforce TLS 1.2
# ------------------------------
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            **pool_kwargs
        )

# Create a global session and mount the TLS adapter for all HTTPS requests
tmdb_session = requests.Session()
tmdb_session.mount("https://", TLSAdapter())

# ------------------------------
# TMDB Bearer Token Header (as provided)
# ------------------------------
TMDB_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzM2Y5YzJkYjM0MzA0MDliNzM2NjU3Zjc1ZDA2OWY2YiIsInN1YiI6IjY0NmRkZTQ1MzNhMzc2MDEwMWZjZDdmZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.GR4lTzq43kK7_2OKrOeYh6SB0busifckYNaQsdwbzQQ"
}

#####################################
# TMDB HELPER FUNCTIONS
#####################################
def tmdb_get(url, params=None):
    if params is None:
        params = {}
    try:
        # Use our custom session with TLSAdapter
        response = tmdb_session.get(url, headers=TMDB_HEADERS, params=params, verify=False, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.SSLError as ssl_err:
        print("SSL Error:", ssl_err)
    except Exception as e:
        print("An error occurred:", e)
    return {}

def search_movies(query):
    if not query:
        return []
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"query": query, "language": "en-US", "page": 1, "include_adult": False}
    data = tmdb_get(url, params)
    return data.get("results", [])

def discover_movies_by_genres(genre_ids):
    if not genre_ids:
        return []
    genre_str = ",".join(map(str, genre_ids))
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {"with_genres": genre_str, "language": "en-US", "sort_by": "popularity.desc", "page": 1}
    data = tmdb_get(url, params)
    return data.get("results", [])

def discover_movies_by_actor(person_id):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {"with_people": str(person_id), "language": "en-US", "sort_by": "popularity.desc", "page": 1}
    data = tmdb_get(url, params)
    return data.get("results", [])

def get_movie_details(movie_id):
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    detail_data = tmdb_get(base_url, {"language": "en-US"})
    credits_data = tmdb_get(f"{base_url}/credits")
    # Get top 5 actors from cast
    cast_list = credits_data.get("cast", [])
    top_actors = cast_list[:5]
    detail_data["top_actor_ids"] = [c["id"] for c in top_actors]
    detail_data["top_actor_names"] = [c["name"] for c in top_actors]
    # Find director
    director = None
    for c in credits_data.get("crew", []):
        if c.get("job") == "Director":
            director = c.get("name")
            break
    detail_data["director"] = director
    return detail_data

def get_popular_movies():
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"language": "en-US", "page": 1}
    data = tmdb_get(url, params)
    return data.get("results", [])

#####################################
# RECOMMENDATION LOGIC
#####################################
def get_combined_recommendations():
    all_movies = {}
    # Discover movies by genres stored in session
    genre_list = session.get("genres", [])
    if genre_list:
        results = discover_movies_by_genres(genre_list)
        for mv in results:
            all_movies[mv["id"]] = mv
    # Discover movies by actors stored in session
    actor_list = session.get("actors", [])
    for actor_id in actor_list:
        results = discover_movies_by_actor(actor_id)
        for mv in results:
            all_movies[mv["id"]] = mv
    # Search by movie titles stored in session
    title_list = session.get("titles", [])
    for title in title_list:
        results = search_movies(title)
        for mv in results:
            all_movies[mv["id"]] = mv
    combined_list = list(all_movies.values())
    combined_list.sort(key=lambda x: x.get("popularity", 0), reverse=True)
    return combined_list

#####################################
# SESSION HELPER FUNCTIONS
#####################################
def add_genre(genre_id):
    genres_list = session.get("genres", [])
    genres_set = set(genres_list)
    genres_set.add(genre_id)
    session["genres"] = list(genres_set)

def add_actor(actor_id):
    actors_list = session.get("actors", [])
    actors_set = set(actors_list)
    actors_set.add(actor_id)
    session["actors"] = list(actors_set)

def add_title(title_str):
    titles_list = session.get("titles", [])
    titles_set = set(titles_list)
    titles_set.add(title_str)
    session["titles"] = list(titles_set)

#####################################
# LOCAL PROFILE PICTURE UPLOAD
#####################################
def save_profile_picture_locally(file, uid):
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.isdir(upload_folder):
        os.makedirs(upload_folder)
    filename = secure_filename(f"{uid}.jpg")
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return url_for('static', filename=f'uploads/{filename}', _external=True)

#####################################
# FLASK ROUTES
#####################################
@app.route("/")
def root():
    return redirect(url_for("index"))

@app.route("/index")
def index():
    if "uid" not in session:
        return render_template("index.html")
    return redirect(url_for("home"))

# Signup Step 1: Email & Password
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            session["temp_user"] = {"email": email, "password": password}
            return redirect(url_for("signup_customization"))
        else:
            flash("Email and password are required.", "error")
    return render_template("signup_step1.html")

# Signup Step 2: Customization (name, age, genres, profile picture)
@app.route("/signup_customization", methods=["GET", "POST"])
def signup_customization():
    if "temp_user" not in session:
        flash("Please sign up with your email and password first.", "error")
        return redirect(url_for("signup"))
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        genres = request.form.getlist("genres")
        pfp = request.files.get("pfp")
        email = session["temp_user"]["email"]
        password = session["temp_user"]["password"]
        try:
            user_record = create_user_account(email, password)
            uid = getattr(user_record, "uid", "some_uid")
        except Exception as e:
            flash("Failed to create user: " + str(e), "error")
            return redirect(url_for("signup"))
        session["uid"] = uid
        session["user_email"] = email
        profile_data = {"name": name, "age": age, "genres": genres, "email": email}
        save_user_profile(uid, profile_data)
        if pfp:
            try:
                pfp_url = save_profile_picture_locally(pfp, uid)
                profile_data["pfp_url"] = pfp_url
                save_user_profile(uid, profile_data)
            except Exception as e:
                flash("Failed to upload profile picture: " + str(e), "error")
        session["profile"] = profile_data
        session["genres"] = genres
        session["actors"] = []
        session["titles"] = []
        session["watchlist"] = []
        session.pop("temp_user", None)
        flash("Signup successful!", "success")
        return redirect(url_for("home"))
    return render_template("signup_step2.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            api_key = "YOUR_FIREBASE_API_KEY_HERE"
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                # Debug print to see the Firebase response if needed:
                # print(response.json())
                if response.status_code == 200:
                    data = response.json()
                    session["uid"] = data["localId"]
                    session["user_email"] = email

                    # Retrieve the user profile from Firestore.
                    profile = get_user_profile(data["localId"])
                    if profile:
                        session["profile"] = profile
                        session["genres"] = profile.get("genres", [])
                    else:
                        session["profile"] = {}
                        session["genres"] = []

                    session.setdefault("actors", [])
                    session.setdefault("titles", [])
                    session.setdefault("watchlist", [])
                    flash("Login successful!", "success")
                    return redirect(url_for("home"))
                else:
                    # Optionally, print the error response for debugging:
                    # print(response.json())
                    flash("Invalid credentials!", "error")
            except Exception as e:
                flash("An error occurred during login: " + str(e), "error")
        else:
            flash("Please fill in both email and password.", "error")
    return render_template("login.html")
# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out!", "info")
    return redirect(url_for("index"))

# Profile Settings Route: Update name, password, and profile picture
@app.route("/profile_settings", methods=["GET", "POST"])
def profile_settings():
    if "uid" not in session:
        flash("Please log in!", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        new_name = request.form.get("name")
        new_password = request.form.get("password")
        new_picture = request.files.get("pfp")
        uid = session["uid"]
        profile = session.get("profile", {})
        if new_name:
            profile["name"] = new_name
        if new_password:
            pass
        if new_picture:
            try:
                pfp_url = save_profile_picture_locally(new_picture, uid)
                profile["pfp_url"] = pfp_url
            except Exception as e:
                flash("Failed to update profile picture: " + str(e), "error")
        save_user_profile(uid, profile)
        session["profile"] = profile
        flash("Profile updated!", "success")
        return redirect(url_for("profile_settings"))
    return render_template("profile_settings.html", profile=session.get("profile", {}))

# Home Route
@app.route("/home")
def home():
    if "uid" not in session:
        flash("Please log in!", "error")
        return redirect(url_for("login"))
    recommended = get_combined_recommendations()[:6]
    popular = get_popular_movies()[:6]
    watchlist = session.get("watchlist", [])
    watchlist_preview = watchlist[:4]
    return render_template("home.html",
                           recommended=recommended,
                           top_movies=popular,
                           watchlist_preview=watchlist_preview)

# Search Route
@app.route("/search")
def search_route():
    if "uid" not in session:
        flash("Please log in!", "error")
        return redirect(url_for("login"))
    query = request.args.get("query", "").strip()
    if not query:
        flash("No search query provided.", "info")
        return redirect(url_for("home"))
    results = search_movies(query)
    for mv in results[:3]:
        add_title(mv["title"])
        for g in mv.get("genre_ids", []):
            add_genre(g)
    flash("Search updated your recommendation profile!", "info")
    return render_template("search_results.html", query=query, results=results)

# Movie Detail Route
@app.route("/movie/<int:movie_id>")
def movie_detail_route(movie_id):
    if "uid" not in session:
        flash("Please log in!", "error")
        return redirect(url_for("login"))
    detail = get_movie_details(movie_id)
    return render_template("movie_detail.html", movie=detail)

# Add to Watchlist Route
@app.route("/add_to_watchlist/<int:movie_id>", methods=["POST"])
def add_to_watchlist_route(movie_id):
    if "uid" not in session:
        flash("Please log in!", "error")
        return redirect(url_for("login"))
    detail = get_movie_details(movie_id)
    wlist = session.get("watchlist", [])
    if any(m["id"] == movie_id for m in wlist):
        flash("Movie is already in your watchlist!", "info")
        return redirect(url_for("movie_detail_route", movie_id=movie_id))
    movie_data = {
        "id": detail["id"],
        "title": detail["title"],
        "poster_path": detail.get("poster_path"),
        "vote_average": detail.get("vote_average", 0)
    }
    wlist.append(movie_data)
    session["watchlist"] = wlist
    for g in detail.get("genres", []):
        add_genre(g["id"])
    for actor_id in detail.get("top_actor_ids", []):
        add_actor(actor_id)
    add_title(detail["title"])
    flash(f"{detail['title']} added to watchlist & rec profile!", "success")
    return redirect(url_for("movie_detail_route", movie_id=movie_id))

# Remove from Watchlist Route
@app.route("/remove_from_watchlist/<int:movie_id>", methods=["POST"])
def remove_from_watchlist_route(movie_id):
    if "uid" not in session:
        flash("Please log in!", "error")
        return redirect(url_for("login"))
    watchlist = session.get("watchlist", [])
    new_watchlist = [movie for movie in watchlist if movie["id"] != movie_id]
    session["watchlist"] = new_watchlist
    remove_from_watchlist(session["uid"], movie_id)
    flash("Movie removed from your watchlist.", "info")
    return redirect(url_for("my_watchlist"))

# My Watchlist Route
@app.route("/my_watchlist")
def my_watchlist():
    if "uid" not in session:
        flash("Please log in!", "error")
        return redirect(url_for("login"))
    wlist = session.get("watchlist", [])
    return render_template("watchlist.html", watchlist=wlist)

if __name__ == "__main__":
    app.run(debug=True)
