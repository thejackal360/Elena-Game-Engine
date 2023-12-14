import os
import shutil
from pathlib import Path

print("This tool will guide you to build your project's directory")
project_name = input("Please enter the name of your project: ")
path = input("Now enter the path where you'd like to build your project: ")

full_path = Path(os.path.abspath(path)) / project_name

if full_path.is_dir():
    print("Project directory already exists!")
    exit(0)
else:
    os.mkdir(full_path)
    shutil.copytree(Path("src/elena/static"), full_path / "static")
    shutil.copytree(Path("src/elena/templates"), full_path / "templates")
    shutil.copyfile(Path("src/example/Procfile"), full_path / "Procfile")
    shutil.copyfile(Path("src/example/runtime.txt"), full_path / "runtime.txt")
    shutil.copyfile(Path("src/example/wsgi.py"), full_path / "wsgi.py")
    print(f"Project: {project_name} directory is now ready in {path}!")
