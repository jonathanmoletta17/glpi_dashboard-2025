import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# GLPI Configuration
GLPI_URL = "http://10.73.0.79/glpi/apirest.php"
GLPI_USER_TOKEN = os.getenv('GLPI_USER_TOKEN')
GLPI_APP_TOKEN = os.getenv('GLPI_APP_TOKEN')

def init_glpi_session():
    """Initialize GLPI session"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {GLPI_USER_TOKEN}',
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        response = requests.get(f"{GLPI_URL}/initSession", headers=headers, timeout=30)
        if response.status_code == 200:
            session_token = response.json().get('session_token')
            print(f"✓ GLPI session initialized successfully")
            return session_token
        else:
            print(f"✗ Failed to initialize GLPI session: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error connecting to GLPI: {e}")
        return None

def get_group_info(session_token, group_id):
    """Get information about a specific group"""
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_APP_TOKEN
    }
    
    try:
        response = requests.get(f"{GLPI_URL}/Group/{group_id}", headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"✗ Failed to get group {group_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error getting group {group_id}: {e}")
        return None

def validate_service_level_groups():
    """Validate N1-N4 group IDs"""
    print("=== GLPI Group Validation ===")
    print(f"GLPI URL: {GLPI_URL}")
    
    # Initialize session
    session_token = init_glpi_session()
    if not session_token:
        return False
    
    # Expected group mapping
    service_levels = {
        'N1': 89,
        'N2': 90,
        'N3': 91,
        'N4': 92
    }
    
    print("\n=== Validating Service Level Groups ===")
    all_valid = True
    
    for level, group_id in service_levels.items():
        print(f"\nChecking {level} (Group ID: {group_id})...")
        group_info = get_group_info(session_token, group_id)
        
        if group_info:
            group_name = group_info.get('name', 'Unknown')
            print(f"✓ {level}: Group ID {group_id} exists - Name: '{group_name}'")
        else:
            print(f"✗ {level}: Group ID {group_id} not found or inaccessible")
            all_valid = False
    
    # Close session
    try:
        headers = {
            'Content-Type': 'application/json',
            'Session-Token': session_token,
            'App-Token': GLPI_APP_TOKEN
        }
        requests.get(f"{GLPI_URL}/killSession", headers=headers, timeout=10)
        print("\n✓ GLPI session closed")
    except:
        pass
    
    return all_valid

if __name__ == "__main__":
    success = validate_service_level_groups()
    if success:
        print("\n🎉 All service level groups are valid!")
    else:
        print("\n⚠️  Some service level groups need attention!")