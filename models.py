from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Bảng lưu thông tin người dùng (giáo viên và học sinh)"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='student') # 'teacher' or 'student'

    # Liên kết một-một với Student
    student = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        """Tạo hash cho mật khẩu"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    """Bảng lưu thông tin học sinh và điểm số"""
    id = db.Column(db.Integer, primary_key=True)
    ho_ten = db.Column(db.String(100), nullable=False)
    ngay_sinh = db.Column(db.Date, nullable=True)
    dia_chi = db.Column(db.String(200), nullable=True)
    
    # Điểm số
    diem_toan = db.Column(db.Float, nullable=True, default=0)
    diem_van = db.Column(db.Float, nullable=True, default=0)
    diem_anh = db.Column(db.Float, nullable=True, default=0)

    # Khóa ngoại liên kết với bảng User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    @property
    def diem_trung_binh(self):
        """Tính điểm trung bình"""
        scores = [s for s in [self.diem_toan, self.diem_van, self.diem_anh] if s is not None]
        if not scores:
            return 0
        return round(sum(scores) / len(scores), 2)

    def __repr__(self):
        return f'<Student {self.ho_ten}>'