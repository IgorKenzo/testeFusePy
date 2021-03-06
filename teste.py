from __future__ import with_statement
  
import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations

import estenografia

class Passthrough(Operations):
    def __init__(self, root, image):
        self.root = root
        self.image = image
        self.files = {}
        self.readFilesFromImg()
    # Helpers
    # =======
    
    def readFilesFromImg(self):
        msg = estenografia.decrypt(self.image)
        if len(msg) > 0:
            msg = msg.split(">>>")[1]

        msg = msg.split("||")
        for i in range(0,len(msg)-1,2):
            self.files[msg[i]] = msg[i+1]

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                    'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        # i=0
        for k,v in self.files.items():
        #     print(full_path+k)
            content = str(v,encoding="utf-8") if type(v) == bytes else v
            with open(full_path+k, "wb+") as f:
                f.write(bytes(content,encoding="utf-8"))
        

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            # dirents.extend(os.listdir(full_path))
            dirents.extend(list(self.files.keys()))
            
            print(dirents)
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        # print("OPEN", path)
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        content = str(buf,encoding="utf-8") if type(buf) == bytes else buf
        if path[1:] in self.files.keys():
            self.files[path[1:]] += content
        else:
            self.files[path[1:]] = content
            
        os.lseek(fh, offset, os.SEEK_SET)
        msg = ""
        for k,v in self.files.items():
            msg += f"{k}||{v}||" #.decode('ascii')
        print(msg)
        estenografia.encrypt(self.image, msg)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


    def destroy(self, path):
        for k in self.files.keys():
            os.remove(self.root +"/" + k)

def main(mountpoint, root, image):
    FUSE(Passthrough(root, image), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[1], "./aimg", sys.argv[2])
