VER="0.15.0"
rm -R dist
rm -R build
rm fmiprot.spec
rm installer.spec
sh clean.sh
mkdir vers/$VER
mkdir vers/$VER/files
mkdir vers/$VER/files/resources
cp src/resources/* vers/$VER/files/resources/
mkdir vers/$VER/files/previews
cp src/previews/0-MONIMET* vers/$VER/files/previews/
mkdir vers/$VER/files/doc
cp doc/readme.txt vers/$VER/files/doc/readme.txt
cp doc/usermanual.pdf vers/$VER/files/doc/usermanual.pdf
cp doc/license.txt vers/$VER/files/doc/license.txt
cp doc/history.txt vers/$VER/files/doc/history.txt
cp doc/readme.txt vers/$VER/readme.txt
cp doc/usermanual.pdf vers/$VER/usermanual.pdf
cp doc/license.txt vers/$VER/license.txt
cp doc/history.txt vers/$VER/history.txt
pyinstaller src/fmiprot.py --onefile
cp dist/fmiprot vers/$VER/files/fmiprot
rm -R dist
rm -R build
rm fmiprot.spec
pyinstaller installer.py --onefile
cp dist/installer vers/$VER/install_linux
cp filelist.lst vers/$VER/filelist.lst
rm -R dist
rm -R build
rm installer.spec
