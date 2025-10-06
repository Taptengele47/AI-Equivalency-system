import os
DATABASE_URI = 'postgresql://postgres:Nyarwaba254@localhost/du_equivalency'  
SECRET_KEY = os.urandom(24).hex()  # Secure random key
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')  # For plan files
ALLOWED_EXTENSIONS = {'csv', 'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)