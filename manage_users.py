"""
User management script for the data entry system
Create, list, and manage users
"""
from data_entry_app import app
from models import db, User
import sys

def list_users():
    """List all users in the system"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found.")
            return
        
        print("\n" + "="*70)
        print(f"{'ID':<5} {'Username':<20} {'Email':<25} {'Active':<8} {'Last Login'}")
        print("="*70)
        for user in users:
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
            active = '✓' if user.is_active else '✗'
            print(f"{user.id:<5} {user.username:<20} {user.email or 'N/A':<25} {active:<8} {last_login}")
        print("="*70 + "\n")

def create_user():
    """Create a new user"""
    with app.app_context():
        print("\n--- Create New User ---")
        username = input("Username: ").strip()
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            print(f"✗ Error: Username '{username}' already exists!")
            return
        
        email = input("Email (optional): ").strip() or None
        password = input("Password: ").strip()
        
        if len(password) < 4:
            print("✗ Error: Password must be at least 4 characters!")
            return
        
        try:
            user = User(username=username, email=email, is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✓ User '{username}' created successfully!")
        except Exception as e:
            print(f"✗ Error creating user: {str(e)}")
            db.session.rollback()

def delete_user():
    """Delete a user"""
    with app.app_context():
        list_users()
        username = input("Enter username to delete: ").strip()
        
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ Error: User '{username}' not found!")
            return
        
        confirm = input(f"Are you sure you want to delete '{username}'? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            db.session.delete(user)
            db.session.commit()
            print(f"✓ User '{username}' deleted successfully!")
        else:
            print("Deletion cancelled.")

def reset_password():
    """Reset a user's password"""
    with app.app_context():
        list_users()
        username = input("Enter username to reset password: ").strip()
        
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ Error: User '{username}' not found!")
            return
        
        new_password = input("Enter new password: ").strip()
        if len(new_password) < 4:
            print("✗ Error: Password must be at least 4 characters!")
            return
        
        user.set_password(new_password)
        db.session.commit()
        print(f"✓ Password reset for '{username}' successfully!")

def toggle_active():
    """Toggle user active status"""
    with app.app_context():
        list_users()
        username = input("Enter username to toggle active status: ").strip()
        
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"✗ Error: User '{username}' not found!")
            return
        
        user.is_active = not user.is_active
        db.session.commit()
        status = "activated" if user.is_active else "deactivated"
        print(f"✓ User '{username}' {status} successfully!")

def main():
    """Main menu"""
    while True:
        print("\n" + "="*50)
        print("USER MANAGEMENT SYSTEM")
        print("="*50)
        print("1. List all users")
        print("2. Create new user")
        print("3. Delete user")
        print("4. Reset password")
        print("5. Toggle active status")
        print("6. Exit")
        print("="*50)
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == '1':
            list_users()
        elif choice == '2':
            create_user()
        elif choice == '3':
            delete_user()
        elif choice == '4':
            reset_password()
        elif choice == '5':
            toggle_active()
        elif choice == '6':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
    main()