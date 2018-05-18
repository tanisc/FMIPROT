SET VER=0.20.1
rmdir dist /s /q
rmdir build /s /q
del fmiprot.spec
call clean.bat
mkdir bin
mkdir bin\%VER%
rmdir bin\%VER%\win /s /q
mkdir bin\%VER%\win
mkdir bin\%VER%\win\resources
copy src\resources\* bin\%VER%\win\resources\
mkdir bin\%VER%\win\previews
copy src\previews\* bin\%VER%\win\previews\
copy README.md bin\%VER%\win\README.md
copy usermanual.pdf bin\%VER%\win\usermanual.pdf
copy LICENSE bin\%VER%\win\LICENSE
copy HISTORY.md bin\%VER%\win\HISTORY.md
pyinstaller src\fmiprot.py
xcopy dist\fmiprot\* bin\%VER%\win\ /q /s
rmdir dist /s /q
rmdir build /s /q
del fmiprot.spec
del bin\%VER%\fmiprot_%VER%.zip
cd bin\%VER%\win
"%PROGRAMFILES%\7-Zip\7z.exe" a ..\fmiprot_%VER%.zip
