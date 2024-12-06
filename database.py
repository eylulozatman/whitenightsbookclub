import firebase_admin
from firebase_admin import credentials, firestore
from config import Config

# Firebase bağlantısını başlat
cred = credentials.Certificate(Config.FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred)

# Firestore veritabanı nesnesi
db = firestore.client()
