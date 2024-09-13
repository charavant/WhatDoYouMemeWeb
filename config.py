class Config:
    # General config
    SECRET_KEY = 'your-secret-key'  # Replace with a real secret key
    
    # Database config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Add other configuration settings as needed

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# You can add more environment-specific configs if needed
