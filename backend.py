from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy 
import uuid
import jwt
import json
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///relationships.db'

db = SQLAlchemy(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Student.query.filter_by(reg_no=data['reg_no']).first()
        except:
            return jsonify({'message': 'Token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorated


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    reg_no = db.Column(db.String(50), unique=True)
    rfid_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    last_intime = db.Column(db.DateTime, nullable=True)
    last_outtime = db.Column(db.DateTime, nullable=True)
    books = db.relationship('Book', backref='assignee')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    barcode_id = db.Column(db.String(50), unique=True)
    tag = db.Column(db.Boolean)
    issued_at = db.Column(db.DateTime, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('student.reg_no'), nullable=True)


@app.route('/get_students', methods=['GET'])
@token_required
def get_students(current_user):
    students_list = []
    students = Student.query.all()

    for student in students:
        stud = {}
        stud['name'] = student.name
        stud['reg_no'] = student.reg_no
        stud['rfid_id'] = student.rfid_id
        students_list.append(stud)

    return jsonify({'students': students_list})

@app.route('/get_book_details/<name>', methods=['GET'])
@token_required
def get_book_details(current_user, name):
    books = Book.query.filter_by(name=name, tag=False).all()

    books_list = []
    for book in books:
        bk = {}
        bk['name'] = book.name
        bk['barcode_id'] = book.barcode_id
        books_list.append(bk)

    return jsonify({'books': books_list})

@app.route('/get_books', methods=['GET'])
@token_required
def get_books(current_user):
    books = Book.query.filter_by(assignee=current_user).all()

    books_list = []
    for book in books:
        bk = {}
        bk['name'] = book.name
        bk['barcode_id'] = book.barcode_id
        bk['issued_at'] = book.issued_at
        books_list.append(bk)

    return jsonify({'books': books_list})

@app.route('/student', methods=['POST'])
def post_student():
    data = request.get_json()
    new_student = Student(reg_no=data['reg_no'], rfid_id = str(uuid.uuid4()), name= data['name'])
    db.session.add(new_student)
    db.session.commit()

    return jsonify({'message': 'Student registered!'})

@app.route('/book', methods=['POST'])
def post_book():
    data = request.get_json()

    new_book = Book(barcode_id = str(uuid.uuid4()), name = data['name'], tag=False)
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Book Registered'})

@app.route('/register', methods=['PUT'])
def register():
    data = request.get_json()
    student = Student.query.filter_by(reg_no=data['reg_no'], name=data['name']).first()

    if not student:
        return jsonify({'message': 'Student not enrolled!'})

    hashed_password = generate_password_hash(data['password'], method='sha256')
    student.password = hashed_password
    db.session.commit()

    return jsonify({'message': 'Student registered successfully!'})

@app.route('/issue/<book_id>', methods=['PUT'])
@token_required
def book_issue(current_user, book_id):
    book = Book.query.filter_by(barcode_id=book_id, tag=False).first()

    current_time = datetime.datetime.utcnow()

    if current_user.last_intime is None:
        return jsonify({'message': 'Cannot return book'})
        
    if current_user.last_outtime is None:
        if not book:
            return jsonify({'message': 'Cannot return book'})

    if not book or ((current_time-current_user.last_intime).total_seconds()<0 or (current_user.last_intime-current_user.last_outtime).total_seconds()<0):
        return jsonify({'message': 'Cannot issue book'})

    book.assignee = current_user
    book.tag = True
    book.issued_at = current_time

    db.session.commit()

    return jsonify({'message': 'Book assigned successfully'})

@app.route('/return/<book_id>', methods=['PUT'])
@token_required
def book_return(current_user, book_id):
    book = Book.query.filter_by(barcode_id=book_id, tag=True, assignee=current_user).first()

    current_time = datetime.datetime.utcnow()
    if current_user.last_intime is None:
        return jsonify({'message': 'Cannot return book'})

    if current_user.last_outtime is None:
        if not book:
            return jsonify({'message': 'Cannot return book'})

    if not book or ((current_time-current_user.last_intime).total_seconds()<0 or (current_user.last_intime-current_user.last_outtime).total_seconds()<0):
        return jsonify({'message': 'Cannot return book'})

    book.assignee = None
    book.tag = False

    db.session.commit()

    return jsonify({'message': 'Book returned successfully'})

@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    student = Student.query.filter_by(reg_no=auth.username).first()

    if not student:
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    if check_password_hash(student.password, auth.password):
        token = jwt.encode({'reg_no' : student.reg_no, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

@app.route('/entry_exit', methods=['PUT'])
def entry_exit():
    data = request.get_json()
    student = Student.query.filter_by(rfid_id=data['rfid_id']).first()
    
    if student.last_intime is None:
        student.last_intime = datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'Entry'})

    if student.last_outtime is not None:
        time_diff = student.last_outtime - student.last_intime

        if time_diff.total_seconds() > 0:
            student.last_intime = datetime.datetime.utcnow()
            db.session.commit()
            return jsonify({'status': 'Entry'})

    
    student.last_outtime = datetime.datetime.utcnow()
    books = Book.query.filter_by(assignee=student).all()
    book_list = []
    for book in books:
        if(student.last_outtime-book.issued_at).total_seconds() > 0 and (book.issued_at-student.last_intime).total_seconds() > 0:
            book_list.append({'name': book.name, 'barcode_id': book.barcode_id})

    db.session.commit()
    return jsonify({'status': 'Exit', 'books': book_list})




if __name__=='__main__':
    app.run(debug=True)
