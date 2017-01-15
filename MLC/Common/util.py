"""
File with useful functions used in the whole project
"""

def make_tarfile(output_filename, source_dir):
    import tarfile
    import os

    with tarfile.open(output_filename, "w:gz") as tar:
        # The second parameter is used to tell the library
        # not to add the entire path in the tar.gz
        tar.add(source_dir, arcname=os.path.basename(source_dir))