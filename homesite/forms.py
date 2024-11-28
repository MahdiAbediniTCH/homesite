from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, MultipleFileField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length, Optional
from homesite.models import User
from homesite import SIGNUP_KEY


class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(message="این کادر نمیتواند خالی باشد")])
    password = PasswordField('رمز عبور', validators=[DataRequired(message="این کادر نمیتواند خالی باشد")])
    submit = SubmitField('ورود')


class RegistrationForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(message="این کادر نمیتواند خالی باشد"), Length(min=2, max=20, message="نام کاربری باید حداقل 2 و حداکثر 20 کاراکتر باشد")])
    display_name = StringField('نام نمایشی (اختیاری)', validators=[Optional()])
    password = PasswordField('رمز عبور', validators=[DataRequired(message="این کادر نمیتواند خالی باشد")])
    confirm_password = PasswordField('تکرار رمز عبور', validators=[DataRequired(message="این کادر نمیتواند خالی باشد"), EqualTo('password', message="مقدار وارد شده با رمز عبور یکسان نیست")])
    signup_key = PasswordField('کلید ثبت نام', )
    submit = SubmitField('ثبت نام')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('نام کاربری تکراری است')

    def validate_signup_key(self, signup_key):
        if signup_key.data != SIGNUP_KEY:
            raise ValidationError('کلید ثبت نام نادرست است')


class UploadFileForm(FlaskForm):
    name = StringField('نام فایل (اختیاری)')
    files = MultipleFileField('انتخاب فایل', validators=[DataRequired(message="لطفا حداقل یک فایل را انتخاب کنید")])
    submit = SubmitField('بارگذاری')


class NewNoteForm(FlaskForm):
    title = StringField('تیتر (اختیاری)')
    content = TextAreaField('متن', validators=[DataRequired(message="این کادر نمیتواند خالی باشد")])
    submit = SubmitField('بارگذاری')


class EditNoteForm(FlaskForm):
    title = StringField('تیتر')
    content = TextAreaField('متن', validators=[DataRequired(message="این کادر نمیتواند خالی باشد")])
    submit = SubmitField('بروزرسانی')