import os
DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:Nyarwaba254@localhost/du_equivalency').replace("postgres://", "postgresql://")
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())  # Fallback to local
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)