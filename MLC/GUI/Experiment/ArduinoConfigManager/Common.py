import os


def create_local_full_path(*files):
    path_list = [os.path.dirname(os.path.abspath(__file__))] + list(files)
    return os.path.join(*path_list)
