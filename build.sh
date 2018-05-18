VER="0.20.1"
rm -R dist
rm -R build
rm fmiprot.spec
sh clean.sh
mkdir bin
mkdir bin/$VER
rm -R bin/$VER/lin
mkdir bin/$VER/lin
mkdir bin/$VER/lin/resources
cp src/resources/* bin/$VER/lin/resources/
mkdir bin/$VER/lin/previews
cp src/previews/0-MONIMET* bin/$VER/lin/previews/
cp README.md bin/$VER/lin/README.md
cp usermanual.pdf bin/$VER/lin/usermanual.pdf
cp LICENSE bin/$VER/lin/LICENSE
cp HISTORY.md bin/$VER/lin/HISTORY.md
pyinstaller src/fmiprot.py
cp -R dist/fmiprot/* bin/$VER/lin/
rm -R dist
rm -R build
rm fmiprot.spec
cd bin/$VER/lin
tar -cvf ../fmiprot_0.20.0.tar.gz *
