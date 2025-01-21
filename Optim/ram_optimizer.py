# ram_optimizer.py
import psutil
from tkinter import messagebox

def optimize_ram():
    try:
        # Esta es una aproximación básica ya que no hay una forma directa de "optimizar" RAM en Windows
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                p = psutil.Process(proc.info['pid'])
                p.empty_working_set()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # Algunos procesos no permitirán esta operación
        messagebox.showinfo("Optimization", "RAM optimization attempted.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to optimize RAM: {e}")