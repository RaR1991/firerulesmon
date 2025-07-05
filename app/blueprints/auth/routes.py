from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models.user import User, UserRole
from .forms import RegistrationForm, LoginForm, ResetPasswordForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # First registered user is an admin, others are viewers
        if form.username.data.lower() == 'admin':
            user = User(username=form.username.data, password_hash=hashed_password, role=UserRole.ADMIN)
        else:
            user = User(username=form.username.data, password_hash=hashed_password, role=UserRole.VIEWER)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
@login_required
def user_management():
    if current_user.role != UserRole.ADMIN:
        abort(403)
    users = User.query.all()
    return render_template('user_management.html', users=users)

@auth_bp.route('/users/promote/<int:user_id>')
@login_required
def promote_user(user_id):
    if current_user.role != UserRole.ADMIN:
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.role == UserRole.VIEWER:
        user.role = UserRole.EDITOR
    elif user.role == UserRole.EDITOR:
        user.role = UserRole.ADMIN
    db.session.commit()
    flash(f'{user.username} has been promoted.', 'success')
    return redirect(url_for('auth.user_management'))

@auth_bp.route('/users/demote/<int:user_id>')
@login_required
def demote_user(user_id):
    if current_user.role != UserRole.ADMIN:
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.role == UserRole.ADMIN:
        user.role = UserRole.EDITOR
    elif user.role == UserRole.EDITOR:
        user.role = UserRole.VIEWER
    db.session.commit()
    flash(f'{user.username} has been demoted.', 'success')
    return redirect(url_for('auth.user_management'))

@auth_bp.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != UserRole.ADMIN:
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('auth.user_management'))
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.username} has been deleted.', 'success')
    return redirect(url_for('auth.user_management'))

@auth_bp.route('/users/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def reset_password(user_id):
    if current_user.role.value != 'admin':
        abort(403)
    user = User.query.get_or_404(user_id)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_password
        db.session.commit()
        flash(f'{user.username}\'s password has been reset.', 'success')
        return redirect(url_for('auth.user_management'))
    return render_template('reset_password.html', form=form, user=user)
