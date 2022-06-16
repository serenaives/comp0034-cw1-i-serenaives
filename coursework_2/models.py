from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from coursework_2.extensions import db
from coursework_2.extensions import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    highscore = db.Column(db.Integer)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def update_highscore(self, current_score):
        if current_score > self.highscore:
            User.query.filter_by(id=self.id).update(dict(highscore=current_score))
            db.session.commit()
            return True
        else:
            return False


    def __repr__(self):
        return '<User {}>'.format(self.username)


class Questions(db.Model):
    q_id = db.Column(db.Integer, primary_key=True)
    ques = db.Column(db.String(350), unique=True)
    option_a = db.Column(db.String(100))
    option_b = db.Column(db.String(100))
    option_c = db.Column(db.String(100))
    ans = db.Column(db.String(100))

    def __repr__(self):
        return '<Question: {}>'.format(self.ques)
