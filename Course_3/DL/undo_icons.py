import winreg
import os
import shutil
import ctypes

# --- CONFIGURATION ---
# The folder where the installer stored the icons
ICONS_FOLDER = r"C:\Icons\VSCode"

def refresh_explorer():
    print("[*] Refreshing Windows Explorer...")
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

def delete_icon_folder():
    if os.path.exists(ICONS_FOLDER):
        try:
            shutil.rmtree(ICONS_FOLDER)
            print(f"[+] Deleted icon folder: {ICONS_FOLDER}")
        except Exception as e:
            print(f"[-] Could not delete folder (files might be in use): {e}")
    else:
        print("[*] Icon folder already gone.")

def clean_registry():
    print("[*] Scanning Registry for VS Code overrides...")
    
    base_path = "Software\\Classes"
    modified_count = 0
    
    try:
        # Open HKCU\Software\Classes
        classes_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_path, 0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        print("[-] Could not access HKCU\\Software\\Classes")
        return

    # Iterate through all ProgIDs (e.g., Python.File, VSCodeStyle.js, etc.)
    i = 0
    keys_to_check = []
    
    # 1. Collect all keys first (cannot delete while iterating)
    while True:
        try:
            subkey_name = winreg.EnumKey(classes_key, i)
            keys_to_check.append(subkey_name)
            i += 1
        except OSError:
            break # End of keys

    # 2. Check each key
    for subkey_name in keys_to_check:
        full_path = f"{base_path}\\{subkey_name}"
        
        # Check if it's a generic "VSCodeStyle" key we created
        if subkey_name.startswith("VSCodeStyle"):
            try:
                # Try to delete the entire key tree
                winreg.DeleteKey(classes_key, subkey_name)
                print(f"[+] Deleted custom key: {subkey_name}")
                modified_count += 1
                continue
            except:
                pass

        # Check for "DefaultIcon" overrides inside standard keys
        try:
            icon_key_path = f"{full_path}\\DefaultIcon"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, icon_key_path) as icon_key:
                val, _ = winreg.QueryValueEx(icon_key, "")
                
                # If the icon points to our folder, DELETE the override
                if ICONS_FOLDER in val:
                    # We must close the key before deleting it, so we reopen parent
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, icon_key_path)
                    print(f"[+] Restored default for: {subkey_name}")
                    modified_count += 1
        except FileNotFoundError:
            continue # No DefaultIcon key, skip
        except Exception as e:
            # print(f"Error checking {subkey_name}: {e}")
            pass

    print(f"\n[+] Reversion complete. {modified_count} registry keys cleaned.")

def main():
    print("=== Reverting to Classic Windows Icons ===")
    
    # 1. Remove Registry Overrides
    clean_registry()
    
    # 2. Force Refresh
    refresh_explorer()
    
    # 3. Delete Files (Optional, asks permission)
    print("\nDo you want to delete the downloaded .ico files?")
    choice = input(f"Delete {ICONS_FOLDER}? (y/n): ").lower()
    if choice == 'y':
        delete_icon_folder()
    
    print("\nDONE. If icons look broken, restart your computer.")

if __name__ == "__main__":
    main()