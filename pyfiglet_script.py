import sys, subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyfiglet'])
import pyfiglet
print(pyfiglet.figlet_format('SpotiSyncer', font='standard'))
