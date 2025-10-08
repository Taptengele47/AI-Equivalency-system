import os
DATABASE_URI = os.environ.get('DATABASE_URL')
if not DATABASE_URI:
    DATABASE_URI = 'postgresql://postgres:Nyarwaba254@localhost/du_equivalency'  # Local only
else:
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://")