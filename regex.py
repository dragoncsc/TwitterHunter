import re


exampleLine = 'prices xom 91.43-234.44/vz50-50.32/s 7.23-7.24'

regEx = re.findall(r'\w{1,3}\s?', exampleLine)

print regEx

