SET VER=0.15.4
rmdir dist /s /q
rmdir build /s /q
del fmiprot.spec
del filelist.lst
del dirlist.lst
mkdir vers\%VER%
rmdir vers\%VER%\win /s /q
mkdir vers\%VER%\win
mkdir vers\%VER%\win\files
mkdir vers\%VER%\win\files\previews
copy src\previews\* vers\%VER%\win\files\previews\
mkdir vers\%VER%\win\files\resources
copy src\resources\* vers\%VER%\win\files\resources\
mkdir vers\%VER%\win\files\doc
copy doc\history.txt vers\%VER%\win\files\doc\history.txt
copy doc\readme.txt vers\%VER%\win\files\doc\readme.txt
copy doc\license.txt vers\%VER%\win\files\doc\license.txt
copy doc\usermanual.pdf vers\%VER%\win\files\doc\usermanual.pdf
copy doc\history.txt vers\%VER%\win\history.txt
copy doc\readme.txt vers\%VER%\win\readme.txt
copy doc\license.txt vers\%VER%\win\license.txt
call clean.bat
pyinstaller src\fmiprot.py
python lister.py
copy filelist.lst vers\%VER%\win\filelist.lst
copy dirlist.lst vers\%VER%\win\dirlist.lst
del filelist.lst
del dirlist.lst
xcopy dist\fmiprot\* vers\%VER%\win\files\ /q /s
rmdir dist /s /q
rmdir build /s /q
del fmiprot.spec
pyinstaller installer.py
xcopy dist\installer\* vers\%VER%\win\ /q /s
rmdir dist /s /q
rmdir build /s /q
del installer.spec
mkdir K:\FMIPROT\vers\%VER%\win
mkdir K:\FMIPROT\vers\%VER%\win\files
copy vers\%VER%\win\files\fmiprot.exe K:\FMIPROT\vers\%VER%\win\files\fmiprot.exe
copy vers\%VER%\win\install_win.exe K:\FMIPROT\vers\%VER%\win\install_win.exe
PAUSE
