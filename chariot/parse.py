__author__ = 'n3tn0'
__version__= 'ALPHA'

import os

output = open('output.txt', 'r')
text = output.read()

beginning, discard1 = text.split('...')
print beginning
print discard1

discard2,command = beginning.split('\n')
output.close()
module = command[0:command.find(' ')]
folder = module.lower()
finalcmd = 'python modules/' + folder + '/main.py' + command[command.find(' '):-1]
os.system(finalcmd)
