import os
import shutil
from pathlib import Path

print("This tool will guide you to build your project's directory")
project_name = input("Please enter the name of your project: ")
path = input("Now enter the path where you'd like to build your project: ")

full_path = Path(".") / project_name


if full_path.is_dir():
    print("Project directory already exists!")
    exit(0)
else:
    os.mkdir(full_path)
    shutil.copytree(Path("elena/static"), full_path / "static")
    shutil.copytree(Path("elena/templates"), full_path / "templates")
    # FIXME Copy also the files Procfile, runtime, and wsgi (these files have
    # to be in the new src/elena directory.

    print(f"Project: {project_name} directory is now ready in {path}!")
