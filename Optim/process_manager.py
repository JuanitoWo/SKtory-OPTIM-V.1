# process_manager.py
import psutil
import time
from datetime import datetime, timedelta
import json

# Grupos de exclusiones con descripciones y procesos asociados
exclusion_groups = {
    "Core": {
        "description": "Windows core processes",
        "processes": ["explorer.exe", "system", "svchost.exe", "wininit.exe", "services.exe", "lsass.exe", "smss.exe", "csrss.exe", "winlogon.exe"],
        "safe_to_close": []
    },
    "Utils": {
        "description": "System utilities",
        "processes": ["taskhost.exe", "taskhostw.exe", "dllhost.exe", "conhost.exe", "fontdrvhost.exe", "sihost.exe", "SearchIndexer.exe", "SearchProtocolHost.exe", "SearchUI.exe", "RuntimeBroker.exe"],
        "safe_to_close": ["SearchIndexer.exe", "SearchProtocolHost.exe", "SearchUI.exe"]
    },
    "MS Services": {
        "description": "Microsoft services",
        "processes": ["jusched.exe", "wlanext.exe", "msmpeng.exe", "NisSrv.exe", "SecurityHealthService.exe", "OneDrive.exe"],
        "safe_to_close": ["OneDrive.exe"]
    },
    "Misc": {
        "description": "Other background tasks",
        "processes": ["ctfmon.exe", "AdobeARM.exe", "AdobeARMhelper.exe"],
        "safe_to_close": ["AdobeARM.exe", "AdobeARMhelper.exe"]
    },
    "Browsers": {
        "description": "Web browsers",
        "processes": ["msedge.exe", "chrome.exe", "firefox.exe"],
        "safe_to_close": []
    }
}

def close_unused_processes(exclusion_config):
    try:
        now = datetime.now()
        two_hours_ago = now - timedelta(hours=2)
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                process_creation_time = datetime.fromtimestamp(proc.info['create_time'])
                if process_creation_time < two_hours_ago:
                    process_name = proc.info['name'].lower()
                    for group_name, group in exclusion_groups.items():
                        if process_name in [p.lower() for p in group['processes']]:
                            if not exclusion_config[group_name]["enabled"]:  # Si el grupo está deshabilitado
                                if exclusion_config[group_name]["close"]:  # Solo si está marcado para cerrar
                                    if process_name in [p.lower() for p in group['safe_to_close']]:
                                        p = psutil.Process(proc.info['pid'])
                                        if p.is_running():
                                            p.terminate()  # Intenta cerrar el proceso suavemente
                                            time.sleep(2)  # Esperamos un poco para que el proceso pueda cerrarse
                                            if p.is_running():
                                                p.kill()  # Forzar el cierre si no responde a terminate()
                                            print(f"Closed process: {proc.info['name']} (PID: {proc.info['pid']})")
                            break  # No es necesario continuar buscando una vez que se ha encontrado el grupo
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # Ignoramos los errores para procesos no accesibles o que ya no existen
    except Exception as e:
        print(f"Failed to manage processes: {e}")