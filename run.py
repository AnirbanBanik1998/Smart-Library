from application import app, db
from application.routes import token_required
from application.models import Student, Book

#Creating the database tables
db.create_all()

#Running the application in debug mode
app.run(debug=True)

