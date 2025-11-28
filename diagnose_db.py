"""
Diagnostic script to check database and user setup
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from data_entry_app import app
    from models import db, User, Item
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def diagnose():
    """Run diagnostics on the database"""
    print("\n" + "="*60)
    print("DATABASE DIAGNOSTICS")
    print("="*60)
    
    with app.app_context():
        try:
            # Check if tables exist
            print("\n1. Checking database tables...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   Tables found: {', '.join(tables) if tables else 'None'}")
            
            if 'user' not in tables:
                print("   ✗ User table missing! Run create_admin.py first")
                return
            else:
                print("   ✓ User table exists")
            
            # Check users
            print("\n2. Checking users in database...")
            users = User.query.all()
            if not users:
                print("   ✗ No users found!")
                print("   Run: python create_admin.py")
                return
            else:
                print(f"   ✓ Found {len(users)} user(s)")
                for user in users:
                    print(f"\n   User: {user.username}")
                    print(f"     ID: {user.id}")
                    print(f"     Email: {user.email}")
                    print(f"     Active: {user.is_active}")
                    print(f"     Password Hash: {user.password_hash[:50]}...")
            
            # Test admin login
            print("\n3. Testing admin credentials...")
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("   ✓ Admin user found")
                if admin.check_password('admin'):
                    print("   ✓ Password 'admin' is CORRECT")
                    print("\n   You should be able to login with:")
                    print("   Username: admin")
                    print("   Password: admin")
                else:
                    print("   ✗ Password 'admin' does NOT match")
                    print("   Run create_admin.py and reset the password")
                
                if not admin.is_active:
                    print("   ✗ WARNING: Admin account is INACTIVE")
                    print("   Run create_admin.py to activate it")
            else:
                print("   ✗ Admin user not found")
                print("   Run: python create_admin.py")
            
            # Check items
            print("\n4. Checking items in database...")
            items = Item.query.all()
            print(f"   Found {len(items)} item(s)")
            
            print("\n" + "="*60)
            print("DIAGNOSIS COMPLETE")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error during diagnosis: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    diagnose()