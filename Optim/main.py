# main.py
import tkinter as tk
from tkinter import messagebox, simpledialog, BooleanVar, Checkbutton, Label, Scrollbar
import file_cleaner
import ram_optimizer
import program_uninstaller
import process_manager
import ctypes
import sys
import os
import json

# Estado de permisos
app_permissions = {
    "file_modification": False,
    "process_management": False
}

# Diccionario de exclusiones con nombres cortos
exclusion_groups = {
    "Core": "Windows core processes",
    "Utils": "System utilities",
    "MS Services": "Microsoft services",
    "Misc": "Other background tasks",
    "Browsers": "Web browsers"
}

# Cargar las configuraciones de exclusión desde un archivo JSON
try:
    with open('exclusion_config.json', 'r') as f:
        exclusion_config = json.load(f)
except FileNotFoundError:
    exclusion_config = {k: {"enabled": True, "close": True, "processes": {}} for k in exclusion_groups.keys()}
    with open('exclusion_config.json', 'w') as f:
        json.dump(exclusion_config, f)

# Placeholder para el contenido de exclusión
current_view = "main"

def save_exclusions():
    with open('exclusion_config.json', 'w') as f:
        json.dump(exclusion_config, f)
    messagebox.showinfo("Exclusions", "Exclusions preferences saved.")

def elevate_privileges():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        if messagebox.askyesno("Permissions", "This action requires administrative privileges. Elevate?"):
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    else:
        messagebox.showinfo("Permissions", "Already running with administrative privileges.")

def on_optimize():
    try:
        if not app_permissions["file_modification"]:
            messagebox.showwarning("Permission", "File modification permissions are required for some operations.")
        else:
            file_cleaner.clean_temp_files()
        
        if not app_permissions["process_management"]:
            messagebox.showwarning("Permission", "Process management permissions are required for RAM and process optimization.")
        else:
            ram_optimizer.optimize_ram()
            process_manager.close_unused_processes(exclusion_config)
        
        messagebox.showinfo("Optimization", "System optimization completed for permitted operations.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during optimization: {e}")

def manage_exclusions():
    global current_view
    current_view = "exclusions"
    
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    # Crear y mostrar el contenido de exclusión
    exclusion_content = tk.Frame(main_frame, bg="lightgray")
    exclusion_content.pack(fill="both", expand=True)
    
    # Scrollbar y Listbox para mostrar grupos y procesos
    scrollbar = Scrollbar(exclusion_content, orient="vertical")
    listbox = tk.Listbox(exclusion_content, yscrollcommand=scrollbar.set, width=70, height=20)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)

    for group_name, group in process_manager.exclusion_groups.items():
        group_enabled = BooleanVar(value=exclusion_config[group_name]["enabled"])
        group_close = BooleanVar(value=exclusion_config[group_name]["close"])
        
        check_frame = tk.Frame(exclusion_content)
        check_frame.pack(pady=2, anchor="w")
        
        Checkbutton(check_frame, text=f"{group_name} - {group['description']}", variable=group_enabled, command=lambda g=group_name, v=group_enabled: on_group_toggle(g, v.get())).pack(side="left")
        Checkbutton(check_frame, text="Close?", variable=group_close, command=lambda g=group_name, v=group_close: on_group_close_toggle(g, v.get())).pack(side="left")
        
        listbox.insert('end', f"{group_name} - {group['description']}")
        
        for process in group['processes']:
            process_var = BooleanVar(value=exclusion_config[group_name]["processes"].get(process.lower(), True if process in group['safe_to_close'] else False))
            process_check = Checkbutton(exclusion_content, text=f"  - {process}", variable=process_var, command=lambda p=process.lower(), v=process_var, g=group_name: on_process_toggle(g, p, v.get()))
            process_check.pack(pady=1, anchor="w")
            listbox.insert('end', f"  - {process}")

    # Botones para guardar y regresar
    tk.Button(exclusion_content, text="Save", command=save_exclusions).pack(side="bottom", pady=5)
    tk.Button(exclusion_content, text="Back", command=main_menu).pack(side="bottom", pady=5)

def on_group_toggle(group_name, value):
    exclusion_config[group_name]["enabled"] = value

def on_group_close_toggle(group_name, value):
    exclusion_config[group_name]["close"] = value

def on_process_toggle(group_name, process_name, value):
    if group_name not in exclusion_config:
        exclusion_config[group_name] = {"processes": {}}
    exclusion_config[group_name]["processes"][process_name] = value

def main_menu():
    global current_view
    current_view = "main"
    
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    # Reconstruir la interfaz principal
    optimize_button = tk.Button(main_frame, text="Optimize", command=on_optimize, font=('Arial', 14))
    optimize_button.pack(padx=10, pady=10)

    # Frame para los botones de configuración
    config_frame = tk.Frame(main_frame, bg="lightgray")
    config_frame.pack(fill="x")

    # Botones de configuración
    config_buttons = [
        ("Exclusions", manage_exclusions),
        ("RAM Config", configure_ram),
        ("Temp Files", configure_temp_files),
        ("Elevate Privileges", elevate_privileges)
    ]

    for i, (text, command) in enumerate(config_buttons):
        button = tk.Button(config_frame, text=text, command=command, font=('Arial', 10))
        button.pack(side="left", padx=5, pady=5)

def configure_ram():
    max_ram = simpledialog.askinteger("RAM Configuration", "Enter the maximum amount of RAM to clean in MB:", minvalue=0, maxvalue=100000)
    if max_ram is not None:
        ram_optimizer.set_max_ram(max_ram)
        messagebox.showinfo("RAM Configuration", f"RAM cleaning limit set to {max_ram} MB")

def configure_temp_files():
    if messagebox.askyesno("Temp Files Permission", "Allow the app to modify temporary files?"):
        file_cleaner.set_temp_permission(True)
    else:
        file_cleaner.set_temp_permission(False)

root = tk.Tk()
root.title("System Optimizer")

# Configurar el tamaño inicial de la ventana
root.geometry("400x500")  # Aumentar el tamaño para acomodar más contenido

# Frame principal para el contenido dinámico
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Inicializar con el menú principal
main_menu()

root.mainloop()