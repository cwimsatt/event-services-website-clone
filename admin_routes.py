import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Event, Category
from werkzeug.utils import secure_filename

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    events = Event.query.all()
    return render_template('admin/dashboard.html', events=events)

@admin.route('/admin/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password')
    return render_template('admin/login.html')

@admin.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@admin.route('/admin/event/<int:id>/delete-file/<file_type>', methods=['POST'])
@login_required
def delete_file(id, file_type):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(id)

    try:
        if file_type == 'image':
            if event.image_path:
                file_path = os.path.join(current_app.static_folder, event.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                event.image_path = None
                flash('Image deleted successfully')
        elif file_type == 'video':
            if event.video_path:
                file_path = os.path.join(current_app.static_folder, event.video_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                event.video_path = None
                flash('Video deleted successfully')

        db.session.commit()
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')

    return redirect(url_for('admin.edit_event', id=id))

@admin.route('/admin/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    categories = Category.query.all()

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        if not category_id or not Category.query.get(category_id):
            flash('Please select a valid category')
            return render_template('admin/event_form.html', categories=categories)

        try:
            # Handle image upload
            image = request.files['image']
            Event.validate_image(image)
            image_filename = secure_filename(image.filename)
            image_path = os.path.join('uploads', 'images', image_filename)
            image.save(os.path.join(current_app.static_folder, image_path))

            # Handle optional video upload
            video_path = None
            if 'video' in request.files and request.files['video'].filename:
                video = request.files['video']
                Event.validate_video(video)
                video_filename = secure_filename(video.filename)
                video_path = os.path.join('uploads', 'videos', video_filename)
                video.save(os.path.join(current_app.static_folder, video_path))

            event = Event(
                title=request.form.get('title'),
                category_id=category_id,
                description=request.form.get('description'),
                image_path=image_path,
                video_path=video_path
            )
        except ValueError as e:
            flash(str(e))
            return render_template('admin/event_form.html', categories=categories)
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/event_form.html', categories=categories)

@admin.route('/admin/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        if not category_id or not Category.query.get(category_id):
            flash('Please select a valid category')
            return render_template('admin/event_form.html', event=event, categories=categories)

        try:
            event.title = request.form.get('title')
            event.category_id = category_id
            event.description = request.form.get('description')

            # Handle image upload if new image is provided
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                Event.validate_image(image)
                image_filename = secure_filename(image.filename)
                image_path = os.path.join('uploads', 'images', image_filename)
                image.save(os.path.join(current_app.static_folder, image_path))
                # Remove old image if exists
                if event.image_path:
                    old_image_path = os.path.join(current_app.static_folder, event.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                event.image_path = image_path

            # Handle video upload if new video is provided
            if 'video' in request.files and request.files['video'].filename:
                video = request.files['video']
                Event.validate_video(video)
                video_filename = secure_filename(video.filename)
                video_path = os.path.join('uploads', 'videos', video_filename)
                video.save(os.path.join(current_app.static_folder, video_path))
                # Remove old video if exists
                if event.video_path:
                    old_video_path = os.path.join(current_app.static_folder, event.video_path)
                    if os.path.exists(old_video_path):
                        os.remove(old_video_path)
                event.video_path = video_path

        except ValueError as e:
            flash(str(e))
            return render_template('admin/event_form.html', event=event, categories=categories)
        db.session.commit()
        flash('Event updated successfully')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/event_form.html', event=event, categories=categories)

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