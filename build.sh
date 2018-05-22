VER="0.20.2"
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
cp README.md bin/$VER/README.md
cp usermanual.pdf bin/$VER/lin/usermanual.pdf
cp usermanual.pdf bin/$VER/usermanual.pdf
cp LICENSE bin/$VER/lin/LICENSE
cp LICENSE bin/$VER/LICENSE
cp HISTORY.md bin/$VER/lin/HISTORY.md
cp HISTORY.md bin/$VER/HISTORY.md
pyinstaller src/fmiprot.py
cp -R dist/fmiprot/* bin/$VER/lin/
rm -R dist
rm -R build
rm fmiprot.spec
cd bin/$VER/lin
rm ../fmiprot_$VER.tar.gz
tar -cvf ../fmiprot_$VER.tar.gz *
