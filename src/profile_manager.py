import json
import os
from jsonschema import validate, ValidationError

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'profile_schema.json')
PROFILE_DIR = os.path.join(os.path.dirname(__file__), '..', 'profiles')

def load_schema():
    """Loads the JSON schema for profile validation."""
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)

def create_profile_dir():
    """Ensures the profiles directory exists."""
    os.makedirs(PROFILE_DIR, exist_ok=True)

def get_profile_path(profile_name):
    """Returns the full path for a given profile name."""
    return os.path.join(PROFILE_DIR, f"{profile_name}.json")

def validate_profile(profile_data, schema):
    """Validates profile data against the schema."""
    try:
        validate(instance=profile_data, schema=schema)
        return True, "Profile is valid."
    except ValidationError as e:
        return False, f"Profile validation error: {e.message}"
    except Exception as e:
        return False, f"An unexpected error occurred during validation: {e}"

def load_profile(profile_name):
    """Loads a profile from a JSON file."""
    profile_path = get_profile_path(profile_name)
    if not os.path.exists(profile_path):
        return None, "Profile not found."
    try:
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)
        schema = load_schema()
        is_valid, message = validate_profile(profile_data, schema)
        if not is_valid:
            print(f"Warning: Loaded profile '{profile_name}' is invalid: {message}")
        return profile_data, None
    except json.JSONDecodeError:
        return None, "Error: Invalid JSON in profile file."
    except Exception as e:
        return None, f"Error loading profile: {e}"

def save_profile(profile_name, profile_data):
    """Saves profile data to a JSON file."""
    create_profile_dir()
    profile_path = get_profile_path(profile_name)
    schema = load_schema()
    is_valid, message = validate_profile(profile_data, schema)
    if not is_valid:
        return False, f"Cannot save invalid profile: {message}"
    try:
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=2)
        return True, f"Profile '{profile_name}' saved successfully."
    except Exception as e:
        return False, f"Error saving profile: {e}"

def create_new_profile(profile_name, initial_data=None):
    """Creates a new profile with optional initial data."""
    if load_profile(profile_name)[0] is not None:
        return False, f"Profile '{profile_name}' already exists."

    schema = load_schema()
    new_profile = initial_data if initial_data else {}

    # Prompt for basic required fields if not provided
    if not new_profile.get("personal_info"):
        print("\nEntering personal information:")
        new_profile["personal_info"] = {
            "name": input("Name: "),
            "email": input("Email: "),
            "phone": input("Phone: "),
            "linkedin": input("LinkedIn Profile URL: "),
            "github": input("GitHub Profile URL: ")
        }
    # For simplicity, other sections are initialized as empty lists/objects if not present
    new_profile.setdefault("education", [])
    new_profile.setdefault("work_experience", [])
    new_profile.setdefault("projects", [])
    new_profile.setdefault("skills", {})

    return save_profile(profile_name, new_profile)

def edit_profile(profile_name):
    """Allows editing an existing profile (basic implementation for now)."""
    profile_data, error = load_profile(profile_name)
    if error:
        return False, error

    print(f"\nEditing profile: {profile_name}")
    print("Current profile data (JSON format):")
    print(json.dumps(profile_data, indent=2))
    
    # In a real CLI, this would be more interactive.
    # For now, we'll allow basic text editing of the JSON.
    print("\nTo edit, paste the updated JSON content below. Press Ctrl+Z (Windows) or Ctrl+D (Unix) and then Enter when done.")
    print("Or type 'cancel' to abort editing.")

    updated_json_lines = []
    while True:
        try:
            line = input()
            if line.lower() == 'cancel':
                print("Editing cancelled.")
                return False, "Editing cancelled by user."
            updated_json_lines.append(line)
        except EOFError: # Ctrl+Z or Ctrl+D
            break
    
    updated_json_str = "\n".join(updated_json_lines)
    
    try:
        updated_profile_data = json.loads(updated_json_str)
    except json.JSONDecodeError:
        return False, "Error: Invalid JSON provided. Editing failed."

    return save_profile(profile_name, updated_profile_data)

def display_profile(profile_name):
    """Displays a profile's content."""
    profile_data, error = load_profile(profile_name)
    if error:
        print(f"Error displaying profile: {error}")
        return
    print(f"\n--- Profile: {profile_name} ---")
    print(json.dumps(profile_data, indent=2))
    print("-----------------------------------")

def list_profiles():
    """Lists all available profiles."""
    create_profile_dir() # Ensure directory exists before listing
    profiles = [f.replace('.json', '') for f in os.listdir(PROFILE_DIR) if f.endswith('.json')]
    if not profiles:
        print("No profiles found.")
        return []
    print("\nAvailable profiles:")
    for p in profiles:
        print(f"- {p}")
    return profiles

def main():
    """Main CLI entry point for the profile manager."""
    schema = load_schema() # Load schema once at startup
    create_profile_dir() # Ensure profiles directory exists

    while True:
        print("\nProfile Manager Menu:")
        print("1. Create New Profile")
        print("2. Load/Display Profile")
        print("3. Edit Profile")
        print("4. List Profiles")
        print("5. Validate Existing Profile")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            profile_name = input("Enter new profile name: ")
            success, message = create_new_profile(profile_name)
            print(message)
        elif choice == '2':
            profile_name = input("Enter profile name to display: ")
            display_profile(profile_name)
        elif choice == '3':
            profile_name = input("Enter profile name to edit: ")
            success, message = edit_profile(profile_name)
            print(message)
        elif choice == '4':
            list_profiles()
        elif choice == '5':
            profile_name = input("Enter profile name to validate: ")
            profile_data, error = load_profile(profile_name)
            if error:
                print(f"Error loading profile for validation: {error}")
            elif profile_data:
                is_valid, message = validate_profile(profile_data, schema)
                print(f"Validation for '{profile_name}': {message}")
        elif choice == '6':
            print("Exiting Profile Manager.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
