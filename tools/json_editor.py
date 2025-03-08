#!/usr/bin/env python3
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import shutil
from pathlib import Path

class JsonEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Donut JSON Editor")
        self.root.geometry("1200x800")
        
        self.project_root = Path(os.path.abspath(__file__)).parent.parent
        self.data_dir = self.project_root / "data"
        
        self.current_file = None
        self.json_data = None
        self.modified = False
        
        self.setup_ui()
        self.load_directory_structure()
        
        self.create_context_menu()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - directory tree
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tree_label = ttk.Label(left_frame, text="Data Files")
        tree_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Right panel - JSON editor
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Top toolbar
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        self.file_label = ttk.Label(toolbar, text="No file selected")
        self.file_label.pack(side=tk.LEFT)
        
        save_btn = ttk.Button(toolbar, text="Save", command=self.save_file)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        add_btn = ttk.Button(toolbar, text="Add Item", command=self.add_item)
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # JSON tree view with columns for key and value
        json_frame = ttk.Frame(right_frame)
        json_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure tree with columns
        self.json_tree = ttk.Treeview(json_frame, columns=("value"))
        self.json_tree.heading("#0", text="Key")
        self.json_tree.heading("value", text="Value")
        self.json_tree.column("#0", width=300)
        self.json_tree.column("value", width=500)
        self.json_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.json_tree.bind("<Double-1>", self.on_item_double_click)
        self.json_tree.bind("<Delete>", self.on_delete_key)
        self.json_tree.bind("<Button-3>", self.show_context_menu)
        
        # Scrollbar for JSON tree
        scrollbar = ttk.Scrollbar(json_frame, orient="vertical", command=self.json_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.json_tree.configure(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(right_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
    
    def load_directory_structure(self):
        self.tree.delete(*self.tree.get_children())
        
        # Add root node
        root_id = self.tree.insert("", "end", text="data", open=True)
        
        # Add subdirectories
        for subdir in sorted(os.listdir(self.data_dir)):
            subdir_path = self.data_dir / subdir
            if subdir_path.is_dir():
                subdir_id = self.tree.insert(root_id, "end", text=subdir, open=True)
                
                # Add JSON files
                for file in sorted(os.listdir(subdir_path)):
                    if file.endswith('.json'):
                        file_path = subdir_path / file
                        self.tree.insert(subdir_id, "end", text=file, values=(str(file_path),))
    
    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item_values = self.tree.item(selected_item[0], "values")
        if not item_values:
            return  # Directory selected, not a file
            
        file_path = item_values[0]
        if self.modified:
            if messagebox.askyesno("Save Changes", "Do you want to save changes to the current file?"):
                self.save_file()
        
        self.load_json_file(file_path)
    
    def load_json_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.json_data = json.load(f)
            
            self.current_file = file_path
            self.file_label.config(text=f"Editing: {os.path.basename(file_path)}")
            self.modified = False
            self.status_var.set(f"Loaded {os.path.basename(file_path)}")
            
            self.display_json_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {str(e)}")
    
    def display_json_data(self):
        self.json_tree.delete(*self.json_tree.get_children())
        
        if not self.json_data:
            return
            
        for key, value in self.json_data.items():
            if isinstance(value, (dict, list)):
                node_type = "" if isinstance(value, dict) else "array"
                node_id = self.json_tree.insert("", "end", text=key, values=(node_type,))
                self.add_json_node(node_id, value)
            else:
                # Display value directly for primitive types
                self.json_tree.insert("", "end", text=key, values=(self.format_value(value),))
    
    def format_value(self, value):
        """Format value for display in the tree"""
        if isinstance(value, bool):
            return str(value).lower()
        elif value is None:
            return "null"
        else:
            return str(value)
    
    def add_json_node(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    node_type = "" if isinstance(value, dict) else "array"
                    child_id = self.json_tree.insert(parent, "end", text=key, values=(node_type,))
                    self.add_json_node(child_id, value)
                else:
                    # Display value directly for primitive types
                    self.json_tree.insert(parent, "end", text=key, values=(self.format_value(value),))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    node_type = "" if isinstance(item, dict) else "array"
                    child_id = self.json_tree.insert(parent, "end", text=f"[{i}]", values=(node_type,))
                else:
                    # Display value directly for primitive types
                    self.json_tree.insert(parent, "end", text=f"[{i}]", values=(self.format_value(item),))
    
    def get_path_to_item(self, item_id):
        path = []
        while item_id:
            item_text = self.json_tree.item(item_id, "text")
            path.insert(0, item_text)
            item_id = self.json_tree.parent(item_id)
        
        return path[1:] if path else path  # Skip root item
    
    def get_value_at_path(self, data, path):
        current = data
        for key in path:
            if isinstance(current, dict):
                if key in current:
                    current = current[key]
                else:
                    return None
            elif isinstance(current, list):
                try:
                    index = int(key.strip('[]'))
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return current
    
    def set_value_at_path(self, data, path, value):
        if not path:
            return value
            
        current = data
        for i, key in enumerate(path[:-1]):
            if isinstance(current, dict):
                if key not in current:
                    current[key] = {} if i < len(path) - 2 else {}
                current = current[key]
            elif isinstance(current, list):
                try:
                    index = int(key.strip('[]'))
                    while len(current) <= index:
                        current.append(None)
                    if current[index] is None:
                        current[index] = {} if i < len(path) - 2 else {}
                    current = current[index]
                except (ValueError, IndexError):
                    return data
        
        last_key = path[-1]
        if isinstance(current, dict):
            current[last_key] = value
        elif isinstance(current, list):
            try:
                index = int(last_key.strip('[]'))
                while len(current) <= index:
                    current.append(None)
                current[index] = value
            except (ValueError, IndexError):
                pass
        
        return data
    
    def delete_value_at_path(self, data, path):
        if not path:
            return {}
            
        if len(path) == 1:
            if isinstance(data, dict) and path[0] in data:
                del data[path[0]]
            elif isinstance(data, list):
                try:
                    index = int(path[0].strip('[]'))
                    if 0 <= index < len(data):
                        data.pop(index)
                except (ValueError, IndexError):
                    pass
            return data
            
        current = data
        for i, key in enumerate(path[:-1]):
            if isinstance(current, dict):
                if key not in current:
                    return data
                current = current[key]
            elif isinstance(current, list):
                try:
                    index = int(key.strip('[]'))
                    if index >= len(current):
                        return data
                    current = current[index]
                except (ValueError, IndexError):
                    return data
            else:
                return data
        
        last_key = path[-1]
        if isinstance(current, dict) and last_key in current:
            del current[last_key]
        elif isinstance(current, list):
            try:
                index = int(last_key.strip('[]'))
                if 0 <= index < len(current):
                    current.pop(index)
            except (ValueError, IndexError):
                pass
        
        return data
    
    def on_item_double_click(self, event):
        item_id = self.json_tree.identify('item', event.x, event.y)
        if not item_id:
            return
        
        # Get the column that was clicked
        column = self.json_tree.identify_column(event.x)
        
        # Get the path to the item
        path = self.get_path_to_item(item_id)
        if not path:
            return
        
        # Get the current value
        current_value = self.get_value_at_path(self.json_data, path)
        
        # If we clicked the value column or it's a leaf node, allow editing
        if column == "#1" or not isinstance(current_value, (dict, list)):
            item_text = self.json_tree.item(item_id, "text")
            
            # If we clicked on the value column, edit the value
            if column == "#1" and not isinstance(current_value, (dict, list)):
                self.edit_value(item_id, path, current_value)
            
            # If we clicked on the key column and it's a primitive value
            elif column == "#0" and not isinstance(current_value, (dict, list)):
                self.edit_value(item_id, path, current_value)
    
    def edit_value(self, item_id, path, current_value):
        item_text = self.json_tree.item(item_id, "text")
        current_display = self.json_tree.item(item_id, "values")[0]
        
        # Ask for the new value
        new_value = simpledialog.askstring(
            "Edit Value", 
            f"Enter new value for {item_text}:",
            initialvalue=current_display
        )
        
        if new_value is not None:  # Not cancelled
            # Try to convert to appropriate type
            try:
                if new_value.lower() == "true":
                    new_value = True
                elif new_value.lower() == "false":
                    new_value = False
                elif new_value.lower() == "null" or new_value.lower() == "none":
                    new_value = None
                elif '.' in new_value and all(c.isdigit() or c == '.' or c == '-' for c in new_value):
                    new_value = float(new_value)
                elif all(c.isdigit() or c == '-' for c in new_value):
                    new_value = int(new_value)
            except (ValueError, AttributeError):
                pass  # Keep as string
            
            # Update the JSON data
            self.json_data = self.set_value_at_path(self.json_data, path, new_value)
            self.modified = True
            self.status_var.set("Modified - not saved")
            self.save_file()  # Auto-save on edit
            
            # Update just this item's display value
            self.json_tree.item(item_id, values=(self.format_value(new_value),))
    
    def on_delete_key(self, event):
        selected_items = self.json_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        item_text = self.json_tree.item(item_id, "text")
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_text}'?"):
            path = self.get_path_to_item(item_id)
            if path:
                self.json_data = self.delete_value_at_path(self.json_data, path)
                self.modified = True
                self.status_var.set("Modified - not saved")
                self.display_json_data()
    
    def add_item(self):
        if not self.json_data:
            messagebox.showinfo("Info", "Please load a JSON file first.")
            return
            
        selected_items = self.json_tree.selection()
        parent_path = []
        
        if selected_items:
            item_id = selected_items[0]
            parent_path = self.get_path_to_item(item_id)
            parent_value = self.get_value_at_path(self.json_data, parent_path)
            
            # If selected item is not a container, use its parent
            if not isinstance(parent_value, (dict, list)):
                if parent_path:
                    parent_path = parent_path[:-1]
                    parent_value = self.get_value_at_path(self.json_data, parent_path)
        else:
            parent_value = self.json_data
        
        # Handle different types of containers
        if isinstance(parent_value, dict):
            key = simpledialog.askstring("Add Item", "Enter key name:")
            if not key:
                return
                
            value_type = simpledialog.askstring(
                "Add Item", 
                "Enter value type (string, number, boolean, object, array):",
                initialvalue="string"
            )
            
            if value_type:
                value_type = value_type.lower()
                if value_type == "string":
                    value = simpledialog.askstring("Add Item", "Enter string value:")
                elif value_type == "number":
                    try:
                        value = float(simpledialog.askstring("Add Item", "Enter number value:"))
                        if value.is_integer():
                            value = int(value)
                    except (ValueError, AttributeError):
                        messagebox.showerror("Error", "Invalid number format")
                        return
                elif value_type == "boolean":
                    value = messagebox.askyesno("Add Item", "Select boolean value")
                elif value_type == "object":
                    value = {}
                elif value_type == "array":
                    value = []
                else:
                    messagebox.showerror("Error", "Invalid type")
                    return
                
                # Update the JSON data
                new_path = parent_path + [key]
                self.json_data = self.set_value_at_path(self.json_data, new_path, value)
                self.modified = True
                self.status_var.set("Modified - not saved")
                self.display_json_data()
                
        elif isinstance(parent_value, list):
            value_type = simpledialog.askstring(
                "Add Item", 
                "Enter value type (string, number, boolean, object, array):",
                initialvalue="string"
            )
            
            if value_type:
                value_type = value_type.lower()
                if value_type == "string":
                    value = simpledialog.askstring("Add Item", "Enter string value:")
                elif value_type == "number":
                    try:
                        value = float(simpledialog.askstring("Add Item", "Enter number value:"))
                        if value.is_integer():
                            value = int(value)
                    except (ValueError, AttributeError):
                        messagebox.showerror("Error", "Invalid number format")
                        return
                elif value_type == "boolean":
                    value = messagebox.askyesno("Add Item", "Select boolean value")
                elif value_type == "object":
                    value = {}
                elif value_type == "array":
                    value = []
                else:
                    messagebox.showerror("Error", "Invalid type")
                    return
                
                # Add to the end of the array
                parent_value.append(value)
                self.modified = True
                self.status_var.set("Modified - not saved")
                self.display_json_data()
    
    def save_file(self):
        if not self.current_file or not self.json_data:
            return
            
        try:
            # Create a backup
            backup_file = f"{self.current_file}.bak"
            shutil.copy2(self.current_file, backup_file)
            
            # Write the updated JSON
            with open(self.current_file, 'w') as f:
                json.dump(self.json_data, f, indent=2)
            
            self.modified = False
            self.status_var.set(f"Saved {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Value", command=self.edit_selected_value)
        self.context_menu.add_command(label="Add Item", command=self.add_item)
        self.context_menu.add_command(label="Delete Item", command=self.delete_selected_item)
    
    def show_context_menu(self, event):
        item = self.json_tree.identify('item', event.x, event.y)
        if item:
            self.json_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def edit_selected_value(self):
        selected_items = self.json_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        path = self.get_path_to_item(item_id)
        if not path:
            return
            
        current_value = self.get_value_at_path(self.json_data, path)
        if not isinstance(current_value, (dict, list)):
            self.edit_value(item_id, path, current_value)
    
    def delete_selected_item(self):
        selected_items = self.json_tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        item_text = self.json_tree.item(item_id, "text")
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_text}'?"):
            path = self.get_path_to_item(item_id)
            if path:
                self.json_data = self.delete_value_at_path(self.json_data, path)
                self.modified = True
                self.status_var.set("Modified - not saved")
                self.save_file()  # Auto-save on delete
                self.display_json_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonEditor(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (
        messagebox.askyesno("Save Changes", "Do you want to save changes before exiting?") and app.save_file() if app.modified else None,
        root.destroy()
    ))
    root.mainloop()
