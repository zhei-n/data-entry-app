"""
Script to create an admin user for the data entry system
Run this once to set up your admin account
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from data_entry_app import app
    from models import db, User
    from datetime import datetime
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project directory")
    sys.exit(1)

def create_admin_user():
    """Create or update admin user"""
    try:
        with app.app_context():
            print("Creating database tables...")
            # Create all tables if they don't exist
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Check if admin exists
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("\nCreating new admin user...")
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_active=True
                )
                admin.set_password('admin')  # Change this password after first login!
                db.session.add(admin)
                db.session.commit()
                print("\n" + "="*60)
                print("✓ Admin user created successfully!")
                print("="*60)
                print("  Username: admin")
                print("  Password: admin")
                print("="*60)
                print("\n⚠️  IMPORTANT: Change this password after first login!")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("Admin user already exists!")
                print("="*60)
                print(f"  Username: {admin.username}")
                print(f"  Email: {admin.email}")
                print(f"  Active: {admin.is_active}")
                print(f"  Created: {admin.created_at}")
                print(f"  Last Login: {admin.last_login or 'Never'}")
                print("="*60)
                
                # Option to reset password
                reset = input("\nDo you want to reset the admin password to 'admin'? (yes/no): ")
                if reset.lower() in ['yes', 'y']:
                    admin.set_password('admin')
                    admin.is_active = True  # Make sure it's active
                    db.session.commit()
                    print("\n✓ Password reset to 'admin' and account activated")
                    print("="*60)
            
            # Verify the user was created/updated
            verify = User.query.filter_by(username='admin').first()
            if verify:
                print("\n✓ Verification: Admin user exists in database")
                print(f"  User ID: {verify.id}")
                print(f"  Username: {verify.username}")
                print(f"  Active: {verify.is_active}")
                
                # Test password
                if verify.check_password('admin'):
                    print("  Password: ✓ Verified correct")
                else:
                    print("  Password: ✗ Something went wrong!")
            else:
                print("\n✗ ERROR: Could not verify admin user creation")
                
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("DATA ENTRY SYSTEM - ADMIN USER SETUP")
    print("="*60)
    create_admin_user()
    print("\nSetup complete! You can now run: python data_entry_app.py")
    print("="*60 + "\n")