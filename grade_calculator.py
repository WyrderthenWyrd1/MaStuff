import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from typing import Dict, List, Optional


class GradeCalculator:
    """Main application class for the Grade Calculator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Grade Calculator")
        self.root.geometry("900x600")
        
        # Data structure to store all classes
        self.classes = {}  # {class_name: {categories: {cat_name: {weight: float, assignments: []}}}}
        self.current_class = None
        self.class_order = []
        self.gpa_scale_var = tk.DoubleVar(value=4.0)
        self.ap_class_var = tk.BooleanVar(value=False)
        self.data_file = "grade_data.json"
        
        # Load existing data
        self.load_data()
        
        # Set up the UI
        self.setup_ui()
        
        # Update display
        self.update_class_list()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Class list
        left_frame = ttk.LabelFrame(main_frame, text="Classes", padding="5")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Class listbox
        self.class_listbox = tk.Listbox(left_frame, width=25, height=20)
        self.class_listbox.pack(fill=tk.BOTH, expand=True)
        self.class_listbox.bind('<<ListboxSelect>>', self.on_class_select)
        
        # Class management buttons
        class_btn_frame = ttk.Frame(left_frame)
        class_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(class_btn_frame, text="Add Class", command=self.add_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(class_btn_frame, text="Remove", command=self.remove_class).pack(side=tk.LEFT, padx=2)

        self.ap_checkbox = ttk.Checkbutton(
            left_frame,
            text="Selected class is AP",
            variable=self.ap_class_var,
            command=self.toggle_ap_for_selected_class
        )
        self.ap_checkbox.pack(anchor=tk.W, pady=(6, 0))
        
        # Right panel - Categories and assignments
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Category section
        category_frame = ttk.LabelFrame(right_frame, text="Categories & Assignments", padding="5")
        category_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for categories and assignments
        tree_frame = ttk.Frame(category_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=('Weight/Points', 'Earned', 'Percentage'),
                                  yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading('#0', text='Category / Assignment')
        self.tree.heading('Weight/Points', text='Weight/Points')
        self.tree.heading('Earned', text='Earned')
        self.tree.heading('Percentage', text='Grade %')
        
        self.tree.column('#0', width=300)
        self.tree.column('Weight/Points', width=120, anchor=tk.CENTER)
        self.tree.column('Earned', width=100, anchor=tk.CENTER)
        self.tree.column('Percentage', width=100, anchor=tk.CENTER)
        
        # Buttons for category/assignment management
        btn_frame = ttk.Frame(category_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Add Assignment", command=self.add_assignment).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit", command=self.edit_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=2)
        
        # Grade display
        grade_frame = ttk.LabelFrame(right_frame, text="Current Grade", padding="10")
        grade_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.grade_label = ttk.Label(grade_frame, text="No class selected", font=('Arial', 16, 'bold'))
        self.grade_label.pack()

        gpa_controls = ttk.Frame(grade_frame)
        gpa_controls.pack(fill=tk.X, pady=(8, 0))

        ttk.Label(gpa_controls, text="GPA Scale:").pack(side=tk.LEFT)
        self.gpa_scale_spinbox = tk.Spinbox(
            gpa_controls,
            from_=1.0,
            to=10.0,
            increment=0.1,
            width=5,
            textvariable=self.gpa_scale_var,
            command=self.on_gpa_scale_change
        )
        self.gpa_scale_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        self.gpa_scale_spinbox.bind('<Return>', lambda e: self.on_gpa_scale_change())
        self.gpa_scale_spinbox.bind('<FocusOut>', lambda e: self.on_gpa_scale_change())

        self.gpa_label = ttk.Label(grade_frame, text="GPA: N/A")
        self.gpa_label.pack(pady=(6, 0))
    
    def add_class(self):
        """Add a new class"""
        class_name = simpledialog.askstring("Add Class", "Enter class name:")
        if class_name:
            if class_name in self.classes:
                messagebox.showwarning("Duplicate", "Class already exists!")
                return
            
            self.classes[class_name] = {'categories': {}, 'is_ap': False}
            self.update_class_list()
            self.save_data()
            
            # Select the new class
            self.class_listbox.selection_clear(0, tk.END)
            idx = self.class_order.index(class_name)
            self.class_listbox.selection_set(idx)
            self.on_class_select(None)
    
    def remove_class(self):
        """Remove the selected class"""
        if not self.current_class:
            messagebox.showwarning("No Selection", "Please select a class to remove.")
            return
        
        if messagebox.askyesno("Confirm", f"Remove class '{self.current_class}'?"):
            del self.classes[self.current_class]
            self.current_class = None
            self.update_class_list()
            self.update_tree()
            self.save_data()
    
    def on_class_select(self, event):
        """Handle class selection"""
        selection = self.class_listbox.curselection()
        if selection:
            idx = selection[0]
            self.current_class = self.class_order[idx]
            self.ap_class_var.set(bool(self.classes.get(self.current_class, {}).get('is_ap', False)))
            self.update_tree()
    
    def update_class_list(self):
        """Update the class listbox"""
        selected_index = None
        self.class_listbox.delete(0, tk.END)
        self.class_order = sorted(self.classes.keys())
        for idx, class_name in enumerate(self.class_order):
            overall, letter = self.calculate_overall_grade_for_class(class_name)
            ap_tag = " [AP]" if self.classes.get(class_name, {}).get('is_ap', False) else ""
            if overall is not None and letter is not None:
                display_text = f"{class_name}{ap_tag} ({overall:.1f}% {letter})"
            else:
                display_text = f"{class_name}{ap_tag} (No grade)"
            self.class_listbox.insert(tk.END, display_text)

            if self.current_class == class_name:
                selected_index = idx

        if selected_index is not None:
            self.class_listbox.selection_set(selected_index)

        self.update_gpa_display()

    def on_gpa_scale_change(self):
        """Handle GPA scale input changes"""
        self.update_gpa_display()

    def toggle_ap_for_selected_class(self):
        """Toggle AP flag for the currently selected class"""
        if not self.current_class or self.current_class not in self.classes:
            return

        self.classes[self.current_class]['is_ap'] = bool(self.ap_class_var.get())
        self.update_class_list()
        self.update_gpa_display()
        self.save_data()

    def calculate_overall_grade_for_class(self, class_name):
        """Calculate overall percentage and letter grade for one class"""
        if class_name not in self.classes:
            return None, None

        categories = self.classes[class_name]['categories']
        if not categories:
            return None, None

        total_weight = 0
        weighted_grade = 0

        for _, cat_data in categories.items():
            weight = cat_data['weight']
            assignments = cat_data['assignments']

            if assignments:
                total_possible = sum(a['total'] for a in assignments)
                total_earned = sum(a['earned'] for a in assignments)
                cat_percentage = (total_earned / total_possible * 100) if total_possible > 0 else 0
                total_weight += weight
                weighted_grade += cat_percentage * (weight / 100)

        if total_weight > 0:
            overall = weighted_grade / (total_weight / 100)
            return overall, self.get_letter_grade(overall)

        return None, None

    def letter_to_base_points(self, letter):
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

    def calculate_gpa(self, scale_max):
        """Calculate GPA across all classes using an adjustable maximum scale"""
        class_points = []
        ap_bonus_scaled = scale_max / 4.0

        for class_name in self.classes.keys():
            _, letter = self.calculate_overall_grade_for_class(class_name)
            if letter is not None:
                base_points = self.letter_to_base_points(letter)
                adjusted_points = (base_points / 4.0) * scale_max
                if self.classes.get(class_name, {}).get('is_ap', False):
                    adjusted_points = min(scale_max, adjusted_points + ap_bonus_scaled)
                class_points.append(adjusted_points)

        if not class_points:
            return None

        return sum(class_points) / len(class_points)

    def update_gpa_display(self):
        """Refresh GPA display from current classes and selected scale"""
        try:
            scale_max = float(self.gpa_scale_var.get())
        except (ValueError, tk.TclError):
            self.gpa_label.config(text="GPA: Invalid scale")
            return

        if scale_max <= 0:
            self.gpa_label.config(text="GPA: Invalid scale")
            return

        gpa_value = self.calculate_gpa(scale_max)
        if gpa_value is None:
            self.gpa_label.config(text=f"GPA: N/A / {scale_max:.1f}")
        else:
            self.gpa_label.config(text=f"GPA: {gpa_value:.2f} / {scale_max:.1f}")
    
    def add_category(self):
        """Add a new category to the current class"""
        if not self.current_class:
            messagebox.showwarning("No Class", "Please select a class first.")
            return
        
        # Create dialog for category info
        dialog = CategoryDialog(self.root, "Add Category")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            cat_name, weight = dialog.result
            
            if cat_name in self.classes[self.current_class]['categories']:
                messagebox.showwarning("Duplicate", "Category already exists!")
                return
            
            self.classes[self.current_class]['categories'][cat_name] = {
                'weight': weight,
                'assignments': []
            }
            
            self.update_tree()
            self.save_data()
    
    def add_assignment(self):
        """Add an assignment to a category"""
        if not self.current_class:
            messagebox.showwarning("No Class", "Please select a class first.")
            return
        
        # Get selected category
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category first.")
            return
        
        item = selection[0]
        # Check if it's a category (top-level item)
        parent = self.tree.parent(item)
        if parent:  # It's an assignment, get its parent category
            category_name = self.tree.item(parent)['text']
        else:  # It's a category
            category_name = self.tree.item(item)['text']
        
        # Create dialog for assignment info
        dialog = AssignmentDialog(self.root, "Add Assignment")
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            assign_name, total_points, earned_points = dialog.result
            
            self.classes[self.current_class]['categories'][category_name]['assignments'].append({
                'name': assign_name,
                'total': total_points,
                'earned': earned_points
            })
            
            self.update_tree()
            self.save_data()
    
    def edit_item(self):
        """Edit the selected category or assignment"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return
        
        item = selection[0]
        parent = self.tree.parent(item)
        
        if not parent:  # It's a category
            category_name = self.tree.item(item)['text']
            current_weight = self.classes[self.current_class]['categories'][category_name]['weight']
            
            dialog = CategoryDialog(self.root, "Edit Category", category_name, current_weight)
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                new_name, new_weight = dialog.result
                
                # Update category
                cat_data = self.classes[self.current_class]['categories'].pop(category_name)
                cat_data['weight'] = new_weight
                self.classes[self.current_class]['categories'][new_name] = cat_data
                
                self.update_tree()
                self.save_data()
        else:  # It's an assignment
            category_name = self.tree.item(parent)['text']
            assign_name = self.tree.item(item)['text']
            
            # Find the assignment
            assignments = self.classes[self.current_class]['categories'][category_name]['assignments']
            for i, assign in enumerate(assignments):
                if assign['name'] == assign_name:
                    dialog = AssignmentDialog(self.root, "Edit Assignment", 
                                             assign['name'], assign['total'], assign['earned'])
                    self.root.wait_window(dialog.dialog)
                    
                    if dialog.result:
                        new_name, total, earned = dialog.result
                        assignments[i] = {'name': new_name, 'total': total, 'earned': earned}
                        self.update_tree()
                        self.save_data()
                    break
    
    def delete_item(self):
        """Delete the selected category or assignment"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        
        item = selection[0]
        parent = self.tree.parent(item)
        item_name = self.tree.item(item)['text']
        
        if not parent:  # It's a category
            if messagebox.askyesno("Confirm", f"Delete category '{item_name}' and all its assignments?"):
                del self.classes[self.current_class]['categories'][item_name]
                self.update_tree()
                self.save_data()
        else:  # It's an assignment
            if messagebox.askyesno("Confirm", f"Delete assignment '{item_name}'?"):
                category_name = self.tree.item(parent)['text']
                assignments = self.classes[self.current_class]['categories'][category_name]['assignments']
                self.classes[self.current_class]['categories'][category_name]['assignments'] = [
                    a for a in assignments if a['name'] != item_name
                ]
                self.update_tree()
                self.save_data()
    
    def update_tree(self):
        """Update the category/assignment tree view"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.current_class:
            self.grade_label.config(text="No class selected")
            self.update_gpa_display()
            return
        
        categories = self.classes[self.current_class]['categories']
        
        if not categories:
            self.grade_label.config(text="No categories defined")
            self.update_gpa_display()
            return
        
        total_weight = 0
        weighted_grade = 0
        
        # Add categories and assignments to tree
        for cat_name, cat_data in sorted(categories.items()):
            weight = cat_data['weight']
            assignments = cat_data['assignments']
            
            # Calculate category grade
            if assignments:
                total_possible = sum(a['total'] for a in assignments)
                total_earned = sum(a['earned'] for a in assignments)
                cat_percentage = (total_earned / total_possible * 100) if total_possible > 0 else 0
            else:
                cat_percentage = 0
            
            # Insert category
            cat_id = self.tree.insert('', 'end', text=cat_name,
                                      values=(f"{weight}%", '', f"{cat_percentage:.1f}%"))
            
            # Insert assignments under category
            for assign in assignments:
                percentage = (assign['earned'] / assign['total'] * 100) if assign['total'] > 0 else 0
                self.tree.insert(cat_id, 'end', text=assign['name'],
                               values=(f"{assign['total']}", f"{assign['earned']}", f"{percentage:.1f}%"))
            
            # Update overall grade calculation
            if assignments:
                total_weight += weight
                weighted_grade += cat_percentage * (weight / 100)
        
        # Display overall grade
        if total_weight > 0:
            overall = weighted_grade / (total_weight / 100)
            letter = self.get_letter_grade(overall)
            self.grade_label.config(text=f"{overall:.2f}% ({letter})")
        else:
            self.grade_label.config(text="No graded assignments")

        self.update_class_list()
    
    def get_letter_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 98:
            return 'A+'
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
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.classes, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {str(e)}")
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.classes = json.load(f)
                if not isinstance(self.classes, dict):
                    self.classes = {}
                for class_name, class_data in self.classes.items():
                    if not isinstance(class_data, dict):
                        self.classes[class_name] = {'categories': {}, 'is_ap': False}
                        continue
                    class_data.setdefault('categories', {})
                    class_data.setdefault('is_ap', False)
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")


class CategoryDialog:
    """Dialog for adding/editing categories"""
    
    def __init__(self, parent, title, name="", weight=0):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Name
        ttk.Label(self.dialog, text="Category Name:").pack(pady=(10, 0))
        self.name_entry = ttk.Entry(self.dialog, width=30)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, name)
        
        # Weight
        ttk.Label(self.dialog, text="Weight (%):").pack(pady=(5, 0))
        self.weight_entry = ttk.Entry(self.dialog, width=30)
        self.weight_entry.pack(pady=5)
        if weight > 0:
            self.weight_entry.insert(0, str(weight))
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.name_entry.focus()
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def ok(self):
        name = self.name_entry.get().strip()
        weight_str = self.weight_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Invalid Input", "Please enter a category name.")
            return
        
        try:
            weight = float(weight_str)
            if weight < 0 or weight > 100:
                messagebox.showwarning("Invalid Input", "Weight must be between 0 and 100.")
                return
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number for weight.")
            return
        
        self.result = (name, weight)
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


class AssignmentDialog:
    """Dialog for adding/editing assignments"""
    
    def __init__(self, parent, title, name="", total=0, earned=0):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Name
        ttk.Label(self.dialog, text="Assignment Name:").pack(pady=(10, 0))
        self.name_entry = ttk.Entry(self.dialog, width=30)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, name)
        
        # Total points
        ttk.Label(self.dialog, text="Total Points:").pack(pady=(5, 0))
        self.total_entry = ttk.Entry(self.dialog, width=30)
        self.total_entry.pack(pady=5)
        if total > 0:
            self.total_entry.insert(0, str(total))
        
        # Earned points
        ttk.Label(self.dialog, text="Points Earned:").pack(pady=(5, 0))
        self.earned_entry = ttk.Entry(self.dialog, width=30)
        self.earned_entry.pack(pady=5)
        if earned > 0:
            self.earned_entry.insert(0, str(earned))
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        self.name_entry.focus()
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def ok(self):
        name = self.name_entry.get().strip()
        total_str = self.total_entry.get().strip()
        earned_str = self.earned_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Invalid Input", "Please enter an assignment name.")
            return
        
        try:
            total = float(total_str)
            earned = float(earned_str)
            
            if total <= 0:
                messagebox.showwarning("Invalid Input", "Total points must be greater than 0.")
                return
            
            if earned < 0:
                messagebox.showwarning("Invalid Input", "Earned points cannot be negative.")
                return
            
            if earned > total:
                if not messagebox.askyesno("Confirm", 
                    "Earned points exceed total points. Are you sure?"):
                    return
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid numbers for points.")
            return
        
        self.result = (name, total, earned)
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = GradeCalculator(root)
    root.mainloop()


if __name__ == '__main__':
    main()
