from application import app, db
from application.routes import token_required
from application.models import Student, Book

#Creating the database tables
db.create_all()

#Running the application
app.run(host='0.0.0.0', port=5000)
