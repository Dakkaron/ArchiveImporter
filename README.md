# ArchiveImporter
A Python2/3 module that allows importing files from password protected ZIP files, .tar, .tar.gz or .tar.bz2 archives.

## Command line usage
```
python ArchiveImporter.py [zipfile] [-p=password] [args...]
```
This loads the given ZIP file that is encrypted with the given password and executes `__main__.py` within it. Works pretty similar to executing a regular unprotected .pyz archive:
```
python [zipfile] [args...]
```
But using the ArchiveImporter.py allows using password protected ZIP/.pyz archives.

## Usage within the code

ArchiveImporter.py can also be used to import modules from a password protected ZIP archive from within Python code. See the following example:
```
# First import the ArchiveImporter module
import ArchiveImporter
# Then add the password encrypted file you want to import from using addZip(zippath, password)
ArchiveImporter.addZip("test.pyz", "password")
# Now import modules from the archive as usual
import testmod
```

ArchiveImporter.py can also handle ZIP archives without a password. In this case `password` needs to be `None`. But that is not necessary, since Python already has this functionality built in:
```
import sys
sys.path.append("path/to/unencrypted/zipfile.pyz")
```
