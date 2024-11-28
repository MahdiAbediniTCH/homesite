import os
import secrets
import jdatetime
import math
from flask import render_template, url_for, flash, redirect, request, send_from_directory, abort
from homesite import app, db, bcrypt, SITENAME
from homesite.forms import LoginForm, RegistrationForm, UploadFileForm, NewNoteForm, EditNoteForm
from homesite.models import User, Note, File
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename


@app.context_processor
def inject_variables():
    return dict(site_name=SITENAME)


@app.route('/')
def redir():
    return redirect("/home")


@app.route('/home')
@login_required
def home():
    return render_template("home.html", title="یادداشت ها", notes=Note.query.all())


@app.route('/protected/<path:filename>')
@login_required
def protected(filename):
    return send_from_directory(
        os.path.join(app.root_path, 'protected'),
        filename
    )


def jdatetime_now():
    return jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def englishify(string):
    dic = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        'ا': 'a',
        'آ': 'a',
        "ب": 'b',
        "پ": 'p', 
        "ت": 't',
        "ث": 's',
        "ج": 'j',
        "چ": 'ch',
        "ح": 'h',
        "خ": 'kh',
        "د": 'd',
        "ذ": 'z',
        "ر": 'r',
        "ز": 'z',
        "ژ": 'zh',
        "س": 's',
        "ش": 'sh',
        "ص": 's',
        "ض": 'z',
        "ط": 't',
        "ظ": 'z',
        "ع": 'a',
        "غ": 'gh',
        "ف": 'f',
        "ق": 'gh',
        "ک": 'k',
        "گ": 'g',
        "ل": 'l',
        "م": 'm',
        "ن": 'n',
        "و": 'v',
        "ه": 'h',
        "ی": 'i'
    }
    string2 = ''
    for char in string:
        if dic.get(char):
            string2 += dic.get(char)
        else:
            string2 += char
    return string2


def save_file(file, name=False):
    f_name, f_ext = os.path.splitext(file.filename)

    if name:
        filename = name
    else:
        filename = f_name
    display_filename = filename
    filename = englishify(filename)
    filename = secure_filename(filename)
    fn = filename
    dfn = display_filename
    file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'][1:], filename + f_ext)
    temp = 1
    while os.path.exists(file_path):
        fn = filename + f' ({temp})'
        dfn = display_filename + f' ({temp})'
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'][1:], fn + f_ext)
        temp += 1
    filename = fn
    display_filename = dfn
    file.save(file_path)
    if os.path.getsize(file_path) == 0:
        os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'][1:], filename))
        return False
    f = File(creator_username=current_user.username, file_name = filename + f_ext, display_name=display_filename + f_ext, 
        file_size=bytes_to_megabytes(os.path.getsize(file_path)))
    db.session.add(f)
    db.session.commit()
    return True


def remove_file(filename, delete_file=True):
    File.query.filter_by(file_name=filename).delete()
    db.session.commit()
    if delete_file:
        os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'][1:], filename))


def update_db_for_files():
    path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'][1:])
    files = [file for file in os.listdir(path) 
         if os.path.isfile(os.path.join(path, file))]
    db_files = []
    for file in File.query.all():
        db_files.append(file.file_name)
    for file in files:
        if file in db_files:
            db_files.remove(file)
        else:
            f = File(file_name=file, file_size=bytes_to_megabytes(os.path.getsize(path + '/' + file)),
                display_name=file, datetime_uploaded=jdatetime_now())
            db.session.add(f)
            db.session.commit()
    for file in db_files:
        remove_file(file, False)


def bytes_to_megabytes(b):
    return "%.2f" % (math.ceil(b / 1000000 * 100) / 100)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method == 'POST':
        json = request.json
        cmd = json['cmd']
        if cmd == 'remove_file':
            filename = json['file_name']
            if current_user.username == File.query.filter_by(file_name=filename).first().creator_username\
             or current_user.username == "admin":
                remove_file(filename)
        elif cmd == 'remove_note':
            if Note.query.get(json['note_id']).author == current_user\
             or current_user.username == "admin":
                Note.query.filter_by(id=json['note_id']).delete()
                db.session.commit()


@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if note.author != current_user:
        abort(403)
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        flash('یادداشت بروزرسانی شد!', 'success')
        return redirect(url_for('home'))
    form.title.data = note.title
    form.content.data = note.content
    return render_template('edit_note.html', title="ویرایش یادداشت", form=form)


@app.route('/files', methods=['GET', 'POST'])
@login_required
def files():
    update_db_for_files()
    form = UploadFileForm()
    files = File.query.all()
    return render_template("files.html", title="فایل ها", form=form, files=files, upload_path=app.config['UPLOAD_FOLDER'] + '/')


@app.route('/upload_files', methods=['GET', 'POST'])
@login_required
def upload_files():
    update_db_for_files()
    form = UploadFileForm()
    if form.validate_on_submit():
        if len(form.files.data) == 1:
            if save_file(form.files.data[0], form.name.data):
                flash('فایل بارگذاری شد.', 'success')
        else:
            for file in form.files.data:
                save_file(file, False)

            flash('فایل ها بارگذاری شدند.', 'success')
    return redirect(url_for('files'))


@app.route('/new_note', methods=['GET', 'POST'])
@login_required
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        post = Note(title=form.title.data, content=form.content.data, author=current_user, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('یادداشت بارگذاری شد!', 'success')
        return redirect(url_for('home'))
    return render_template('new_note.html', title='یادداشت جدید', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password, display_name=form.display_name.data)
        db.session.add(user)
        db.session.commit()
        flash('حساب کاربری ساخته شد.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='ثبت نام', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("نام کاربری یا رمز اشتباه بود، لطفا مجددا تلاش کنید.", 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', title='ورود', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))
