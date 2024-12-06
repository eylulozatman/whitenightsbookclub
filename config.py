import os

class Config:
    # Firebase servis anahtar JSON dosyasının yolu
    FIREBASE_KEY_PATH = os.path.join(os.path.dirname(__file__), 'firebase_key.json')
    SECRET_KEY = os.urandom(24)  # Güvenli bir secret key oluşturuyoruz
    SESSION_TYPE = 'filesystem'  # session için filesystem kullanacağız
