import jdatetime
from homesite import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def jdatetime_now():
    return jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M")


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date_posted = db.Column(db.String(100), nullable=False, default=jdatetime_now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Note('{self.title}', '{self.date_posted}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    display_name = db.Column(db.String(20), nullable=False, default='User')
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.display_name}', '{self.image_file}')"


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_username = db.Column(db.String(20))
    file_name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(50), unique=True, nullable=False)
    file_size = db.Column(db.String(20), nullable=False)
    datetime_uploaded = db.Column(db.String(50), nullable=False, default=jdatetime_now)

    def __repr__(self):
        return f"File('{self.file_name}', '{self.display_name}', '{self.file_size}', '{self.creator_username}', '{self.datetime_uploaded}')"
