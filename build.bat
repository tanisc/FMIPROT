SET VER=0.15.0
rmdir dist /s /q
rmdir build /s /q
del fmiprot.spec
rmdir vers\%VER% /s /q
mkdir vers\%VER%
mkdir vers\%VER%\files
mkdir vers\%VER%\files\previews
copy src\previews\* vers\%VER%\files\previews\
mkdir vers\%VER%\files\resources
copy src\resources\* vers\%VER%\files\resources\
mkdir vers\%VER%\files\doc
copy doc\history.txt vers\%VER%\files\doc\history.txt
copy doc\readme.txt vers\%VER%\files\doc\readme.txt
copy doc\license.txt vers\%VER%\files\doc\license.txt
copy doc\usermanual.pdf vers\%VER%\files\doc\usermanual.pdf
copy doc\history.txt vers\%VER%\history.txt
copy doc\readme.txt vers\%VER%\readme.txt
copy doc\license.txt vers\%VER%\license.txt
copy filelist.lst vers\%VER%\filelist.lst
call clean.bat
pyinstaller src\fmiprot.py --onefile
copy dist\fmiprot.exe vers\%VER%\files\fmiprot.exe
rmdir dist /s /q
rmdir build /s /q
del fmiprot.spec
pyinstaller installer.py --onefile
copy dist\installer.exe vers\%VER%\install_win.exe
rmdir dist /s /q
rmdir build /s /q
del installer.spec
mkdir K:\FMIPROT\vers\%VER%
mkdir K:\FMIPROT\vers\%VER%\files
copy vers\%VER%\files\fmiprot.exe K:\FMIPROT\vers\%VER%\files\fmiprot.exe
copy vers\%VER%\install_win.exe K:\FMIPROT\vers\%VER%\install_win.exe
PAUSE
