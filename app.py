from flask import Flask, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from googletrans import Translator, LANGUAGES
import cv2
import pytesseract
import numpy as np
import requests
import os
import speech_recognition as sr
import fitz

app = Flask(__name__)

recognizer = sr.Recognizer()
app.config['UPLOAD_FOLDER'] = 'uploads'

# Set the path to the Tesseract executable (change this path as per your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app.secret_key = 'your_secret_key_here' 

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists"
        # Create a new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the user exists and password matches
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username  
            return redirect('/text')
        
        return "Invalid username or password"
    
    return render_template('login.html') 

@app.route('/text')
def text():
    if 'username' in session and request.method == 'GET':
        return render_template('text.html')  
    return redirect('/login')

# @app.route('/texttranslate', methods=['POST'])
# def textfunc():
#     input_text = request.form['inputText']
#     print(input_text)
#     destination_language = request.form['destination_language']
#     print(destination_language)
#     translated_text = translate(input_text, destination_language)
#     return jsonify({'translated_text': translated_text})

@app.route('/texttranslate', methods=['POST'])
def textfunc():
    if 'username' in session and request.method == 'POST':
        input_text = request.form['inputText']
        destination_language = request.form['destination_language']
        translated_text = translate(input_text, destination_language)

        # Get the current user
        current_user = User.query.filter_by(username=session['username']).first()

        # Create a TranslationHistory entry associated with the current user
        history_entry = TranslationHistory(
            translated_content=translated_text,
            translation_input=input_text,
            translation_type='text',
            user=current_user
        )
        db.session.add(history_entry)
        db.session.commit()

        return jsonify({'translated_text': translated_text})

    return jsonify({'error': 'Unauthorized access or invalid request'})

@app.route('/speech')
def speech():
    if 'username' in session and request.method == 'GET':
        return render_template('speech.html')
    return redirect('/login')

@app.route('/speech_recognition', methods=['POST'])
def speech_recognition():
    try:
        # Check the action parameter in the request
        action = request.form.get('action')

        if action == 'recognize_speech':
            # Perform speech recognition
            with sr.Microphone() as source:
                print("Say something in English...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=10)
            
            english_text = recognizer.recognize_google(audio)
            print(f"Recognized English input: {english_text}")

            return jsonify({'recognized_text': english_text})

        elif action == 'translate_text':
            # Perform translation
            source_text = request.form.get('source_text')
            translator = Translator()
            translated_result = translator.translate(source_text, dest='ta')
            translated_text = translated_result.text

            return jsonify({'translated_text': translated_text})

        else:
            return jsonify({'error': 'Invalid action'})

    except sr.UnknownValueError:
        return jsonify({'error': 'Sorry, I could not understand what you said.'})
    except sr.RequestError as e:
        return jsonify({'error': f'Could not request results; {e}'})

@app.route('/img')
def index():
    if 'username' in session and request.method == 'GET':
        return render_template('img.html')
    return redirect('/login')

@app.route('/translate', methods=['POST'])
def translatefunc():
    if 'image' in request.files and 'username' in session:
        image_file = request.files['image']
        if image_file.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.png')
            image_file.save(image_path)
            extracted_text = extract_text(image_path)
            destination_language = request.form['destination_language']
            translated_text = translate(extracted_text, destination_language)
            os.remove(image_path)
            return jsonify({'translated_text': translated_text})
    return jsonify({'error': 'No image file received'})

@app.route('/pdf')
def pdf():
    if 'username' in session:
        return render_template('pdf.html')  
    return redirect('/login')

@app.route('/hand')
def hand():
    if 'username' in session:
        return render_template('hand.html')  
    return redirect('/login')

# @app.route('/history')
# def history():
#     if 'username' in session:
#         return render_template('history.html')  
#     return redirect('/login')

class TranslationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    translated_content = db.Column(db.String(500))
    translation_input = db.Column(db.String(500))
    translation_type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('translation_history', lazy=True))

@app.route('/history')
def history():
    if 'username' in session:
        # Fetch translation history for the logged-in user
        user = User.query.filter_by(username=session['username']).first()
        if user:
            translation_history = TranslationHistory.query.filter_by(user_id=user.id).all()
            return render_template('history.html', translation_history=translation_history)
        else:
            # Handle scenario where user does not exist
            return "User not found"
    return redirect('/login')

@app.route('/delete_translation', methods=['POST'])
def delete_translation():
    if 'username' in session:
        translation_id = request.form['translation_id']
        # Retrieve the translation entry from the database
        translation_entry = TranslationHistory.query.get(translation_id)
        if translation_entry:
            # Delete the translation entry
            db.session.delete(translation_entry)
            db.session.commit()
            return redirect('/history')
        else:
            return "Translation entry not found"
    return redirect('/login')

# Create tables
with app.app_context():
    db.create_all()

@app.route('/bookmark')
def bookmark():
    if 'username' in session:
        return render_template('bookmark.html')  
    return redirect('/login') 

@app.route('/feedback')
def feedback():
    if 'username' in session:
        return render_template('feedback.html')  
    return redirect('/login') 
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/extract_text', methods=['POST'])
def extract_text():
    # Get the uploaded file from the request
    uploaded_file = request.files['file']
    destination_language = request.form['destination_language']

    if uploaded_file.filename != '':
        # Read the PDF file and extract text
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype='pdf')
        text = ''
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
        text = text[:5000]
        output = translate(text, destination_language)
        pdf_document.close() 
        return jsonify({'text': output, 'input': text})
    else:
        return jsonify({'error': 'No file provided'})


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Denoising
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Thresholding
    _, threshold = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return threshold

def extract_text(input_img):
    image = cv2.imread(input_img)
    resized_image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    processed_image = preprocess_image(image)
    extracted_text = pytesseract.image_to_string(processed_image)
    return extracted_text

def translate(input_text, destination_language):
    if destination_language in LANGUAGES:
        translator = Translator()
        translated_result = translator.translate(input_text, dest=destination_language)
        return translated_result.text
    else:
        return "Invalid destination language"
    

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
