import os

# Use env vars for Render; fallback for local
DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:Nyarwaba254@localhost/du_equivalency')
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)