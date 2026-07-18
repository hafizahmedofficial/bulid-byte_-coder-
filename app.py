from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Association table for student-class relationship
student_class = db.Table('student_class',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True)
)

# Models
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    classes = db.relationship('Class', backref='teacher', lazy=True)
    students = db.relationship('Student', backref='created_by', lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    students = db.relationship('Student', secondary=student_class, lazy='subquery',
                              backref=db.backref('classes', lazy=True))
    attendance_records = db.relationship('Attendance', backref='class_obj', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'class_id', 'date', name='unique_attendance'),)

# Decorators
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'teacher':
            flash('Please login as a teacher to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please login as a student to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('user_type') == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if user_type == 'teacher':
            user = Teacher.query.filter_by(username=username).first()
        else:
            user = Student.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_type'] = user_type
            session['user_name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            if user_type == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        
        if Teacher.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
        
        if Teacher.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        
        teacher = Teacher(
            username=username,
            password_hash=generate_password_hash(password),
            name=name,
            email=email
        )
        db.session.add(teacher)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Teacher Routes
@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    teacher = Teacher.query.get(session['user_id'])
    classes = Class.query.filter_by(teacher_id=teacher.id).all()
    students = Student.query.all()
    
    # Get today's attendance stats
    today = date.today()
    total_attendance_today = Attendance.query.join(Class).filter(
        Class.teacher_id == teacher.id,
        Attendance.date == today
    ).count()
    
    present_today = Attendance.query.join(Class).filter(
        Class.teacher_id == teacher.id,
        Attendance.date == today,
        Attendance.status == 'present'
    ).count()
    
    return render_template('teacher/dashboard.html', 
                          teacher=teacher,
                          classes=classes, 
                          students=students,
                          total_attendance=total_attendance_today,
                          present_today=present_today)

@app.route('/teacher/classes')
@teacher_required
def teacher_classes():
    teacher = Teacher.query.get(session['user_id'])
    classes = Class.query.filter_by(teacher_id=teacher.id).all()
    return render_template('teacher/classes.html', classes=classes)

@app.route('/teacher/class/create', methods=['GET', 'POST'])
@teacher_required
def create_class():
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        description = request.form.get('description')
        
        new_class = Class(
            name=name,
            subject=subject,
            description=description,
            teacher_id=session['user_id']
        )
        db.session.add(new_class)
        db.session.commit()
        
        flash('Class created successfully!', 'success')
        return redirect(url_for('teacher_classes'))
    
    return render_template('teacher/create_class.html')

@app.route('/teacher/class/<int:class_id>')
@teacher_required
def view_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher_classes'))
    
    # Get all students not in this class
    all_students = Student.query.all()
    available_students = [s for s in all_students if s not in class_obj.students]
    
    return render_template('teacher/view_class.html', 
                          class_obj=class_obj, 
                          available_students=available_students)

@app.route('/teacher/class/<int:class_id>/add_student', methods=['POST'])
@teacher_required
def add_student_to_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    student_id = request.form.get('student_id')
    student = Student.query.get_or_404(student_id)
    
    if student not in class_obj.students:
        class_obj.students.append(student)
        db.session.commit()
        flash(f'{student.name} added to class!', 'success')
    
    return redirect(url_for('view_class', class_id=class_id))

@app.route('/teacher/class/<int:class_id>/remove_student/<int:student_id>', methods=['POST'])
@teacher_required
def remove_student_from_class(class_id, student_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.get_or_404(student_id)
    
    if student in class_obj.students:
        class_obj.students.remove(student)
        db.session.commit()
        flash(f'{student.name} removed from class!', 'success')
    
    return redirect(url_for('view_class', class_id=class_id))

@app.route('/teacher/class/<int:class_id>/delete', methods=['POST'])
@teacher_required
def delete_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher_classes'))
    
    # Delete attendance records first
    Attendance.query.filter_by(class_id=class_id).delete()
    db.session.delete(class_obj)
    db.session.commit()
    
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('teacher_classes'))

@app.route('/teacher/students')
@teacher_required
def teacher_students():
    students = Student.query.all()
    return render_template('teacher/students.html', students=students)

@app.route('/teacher/student/create', methods=['GET', 'POST'])
@teacher_required
def create_student():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        roll_number = request.form.get('roll_number')
        
        if Student.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('create_student'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('create_student'))
        
        if Student.query.filter_by(roll_number=roll_number).first():
            flash('Roll number already exists.', 'error')
            return redirect(url_for('create_student'))
        
        student = Student(
            username=username,
            password_hash=generate_password_hash(password),
            name=name,
            email=email,
            roll_number=roll_number,
            teacher_id=session['user_id']
        )
        db.session.add(student)
        db.session.commit()
        
        flash('Student created successfully!', 'success')
        return redirect(url_for('teacher_students'))
    
    return render_template('teacher/create_student.html')

@app.route('/teacher/student/<int:student_id>/delete', methods=['POST'])
@teacher_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Delete attendance records first
    Attendance.query.filter_by(student_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()
    
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('teacher_students'))

@app.route('/teacher/attendance')
@teacher_required
def teacher_attendance():
    classes = Class.query.filter_by(teacher_id=session['user_id']).all()
    return render_template('teacher/attendance.html', classes=classes)

@app.route('/teacher/attendance/mark/<int:class_id>', methods=['GET', 'POST'])
@teacher_required
def mark_attendance(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher_attendance'))
    
    attendance_date = request.args.get('date', date.today().isoformat())
    attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
    
    if request.method == 'POST':
        attendance_date = datetime.strptime(request.form.get('attendance_date'), '%Y-%m-%d').date()
        
        for student in class_obj.students:
            status = request.form.get(f'status_{student.id}')
            if status:
                # Check if record exists
                existing = Attendance.query.filter_by(
                    student_id=student.id,
                    class_id=class_id,
                    date=attendance_date
                ).first()
                
                if existing:
                    existing.status = status
                    existing.marked_at = datetime.utcnow()
                else:
                    attendance = Attendance(
                        student_id=student.id,
                        class_id=class_id,
                        date=attendance_date,
                        status=status
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('mark_attendance', class_id=class_id, date=attendance_date.isoformat()))
    
    # Get existing attendance for the date
    existing_attendance = {}
    for record in Attendance.query.filter_by(class_id=class_id, date=attendance_date).all():
        existing_attendance[record.student_id] = record.status
    
    return render_template('teacher/mark_attendance.html', 
                          class_obj=class_obj, 
                          attendance_date=attendance_date,
                          existing_attendance=existing_attendance)

@app.route('/teacher/reports')
@teacher_required
def teacher_reports():
    classes = Class.query.filter_by(teacher_id=session['user_id']).all()
    return render_template('teacher/reports.html', classes=classes)

@app.route('/teacher/reports/<int:class_id>')
@teacher_required
def class_report(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('teacher_reports'))
    
    # Get attendance stats for each student
    student_stats = []
    for student in class_obj.students:
        total = Attendance.query.filter_by(student_id=student.id, class_id=class_id).count()
        present = Attendance.query.filter_by(student_id=student.id, class_id=class_id, status='present').count()
        absent = Attendance.query.filter_by(student_id=student.id, class_id=class_id, status='absent').count()
        late = Attendance.query.filter_by(student_id=student.id, class_id=class_id, status='late').count()
        
        percentage = (present / total * 100) if total > 0 else 0
        
        student_stats.append({
            'student': student,
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': round(percentage, 1)
        })
    
    return render_template('teacher/class_report.html', 
                          class_obj=class_obj, 
                          student_stats=student_stats)

# Student Routes
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student = Student.query.get(session['user_id'])
    
    # Get attendance stats
    total_records = Attendance.query.filter_by(student_id=student.id).count()
    present_count = Attendance.query.filter_by(student_id=student.id, status='present').count()
    absent_count = Attendance.query.filter_by(student_id=student.id, status='absent').count()
    late_count = Attendance.query.filter_by(student_id=student.id, status='late').count()
    
    overall_percentage = (present_count / total_records * 100) if total_records > 0 else 0
    
    # Get recent attendance
    recent_attendance = Attendance.query.filter_by(student_id=student.id)\
        .order_by(Attendance.date.desc()).limit(10).all()
    
    return render_template('student/dashboard.html',
                          student=student,
                          total_records=total_records,
                          present_count=present_count,
                          absent_count=absent_count,
                          late_count=late_count,
                          overall_percentage=round(overall_percentage, 1),
                          recent_attendance=recent_attendance)

@app.route('/student/classes')
@student_required
def student_classes():
    student = Student.query.get(session['user_id'])
    return render_template('student/classes.html', student=student)

@app.route('/student/attendance/<int:class_id>')
@student_required
def student_attendance(class_id):
    student = Student.query.get(session['user_id'])
    class_obj = Class.query.get_or_404(class_id)
    
    if class_obj not in student.classes:
        flash('Access denied.', 'error')
        return redirect(url_for('student_classes'))
    
    # Get all attendance records for this class
    attendance_records = Attendance.query.filter_by(
        student_id=student.id,
        class_id=class_id
    ).order_by(Attendance.date.desc()).all()
    
    # Calculate stats
    total = len(attendance_records)
    present = sum(1 for r in attendance_records if r.status == 'present')
    percentage = (present / total * 100) if total > 0 else 0
    
    return render_template('student/attendance.html',
                          class_obj=class_obj,
                          attendance_records=attendance_records,
                          total=total,
                          present=present,
                          percentage=round(percentage, 1))

# API endpoints for AJAX
@app.route('/api/attendance/stats/<int:class_id>')
@teacher_required
def api_attendance_stats(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get last 7 days stats
    from datetime import timedelta
    stats = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        total = Attendance.query.filter_by(class_id=class_id, date=day).count()
        present = Attendance.query.filter_by(class_id=class_id, date=day, status='present').count()
        stats.append({
            'date': day.strftime('%b %d'),
            'present': present,
            'total': total
        })
    
    return jsonify(stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)