import firebase_admin
from firebase_admin import credentials, firestore
from config import ConfigClass

# Firebase bağlantısı
cred = credentials.Certificate(ConfigClass.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

# Firestore veritabanı örneği
db = firestore.client()
