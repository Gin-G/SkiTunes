from flask_login import UserMixin
from skitunes import db

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    user_id = db.Column('id', db.String(100), primary_key = True)
    name = db.Column('Name', db.String(100))
    email = db.Column('Email', db.String(100))
    profile_pic = db.Column('Picture', db.String(100))
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def get_id(self):
        return(self.user_id)
        
    def __init__(self, user_id, name, email, profile_pic, pwd):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic   
        self.pwd = pwd

    @staticmethod
    def get(user_id):
        user = User.query.filter(User.user_id == user_id).first()
        if not user:
            return None
        return user

    @staticmethod
    def create(user_id, name, email, profile_pic, pwd):
        user = User(user_id=user_id, name=name, email=email, profile_pic=profile_pic, pwd=pwd)
        db.session.add(user)
        db.session.commit()