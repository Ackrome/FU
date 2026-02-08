import json

# Use the exact path to the file you are opening in VS Code
file_path = r"C:\Users\Rog G16\Downloads\icepyx2 (7).ipynb"

with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 1. Kill the global widget metadata
if "metadata" in nb:
    nb["metadata"].pop("widgets", None)

# 2. Kill widget data in every cell
for cell in nb.get("cells", []):
    if "outputs" in cell:
        for output in cell["outputs"]:
            if "data" in output:
                # Remove the widget mimetype that causes the crash
                output["data"].pop("application/vnd.jupyter.widget-view+json", None)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook stripped of all widget metadata. You can now export.")