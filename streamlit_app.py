import streamlit as st
import json
import os
import re
import hashlib
from datetime import datetime
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Grade Calculator",
    layout="wide"
)

# Per-profile data location
DATA_DIR = "user_data"
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
CHAT_FILE = os.path.join(DATA_DIR, "chat.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize session state
if 'classes' not in st.session_state:
    st.session_state.classes = {}

if 'current_class' not in st.session_state:
    st.session_state.current_class = None

if 'profile_name' not in st.session_state:
    st.session_state.profile_name = ""

if 'profile_key' not in st.session_state:
    st.session_state.profile_key = ""

if 'profile_loaded' not in st.session_state:
    st.session_state.profile_loaded = False

if 'last_loaded_profile' not in st.session_state:
    st.session_state.last_loaded_profile = ""

if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False


def sanitize_profile_key(profile_name):
    """Create a safe file key from a profile name"""
    cleaned = re.sub(r'[^a-zA-Z0-9_-]+', '_', profile_name.strip().lower())
    return cleaned.strip('_')


def get_profile_data_file(profile_key):
    """Get data filename for a profile"""
    return os.path.join(DATA_DIR, f"{profile_key}.json")


def hash_pin(pin):
    """Hash a 4-digit PIN"""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def load_chat_messages():
    """Load chat messages"""
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []


def get_mean_ai_response(user_message):
    """Generate a mean AI response (around 5 words)"""
    import random
    
    # Check for keywords to give specific mean responses
    msg_lower = user_message.lower()
    
    if any(word in msg_lower for word in ['hi', 'hello', 'hey']):
        responses = [
            "Nobody asked you here",
            "Wow, how incredibly original",
            "Great, another person talking",
            "Did I ask though"
        ]
    elif any(word in msg_lower for word in ['help', 'question', '?']):
        responses = [
            "Figure it out yourself",
            "Not my problem honestly",
            "Google exists for a reason",
            "Why are you like this"
        ]
    elif any(word in msg_lower for word in ['thanks', 'thank']):
        responses = [
            "Whatever helps you sleep tonight",
            "I literally did nothing",
            "You're still annoying me",
            "Don't mention it. Ever."
        ]
    elif any(word in msg_lower for word in ['grade', 'test', 'exam', 'homework']):
        responses = [
            "Maybe try studying next time",
            "Your grades aren't my problem",
            "Should've worked harder honestly",
            "That's embarrassing for you"
        ]
    else:
        # General mean responses
        responses = [
            "Nobody cares about this",
            "That's the dumbest thing ever",
            "Why even bother typing that",
            "Cool story, tell someone else",
            "Literally no one asked you",
            "This ain't it chief",
            "Try harder next time maybe",
            "Embarrassing post honestly",
            "Delete this immediately please",
            "Yikes, that's rough buddy",
            "Not impressed by this honestly",
            "Did you think before typing",
            "What a waste of bandwidth",
            "I've seen better from toddlers",
            "This is why nobody texts"
        ]
    
    return random.choice(responses)


def save_chat_message(username, message, is_bot=False):
    """Save a new chat message"""
    try:
        messages = load_chat_messages()
        messages.append({
            'user': username,
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'is_bot': is_bot
        })
        # Keep only last 50 messages
        messages = messages[-50:]
        with open(CHAT_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
        return True
    except Exception:
        return False


def load_profiles():
    """Load profile PIN metadata"""
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            st.error(f"Failed to load profiles: {str(e)}")
    return {}


def save_profiles(profiles):
    """Save profile PIN metadata"""
    try:
        with open(PROFILES_FILE, 'w') as f:
            json.dump(profiles, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save profiles: {str(e)}")
        return False


def load_profile_data(profile_key):
    """Load classes for a specific profile"""
    data_file = get_profile_data_file(profile_key)
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            st.error(f"Failed to load profile data: {str(e)}")
    return {}

def save_data():
    """Save data to the current profile JSON file"""
    if not st.session_state.profile_key:
        st.error("Please load a profile first.")
        return False

    try:
        data_file = get_profile_data_file(st.session_state.profile_key)
        with open(data_file, 'w') as f:
            json.dump(st.session_state.classes, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save data: {str(e)}")
        return False

def get_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 93:
        return 'A'
    elif percentage >= 90:
        return 'A-'
    elif percentage >= 87:
        return 'B+'
    elif percentage >= 83:
        return 'B'
    elif percentage >= 80:
        return 'B-'
    elif percentage >= 77:
        return 'C+'
    elif percentage >= 73:
        return 'C'
    elif percentage >= 70:
        return 'C-'
    elif percentage >= 67:
        return 'D+'
    elif percentage >= 63:
        return 'D'
    elif percentage >= 60:
        return 'D-'
    else:
        return 'F'

def calculate_category_grade(assignments):
    """Calculate grade for a category"""
    if not assignments:
        return 0.0
    total_possible = sum(a['total'] for a in assignments)
    total_earned = sum(a['earned'] for a in assignments)
    return (total_earned / total_possible * 100) if total_possible > 0 else 0

def calculate_overall_grade(class_name):
    """Calculate overall grade for a class"""
    if class_name not in st.session_state.classes:
        return None, None
    
    categories = st.session_state.classes[class_name]['categories']
    if not categories:
        return None, None
    
    total_weight = 0
    weighted_grade = 0
    
    for cat_name, cat_data in categories.items():
        weight = cat_data['weight']
        assignments = cat_data['assignments']
        
        if assignments:
            cat_percentage = calculate_category_grade(assignments)
            total_weight += weight
            weighted_grade += cat_percentage * (weight / 100)
    
    if total_weight > 0:
        overall = weighted_grade / (total_weight / 100)
        letter = get_letter_grade(overall)
        return overall, letter
    
    return None, None

# Main app
st.title("Grade Calculator")

# Sidebar for class management
with st.sidebar:
    st.header("Profile")

    profile_input = st.text_input(
        "Profile Name",
        value=st.session_state.profile_name,
        key="profile_name_input"
    )

    pin_input = st.text_input(
        "PIN",
        type="password",
        max_chars=4,
        key="profile_pin_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load Profile", use_container_width=True):
            profile_key = sanitize_profile_key(profile_input)
            if not profile_key:
                st.warning("Enter a valid profile name")
            elif not re.fullmatch(r"\d{4}", pin_input.strip()):
                st.warning("PIN must be 4 digits")
            else:
                pin_value = pin_input.strip()
                profiles = load_profiles()

                if profile_key in profiles:
                    saved_hash = profiles[profile_key].get('pin_hash', '')
                    if saved_hash != hash_pin(pin_value):
                        st.error("Incorrect PIN")
                        st.stop()
                else:
                    profiles[profile_key] = {
                        'name': profile_input.strip(),
                        'pin_hash': hash_pin(pin_value)
                    }
                    if not save_profiles(profiles):
                        st.stop()

                st.session_state.profile_name = profile_input.strip()
                st.session_state.profile_key = profile_key
                st.session_state.classes = load_profile_data(profile_key)
                st.session_state.current_class = None
                st.session_state.profile_loaded = True
                st.session_state.last_loaded_profile = profile_input.strip()
                st.rerun()
    with col2:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.profile_name = ""
            st.session_state.profile_key = ""
            st.session_state.profile_loaded = False
            st.session_state.classes = {}
            st.session_state.current_class = None
            st.rerun()

    if st.session_state.profile_loaded:
        st.caption(f"Profile: {st.session_state.profile_name}")

    st.divider()
    st.header("Classes")
    
    if st.session_state.profile_loaded:
        # Add new class
        with st.expander("Add New Class"):
            new_class = st.text_input("Class Name", key="new_class_input")
            if st.button("Add Class"):
                if new_class:
                    if new_class in st.session_state.classes:
                        st.error("Class already exists")
                    else:
                        st.session_state.classes[new_class] = {
                            'categories': {}
                        }
                        st.session_state.current_class = new_class
                        save_data()
                        st.rerun()
                else:
                    st.warning("Enter a class name")
    
    # List classes
    if st.session_state.profile_loaded and st.session_state.classes:
        st.subheader("Your Classes")
        for class_name in sorted(st.session_state.classes.keys()):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(class_name, key=f"class_{class_name}", use_container_width=True):
                    st.session_state.current_class = class_name
                    st.rerun()
            with col2:
                if st.button("Delete", key=f"del_class_{class_name}"):
                    del st.session_state.classes[class_name]
                    if st.session_state.current_class == class_name:
                        st.session_state.current_class = None
                    save_data()
                    st.rerun()

# Main content area
if not st.session_state.profile_loaded:
    st.write("Load profile to begin")
elif st.session_state.current_class:
    class_name = st.session_state.current_class
    st.header(f"{class_name}")
    
    # Calculate and display overall grade
    overall, letter = calculate_overall_grade(class_name)
    if overall is not None:
        st.markdown(f"### Current Grade: **{overall:.2f}%** ({letter})")
    
    st.divider()
    
    # Add category section
    with st.expander("Add New Category"):
        col1, col2 = st.columns(2)
        with col1:
            cat_name = st.text_input("Category Name", key="new_cat_name")
        with col2:
            cat_weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0, value=0.0, key="new_cat_weight")
        
        if st.button("Add Category"):
            if not cat_name:
                st.warning("Enter a category name")
            elif cat_name in st.session_state.classes[class_name]['categories']:
                st.error("Category already exists")
            else:
                st.session_state.classes[class_name]['categories'][cat_name] = {
                    'weight': cat_weight,
                    'assignments': []
                }
                save_data()
                st.rerun()
    
    # Display categories and assignments
    categories = st.session_state.classes[class_name]['categories']
    
    if categories:
        for cat_name in sorted(categories.keys()):
            cat_data = categories[cat_name]
            cat_grade = calculate_category_grade(cat_data['assignments'])
            
            with st.container():
                # Category header
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.subheader(f"{cat_name}")
                with col2:
                    st.metric("Weight", f"{cat_data['weight']}%")
                with col3:
                    st.metric("Grade", f"{cat_grade:.1f}%")
                with col4:
                    if st.button("Delete", key=f"del_cat_{cat_name}"):
                        del st.session_state.classes[class_name]['categories'][cat_name]
                        save_data()
                        st.rerun()
                
                # Add assignment to this category
                with st.expander(f"Add Assignment to {cat_name}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        assign_name = st.text_input("Assignment Name", key=f"assign_name_{cat_name}")
                    with col2:
                        total_points = st.number_input("Total Points", min_value=0.0, value=100.0, key=f"total_{cat_name}")
                    with col3:
                        earned_points = st.number_input("Points Earned", min_value=0.0, value=0.0, key=f"earned_{cat_name}")
                    
                    if st.button("Add Assignment", key=f"add_assign_{cat_name}"):
                        if not assign_name:
                            st.warning("Enter an assignment name")
                        elif total_points <= 0:
                            st.warning("Total points must be greater than 0")
                        else:
                            st.session_state.classes[class_name]['categories'][cat_name]['assignments'].append({
                                'name': assign_name,
                                'total': total_points,
                                'earned': earned_points
                            })
                            save_data()
                            st.rerun()
                
                # Display assignments
                if cat_data['assignments']:
                    for idx, assign in enumerate(cat_data['assignments']):
                        percentage = (assign['earned'] / assign['total'] * 100) if assign['total'] > 0 else 0
                        
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                        with col1:
                            st.write(f"{assign['name']}")
                        with col2:
                            st.write(f"{assign['earned']}/{assign['total']}")
                        with col3:
                            st.write(f"{percentage:.1f}%")
                        with col4:
                            # Edit button
                            if st.button("Edit", key=f"edit_{cat_name}_{idx}"):
                                st.session_state[f'editing_{cat_name}_{idx}'] = True
                                st.rerun()
                        with col5:
                            # Delete button
                            if st.button("Delete", key=f"del_{cat_name}_{idx}"):
                                st.session_state.classes[class_name]['categories'][cat_name]['assignments'].pop(idx)
                                save_data()
                                st.rerun()
                        
                        # Edit form (if editing)
                        if st.session_state.get(f'editing_{cat_name}_{idx}', False):
                            with st.form(key=f"edit_form_{cat_name}_{idx}"):
                                st.write("**Edit Assignment**")
                                edit_col1, edit_col2, edit_col3 = st.columns(3)
                                with edit_col1:
                                    new_name = st.text_input("Name", value=assign['name'], key=f"edit_name_{cat_name}_{idx}")
                                with edit_col2:
                                    new_total = st.number_input("Total", value=float(assign['total']), key=f"edit_total_{cat_name}_{idx}")
                                with edit_col3:
                                    new_earned = st.number_input("Earned", value=float(assign['earned']), key=f"edit_earned_{cat_name}_{idx}")
                                
                                submit_col1, submit_col2 = st.columns(2)
                                with submit_col1:
                                    if st.form_submit_button("Save"):
                                        st.session_state.classes[class_name]['categories'][cat_name]['assignments'][idx] = {
                                            'name': new_name,
                                            'total': new_total,
                                            'earned': new_earned
                                        }
                                        save_data()
                                        st.session_state[f'editing_{cat_name}_{idx}'] = False
                                        st.rerun()
                                with submit_col2:
                                    if st.form_submit_button("Cancel"):
                                        st.session_state[f'editing_{cat_name}_{idx}'] = False
                                        st.rerun()
                
                st.divider()

else:
    st.write("Select a class to continue")

# Chat section
st.divider()

col1, col2 = st.columns([5, 1])
with col2:
    if st.button("💬 Chat" if not st.session_state.show_chat else "✕ Close"):
        st.session_state.show_chat = not st.session_state.show_chat
        st.rerun()

if st.session_state.show_chat:
    st.subheader("Message Board")
    
    # Display messages
    messages = load_chat_messages()
    if messages:
        chat_container = st.container()
        with chat_container:
            for msg in messages[-20:]:
                user_display = msg['user']
                if msg.get('is_bot', False):
                    user_display = "🤖 Bot"
                st.text(f"{msg['timestamp']} - {user_display}: {msg['message']}")
    
    # Input for new message
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            new_message = st.text_input("Message", key="chat_input", label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("Send")
        
        if submitted and new_message:
            username = st.session_state.profile_name if st.session_state.profile_loaded else "Anonymous"
            save_chat_message(username, new_message, is_bot=False)
            
            # AI bot responds with a mean comment
            import time
            time.sleep(0.1)  # Small delay for realism
            ai_response = get_mean_ai_response(new_message)
            save_chat_message("Bot", ai_response, is_bot=True)
            
            st.rerun()

# Footer
st.caption("Made by seb.")
