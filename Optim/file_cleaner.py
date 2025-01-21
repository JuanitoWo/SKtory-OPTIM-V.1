# file_cleaner.py
import os
from tkinter import messagebox

def clean_temp_files():
    try:
        temp_dir = os.environ.get('TEMP')
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                import shutil  # Importamos shutil solo si es necesario
                shutil.rmtree(item_path, ignore_errors=True)
        messagebox.showinfo("Cleaning", "Temporary files cleaned.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clean temp files: {e}")