import zipfile
import os
from pathlib import Path

print("📦 Creating ZIP archive...")
print()

# Configuration
output_filename = 'BDPA_TugasProyek_Kelompok5_LabKebidanan.zip'
current_dir = Path.cwd()
parent_dir = current_dir.parent
output_path = parent_dir / output_filename

# Files/folders to exclude
exclude_patterns = [
    '.venv',
    '__pycache__',
    '.pyc',
    '.git',
    'test_data',
    '.pytest_cache',
    '.vscode',
    '*.egg-info',
    'node_modules'
]

def should_exclude(path_str):
    """Check if path should be excluded"""
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
    return False

try:
    # Create ZIP file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0
        
        # Walk through all files in current directory
        for root, dirs, files in os.walk(current_dir):
            # Remove excluded directories from dirs to prevent walking into them
            dirs[:] = [d for d in dirs if not should_exclude(d)]
            
            for file in files:
                if should_exclude(file):
                    continue
                
                file_path = Path(root) / file
                
                # Calculate relative path from parent directory
                arcname = file_path.relative_to(parent_dir)
                
                # Add file to zip
                zipf.write(file_path, arcname)
                file_count += 1
                
                if file_count % 10 == 0:
                    print(f"📄 Added {file_count} files...", end='\r')
    
    # Success message
    print(f"\n✅ Success! Created: {output_filename}")
    print(f"📁 Location: {parent_dir}")
    
    # Show file size
    zip_size = output_path.stat().st_size
    print(f"📊 Size: {zip_size / 1024 / 1024:.2f} MB")
    print(f"📦 Files included: {file_count}")
    print()
    print("🎉 Ready to submit!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print()
    print("💡 Try manual method:")
    print("   1. Close this terminal")
    print("   2. Open File Explorer")
    print("   3. Go to F:\\")
    print("   4. Right-click 'iot_project' folder")
    print("   5. Send to → Compressed (zipped) folder")
    print("   6. Rename to: BDPA_TugasProyek_Kelompok5_LabKebidanan.zip")