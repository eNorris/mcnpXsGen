__author__ = 'Edward'

import os
import mcnpCardClasses

print("> " + os.getcwd())

input = mcnpCardClasses.McnpInputFile()

input.setfilename("./ctinput.inp")
input.parse()

print(input.celldeck)
print(input.surfdeck)
print(input.datadeck)