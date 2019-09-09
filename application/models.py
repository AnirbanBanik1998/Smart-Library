from application import db


# Class student representing a table student with it's various columns having various attributes
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    reg_no = db.Column(db.String(50), unique=True)
    rfid_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    last_intime = db.Column(db.DateTime, nullable=True)
    last_outtime = db.Column(db.DateTime, nullable=True)
    num_of_books = db.Column(db.Integer)
    books = db.relationship('Book', backref='assignee')

# Class Book representing a table book
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    barcode_id = db.Column(db.String(50), unique=True)
    tag = db.Column(db.Boolean)
    issued_at = db.Column(db.DateTime, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('student.reg_no'), nullable=True)