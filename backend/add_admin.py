import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
import uuid
import time
import os
import sys

# Initialize Firebase Admin SDK
try:
    # Look for the service account key file in the current directory
    cred_file = next((f for f in os.listdir('.') if f.endswith('.json') and 'firebase-adminsdk' in f), None)
    
    if not cred_file:
        print("Error: Firebase service account key file not found.")
        sys.exit(1)
    
    cred = credentials.Certificate(cred_file)
    firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("Firebase initialized successfully.")
except Exception as e:
    print(f"Firebase initialization error: {str(e)}")
    sys.exit(1)

# Admin details from the table
admins_list = [
    {
        "sevarthId": "REVDKGM7003",
        "firstName": "Dilip",
        "lastName": "Gayakwad",
        "organizationName": "Tahsil OFFICE Sengaon",
        "phoneNumber": "9850916726",
        "email": "dilipkg024@gmail.com",
    },
    {
        "sevarthId": "REVAHSM7001",
        "firstName": "Anil",
        "lastName": "Sarode",
        "organizationName": "Tahsil OFFICE Sengaon",
        "phoneNumber": "8856826524",
        "email": "anilsarode358@gmail.com",
    },
    {
        "sevarthId": "REVDKKM7301",
        "firstName": "Devrao",
        "lastName": "kargude",
        "organizationName": "Tahsil OFFICE Sengaon",
        "phoneNumber": "9689553304",
        "email": "devraokargude@gmail.com",
    }
]

# Default password for the admin
default_password = "Admin@123"

# Function to create the admin user in Firebase Authentication
def create_admin_auth_user(admin_data):
    try:
        # Check if user already exists
        try:
            user = auth.get_user_by_email(admin_data["email"])
            print(f"User already exists with UID: {user.uid}")
            return user.uid
        except auth.UserNotFoundError:
            # User doesn't exist, create a new one
            user = auth.create_user(
                email=admin_data["email"],
                password=default_password,
                display_name=f"{admin_data['firstName']} {admin_data['lastName']}",
                disabled=False
            )
            print(f"Created new user with UID: {user.uid}")
            
            # Set custom claims to mark as admin
            auth.set_custom_user_claims(user.uid, {"admin": True})
            print("Set admin claims for the user")
            
            return user.uid
    except Exception as e:
        print(f"Error creating auth user: {str(e)}")
        return None

# Function to add admin to Firestore
def add_admin_to_firestore(admin_data, auth_uid=None):
    try:
        # Add common fields
        admin_data["id"] = str(uuid.uuid4())
        admin_data["role"] = "admin"
        admin_data["active"] = True
        admin_data["createdAt"] = int(time.time() * 1000)
        admin_data["updatedAt"] = int(time.time() * 1000)
        
        # If we have an auth UID, add it to the admin data
        if auth_uid:
            admin_data["authUid"] = auth_uid
        
        # Add to admins collection
        db.collection("admins").document(admin_data["sevarthId"]).set(admin_data)
        print(f"Admin added to Firestore successfully with Sevarth ID: {admin_data['sevarthId']}")
        
        # Add to users collection as well for consistency
        db.collection("users").document(admin_data["sevarthId"]).set(admin_data)
        print(f"Admin also added to users collection for consistency")
        
        return True
    except Exception as e:
        print(f"Error adding admin to Firestore: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    for admin_data in admins_list:
        print(f"\nAdding admin {admin_data['firstName']} {admin_data['lastName']} to Firebase...")
        uid = create_admin_auth_user(admin_data)
        if uid:
            success = add_admin_to_firestore(admin_data, uid)
            if success:
                print(f"Admin {admin_data['firstName']} {admin_data['lastName']} added successfully!")
                print(f"Email: {admin_data['email']}")
                print(f"Default Password: {default_password}")
                print("NOTE: Please change the password after first login.")
            else:
                print(f"Failed to add admin {admin_data['firstName']} {admin_data['lastName']} to Firestore.")
        else:
            print(f"Failed to create admin authentication user for {admin_data['firstName']} {admin_data['lastName']}.") 