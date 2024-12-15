import os

class Config:
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = 'filesystem'

class ConfigClass(Config):
    # Yerel firebasekey.json dosyasının yolu
    FIREBASE_CREDENTIALS = os.path.join(os.path.dirname(__file__), 'firebasekey.json')
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = 'filesystem'

# import os 
# import json
# from dotenv import load_dotenv

# # .env dosyasındaki değişkenleri yükle
# load_dotenv()

# class Config:
#     SECRET_KEY = os.urandom(24)
#     SESSION_TYPE = 'filesystem'

# class DevelopmentConfig(Config):
#     FIREBASE_CREDENTIALS = os.path.join(os.path.dirname(__file__), 'firebasekey.json')  # Yerel firebase_key.json
#     SECRET_KEY = os.urandom(24)
#     SESSION_TYPE = 'filesystem'

# class ProductionConfig(Config):
#     FIREBASE_CREDENTIALS = json.loads(os.getenv('FIREBASE_KEY_PROD', "{}"))  # Üretimde ortam değişkeni

# # Ortam değişkenine göre uygun yapılandırmayı seç
# if os.getenv('FLASK_ENV') == 'production':
#     ConfigClass = ProductionConfig
# else:
#     ConfigClass = DevelopmentConfig
