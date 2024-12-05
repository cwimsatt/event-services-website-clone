from flask import render_template, request, flash, redirect, url_for, current_app
from app import app, db
from models import Event, Testimonial, Contact, Category

@app.route('/')
def index():
    featured_events = Event.query.limit(6).all()
    testimonials = Testimonial.query.limit(3).all()
    return render_template('index.html', events=featured_events, testimonials=testimonials)

@app.route('/portfolio')
def portfolio():
    categories = Category.query.all()
    category_id = request.args.get('category_id', 'all')
    
    # Log image paths for debugging
    current_app.logger.info("Loading portfolio images...")
    
    if category_id != 'all':
        events = Event.query.filter_by(category_id=category_id).all()
    else:
        events = Event.query.all()
    
    # Debug log each event's image path
    for event in events:
        current_app.logger.info(f"Event {event.title}: Image path = {event.image_path}")
    
    return render_template('portfolio.html', 
                         events=events, 
                         categories=categories, 
                         active_category=category_id)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        contact = Contact(
            name=request.form['name'],
            email=request.form['email'],
            message=request.form['message']
        )
        db.session.add(contact)
        db.session.commit()
        flash('Thank you for your message! We will get back to you soon.')
        return redirect(url_for('contact'))
    return render_template('contact.html')
