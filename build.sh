VER="0.15.3"
rm -R dist
rm -R build
rm fmiprot.spec
rm installer.spec
rm filelist.lst
rm dirlist.lst
sh clean.sh
mkdir vers/$VER
rm -R vers/$VER/lin
mkdir vers/$VER/lin
mkdir vers/$VER/lin/files
mkdir vers/$VER/lin/files/resources
cp src/resources/* vers/$VER/lin/files/resources/
mkdir vers/$VER/lin/files/previews
cp src/previews/0-MONIMET* vers/$VER/lin/files/previews/
mkdir vers/$VER/lin/files/doc
cp doc/readme.txt vers/$VER/lin/files/doc/readme.txt
cp doc/usermanual.pdf vers/$VER/lin/files/doc/usermanual.pdf
cp doc/license.txt vers/$VER/lin/files/doc/license.txt
cp doc/history.txt vers/$VER/lin/files/doc/history.txt
cp doc/readme.txt vers/$VER/lin/readme.txt
cp doc/usermanual.pdf vers/$VER/lin/usermanual.pdf
cp doc/license.txt vers/$VER/lin/license.txt
cp doc/history.txt vers/$VER/lin/history.txt
pyinstaller src/fmiprot.py
python lister.py
cp filelist.lst vers/$VER/lin/filelist.lst
cp dirlist.lst vers/$VER/lin/dirlist.lst
rm filelist.lst
rm dirlist.lst
cp -R dist/fmiprot/* vers/$VER/lin/files/
rm -R dist
rm -R build
rm fmiprot.spec
pyinstaller installer.py
cp -R dist/installer/* vers/$VER/lin/
rm -R dist
rm -R build
rm installer.spec
