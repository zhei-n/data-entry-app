from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
import csv
import os
from io import StringIO, BytesIO
from functools import wraps
from datetime import datetime, timedelta
from models import db, Item, User  # Add User model
from forms import LoginForm, ItemForm

app = Flask(__name__)

# Improved Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///items.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32))
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db.init_app(app)
csrf = CSRFProtect(app)

# ============ HELPERS ============

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_paginated_items(search_query='', page=1, per_page=10, sort='id', direction='asc'):
    """Helper function for consistent pagination logic"""
    query = Item.query
    
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            (Item.name.ilike(like)) |
            (Item.brand.ilike(like)) |
            (Item.model.ilike(like)) |
            (Item.location.ilike(like)) |
            (Item.serial_number.ilike(like)) |
            (Item.owner.ilike(like)) |
            (Item.status.ilike(like))
        )
    
    # Sorting with validation
    valid_sorts = ['id', 'name', 'brand', 'model', 'location', 'serial_number', 'owner', 'status']
    sort = sort if sort in valid_sorts else 'id'
    sort_column = getattr(Item, sort)
    sort_column = sort_column.desc() if direction == 'desc' else sort_column.asc()
    
    query = query.order_by(sort_column)
    return query.paginate(page=page, per_page=per_page, error_out=False)


def validate_csv_structure(file):
    """Validate CSV has required columns"""
    required_columns = {'Name', 'Brand', 'Model', 'Location', 'Serial Number', 'Owner', 'Status'}
    try:
        file.stream.seek(0)
        sample = file.stream.read(1024).decode('utf-8')
        file.stream.seek(0)
        reader = csv.DictReader(StringIO(sample))
        headers = set(reader.fieldnames or [])
        return required_columns.issubset(headers)
    except Exception:
        return False


# ============ ROUTES ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with database authentication"""
    if session.get('logged_in'):
        return redirect(url_for('index'))
    
    form = LoginForm()
    error = None
    
    if form.validate_on_submit():
        try:
            # Database user lookup
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.is_active and user.check_password(form.password.data):
                session['logged_in'] = True
                session['username'] = form.username.data
                session['user_id'] = user.id
                session.permanent = True
                
                # Update last login time
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid username or password.'
                flash(error, 'danger')
        except Exception as e:
            error = 'An error occurred during login. Please try again.'
            flash(error, 'danger')
            app.logger.error(f'Login error: {str(e)}')
    
    return render_template('login.html', form=form, error=error)


@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Main page with item listing and add functionality"""
    form = ItemForm()
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'asc')
    
    # Handle form submission (add item)
    if form.validate_on_submit():
        try:
            new_item = Item(
                name=form.name.data,
                brand=form.brand.data,
                model=form.model.data,
                location=form.location.data,
                serial_number=form.serial_number.data,
                owner=form.owner.data,
                status=form.status.data
            )
            db.session.add(new_item)
            db.session.commit()
            flash('Item added successfully!', 'success')
            
            # Preserve query parameters in redirect
            return redirect(url_for('index', 
                                  q=search_query, 
                                  page=page, 
                                  sort=sort, 
                                  direction=direction))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {str(e)}', 'danger')
    
    # Get paginated items
    pagination = get_paginated_items(search_query, page, 10, sort, direction)
    items = pagination.items
    
    return render_template('index.html', 
                         items=items, 
                         form=form, 
                         pagination=pagination, 
                         search_query=search_query)


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Edit an existing item"""
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'asc')
    
    if form.validate_on_submit():
        try:
            form.populate_obj(item)
            db.session.commit()
            flash('Item updated successfully!', 'success')
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                pagination = get_paginated_items(search_query, page, 10, sort, direction)
                return render_template('index.html', 
                                     items=pagination.items, 
                                     form=ItemForm(), 
                                     pagination=pagination, 
                                     search_query=search_query)
            
            return redirect(url_for('index', 
                                  q=search_query, 
                                  page=page,
                                  sort=sort,
                                  direction=direction))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating item: {str(e)}', 'danger')
    
    # Handle validation errors for AJAX
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'errors': form.errors}), 400
    
    return render_template('edit.html', item=item, form=form)


@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    """Delete a single item"""
    item = Item.query.get_or_404(item_id)
    
    try:
        db.session.delete(item)
        db.session.commit()
        
        # AJAX response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Item deleted successfully'})
        
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'Error deleting item: {str(e)}', 'danger')
    
    # Preserve query parameters
    return redirect(url_for('index', 
                          q=request.args.get('q', ''), 
                          page=request.args.get('page', 1)))


@app.route('/bulk_delete', methods=['POST'])
@login_required
def bulk_delete():
    """Delete multiple items"""
    ids = request.form.getlist('item_ids')
    
    if not ids:
        flash('No items selected for deletion.', 'warning')
        return redirect(url_for('index'))
    
    try:
        count = Item.query.filter(Item.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        flash(f'{count} item(s) deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting items: {str(e)}', 'danger')
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return '', 204
    
    return redirect(url_for('index'))


@app.route('/export', methods=['GET'])
@login_required
def export_items():
    """Export all items to CSV"""
    try:
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Name', 'Brand', 'Model', 'Location', 'Serial Number', 'Owner', 'Status'])
        
        for item in Item.query.all():
            cw.writerow([
                item.name, 
                item.brand, 
                item.model, 
                item.location, 
                item.serial_number, 
                item.owner, 
                item.status
            ])
        
        output = BytesIO(si.getvalue().encode('utf-8'))
        output.seek(0)
        
        filename = f'items_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting items: {str(e)}', 'danger')
        return redirect(url_for('index'))


@app.route('/import', methods=['POST'])
@login_required
def import_items():
    """Import items from CSV file"""
    file = request.files.get('file')
    
    if not file or not file.filename.endswith('.csv'):
        flash('Please upload a valid CSV file.', 'danger')
        return redirect(url_for('index'))
    
    # Validate CSV structure
    if not validate_csv_structure(file):
        flash('CSV file is missing required columns.', 'danger')
        return redirect(url_for('index'))
    
    try:
        file.stream.seek(0)
        content = file.stream.read().decode('utf-8')
        reader = csv.DictReader(StringIO(content))
        
        count = 0
        for row in reader:
            item = Item(
                name=row['Name'].strip(),
                brand=row['Brand'].strip(),
                model=row['Model'].strip(),
                location=row['Location'].strip(),
                serial_number=row['Serial Number'].strip(),
                owner=row['Owner'].strip(),
                status=row['Status'].strip()
            )
            db.session.add(item)
            count += 1
        
        db.session.commit()
        flash(f'{count} items imported successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing items: {str(e)}', 'danger')
    
    return redirect(url_for('index'))


@app.route('/item/<int:item_id>', methods=['GET'])
@login_required
def get_item_detail(item_id):
    """Get item details (API endpoint)"""
    item = Item.query.get_or_404(item_id)
    return jsonify({
        'success': True,
        'item': {
            'id': item.id,
            'name': item.name,
            'brand': item.brand,
            'model': item.model,
            'location': item.location,
            'serial_number': item.serial_number,
            'owner': item.owner,
            'status': item.status
        }
    })


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Use environment variable for debug mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)