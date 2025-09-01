import json

# Read the current credentials file
with open('firebase_credentials.json', 'r') as f:
    data = json.load(f)

# Fix the private key by replacing literal \n with actual newlines
data['private_key'] = data['private_key'].replace('\\n', '\n')

# Write the fixed credentials to a new file
with open('firebase_credentials_fixed.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Fixed credentials file created: firebase_credentials_fixed.json")

# Test if the fixed credentials can be loaded
try:
    from firebase_admin import credentials
    creds = credentials.Certificate('firebase_credentials_fixed.json')
    print("✅ Fixed credentials loaded successfully!")
except Exception as e:
    print(f"❌ Still having issues: {e}")
