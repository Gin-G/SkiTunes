from flask_login import UserMixin
from skitunes import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    user_id = db.Column('id', db.String(100), primary_key=True)
    name = db.Column('Name', db.String(100))
    email = db.Column('Email', db.String(100), unique=True)
    profile_pic = db.Column('Picture', db.String(100))
    pwd = db.Column(db.String(300), nullable=False)

    def get_id(self):
        return self.user_id
        
    def __init__(self, user_id, name, email, profile_pic, pwd):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.pwd = generate_password_hash(pwd)  # Hash the password

    def check_password(self, password):
        return check_password_hash(self.pwd, password)

    @staticmethod
    def get(user_id):
        user = User.query.filter(User.user_id == user_id).first()
        if not user:
            return None
        return user
    
    @classmethod
    def generate_next_user_id(cls):
        # Find the maximum current user ID and increment
        max_id = db.session.query(func.max(cls.user_id)).scalar()
        
        if max_id is None:
            # First user
            return '000001'
        
        # Increment the ID, padding with zeros
        next_id = str(int(max_id) + 1).zfill(6)
        return next_id

    @classmethod
    def create(cls, user_id, name, email, profile_pic, pwd):
        # Remove the user_id generation since we're now passing it in
        existing_user = cls.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError('Email already registered')
        
        print("Creating user with:")
        print(f"User ID: {user_id}")
        print(f"Email: {email}")
        
        user = cls(
            user_id=user_id, 
            name=name, 
            email=email, 
            profile_pic=profile_pic, 
            pwd=pwd
        )
        
        print(f"Generated password hash: {user.pwd}")
        
        db.session.add(user)
        db.session.commit()
        
        return user