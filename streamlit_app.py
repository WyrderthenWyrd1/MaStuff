import streamlit as st
import json
import os
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Grade Calculator",
    page_icon="📚",
    layout="wide"
)

# Data file location
DATA_FILE = "grade_data.json"

# Initialize session state
if 'classes' not in st.session_state:
    st.session_state.classes = {}
    # Load existing data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                st.session_state.classes = json.load(f)
        except Exception as e:
            st.error(f"Failed to load data: {str(e)}")

if 'current_class' not in st.session_state:
    st.session_state.current_class = None


def get_class_icon(class_name):
    """Get icon for a class, with fallback for older saved data"""
    class_data = st.session_state.classes.get(class_name, {})
    return class_data.get('icon', '📖')

def save_data():
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
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
st.title("📚 Grade Calculator")

# Sidebar for class management
with st.sidebar:
    st.header("Classes")
    
    # Add new class
    with st.expander("➕ Add New Class"):
        class_icon_choices = ["📖", "📘", "📗", "📕", "🧪", "🧮", "📝", "💻", "🎨", "🌍", "🎵", "🏫"]
        col1, col2 = st.columns([4, 1])
        with col1:
            new_class = st.text_input("Class Name", key="new_class_input")
        with col2:
            new_class_icon = st.selectbox("Icon", options=class_icon_choices, index=0, key="new_class_icon")
        if st.button("Add Class"):
            if new_class:
                if new_class in st.session_state.classes:
                    st.error("Class already exists!")
                else:
                    st.session_state.classes[new_class] = {
                        'icon': new_class_icon,
                        'categories': {}
                    }
                    st.session_state.current_class = new_class
                    if save_data():
                        st.success(f"Added {new_class}!")
                        st.rerun()
            else:
                st.warning("Please enter a class name")
    
    # List classes
    if st.session_state.classes:
        st.subheader("Your Classes")
        for class_name in sorted(st.session_state.classes.keys()):
            class_icon = get_class_icon(class_name)
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"{class_icon} {class_name}", key=f"class_{class_name}", use_container_width=True):
                    st.session_state.current_class = class_name
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_class_{class_name}"):
                    del st.session_state.classes[class_name]
                    if st.session_state.current_class == class_name:
                        st.session_state.current_class = None
                    save_data()
                    st.rerun()
    else:
        st.info("No classes yet. Add one above!")

# Main content area
if st.session_state.current_class:
    class_name = st.session_state.current_class
    class_icon = get_class_icon(class_name)
    st.header(f"{class_icon} {class_name}")
    
    # Calculate and display overall grade
    overall, letter = calculate_overall_grade(class_name)
    if overall is not None:
        st.markdown(f"### Current Grade: **{overall:.2f}%** ({letter})")
    else:
        st.info("Add categories and assignments to see your grade")
    
    st.divider()
    
    # Add category section
    with st.expander("➕ Add New Category"):
        col1, col2 = st.columns(2)
        with col1:
            cat_name = st.text_input("Category Name", key="new_cat_name")
        with col2:
            cat_weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0, value=0.0, key="new_cat_weight")
        
        if st.button("Add Category"):
            if not cat_name:
                st.warning("Please enter a category name")
            elif cat_name in st.session_state.classes[class_name]['categories']:
                st.error("Category already exists!")
            else:
                st.session_state.classes[class_name]['categories'][cat_name] = {
                    'weight': cat_weight,
                    'assignments': []
                }
                if save_data():
                    st.success(f"Added category: {cat_name}")
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
                    st.subheader(f"📁 {cat_name}")
                with col2:
                    st.metric("Weight", f"{cat_data['weight']}%")
                with col3:
                    st.metric("Grade", f"{cat_grade:.1f}%")
                with col4:
                    if st.button("🗑️", key=f"del_cat_{cat_name}"):
                        del st.session_state.classes[class_name]['categories'][cat_name]
                        save_data()
                        st.rerun()
                
                # Add assignment to this category
                with st.expander(f"➕ Add Assignment to {cat_name}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        assign_name = st.text_input("Assignment Name", key=f"assign_name_{cat_name}")
                    with col2:
                        total_points = st.number_input("Total Points", min_value=0.0, value=100.0, key=f"total_{cat_name}")
                    with col3:
                        earned_points = st.number_input("Points Earned", min_value=0.0, value=0.0, key=f"earned_{cat_name}")
                    
                    if st.button("Add Assignment", key=f"add_assign_{cat_name}"):
                        if not assign_name:
                            st.warning("Please enter an assignment name")
                        elif total_points <= 0:
                            st.warning("Total points must be greater than 0")
                        else:
                            st.session_state.classes[class_name]['categories'][cat_name]['assignments'].append({
                                'name': assign_name,
                                'total': total_points,
                                'earned': earned_points
                            })
                            if save_data():
                                st.success(f"Added assignment: {assign_name}")
                                st.rerun()
                
                # Display assignments
                if cat_data['assignments']:
                    for idx, assign in enumerate(cat_data['assignments']):
                        percentage = (assign['earned'] / assign['total'] * 100) if assign['total'] > 0 else 0
                        
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                        with col1:
                            st.write(f"📝 {assign['name']}")
                        with col2:
                            st.write(f"{assign['earned']}/{assign['total']}")
                        with col3:
                            st.write(f"{percentage:.1f}%")
                        with col4:
                            # Edit button
                            if st.button("✏️", key=f"edit_{cat_name}_{idx}"):
                                st.session_state[f'editing_{cat_name}_{idx}'] = True
                                st.rerun()
                        with col5:
                            # Delete button
                            if st.button("🗑️", key=f"del_{cat_name}_{idx}"):
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
                else:
                    st.info(f"No assignments in {cat_name} yet")
                
                st.divider()
    else:
        st.info("No categories yet. Add one above to get started!")

else:
    st.info("👈 Select or create a class from the sidebar to get started!")

# Footer
st.divider()
st.caption("Made by seb.")
