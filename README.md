# Data Entry System

A modern, dark-themed Flask web application for managing and tracking items with features like search, import/export CSV, and modal-based add/edit forms.

## Features
- User authentication (login/logout)
- Add, edit, and delete items using Bootstrap modals
- Search and sort items
- Import and export items as CSV
- Responsive, minimalist dark mode UI
- Animated particles background

## Technologies Used
- Python 3 (Flask, Flask-WTF, Flask-SQLAlchemy, WTForms)
- Bootstrap 5
- jQuery
- Font Awesome
- particles.js

## Setup & Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/data-entry-app.git
   cd data-entry-app
   ```
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install flask flask-wtf flask-sqlalchemy
   ```
   Or, if you have a `requirements.txt` file:
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```sh
   flask run
   ```
   The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage
- Log in with your credentials.
- Add new items using the "Add Item" button.
- Edit or delete items using the action buttons in the table.
- Use the search bar to filter items.
- Import/export items as CSV using the provided buttons.

## Screenshots
<!-- Optionally add screenshots here -->

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)

---

**Maintained by Piero.**
