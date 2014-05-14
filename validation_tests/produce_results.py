"""
Script to run all the produce_results scripts in the Tests/xxx/xxx/ directories
"""

import os
import time

import anuga
from anuga import indent
from parameters import alg
from parameters import cfl

#---------------------------------
# Get the current svn revision
#---------------------------------
timestamp = time.asctime()
major_revision = anuga.config.major_revision
try:
    # This fails if using git for version control
    minor_revision = anuga.utilities.system_tools.get_revision_number()
except:
    try:
        # This works when using git on unix
        minor_revision = os.popen("git show-ref --head -s | head -n1").read().strip()
    except:
        # This is a fallback position
        minor_revision = 'unknown'

#---------------------------------
# Run the tests
#---------------------------------
buildroot = os.getcwd()

Upper_dirs = os.listdir('.')
dir = '.'
Upper_dirs = [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]


try:
    Upper_dirs.remove('.svn')
    Upper_dirs.remove('utilities')
except ValueError:
    pass



#print Upper_dirs
#os.chdir('./Tests')

#print 'Tests'
print Upper_dirs

time_total = 0.0
test_number = 1
for dir in Upper_dirs:

    os.chdir(dir)

    print 72*'='
    print 'Directory: ' + dir
    print 72*'='
    
    #print 'Changing to', os.getcwd()
    dir = '.'
    Lower_dirs =  [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]
    try:
        Lower_dirs.remove('.svn')
    except ValueError:
        pass
    #print Lower_dirs




    for l_dir in Lower_dirs:
        os.chdir(l_dir)
        #print os.getcwd()
        print 50*'-'
        print 'Subdirectory %g: '% (test_number)  + l_dir
        test_number += 1
        print 50*'-'
        try:
            t0 = time.time()
            cmd = 'python produce_results.py'
            print 2 * indent + 'Running: ' + cmd
            os.system(cmd)
            t1 = time.time() - t0
            time_total += t1
            print 2 * indent + 'That took ' + str(t1) + ' secs'
        except:
            print 2 * indent + 'Failed running produce_results in ' + os.getcwd()
            pass

        os.chdir('..')
        #print 'Changing to', os.getcwd()

    os.chdir('..')
    #print 'Changing to', os.getcwd()
    
os.chdir(buildroot)

print 72*'='
print 'That took ' + str(time_total) + ' secs'
print 72*'='

#----------------------------------
# Now it is ok to create the latex 
# macro file with run parameters
#----------------------------------

f = open('saved_parameters.tex', 'w')
f.write('\\newcommand{\\cfl}{\\UScore{%s}}\n' % str(cfl))
f.write('\\newcommand{\\alg}{\\UScore{%s}}\n' % str(alg))
f.write('\\newcommand{\\majorR}{\\UScore{%s}}\n' % str(major_revision))
f.write('\\newcommand{\\minorR}{\\UScore{%s}}\n' % str(minor_revision))
f.write('\\newcommand{\\timeR}{{%s}}\n' % str(timestamp))

f.close()


import os

from anuga_validation_tests.utilities.fabricate import *

os.system('python typeset_report.py')

#cmd = 'pdflatex -shell-escape -interaction=batchmode report.tex'
#print cmd
#import subprocess
#subprocess.call([cmd], shell=True)

import subprocess
cmd = 'mv report.pdf report_cfl_%s_alg_%s.pdf' % (str(cfl), str(alg))
print cmd
subprocess.call([cmd], shell=True)





