import sys

to_fix = sys.argv[1]
fd = open(to_fix)

nlines = []
# scan file
for line in fd.readlines():
    newline = line
    if '{%' in line.lstrip(' ').lstrip('\t'):
        newline = newline.replace('&quot;', "\"")
    nlines.append(newline)

fd.close()
fd = open(to_fix, 'w')
fd.write(''.join(nlines))
fd.close()