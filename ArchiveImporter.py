import sys
from types import ModuleType
try:
    from importlib.machinery import ModuleSpec
    useModuleSpec = True
except ImportError:
    useModuleSpec = False
import zipfile
import tarfile
import os


if not useModuleSpec:
    class ModuleSpec(object):
        def __init__(self, name, loader, is_package):
            self.name = name
            self.loader = loader
            self.is_package = is_package

class ArchiveImporter(object):
    def __init__(self, archivePath, format, password=None):
        if isinstance(password, str) and sys.version_info[0]>=3:
                password = bytes(password, "utf-8")
        self._archivePath = archivePath
        self._password = password
        self._format = format.strip().lower()
        if self._format == "zip":
            self._archiveHandler = zipfile.ZipFile
        elif self._format == "tar":
            self._archiveHandler = tarfile.open
        else:
            raise ValueError("Error: File "+archivePath+" is neither zip nor tar!")
    
    def getModlist(self):
        with self._archiveHandler(self._archivePath) as archive:
            if self._format == "zip":
                filelist = archive.namelist()
            elif self._format == "tar":
                filelist = archive.getnames()
            namelist = [ x.replace("/", ".")  for x in filelist ]
            modlist = [ x[:-3] for x in namelist if x.endswith(".py") ]
            modlist += [ x[:-9] for x in modlist if x.endswith(".__init__") ]
        return modlist
    
    def find_module(self, fullname, path=None):
        if self.find_spec(fullname):
            return self
        return None
    
    def find_spec(self, fullname, path=None, target=None):
        modlist = self.getModlist()
        filename = fullname.replace(".","/")
        if fullname in self.getModlist() or fullname=="__zipmain__":
            isPackage = fullname+".__init__" in modlist or True
            spec = ModuleSpec(name=fullname, loader=self, is_package=isPackage)
            return spec
        else:
            return None
    
    def load_module(self, fullname):
        if fullname=="__zipmain__":
            filename = "__main__"
        else:
            filename = fullname
        modlist = self.getModlist()
        isPackage = False
        if filename+".__init__" in modlist:
            filename = filename+".__init__"
            isPackage = True
        filename = filename.replace(".","/")+".py"
        with self._archiveHandler(self._archivePath) as archive:
            if self._format=="zip":
                with archive.open(filename, pwd=self._password) as file:
                    data = file.read()
            else:
                data = archive.extractfile(archive.getmember(filename)).read()
            newModule = ModuleType(fullname)
            exec(data, newModule.__dict__)
            if isPackage:
                newModule.__path__ = os.path.dirname(filename.rstrip("/"))
            sys.modules[fullname] = newModule
            return newModule

def addZip(zippath, password=None):
    """Add the zip file that resides at the path zippath and is encrypted with the given password to
    the list of import locations.
    zippath is a path given as a string.
    password is the zip file's password as a string. Needs to be None if the ZIP file does not have a password.
    """
    sys.meta_path.append(ArchiveImporter(archivePath=zippath, format="zip", password=password))

def addTar(tarpath):
    """Add the tar file that resides at the path tarpath to the list of import locations.
    tarpath is a path given as a string.
    The given tar file can be compressed using either gzip or bz2.
    """
    sys.meta_path.append(ArchiveImporter(archivePath=tarpath, format="tar"))

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage: python3 ArchiveImporter.py [zipfile|tarfile] [-p=password] [args...]")
        exit(1)
    archivePath = sys.argv[1]
    if sys.version_info[0]>=3:
        passwd = bytes(sys.argv[2][3:], "utf-8") if len(sys.argv)>2 and sys.argv[2].startswith("-p=") else None
    else:
        passwd = sys.argv[2][3:] if len(sys.argv)>2 and sys.argv[2].startswith("-p=") else None
    if passwd=="":
        passwd = None
    sys.argv = sys.argv[2:] if passwd is None else sys.argv[3:]
    if zipfile.is_zipfile(archivePath):
        addZip(archivePath, passwd)
    elif tarfile.is_tarfile(archivePath):
        addTar(archivePath)
    else:
        raise ValueError("Error: File "+archivePath+" is neither zip nor tar!")
    import __zipmain__
