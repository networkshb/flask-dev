from flask import render_template, redirect, request, url_for, flash
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, EmailChangeForm
from flask_login import login_required, logout_user, login_user, current_user
from ..email import send_email
from ..models import User
from .. import db

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            print(next)
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,
                username = form.username.data,
                password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                  'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if user.verify_password(form.old_password.data):
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Your password has been updated')
            return redirect(url_for('auth.login'))
        else:
            flash('Passwold not correct')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET','POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            token = user.generate_reset_password_token()
            send_email(user.email, '修改密码', \
                    'auth/email/reset_password', user=user, token=token)
            flash('A reset password email has been sent to you by email.')
        else:
            flash('not found')
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET','POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.password_reset(token, form.password.data):
            db.session.commit()
            flash('Your password update')
            redirect(url_for('auth.login'))
        else:
            flash('error')
    return render_template('auth/reset_password.html',form=form)

@auth.route('/change-email',  methods=['GET','POST'])
@login_required
def change_email():
    form = EmailChangeForm()
    if form.validate_on_submit():
        new_email = form.data.get('email')
        token = current_user.generate_email_change_token(new_email)
        send_email(new_email, '重置邮箱地址', 'auth/email/change_email', user=current_user, token = token)
        flash('a change-email email has sent to you by email')
        redirect(url_for('main.index'))
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>', methods=['GET'])
def change_email_confirm(token):
    if current_user.change_email(token):
        db.session.commit()
        redirect('auth/login.html')
    return render_template('auth/unconfirmed.html')



@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

