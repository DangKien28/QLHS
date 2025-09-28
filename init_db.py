from app import app
from models import db, User

def create_database():
    with app.app_context():
        # Xóa và tạo lại CSDL (chỉ dùng khi phát triển)
        # db.drop_all() 
        db.create_all()
        
        # Kiểm tra xem tài khoản giáo viên đã tồn tại chưa
        if not User.query.filter_by(username='teacher').first():
            print("Tạo tài khoản giáo viên mặc định...")
            # Tạo tài khoản giáo viên
            teacher_user = User(username='teacher', role='teacher')
            teacher_user.set_password('123456') # Mật khẩu mặc định
            db.session.add(teacher_user)
            db.session.commit()
            print("Tài khoản: teacher | Mật khẩu: 123456")
        else:
            print("Tài khoản giáo viên đã tồn tại.")

if __name__ == '__main__':
    create_database()