import firebase_admin
from firebase_admin import credentials, auth, firestore
# Removed the 'storage' import since it's no longer needed

# Initialize Firebase with your service account
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)  # Removed storageBucket parameter

db = firestore.client()

# --------- Auth ---------
def create_user_account(email, password):
    return auth.create_user(email=email, password=password)

def get_user_by_email(email):
    try:
        return auth.get_user_by_email(email)
    except Exception as e:
        return None

# --------- Firestore: Profile ---------
def save_user_profile(uid, data):
    db.collection("users").document(uid).set(data)

def get_user_profile(uid):
    return db.collection("users").document(uid).get().to_dict()

# --------- Watchlist ---------
def add_to_watchlist(uid, movie_data):
    db.collection("users").document(uid).collection("watchlist").document(str(movie_data["id"])).set(movie_data)

def remove_from_watchlist(uid, movie_id):
    db.collection("users").document(uid).collection("watchlist").document(str(movie_id)).delete()

def get_watchlist(uid):
    docs = db.collection("users").document(uid).collection("watchlist").stream()
    return [doc.to_dict() for doc in docs]
