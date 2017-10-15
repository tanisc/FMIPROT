import os
fle = open('filelist.lst','w')
dle = open('dirlist.lst','w')
os.chdir('dist')
os.chdir('fmiprot')
for dp, dn, filenames in os.walk('.'):
    for fname in filenames:
        fle.write(os.path.join(dp,fname)[2:])
        fle.write('\n')
for dp, dn, filenames in os.walk('.'):
    if dp == '.':
        continue
    dle.write(dp[2:])
    dle.write('\n')
dle.write('previews')
dle.write('\n')
dle.write('resources')
dle.write('\n')
dle.write('doc')
os.chdir('..')
os.chdir('..')
for dp, dn, filenames in os.walk('doc'):
    for fname in filenames:
        if os.path.splitext(fname)[1] == '.docx':
            continue
        fle.write(os.path.join('.',dp,fname)[2:])
        fle.write('\n')
os.chdir('src')
for dp, dn, filenames in os.walk('previews'):
    for fname in filenames:
        fle.write(os.path.join('.',dp,fname)[2:])
        fle.write('\n')
for dp, dn, filenames in os.walk('resources'):
    for fname in filenames:
        fle.write(os.path.join('.',dp,fname)[2:])
        if filenames.index(fname) != len(filenames)-1:
            fle.write('\n')

os.chdir('..')
fle.close()
dle.close()
