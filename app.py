from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin, login_required
from firebase_admin.auth import create_user, verify_id_token, get_user_by_email
from firebase_admin import auth
from database import db
from datetime import datetime
import firebase_admin
from firebase_admin.exceptions import FirebaseError
import os
from config import ConfigClass  # Load the appropriate configuration based on the environment

app = Flask(__name__)
app.config.from_object(ConfigClass)  # Apply the selected configuration
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user_ref = db.collection('users').document(user_id).get()
    if user_ref.exists:
        user_data = user_ref.to_dict()
        return User(user_id, user_data['username'], user_data['email'])
    return None

@app.route('/')
def welcome():
    return render_template('pages/welcome-page.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Firestore'da aynı username var mı kontrol et
            user_ref = db.collection('users').where('username', '==', username).get()
            
            if user_ref:
                flash("Username already taken. Please choose another.", "danger")
                return render_template('pages/register.html')

            # Firebase kullanıcısını oluştur
            user = auth.create_user(
                email=email,
                password=password
            )
            
            # Firestore'a kullanıcı verilerini kaydet
            db.collection('users').document(user.uid).set({
                'email': email,
                'username': username
            })
            
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        
        except Exception as e:
            flash(f"Error: {e}", "danger")
            
    return render_template('pages/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            # Firebase Authentication ile giriş yap
            user = auth.get_user_by_email(email)
        
            user_data = User(user.uid, user.display_name, email)
            login_user(user_data)
            session['user'] = user.uid  # Oturum açan kullanıcının UID'si
            flash("Login successful!", "success")
            return redirect(url_for('homepage'))
        except firebase_admin.exceptions.FirebaseError as e:
            flash(f"Authentication error: {e}", "danger")
            print("error in login")

    return render_template('pages/login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    flash("You have logged out.", "info")
    return redirect(url_for('welcome'))

@app.route('/homepage')
def homepage():
    query = request.args.get('q', '').lower()  # 'q' parametresini al ve küçük harfe çevir
    books_ref = db.collection('books')
    filtered_books = []

    # Kitapları filtrele
    for doc in books_ref.stream():
        book_data = doc.to_dict()

        # Filtre: Sorguyu başlık, yazar veya yorum içinde arayın
        if query in book_data.get('title', '').lower() or \
           query in book_data.get('author', '').lower() or \
           query in book_data.get('review', '').lower():
           filtered_books.append(book_data)

    # Yayıncı bilgilerini çek
    for book_data in filtered_books:
        user_id = book_data.get('user_id')
        if user_id:
            user_ref = db.collection('users').document(user_id).get()
            if user_ref.exists:
                user_data = user_ref.to_dict()
                publisher = user_data.get('username', 'Unknown')
            else:
                publisher = 'Unknown'
        else:
            publisher = 'Unknown'

        # Yayıncıyı kitap verisine ekle
        book_data['publisher'] = publisher

        # Like sayısını hesapla
        like_count = len(db.collection('likes').where('book_id', '==', book_data['book_id']).get())
        book_data['like_count'] = like_count

    per_page = 6
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_books = filtered_books[start:end]
    total_pages = (len(filtered_books) + per_page - 1) // per_page

    # Template'e render et
    return render_template(
        'pages/homepage.html',
        books=paginated_books,
        current_page=page,
        total_pages=total_pages,
        query=query  
    )


@app.route('/handle-like/<book_id>', methods=['POST'])
@login_required
def handle_like(book_id):
    # Kullanıcının beğendiği kitabı kontrol et
    like_ref = db.collection('likes').where('book_id', '==', book_id).where('user_id', '==', current_user.id).get()

    if len(like_ref) > 0:
        # Eğer daha önce beğenmişse, like'ı kaldır
        for like in like_ref:
            like.reference.delete()
        flash('You unliked this book!', 'success')
    else:
        # Eğer daha önce beğenmemişse, like ekle
        db.collection('likes').add({
            'book_id': book_id,
            'user_id': current_user.id
        })
        flash('You liked this book!', 'success')

    return redirect(url_for('book_detail', book_id=book_id))


@app.route('/book-detail/<string:book_id>', methods=['GET', 'POST'])
@login_required
def book_detail(book_id):
    try:
        # Kitabı Firestore'dan ID ile al
        book_ref = db.collection('books').document(book_id).get()
        
        if book_ref.exists:
            book = book_ref.to_dict()
            
            # Kullanıcının bu kitabı beğenip beğenmediğini kontrol et
            user_id = current_user.id  # Kullanıcının ID'si
            like_ref = db.collection('likes').where('book_id', '==', book_id).where('user_id', '==', user_id).get()
            
            # Eğer beğenilmişse is_liked True döndür, değilse False
            is_liked = len(like_ref) > 0
            
            return render_template('pages/book-detail.html', book=book, is_liked=is_liked)
        else:
            flash("Book not found.", "danger")
            return redirect(url_for('homepage'))
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('homepage'))



@app.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        review = request.form['review']
        cover_image_url = request.form['cover_image_url']
        rating = int(request.form['rating'])  # Puanı al ve integer olarak işle

        # Şu anki tarihi al
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        new_book_ref = db.collection('books').document()  
        book_id = new_book_ref.id  # Otomatik oluşturulan ID'yi al

        new_book = {
            'book_id': book_id,  # Otomatik oluşturulan ID'yi ekle
            'title': title,
            'author': author,
            'review': review,
            'cover_image_url': cover_image_url,
            'rating': rating, 
            'user_id': current_user.id,
            'added_date': current_date  # Eklenme tarihini kaydet
        }

        new_book_ref.set(new_book)  # Belgeyi ID ile kaydet

        flash("Book added successfully!", "success")
        return redirect(url_for('homepage'))

    return render_template('pages/add-book.html')

@app.route('/user-profile/<string:user_id>', methods=['GET'])
@login_required
def user_profile(user_id):
    try:
        # Kullanıcının bilgilerini al
        user_ref = db.collection('users').document(user_id).get()
        if user_ref.exists:
            user = user_ref.to_dict()
        else:
            flash("User not found.", "danger")
            return redirect(url_for('homepage'))

        # Kullanıcının yazdığı kitaplar
        books_ref = db.collection('books').where('user_id', '==', user_id).get()
        books = [book.to_dict() for book in books_ref]

        # Her kitap için yayıncıyı al (user_id'ye göre)
        for book in books:
            publisher = user['username']  # Kitap yazarı, profilin sahibi
            book['publisher'] = publisher

            # Like sayısını hesapla
            like_count = len(db.collection('likes').where('book_id', '==', book['book_id']).get())
            book['like_count'] = like_count

        return render_template('pages/profile.html', user=user, books=books)

    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('homepage'))



@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        # Kullanıcı ID'sini al
        user_id = request.form['user_id']  
        
        # Firebase Authentication'dan kullanıcıyı sil
        auth.delete_user(user_id)
        
        user_books_ref = db.collection('user_books').where('userId', '==', user_id)
        for relationship in user_books_ref.stream():
            relationship.reference.delete()
        # Firestore'dan kullanıcı verilerini sil
        db.collection('users').document(user_id).delete()
        
        flash("User successfully deleted.", "success")
        return redirect(url_for('homepage'))
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('homepage'))

   

if __name__ == '__main__':
    app.run(debug=True)
