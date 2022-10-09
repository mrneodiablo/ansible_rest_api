# pylint: disable=expression-not-assigned,abstract-method,import-error
from __future__ import unicode_literals
import tarfile
from ._base import _ArchiveRepo, shutil


class Tar(_ArchiveRepo):
    def _extract(self, archive, path, options):
        # pylint: disable=broad-except
        shutil.move(path, path + ".bak")
        try:
            with tarfile.open(archive) as arch:
                
                import os
                
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(arch, path)
        except:
            self.delete()
            shutil.move(path + ".bak", path)
        else:
            shutil.rmtree(path + ".bak")
