from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify, abort, make_response
from flask_wtf.csrf import CSRFProtect
import csv
from io import StringIO
from functools import wraps
from models import db, Item
from forms import LoginForm, ItemForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-very-secret-key'  # Change this to a secure random value!
db.init_app(app)
csrf = CSRFProtect(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        # Demo: hardcoded username/password
        if form.username.data == 'admin' and form.password.data == 'admin':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password.'
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Add this decorator to require login for protected routes ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = ItemForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('q', '').strip()  # Always use current query param
    sort = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'asc')
    # Remove session-based page memory as well for clarity
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
    # Sorting
    sort_column = getattr(Item, sort, Item.id)
    if direction == 'desc':
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()
    query = query.order_by(sort_column)
    if form.validate_on_submit():
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
        # Preserve search, page, sort, direction in redirect
        args = {}
        if search_query:
            args['q'] = search_query
        if page != 1:
            args['page'] = page
        if sort:
            args['sort'] = sort
        if direction:
            args['direction'] = direction
        return redirect(url_for('index', **args))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    return render_template('index.html', items=items, form=form, pagination=pagination, search_query=search_query)

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            per_page = 10
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
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            items = pagination.items
            return render_template('index.html', items=items, form=ItemForm(), pagination=pagination, search_query=search_query)
        else:
            args = {}
            if search_query:
                args['q'] = search_query
            if page != 1:
                args['page'] = page
            return redirect(url_for('index', **args))
    if request.method == 'GET':
        return render_template('edit.html', item=item, form=form)
    # If POST but not valid, return errors (AJAX or not)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        per_page = 10
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
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination.items
        return render_template('index.html', items=items, form=form, pagination=pagination, search_query=search_query)
    return render_template('edit.html', item=item, form=form)

@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    # AJAX request: return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    # Normal request: redirect
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    args = {}
    if search_query:
        args['q'] = search_query
    if page != 1:
        args['page'] = page
    return redirect(url_for('index', **args))

@app.route('/bulk_delete', methods=['POST'])
@login_required
def bulk_delete():
    ids = request.form.getlist('item_ids')
    if not ids:
        flash('No items selected for deletion.', 'warning')
        return redirect(url_for('index'))
    Item.query.filter(Item.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    flash(f'{len(ids)} item(s) deleted.', 'success')
    return ('', 204) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else redirect(url_for('index'))

@app.route('/export', methods=['GET'])
@login_required
def export_items():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Name', 'Brand', 'Model', 'Location', 'Serial Number', 'Owner', 'Status'])
    for item in Item.query.all():
        cw.writerow([item.name, item.brand, item.model, item.location, item.serial_number, item.owner, item.status])
    si.seek(0)
    from io import BytesIO
    output = BytesIO(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'items_export_{__import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/import', methods=['POST'])
@login_required
def import_items():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.csv'):
        flash('Please upload a valid CSV file.', 'danger')
        return redirect(url_for('index'))
    reader = csv.DictReader(StringIO(file.stream.read().decode('utf-8')))
    for row in reader:
        item = Item(
            name=row['Name'],
            brand=row['Brand'],
            model=row['Model'],
            location=row['Location'],
            serial_number=row['Serial Number'],
            owner=row['Owner'],
            status=row['Status']
        )
        db.session.add(item)
    db.session.commit()
    flash('Items imported successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/item/<int:item_id>', methods=['GET'])
@csrf.exempt
@login_required
def get_item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return {
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
    }

@app.after_request
def add_header(response):
    # Prevent caching of authenticated pages
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
