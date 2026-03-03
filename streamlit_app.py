import streamlit as st
import json
import os
import re
import hashlib
import base64
import html
from datetime import datetime
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Grade Calculator",
    layout="wide"
)

st.markdown(
    """
    <style>
    div[data-testid="stSegmentedControl"] button[aria-checked="false"] {
        background-color: #2f2f2f !important;
        color: #e6e6e6 !important;
        border: 1px solid #4a4a4a !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background-color: #4F8BF9 !important;
        color: #ffffff !important;
        border: 1px solid #4F8BF9 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Per-profile data location
DATA_DIR = "user_data"
PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")
CHAT_FILE = os.path.join(DATA_DIR, "chat.json")
DUELS_FILE = os.path.join(DATA_DIR, "duels.json")
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

if 'display_name' not in st.session_state:
    st.session_state.display_name = ""

if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

if 'chat_sort_order' not in st.session_state:
    st.session_state.chat_sort_order = "Newest"
elif st.session_state.chat_sort_order not in ["Newest", "Oldest"]:
    st.session_state.chat_sort_order = "Newest"

if 'selected_chat_profile_key' not in st.session_state:
    st.session_state.selected_chat_profile_key = ""

if 'selected_chat_profile_name' not in st.session_state:
    st.session_state.selected_chat_profile_name = ""


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
                    normalized_messages = []
                    for msg in data:
                        if not isinstance(msg, dict):
                            continue

                        if msg.get('is_bot', False):
                            continue

                        user = str(msg.get('user', '')).strip()
                        message = str(msg.get('message', '')).strip()

                        if not user or not message:
                            continue

                        if user.lower() in {'bot', 'ai', 'assistant'}:
                            continue

                        normalized_messages.append({
                            'user': user,
                            'message': message,
                            'profile_key': str(msg.get('profile_key', '')).strip()
                        })

                    if normalized_messages != data:
                        with open(CHAT_FILE, 'w') as write_file:
                            json.dump(normalized_messages[-50:], write_file, indent=2)

                    return normalized_messages[-50:]
        except Exception:
            pass
    return []



def save_chat_message(username, message):
    """Save a new chat message"""
    try:
        messages = load_chat_messages()
        messages.append({
            'user': username,
            'message': message,
            'profile_key': st.session_state.profile_key if st.session_state.profile_loaded else ""
        })
        # Keep only last 50 messages
        messages = messages[-50:]
        with open(CHAT_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
        return True
    except Exception:
        return False


def save_system_chat_message(message):
    """Save a system message to chat"""
    try:
        messages = load_chat_messages()
        messages.append({
            'user': 'System',
            'message': message,
            'profile_key': ''
        })
        messages = messages[-50:]
        with open(CHAT_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
        return True
    except Exception:
        return False


def load_duels():
    """Load duel data"""
    if os.path.exists(DUELS_FILE):
        try:
            with open(DUELS_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    normalized = []
                    for duel in data:
                        if not isinstance(duel, dict):
                            continue
                        if not duel.get('id'):
                            continue
                        normalized.append({
                            'id': str(duel.get('id')),
                            'challenger_key': str(duel.get('challenger_key', '')),
                            'challenged_key': str(duel.get('challenged_key', '')),
                            'status': str(duel.get('status', 'pending')),
                            'challenger_move': duel.get('challenger_move'),
                            'challenged_move': duel.get('challenged_move'),
                            'created_at': str(duel.get('created_at', datetime.now().isoformat())),
                            'announced': bool(duel.get('announced', False))
                        })
                    return normalized[-200:]
        except Exception:
            pass
    return []


def save_duels(duels):
    """Save duel data"""
    try:
        with open(DUELS_FILE, 'w') as f:
            json.dump(duels[-200:], f, indent=2)
        return True
    except Exception:
        return False


def get_profile_display_name(profile_key, profiles):
    profile = profiles.get(profile_key, {}) if isinstance(profiles, dict) else {}
    return profile.get('display_name') or profile.get('name') or profile_key


def determine_rps_winner(challenger_move, challenged_move):
    """Return winner side: challenger, challenged, tie"""
    if challenger_move == challenged_move:
        return 'tie'

    win_map = {
        'Rock': 'Scissors',
        'Paper': 'Rock',
        'Scissors': 'Paper'
    }
    if win_map.get(challenger_move) == challenged_move:
        return 'challenger'
    return 'challenged'


def resolve_due_duels_and_announce(duels, profiles):
    """Resolve completed duel moves and announce winner in chat"""
    changed = False
    for duel in duels:
        if duel.get('status') != 'active':
            continue

        challenger_move = duel.get('challenger_move')
        challenged_move = duel.get('challenged_move')
        if not challenger_move or not challenged_move:
            continue

        winner_side = determine_rps_winner(challenger_move, challenged_move)
        challenger_name = get_profile_display_name(duel.get('challenger_key', ''), profiles)
        challenged_name = get_profile_display_name(duel.get('challenged_key', ''), profiles)

        if winner_side == 'tie':
            result_message = (
                f"⚔️ Duel Result: {challenger_name} ({challenger_move}) vs "
                f"{challenged_name} ({challenged_move}) ended in a tie!"
            )
        elif winner_side == 'challenger':
            result_message = (
                f"🏆 Duel Winner: {challenger_name}! "
                f"({challenger_move} beats {challenged_name}'s {challenged_move})"
            )
        else:
            result_message = (
                f"🏆 Duel Winner: {challenged_name}! "
                f"({challenged_move} beats {challenger_name}'s {challenger_move})"
            )

        if not duel.get('announced', False):
            save_system_chat_message(result_message)
            duel['announced'] = True

        duel['status'] = 'completed'
        changed = True

    return changed


def update_chat_display_name_for_profile(profile_key, new_display_name, login_name, previous_display_name):
    """Update past chat messages for a profile when display name changes"""
    try:
        messages = load_chat_messages()
        if not messages:
            return 0

        old_names = {str(login_name).strip(), str(previous_display_name).strip()}
        old_names = {name for name in old_names if name}

        updated_count = 0
        for msg in messages:
            msg_profile_key = str(msg.get('profile_key', '')).strip()
            msg_user = str(msg.get('user', '')).strip()

            belongs_to_profile = msg_profile_key == profile_key
            likely_legacy_message = (not msg_profile_key) and (msg_user in old_names)

            if belongs_to_profile or likely_legacy_message:
                if msg_user != new_display_name or msg_profile_key != profile_key:
                    msg['user'] = new_display_name
                    msg['profile_key'] = profile_key
                    updated_count += 1

        if updated_count > 0:
            with open(CHAT_FILE, 'w') as f:
                json.dump(messages[-50:], f, indent=2)

        return updated_count
    except Exception:
        return 0


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


def normalize_profiles(profiles):
    """Ensure profile records have expected defaults"""
    if not isinstance(profiles, dict):
        return {}, False

    changed = False
    today = datetime.now().strftime("%Y-%m-%d")

    for profile_key, profile in profiles.items():
        if not isinstance(profile, dict):
            profiles[profile_key] = {
                'name': profile_key,
                'pin_hash': '',
                'display_name': profile_key,
                'name_color': '#4F8BF9',
                'avatar_emoji': '🙂',
                'avatar_image_b64': '',
                'join_date': today,
                'blocked_profiles': []
            }
            changed = True
            continue

        if 'name' not in profile:
            profile['name'] = profile_key
            changed = True
        if 'display_name' not in profile:
            profile['display_name'] = profile.get('name', profile_key)
            changed = True
        if 'name_color' not in profile:
            profile['name_color'] = '#4F8BF9'
            changed = True
        if 'avatar_emoji' not in profile:
            profile['avatar_emoji'] = '🙂'
            changed = True
        if 'avatar_image_b64' not in profile:
            profile['avatar_image_b64'] = ''
            changed = True
        if 'join_date' not in profile:
            profile['join_date'] = today
            changed = True
        if 'blocked_profiles' not in profile or not isinstance(profile.get('blocked_profiles'), list):
            profile['blocked_profiles'] = []
            changed = True

    return profiles, changed


def get_profile_chat_style(profile_key, profiles):
    """Get chat style settings for a profile"""
    profile = profiles.get(profile_key, {}) if isinstance(profiles, dict) else {}
    return {
        'name_color': profile.get('name_color', '#4F8BF9'),
        'avatar_emoji': profile.get('avatar_emoji', '🙂'),
        'avatar_image_b64': profile.get('avatar_image_b64', '')
    }


def get_avatar_for_chat(profile_style):
    """Build Streamlit chat avatar from profile settings"""
    avatar_b64 = profile_style.get('avatar_image_b64', '')
    if avatar_b64:
        try:
            return base64.b64decode(avatar_b64)
        except Exception:
            pass
    return profile_style.get('avatar_emoji', '🙂')


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
        return 'YOU FUCKING FAILED, LOSER!'

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


def letter_to_base_points(letter):
    """Convert letter grade to base 4.0 GPA points"""
    points_map = {
        'A': 4.0,
        'A-': 3.7,
        'B+': 3.3,
        'B': 3.0,
        'B-': 2.7,
        'C+': 2.3,
        'C': 2.0,
        'C-': 1.7,
        'D+': 1.3,
        'D': 1.0,
        'D-': 0.7,
        'F': 0.0,
    }
    return points_map.get(letter, 0.0)


def calculate_gpa(scale_max):
    """Calculate GPA across all classes using an adjustable maximum scale"""
    class_points = []

    for class_name in st.session_state.classes.keys():
        _, letter = calculate_overall_grade(class_name)
        if letter is not None:
            base_points = letter_to_base_points(letter)
            adjusted_points = (base_points / 4.0) * scale_max
            class_points.append(adjusted_points)

    if not class_points:
        return None

    return sum(class_points) / len(class_points)

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
                profiles, profiles_changed = normalize_profiles(profiles)
                if profiles_changed:
                    save_profiles(profiles)

                if profile_key in profiles:
                    saved_hash = profiles[profile_key].get('pin_hash', '')
                    if saved_hash != hash_pin(pin_value):
                        st.error("Incorrect PIN")
                        st.stop()
                else:
                    profiles[profile_key] = {
                        'name': profile_input.strip(),
                        'pin_hash': hash_pin(pin_value),
                        'display_name': profile_input.strip(),
                        'name_color': '#4F8BF9',
                        'avatar_emoji': '🙂',
                        'avatar_image_b64': '',
                        'join_date': datetime.now().strftime("%Y-%m-%d"),
                        'blocked_profiles': []
                    }
                    if not save_profiles(profiles):
                        st.stop()

                profile_record = profiles.get(profile_key, {})
                profile_record['name'] = profile_input.strip()
                profile_record.setdefault('display_name', profile_input.strip())
                profile_record.setdefault('name_color', '#4F8BF9')
                profile_record.setdefault('avatar_emoji', '🙂')
                profile_record.setdefault('avatar_image_b64', '')
                profile_record.setdefault('join_date', datetime.now().strftime("%Y-%m-%d"))
                profile_record.setdefault('blocked_profiles', [])
                profiles[profile_key] = profile_record
                save_profiles(profiles)

                st.session_state.profile_name = profile_input.strip()
                st.session_state.display_name = profile_record.get('display_name', profile_input.strip())
                st.session_state.profile_key = profile_key
                st.session_state.classes = load_profile_data(profile_key)
                st.session_state.current_class = None
                st.session_state.profile_loaded = True
                st.session_state.last_loaded_profile = profile_input.strip()
                st.rerun()
    with col2:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.profile_name = ""
            st.session_state.display_name = ""
            st.session_state.profile_key = ""
            st.session_state.profile_loaded = False
            st.session_state.classes = {}
            st.session_state.current_class = None
            st.rerun()

    if st.session_state.profile_loaded:
        st.caption(f"Profile: {st.session_state.profile_name}")

        profiles = load_profiles()
        profiles, profiles_changed = normalize_profiles(profiles)
        if profiles_changed:
            save_profiles(profiles)
        current_profile = profiles.get(st.session_state.profile_key, {})
        current_display_name = current_profile.get('display_name', st.session_state.profile_name)
        current_name_color = current_profile.get('name_color', '#4F8BF9')
        current_avatar_emoji = current_profile.get('avatar_emoji', '😎')

        with st.expander("Chat Profile"):
            selected_display_name = st.text_input(
                "Display Name",
                value=current_display_name,
                max_chars=30,
                key="profile_display_name_input"
            )

            selected_name_color = st.color_picker(
                "Name Color",
                value=current_name_color,
                key="profile_name_color_picker"
            )

            selected_avatar_emoji = st.selectbox(
                "Avatar Emoji",
                options=['🙂', '😎', '🧠', '🎯', '🔥', '⭐', '🐱', '🐶', '🦊', '🐼'],
                index=['🙂', '😎', '🧠', '🎯', '🔥', '⭐', '🐱', '🐶', '🦊', '🐼'].index(current_avatar_emoji)
                if current_avatar_emoji in ['🙂', '😎', '🧠', '🎯', '🔥', '⭐', '🐱', '🐶', '🦊', '🐼'] else 0,
                key="profile_avatar_emoji_select"
            )

            uploaded_avatar = st.file_uploader(
                "Profile Picture (optional)",
                type=["png", "jpg", "jpeg", "webp"],
                key="profile_avatar_upload"
            )

            preview_style = get_profile_chat_style(st.session_state.profile_key, profiles)
            preview_style['name_color'] = selected_name_color
            preview_style['avatar_emoji'] = selected_avatar_emoji
            if uploaded_avatar is not None:
                preview_style['avatar_image_b64'] = base64.b64encode(uploaded_avatar.getvalue()).decode("utf-8")

            avatar_preview = get_avatar_for_chat(preview_style)
            if isinstance(avatar_preview, bytes):
                st.image(avatar_preview, width=60)
            else:
                st.markdown(f"### {avatar_preview}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Save Chat Style", use_container_width=True):
                    cleaned_display_name = selected_display_name.strip()
                    if not cleaned_display_name:
                        st.warning("Display name cannot be empty")
                        st.stop()

                    profile_data = profiles.get(st.session_state.profile_key, {})
                    previous_display_name = profile_data.get('display_name', st.session_state.display_name or st.session_state.profile_name)
                    profile_data['name'] = st.session_state.profile_name
                    profile_data['pin_hash'] = profile_data.get('pin_hash', '')
                    profile_data['display_name'] = cleaned_display_name
                    profile_data['name_color'] = selected_name_color
                    profile_data['avatar_emoji'] = selected_avatar_emoji
                    profile_data.setdefault('join_date', datetime.now().strftime("%Y-%m-%d"))
                    profile_data.setdefault('blocked_profiles', [])
                    if uploaded_avatar is not None:
                        profile_data['avatar_image_b64'] = base64.b64encode(uploaded_avatar.getvalue()).decode("utf-8")
                    else:
                        profile_data.setdefault('avatar_image_b64', '')
                    profiles[st.session_state.profile_key] = profile_data
                    save_profiles(profiles)

                    updated_messages = update_chat_display_name_for_profile(
                        st.session_state.profile_key,
                        cleaned_display_name,
                        st.session_state.profile_name,
                        previous_display_name
                    )

                    st.session_state.display_name = cleaned_display_name
                    if updated_messages > 0:
                        st.success(f"Chat profile updated ({updated_messages} old messages renamed)")
                    else:
                        st.success("Chat profile updated")
            with col_b:
                if st.button("Remove Picture", use_container_width=True):
                    profile_data = profiles.get(st.session_state.profile_key, {})
                    profile_data['name'] = st.session_state.profile_name
                    profile_data['pin_hash'] = profile_data.get('pin_hash', '')
                    profile_data['display_name'] = selected_display_name.strip() or st.session_state.display_name or st.session_state.profile_name
                    profile_data['name_color'] = selected_name_color
                    profile_data['avatar_emoji'] = selected_avatar_emoji
                    profile_data.setdefault('join_date', datetime.now().strftime("%Y-%m-%d"))
                    profile_data.setdefault('blocked_profiles', [])
                    profile_data['avatar_image_b64'] = ''
                    profiles[st.session_state.profile_key] = profile_data
                    save_profiles(profiles)
                    st.success("Profile picture removed")

        with st.expander("Blocked Users"):
            current_profile = profiles.get(st.session_state.profile_key, {})
            blocked_keys = list(current_profile.get('blocked_profiles', []))

            if blocked_keys:
                for blocked_key in blocked_keys:
                    blocked_profile = profiles.get(blocked_key, {})
                    blocked_name = blocked_profile.get('display_name') or blocked_profile.get('name') or blocked_key

                    row_col1, row_col2 = st.columns([3, 1])
                    with row_col1:
                        st.write(blocked_name)
                    with row_col2:
                        if st.button("Unblock", key=f"sidebar_unblock_{blocked_key}", use_container_width=True):
                            updated_blocked = [key for key in blocked_keys if key != blocked_key]
                            current_profile['blocked_profiles'] = updated_blocked
                            profiles[st.session_state.profile_key] = current_profile
                            save_profiles(profiles)
                            st.rerun()
            else:
                st.caption("No blocked users")

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

        gpa_scale = st.number_input(
            "GPA Scale",
            min_value=1.0,
            max_value=10.0,
            value=4.0,
            step=0.1,
            help="Adjust the maximum GPA scale (for example, 4.0 or 5.0)",
            key="gpa_scale_input"
        )

        gpa_value = calculate_gpa(gpa_scale)
        if gpa_value is not None:
            st.metric("GPA", f"{gpa_value:.2f} / {gpa_scale:.1f}")
        else:
            st.caption("GPA: No graded classes yet")

        for class_name in sorted(st.session_state.classes.keys()):
            overall, letter = calculate_overall_grade(class_name)
            grade_text = "No grade"
            if overall is not None and letter is not None:
                grade_text = f"{overall:.1f}% ({letter})"

            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                if st.button(class_name, key=f"class_{class_name}", use_container_width=True):
                    st.session_state.current_class = class_name
                    st.rerun()
            with col2:
                st.caption(grade_text)
            with col3:
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
    chat_title_col, chat_sort_col, chat_refresh_col = st.columns([4, 2, 1])
    with chat_title_col:
        st.subheader("Message Board")
    with chat_sort_col:
        st.segmented_control(
            "Order",
            options=["Newest", "Oldest"],
            key="chat_sort_order",
            label_visibility="collapsed"
        )
    with chat_refresh_col:
        if st.button("⟳ Refresh", key="refresh_chat_btn", use_container_width=True):
            st.rerun()
    
    # Display messages
    messages = load_chat_messages()
    profiles = load_profiles()
    profiles, profiles_changed = normalize_profiles(profiles)
    if profiles_changed:
        save_profiles(profiles)

    duel_data = load_duels()
    if resolve_due_duels_and_announce(duel_data, profiles):
        save_duels(duel_data)
        messages = load_chat_messages()

    current_profile_key = st.session_state.profile_key if st.session_state.profile_loaded else ""
    blocked_profiles = set()
    if current_profile_key and current_profile_key in profiles:
        blocked_profiles = set(profiles[current_profile_key].get('blocked_profiles', []))

    if st.session_state.profile_loaded and current_profile_key:
        with st.expander("⚔️ Duel Arena"):
            other_profile_keys = [
                key for key in sorted(profiles.keys())
                if key != current_profile_key
            ]

            st.caption("Mini-game: Rock • Paper • Scissors")
            if other_profile_keys:
                opponent_key = st.selectbox(
                    "Challenge User",
                    options=other_profile_keys,
                    format_func=lambda key: get_profile_display_name(key, profiles),
                    key="duel_opponent_select"
                )
                if st.button("Send Duel Challenge", key="send_duel_challenge", use_container_width=True):
                    has_existing = any(
                        duel.get('status') in {'pending', 'active'} and
                        {duel.get('challenger_key'), duel.get('challenged_key')} == {current_profile_key, opponent_key}
                        for duel in duel_data
                    )
                    if has_existing:
                        st.warning("A pending or active duel with this user already exists")
                    else:
                        duel_data.append({
                            'id': f"duel_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                            'challenger_key': current_profile_key,
                            'challenged_key': opponent_key,
                            'status': 'pending',
                            'challenger_move': None,
                            'challenged_move': None,
                            'created_at': datetime.now().isoformat(),
                            'announced': False
                        })
                        save_duels(duel_data)
                        challenger_name = get_profile_display_name(current_profile_key, profiles)
                        opponent_name = get_profile_display_name(opponent_key, profiles)
                        save_system_chat_message(f"⚔️ {challenger_name} challenged {opponent_name} to a duel!")
                        st.success("Challenge sent")
                        st.rerun()
            else:
                st.caption("No other users available to challenge")

            incoming_challenges = [
                duel for duel in duel_data
                if duel.get('status') == 'pending' and duel.get('challenged_key') == current_profile_key
            ]
            if incoming_challenges:
                st.markdown("**Incoming Challenges**")
                for duel in incoming_challenges:
                    challenger_name = get_profile_display_name(duel.get('challenger_key', ''), profiles)
                    row1, row2 = st.columns(2)
                    with row1:
                        if st.button(f"Accept {challenger_name}", key=f"accept_duel_{duel['id']}", use_container_width=True):
                            duel['status'] = 'active'
                            save_duels(duel_data)
                            save_system_chat_message(f"⚔️ {get_profile_display_name(current_profile_key, profiles)} accepted {challenger_name}'s duel!")
                            st.rerun()
                    with row2:
                        if st.button(f"Decline {challenger_name}", key=f"decline_duel_{duel['id']}", use_container_width=True):
                            duel['status'] = 'declined'
                            save_duels(duel_data)
                            save_system_chat_message(f"⚔️ {get_profile_display_name(current_profile_key, profiles)} declined {challenger_name}'s duel.")
                            st.rerun()

            active_duels = [
                duel for duel in duel_data
                if duel.get('status') == 'active' and
                current_profile_key in {duel.get('challenger_key'), duel.get('challenged_key')}
            ]
            if active_duels:
                st.markdown("**Active Duels**")
                for duel in active_duels:
                    challenger_key = duel.get('challenger_key', '')
                    challenged_key = duel.get('challenged_key', '')
                    challenger_name = get_profile_display_name(challenger_key, profiles)
                    challenged_name = get_profile_display_name(challenged_key, profiles)

                    if current_profile_key == challenger_key:
                        your_move = duel.get('challenger_move')
                        your_field = 'challenger_move'
                    else:
                        your_move = duel.get('challenged_move')
                        your_field = 'challenged_move'

                    st.write(f"{challenger_name} vs {challenged_name}")
                    if your_move:
                        st.caption(f"Your move is locked: {your_move}. Waiting for opponent...")
                    else:
                        move_choice = st.radio(
                            "Choose your move",
                            options=['Rock', 'Paper', 'Scissors'],
                            key=f"move_choice_{duel['id']}",
                            horizontal=True
                        )
                        if st.button("Submit Move", key=f"submit_move_{duel['id']}", use_container_width=True):
                            duel[your_field] = move_choice
                            save_duels(duel_data)
                            if resolve_due_duels_and_announce(duel_data, profiles):
                                save_duels(duel_data)
                            st.rerun()

    if st.session_state.selected_chat_profile_key:
        selected_profile_key = st.session_state.selected_chat_profile_key
        selected_profile = profiles.get(selected_profile_key, {})
        selected_style = get_profile_chat_style(selected_profile_key, profiles)
        selected_avatar = get_avatar_for_chat(selected_style)
        selected_name = selected_profile.get('display_name') or st.session_state.selected_chat_profile_name or selected_profile.get('name') or "Unknown User"
        selected_join_date = selected_profile.get('join_date', 'Unknown')

        with st.container(border=True):
            if isinstance(selected_avatar, bytes):
                st.image(selected_avatar, width=140)
            else:
                st.markdown(f"# {selected_avatar}")

            st.markdown(
                f"<h1 style='margin-bottom:0; color:{selected_style['name_color']};'>{html.escape(selected_name)}</h1>",
                unsafe_allow_html=True
            )
            st.caption(f"Joined: {selected_join_date}")

            recent_messages = [
                msg for msg in messages
                if (msg.get('profile_key') or sanitize_profile_key(msg['user'])) == selected_profile_key
            ][-10:]
            if recent_messages:
                st.markdown("**Previous Messages**")
                for old_msg in recent_messages:
                    st.write(f"• {old_msg['message']}")
            else:
                st.caption("No previous messages")

            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if current_profile_key and selected_profile_key and selected_profile_key != current_profile_key:
                    is_blocked = selected_profile_key in blocked_profiles
                    button_label = "Unblock User" if is_blocked else "Block User"
                    if st.button(button_label, key=f"toggle_block_{selected_profile_key}", use_container_width=True):
                        current_profile = profiles.get(current_profile_key, {})
                        current_blocked = set(current_profile.get('blocked_profiles', []))
                        if selected_profile_key in current_blocked:
                            current_blocked.remove(selected_profile_key)
                        else:
                            current_blocked.add(selected_profile_key)
                        current_profile['blocked_profiles'] = sorted(current_blocked)
                        profiles[current_profile_key] = current_profile
                        save_profiles(profiles)
                        st.rerun()
            with action_col2:
                if st.button("Close Profile", key="close_viewed_profile", use_container_width=True):
                    st.session_state.selected_chat_profile_key = ""
                    st.session_state.selected_chat_profile_name = ""
                    st.rerun()

    visible_messages = [
        msg for msg in messages
        if (msg.get('profile_key') or sanitize_profile_key(msg['user'])) not in blocked_profiles
    ]

    if visible_messages:
        chat_container = st.container(height=460, border=True)
        with chat_container:
            if st.session_state.chat_sort_order == "Newest":
                recent_window = list(reversed(visible_messages))[:200]
            else:
                recent_window = visible_messages[:200]
            for idx, msg in enumerate(recent_window):
                message_profile_key = msg.get('profile_key') or sanitize_profile_key(msg['user'])
                profile_style = get_profile_chat_style(message_profile_key, profiles)
                bubble_type = "user" if current_profile_key and message_profile_key == current_profile_key else "assistant"
                if current_profile_key and message_profile_key == current_profile_key:
                    bubble_type = "user"
                bubble_avatar = get_avatar_for_chat(profile_style)
                safe_user_name = html.escape(msg['user'])
                with st.chat_message(bubble_type, avatar=bubble_avatar):
                    if st.button(msg['user'], key=f"view_user_{idx}_{message_profile_key}"):
                        st.session_state.selected_chat_profile_key = message_profile_key
                        st.session_state.selected_chat_profile_name = msg['user']
                        st.rerun()
                    st.markdown(
                        f"<span style='font-weight:700; color:{profile_style['name_color']};'>{safe_user_name}</span>",
                        unsafe_allow_html=True
                    )
                    st.write(msg['message'])
    else:
        if blocked_profiles:
            st.caption("No visible messages (blocked users are hidden).")
        else:
            st.caption("No messages yet. Start the conversation.")
    
    # Input for new message
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            new_message = st.text_input("Message", key="chat_input", label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("Send")
        
        if submitted and new_message:
            username = st.session_state.display_name if st.session_state.profile_loaded else "Anonymous"
            save_chat_message(username, new_message)
            st.rerun()

# Footer
st.caption("Made by seb.")
