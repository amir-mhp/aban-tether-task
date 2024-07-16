import importlib
import os
import sys


def load_modules(base_path):
    sys.path.append(base_path)

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.relpath(os.path.join(root, file), base_path)
                module_name = os.path.splitext(module_path)[0].replace(os.sep, ".")
                importlib.import_module(module_name)


current_dir = os.path.dirname(os.path.abspath(__file__))

load_modules(current_dir)
