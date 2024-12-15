import firebase_admin
from firebase_admin import credentials, firestore
from config import ConfigClass  # Geliştirme ayarlarını kullanıyoruz

# Firebase Admin SDK'yı başlatıyoruz
if not firebase_admin._apps:
    # Firebase anahtarını yerel yoldan alıyoruz
    cred = credentials.Certificate(ConfigClass.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

# Firestore veritabanı bağlantısı
db = firestore.client()
