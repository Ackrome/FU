import os
import requests
import json
import subprocess
import winreg
import ctypes
import re

# --- CONFIGURATION ---
ICONS_FOLDER = r"C:\Icons\VSCode"
BASE_ICON_URL = "https://raw.githubusercontent.com/vscode-icons/vscode-icons/master/icons/"

# URL candidates for the mapping file (New vs Old paths)
MAPPING_URLS = [
    # 1. GitHub Source (New Structure 2024+) - CamelCase
    "https://raw.githubusercontent.com/vscode-icons/vscode-icons/master/src/iconsManifest/supportedExtensions.ts",
    # 2. GitHub Source (Old Structure) - KebabCase
    "https://raw.githubusercontent.com/vscode-icons/vscode-icons/master/src/icon-manifest/supportedExtensions.ts",
    # 3. NPM Mirror (Compiled JSON)
    "https://unpkg.com/vscode-icons/dist/src/iconsManifest/supportedExtensions.json",
    "https://unpkg.com/vscode-icons/dist/src/icon-manifest/supportedExtensions.json",
]

# EMERGENCY BACKUP: If internet/parsing fails completely, use this list.
HARDCODED_MAPPING = {
    ".py": "file_type_python", ".js": "file_type_javascript", ".ts": "file_type_typescript",
    ".html": "file_type_html", ".css": "file_type_css", ".scss": "file_type_scss",
    ".json": "file_type_json", ".md": "file_type_markdown", ".xml": "file_type_xml",
    ".c": "file_type_c", ".cpp": "file_type_cpp", ".h": "file_type_cppheader",
    ".java": "file_type_java", ".class": "file_type_class", ".go": "file_type_go",
    ".php": "file_type_php", ".rb": "file_type_ruby", ".rs": "file_type_rust",
    ".sh": "file_type_shell", ".bat": "file_type_bat", ".ps1": "file_type_powershell",
    ".txt": "file_type_text", ".zip": "file_type_zip", ".7z": "file_type_zip",
    ".pdf": "file_type_pdf", ".sql": "file_type_sql", ".lua": "file_type_lua",
    ".cs": "file_type_csharp", ".vb": "file_type_vb", ".vue": "file_type_vue",
    ".jsx": "file_type_reactjs", ".tsx": "file_type_reactts", ".dart": "file_type_dart",
    ".dockerfile": "file_type_docker", ".env": "file_type_env", ".gitignore": "file_type_git",
    ".yaml": "file_type_yaml", ".yml": "file_type_yaml", ".exe": "file_type_binary",
}

TARGET_EXTENSIONS = list(HARDCODED_MAPPING.keys())

def setup_env():
    if not os.path.exists(ICONS_FOLDER):
        os.makedirs(ICONS_FOLDER)

def parse_ts_manifest(text):
    """Parses the TypeScript source file using Regex."""
    print("    [*] Parsing TypeScript source...")
    mapping = {}
    # Regex matches: icon: 'name', extensions: ['a', 'b']
    pattern = r"icon:\s*['\"]([\w-]+)['\"],\s*extensions:\s*\[([^\]]+)\]"
    matches = re.findall(pattern, text)
    
    for icon_name, ext_list_str in matches:
        exts = [e.strip().strip("'").strip('"') for e in ext_list_str.split(',')]
        full_icon_name = f"file_type_{icon_name}"
        for ext in exts:
            dot_ext = f".{ext}"
            mapping[dot_ext] = full_icon_name
    return mapping

def get_mapping():
    print("[*] Attempting to download icon mappings...")
    
    # Try all known URLs
    for url in MAPPING_URLS:
        print(f"    Testing: {url} ...")
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                if url.endswith(".json"):
                    # Parse JSON
                    data = r.json()
                    mapping = {}
                    for entry in data.get('supported', []):
                        icon = f"file_type_{entry['icon']}"
                        for ext in entry['extensions']:
                            mapping[f".{ext}"] = icon
                    print(f"    [+] Success! Loaded from JSON ({len(mapping)} icons).")
                    return mapping
                else:
                    # Parse TypeScript
                    mapping = parse_ts_manifest(r.text)
                    if mapping:
                        print(f"    [+] Success! Parsed TS ({len(mapping)} icons).")
                        return mapping
        except Exception as e:
            print(f"    [-] Failed: {e}")

    print("[!] All downloads failed. Using HARDCODED backup list.")
    return HARDCODED_MAPPING

def download_and_convert(icon_name):
    local_svg = os.path.join(ICONS_FOLDER, f"{icon_name}.svg")
    local_ico = os.path.join(ICONS_FOLDER, f"{icon_name}.ico")

    if os.path.exists(local_ico):
        return local_ico

    svg_url = f"{BASE_ICON_URL}{icon_name}.svg"
    try:
        r = requests.get(svg_url)
        if r.status_code != 200:
            return None
        with open(local_svg, 'wb') as f:
            f.write(r.content)
    except:
        return None

    # Convert using ImageMagick
    cmd = [
        "magick", "convert", "-background", "none", local_svg,
        "-define", "icon:auto-resize=256,64,48,32,16", local_ico
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(local_svg)
        print(f"    [OK] Converted: {icon_name}.ico")
        return local_ico
    except:
        return None

def get_progid(extension):
    # 1. UserChoice
    try:
        path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\{extension}\\UserChoice"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            return winreg.QueryValueEx(key, "ProgId")[0]
    except:
        pass
    # 2. HKCU Class
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{extension}") as key:
            return winreg.QueryValueEx(key, "")[0]
    except:
        pass
    # 3. HKCR Class
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
            return winreg.QueryValueEx(key, "")[0]
    except:
        pass
    return None

def apply_registry_icon(extension, icon_path):
    progid = get_progid(extension)
    
    # If no ProgID, create one
    if not progid:
        progid = f"VSCodeStyle{extension}"
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{extension}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, progid)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{progid}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, f"{extension} File")
        except:
            pass

    if progid:
        key_path = f"Software\\Classes\\{progid}\\DefaultIcon"
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValue(key, "", winreg.REG_SZ, icon_path)
                print(f"[+] Applied: {extension} -> {progid}")
        except Exception as e:
            print(f"[-] Error writing registry for {extension}: {e}")

def main():
    print("=== VS Code Icon Patcher (Robust) ===")
    setup_env()
    
    # Get Mapping (Online or Backup)
    mapping = get_mapping()
    
    print(f"\n[*] Processing extensions...")
    
    # Filter mapping to only include common extensions to save time
    # (Or remove 'if' to do ALL 500+ extensions)
    for ext, icon_name in mapping.items():
        if ext in TARGET_EXTENSIONS or ext in HARDCODED_MAPPING:
            icon_path = download_and_convert(icon_name)
            if icon_path:
                apply_registry_icon(ext, icon_path)
    
    print("\n[*] Refreshing Explorer...")
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
    print("DONE. If icons are blank, restart your PC.")

if __name__ == "__main__":
    main()