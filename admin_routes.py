from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Event, Category

admin = Blueprint('admin', __name__)

@admin.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password')
    return render_template('admin/login.html')

@admin.route('/admin/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    events = Event.query.all()
    return render_template('admin/dashboard.html', events=events)

@admin.route('/admin/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            image_url=request.form.get('image_url'),
            video_url=request.form.get('video_url')
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/event_form.html')

@admin.route('/admin/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.category = request.form.get('category')
        event.description = request.form.get('description')
        event.image_url = request.form.get('image_url')
        event.video_url = request.form.get('video_url')
        db.session.commit()
        flash('Event updated successfully')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/event_form.html', event=event)

@admin.route('/admin/event/<int:id>/delete', methods=['POST'])
@login_required
def delete_event(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully')
    return redirect(url_for('admin.dashboard'))

@admin.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@admin.route('/admin/categories')
@login_required
def list_categories():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/admin/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        category = Category(
            name=request.form.get('name'),
            slug=request.form.get('name').lower().replace(' ', '-'),
            description=request.form.get('description')
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully')
        return redirect(url_for('admin.list_categories'))
    
    return render_template('admin/category_form.html')

@admin.route('/admin/category/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('name').lower().replace(' ', '-')
        category.description = request.form.get('description')
        db.session.commit()
        flash('Category updated successfully')
        return redirect(url_for('admin.list_categories'))
    
    return render_template('admin/category_form.html', category=category)

@admin.route('/admin/category/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(id)
    if Event.query.filter_by(category_id=category.id).first():
        flash('Cannot delete category that has events')
        return redirect(url_for('admin.list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully')
    return redirect(url_for('admin.list_categories'))