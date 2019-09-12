from flask import request, jsonify, make_response
from application import app, db, token_required
from application.models import Student, Book
import uuid
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# This route is used to get the list of all students. Primarily required for testing purposes.
@app.route('/get_students', methods=['GET'])
def get_students():
    students_list = []
    students = Student.query.all()

    for student in students:
        stud = {}
        stud['name'] = student.name
        stud['reg_no'] = student.reg_no
        stud['rfid_id'] = student.rfid_id
        students_list.append(stud)

    return jsonify({'students': students_list})

# This is required to get the details of a book, like it's barcode id, rack no. just from it's name. To be improved upon
@app.route('/get_book_details/<name>', methods=['GET'])
def get_book_details(name):
    books = Book.query.filter_by(name=name, tag=False).all()

    books_list = []
    for book in books:
        bk = {}
        bk['name'] = book.name
        bk['barcode_id'] = book.barcode_id
        books_list.append(bk)

    return jsonify({'books': books_list})

# This returns the list of books issued by the student
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

# This is used to post a student to the library database. To be performed by admins.
@app.route('/student', methods=['POST'])
def post_student():
    data = request.get_json()
    new_student = Student(reg_no=data['reg_no'], rfid_id = str(uuid.uuid4()), name= data['name'])
    db.session.add(new_student)
    db.session.commit()

    return jsonify({'message': 'Student registered!'})

# This is used to add a book to the library database. Also performed by the admins.
@app.route('/book', methods=['POST'])
def post_book():
    data = request.get_json()

    new_book = Book(barcode_id = str(uuid.uuid4()), name = data['name'], tag=False)
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Book Registered'})

# This is used to register the students through the app. The student has to enter name, reg_no, and password as details.
@app.route('/register', methods=['PUT'])
def register():
    data = request.get_json()
    student = Student.query.filter_by(reg_no=data['reg_no'], name=data['name']).first()

    if not student:
        return jsonify({'message': 'Student not enrolled!'})
    if student.password:
        return jsonify({'message': 'Student already registered!'})

    hashed_password = generate_password_hash(data['password'], method='sha256')
    student.password = hashed_password
    student.num_of_books = 0
    db.session.commit()

    return jsonify({'message': 'Student registered successfully!'})

# This is used to issue the book through the app. Book can be issued only between entry and exit time.
@app.route('/issue/<book_id>', methods=['PUT'])
@token_required
def book_issue(current_user, book_id):
    book = Book.query.filter_by(barcode_id=book_id, tag=False).first()

    current_time = datetime.datetime.utcnow()
    
    # For first timers
    if current_user.last_intime is None:
        return jsonify({'message': 'Cannot return book'})
        
    if current_user.last_outtime is None:
        if not book:
            return jsonify({'message': 'Cannot return book'})
    
    # If regular student at library, or at least has come more than once. Checking if student is issuing book in library.
    if not book or ((current_time-current_user.last_intime).total_seconds()<0 or (current_user.last_intime-current_user.last_outtime).total_seconds()<0) or current_user.num_of_books == 5:
        return jsonify({'message': 'Cannot issue book'})
    
    # Assigning the book to the student
    book.assignee = current_user
    book.tag = True
    book.issued_at = current_time
    current_user.num_of_books += 1

    db.session.commit()

    return jsonify({'message': 'Book assigned successfully'})

# Similarly this is for returning the books, subject to similar conditions as in issuing the books.
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

    if not book or ((current_time-current_user.last_intime).total_seconds()<0 or (current_user.last_intime-current_user.last_outtime).total_seconds()<0) or current_user.num_of_books == 0:
        return jsonify({'message': 'Cannot return book'})

    book.assignee = None
    book.tag = False
    current_user.num_of_books -= 1

    db.session.commit()

    return jsonify({'message': 'Book returned successfully'})

# Used by the students to log in their account through the app 
@app.route('/login')
def login():
    auth = request.authorization
    
    # If authorization values are not provided
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    student = Student.query.filter_by(reg_no=auth.username).first()
    
    # If student not found in database. Can occur if not registered.
    if not student:
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

    # Generating token which has an expiry time after which student has to log in again
    if check_password_hash(student.password, auth.password):
        token = jwt.encode({'reg_no' : student.reg_no, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})

# Route to integrate the entry-exit system. Student just has to scan the rfid card, and will be allowed entry or exit.
@app.route('/entry_exit', methods=['PUT'])
def entry_exit():
    data = request.get_json()
    student = Student.query.filter_by(rfid_id=data['rfid_id']).first()
    
    # If intime is none, then student is a first timer and is entering the library for the first time.
    if student.last_intime is None:
        student.last_intime = datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'Entry'})
    
    # If student is not a first timer
    if student.last_outtime is not None:
        time_diff = student.last_outtime - student.last_intime

        if time_diff.total_seconds() > 0:
            student.last_intime = datetime.datetime.utcnow()
            db.session.commit()
            return jsonify({'status': 'Entry'})

    
    student.last_outtime = datetime.datetime.utcnow()
    
    # Checking for books issued by student between his last entry and exit times. They will be displayed on screen.
    books = Book.query.filter_by(assignee=student).all()
    book_list = []
    for book in books:
        if(student.last_outtime-book.issued_at).total_seconds() > 0 and (book.issued_at-student.last_intime).total_seconds() > 0:
            book_list.append({'name': book.name, 'barcode_id': book.barcode_id})

    db.session.commit()
    return jsonify({'status': 'Exit', 'books': book_list})