from homesite import db, bcrypt
from homesite.models import User, File, Note


def show_users():
    for user in User.query.all():
        print(user)


def show_files():
    for file in File.query.all():
        print(file)


def show_notes():
    for note in Note.query.all():
        print(note)

        
def remove_user(username):
    User.query.filter_by(username=username).delete()


def commit():
    db.session.commit()


def change_password(username, password):
    User.query.filter_by(username=username).first().password = bcrypt.generate_password_hash(password).decode('utf-8')
    
show_users()
print()
show_files()
print()
show_notes()
input()
print('finished')
