from flask import render_template, session, redirect, url_for, current_app, flash
from .. import db
from ..models import User, Permission, Role
from ..email import send_email
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    return render_template('user.html', user= user)

@main.route('/edit-profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        print(form)
        print(current_user)
        current_user.name = form.name.data
        current_user.location= form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('update success.')
        return redirect(url_for('main.user', username = current_user.username))
    form.name.data = current_user.name
    print(current_user.name)
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit-profile.html', form = form)

@main.route('/edit-profile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.name = form.name.data
        user.location= form.location.data
        user.about_me = form.about_me.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)

        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit-profile.html', form=form, user=user)

@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return "For Administrators only!"

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderate_only():
    return "For comment moderators!"

