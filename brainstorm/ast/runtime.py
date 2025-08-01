import importlib.util


def load_module_from_path(path: str, module_name: str = "custom_module"):
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
