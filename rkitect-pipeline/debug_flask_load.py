#!/usr/bin/env python
"""Debug Flask module loading."""
import sys
from pathlib import Path

# This simulates what happens when dashboard/app.py is executed
print(f"Script location: {Path(__file__).resolve()}")
print(f"Working dir: {Path.cwd()}")

# When Flask(__name__) is called from dashboard/app.py:
# __name__ will be "dashboard.app" or "__main__"
# Flask will infer the root path from the module location

# Check if dashboard module can be imported
try:
    import dashboard.app
    print(f"\nDashboard app module: {dashboard.app}")
    print(f"Dashboard app file: {dashboard.app.__file__}")
    
    app = dashboard.app.app
    print(f"\nFlask app root_path: {app.root_path}")
    print(f"Flask app instance_path: {app.instance_path}")
    print(f"Flask template folder setting: {app.template_folder}")
    
    # Infer the actual template path Flask will use
    if app.template_folder:
        if Path(app.template_folder).is_absolute():
            template_path = Path(app.template_folder)
        else:
            template_path = Path(app.root_path) / app.template_folder
    else:
        template_path = Path(app.root_path) / "templates"
    
    print(f"\nInferred template path: {template_path}")
    print(f"Path exists: {template_path.exists()}")
    
    # Check if the template has our new content
    index_template = template_path / "index.html"
    if index_template.exists():
        content = index_template.read_bytes()
        print(f"\nindex.html size: {len(content)} bytes")
        print(f"  Has 'Generated Images': {b'Generated Images' in content}")
        print(f"  Has 'renderGeneratedImages': {b'renderGeneratedImages' in content}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
