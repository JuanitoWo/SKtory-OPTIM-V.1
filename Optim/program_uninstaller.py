# program_uninstaller.py
import winreg
import subprocess

def uninstall_program(program_name):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        index = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, index)
                subkey = winreg.OpenKey(key, subkey_name)
                try:
                    display_name, reg_type = winreg.QueryValueEx(subkey, "DisplayName")
                    if program_name.lower() in display_name.lower():
                        uninstall_string, reg_type = winreg.QueryValueEx(subkey, "UninstallString")
                        if uninstall_string:
                            subprocess.run(uninstall_string, shell=True)
                            return True
                except WindowsError:
                    pass
                finally:
                    winreg.CloseKey(subkey)
                index += 1
            except WindowsError:
                break
        return False
    finally:
        winreg.CloseKey(key)