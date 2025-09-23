import platform
import sys

def identify_OS():
  try:
    return platform.platform()
  except:
    return "N/A"
    
# ------------------------------------------------------------------------------------------
# - Print Example of Probable Results
# ------------------------------------------------------------------------------------------
#def linux_distribution():
#  try:
#    return platform.linux_distribution()
#  except:
#    return "N/A"
#
#def dist():
#  try:
#    return platform.dist()
#  except:
#    return "N/A"
#    
#print("""Python version: %s
#dist: %s
#linux_distribution: %s
#system: %s
#machine: %s
#platform: %s
#uname: %s
#version: %s
#mac_ver: %s
#""" % (
#sys.version.split('\n'),
#str(dist()),
#linux_distribution(),
#platform.system(),
#platform.machine(),
#platform.platform(),
#platform.uname(),
#platform.version(),
#platform.mac_ver(),
#))
# ------------------------------------------------------------------------------------------

operating_system = identify_OS()
print ("Operating System: " + operating_system)