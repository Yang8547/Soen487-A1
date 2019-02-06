from flask_sqlalchemy import SQLAlchemy
from main import app
from config import Config

app.config.from_object(Config)
db = SQLAlchemy(app)


def row2dict(row):
    return {c.name: str(getattr(row, c.name)) for c in row.__table__.columns}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text(), nullable=False)
    questions = db.relationship('Question', backref='user', cascade="all, delete-orphan")
    answers = db.relationship('Answer', backref='user', cascade="all, delete-orphan")

    def __repr__(self):
        return "<User {}: {}>".format(self.id, self.username)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answers = db.relationship('Answer', backref='question', cascade="all, delete-orphan")

    def __repr__(self):
        return "<Question {}: {}: {}>".format(self.id, self.title, self.content)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __repr__(self):
        return "<Answer {}: {} for question {}>".format(self.id, self.content, self.question_id)

