from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Student
from datetime import datetime
import os

# --- Cấu hình ứng dụng ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key' # Thay bằng một chuỗi bí mật thật sự
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-fallback-key')

# --- Khởi tạo các tiện ích ---
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Chuyển hướng đến trang login nếu chưa đăng nhập

@login_manager.user_loader
def load_user(user_id):
    """Tải người dùng từ ID"""
    return User.query.get(int(user_id))

# --- Các Route (đường dẫn URL) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            # Chuyển hướng dựa trên vai trò
            if user.role == 'teacher':
                return redirect(url_for('dashboard'))
            else:
                # Sẽ làm sau: trang của học sinh
                return redirect(url_for('dashboard')) 
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Đăng xuất"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Trang quản lý chính"""
    if current_user.role == 'teacher':
        students = Student.query.all()
        return render_template('dashboard.html', students=students)
    else:
        # Nếu là học sinh, chỉ xem thông tin của mình
        student = current_user.student
        # Chúng ta sẽ tạo template `student_view.html` sau
        return render_template('student_view.html', student=student)

# --- Chức năng quản lý học sinh (Dành cho giáo viên) ---

@app.route('/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'teacher':
        flash('Bạn không có quyền truy cập chức năng này.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ho_ten = request.form.get('ho_ten')
        ngay_sinh_str = request.form.get('ngay_sinh')
        dia_chi = request.form.get('dia_chi')
        username = request.form.get('username')
        password = request.form.get('password')

        # Kiểm tra username đã tồn tại chưa
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập này đã tồn tại.', 'warning')
            return render_template('student_form.html', action='add')
        
        # Tạo user mới cho học sinh
        new_user = User(username=username, role='student')
        new_user.set_password(password)

        # Tạo học sinh mới
        new_student = Student(
            ho_ten=ho_ten,
            dia_chi=dia_chi,
            user=new_user # Liên kết học sinh với user
        )
        if ngay_sinh_str:
            new_student.ngay_sinh = datetime.strptime(ngay_sinh_str, '%Y-%m-%d').date()

        # Lưu vào CSDL
        db.session.add(new_user)
        db.session.add(new_student)
        db.session.commit()

        flash('Thêm học sinh thành công!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('student_form.html', action='add')

# Các chức năng sửa, xóa sẽ được thêm vào sau

# --- Chạy ứng dụng ---
if __name__ == '__main__':
    app.run(debug=True)