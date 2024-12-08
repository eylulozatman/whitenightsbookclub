import os
import json

class Config:
    # Firebase servis anahtarını çevresel değişkenden yükleme
    FIREBASE_CREDENTIALS = json.loads(os.environ.get("FIREBASE_KEY", "{}"))
    
    SECRET_KEY = os.urandom(24)  # Güvenli bir secret key oluşturuyoruz
    SESSION_TYPE = 'filesystem'  # session için filesystem kullanacağız
