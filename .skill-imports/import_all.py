from pathlib import Path
import os, json, subprocess, zipfile
root=Path('/Users/jdelon02/.agents/skills')
out=root/'.skill-imports'
excluded={'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.DS_Store'}
folders=sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith('.'))
for folder in folders:
    archive=out/(folder.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(folder):
            dirs[:]=sorted(d for d in dirs if d not in excluded)
            for name in sorted(files):
                p=Path(base)/name
                if name not in excluded and p.is_file():
                    z.write(p,p.relative_to(folder))
    print(f'Created {archive.name} ({archive.stat().st_size} bytes)',flush=True)
