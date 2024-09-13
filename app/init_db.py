import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, PredefinedResponse

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Add some predefined responses
        responses = [
            ('123456', 'That feeling when...'),
            ('234567', 'Me on Mondays'),
            ('345678', 'When you realize...'),
            ('456789', 'Nobody:'),
            ('567890', 'My last brain cell:'),
        ]

        for barcode, text in responses:
            response = PredefinedResponse(barcode=barcode, text=text)
            db.session.add(response)

        db.session.commit()

if __name__ == '__main__':
    init_db()
