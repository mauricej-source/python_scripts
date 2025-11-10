#!/usr/bin/python
import os
import sys
import shutil
import platform
import winshell
import psutil
#
# ------------------------------------------------------------------------------------------
# Declarations Section
# ------------------------------------------------------------------------------------------         
_OPSYS = ""         
_OPSYS_LowerCase = ""   
_WIN_OS = "windows"      
_WIN_OS_01 = "win" 
_LINUX_OS_01 = "linux" 
_LINUX_OS_02 = "arch" 
_LINUX_OS_03 = "centos" 
_LINUX_OS_04 = "debian" 
_LINUX_OS_05 = "gentoo" 
_LINUX_OS_06 = "fedora" 
_LINUX_OS_07 = "opensuse" 
_LINUX_OS_08 = "ubuntu" 
_LINUX_OS_09 = "kali" 
_LINUX_OS_10 = "redhat" 
_UNIX_OS = "unix" 
#
#Remove Temp files from various locations in Windows
_PATH_01 = "C:\\Windows\\Temp"
_PATH_02 = "C:\\Windows\\Prefetch"
_PATH_03 = "C:\\Users"
_PATH_03a = "AppData\\Local\\Temp"
_USERS_ARRY_STR = []
# ------------------------------------------------------------------------------------------
# Functions Declaration Section
# ------------------------------------------------------------------------------------------
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
def getUsers():
  try:
    user_list = psutil.users()
    
    print("Users associated with this System are :")
    
    for user in user_list:
        username = user.name
        #print(username)
        _USERS_ARRY_STR.append(username)
  except:
    pass
    
def diskCleanup_Linux():  
    os.system("rm -rf ~/.local/share/Trash/*")
        
def fileInUse(fileFolderName):
    if os.path.exists(fileFolderName):
        try:
            os.rename(fileFolderName, fileFolderName)
            return False
        except OSError as e:
            return True   
            
def deletefolder_Windows(folderName):
    #print("Received Folder: " + folderName)
    try:
        if os.path.isdir(f'{folderName}'):
           #print("   - Folder: " + folderName)
           shutil.rmtree(os.path.join(f'{folderName}'))
           
           #Printing the confirmation message of deletion
           print("   - DELETED FOLDER SUCCESFULLY - " + folderName)                 
    except OSError as e: # name the Exception `e`
        #print("ERROR THROWN - " + e.strerror)
        #print("ERROR CODE - " + e.code)
        pass
        
def deletefile_Windows(fileName):
    #print("Received File: " + fileName)
    try:
       if os.path.isfile(f'{fileName}'):
           #if(os.path.isfile(fileName) and fileName.lower().endswith(('.txt', '.log', '.doc', '.docx'))):
           #print("   - File: " + fileName)
       
           if(fileInUse(fileName) == False):
               #Printing the confirmation message of deletion
               #print("   - File to be Deleted - " + fileName)  
               
               os.remove(f'{fileName}')
           
               #Printing the confirmation message of deletion
               print("   - DELETED FiLE SUCCESFULLY - " + fileName)   
    except OSError as e: # name the Exception `e`
        #print("ERROR THROWN - " + e.strerror)
        #print("ERROR CODE - " + e.code)
        pass
        
def traversePath_Windows(file_path):
    for subdir, dirs, files in os.walk(file_path):
        for file in files:
            fileFolderName = os.path.join(subdir, file)
            #print("   - File and or Foldername: " + fileFolderName)
            deletefile_Windows(fileFolderName)
            
        deletefolder_Windows(subdir)
        
def emptyTempFolders_Windows(_platform):    
    if _platform == "win":       
        try:           
            print ("------------------------------------------------")
            print (" - DiskCleanup - WINDOWS - Empty Temp Folders")
            print ("------------------------------------------------")
            print (f" - Removing the '{_PATH_01}' Directory and its Content:")
            traversePath_Windows(_PATH_01)
            
            print(f" - Removing the '{_PATH_02}' Directory and its Content:")
            traversePath_Windows(_PATH_02)
            
            getUsers()            
            for user in _USERS_ARRY_STR:
                #print(user)
                _PATH_03_ADJ = _PATH_03 + "\\" + user + "\\" + _PATH_03a
                
                print(f" - Removing the '{_PATH_03_ADJ}' Directory and its Content:")
                traversePath_Windows(_PATH_03_ADJ)
            
        except:
            pass
        #try:
        #    os.system("rd /s c:\\\\$Recycle.Bin")  # newer Windows..
        #except:
        #    pass
        #try:
        #    os.system("rd /s c:\\\\recycler")  #  Windows XP, Vista, or Server 2003
        #except:
        #    pass 
    else:
        print("DiskCleanUp - Platform NOT Recognized: " + _platform)
        
def emptyTrashCan_Windows(_platform):    
    if _platform == "win":       
        try:
            print ("------------------------------------------------")
            print (" - DiskCleanup - WINDOWS - Empty TrashCan")
            print ("------------------------------------------------")
            winshell.recycle_bin().empty(confirm=False, show_progress=True, sound=True)
        except:
            pass
        #try:
        #    os.system("rd /s c:\\\\$Recycle.Bin")  # newer Windows..
        #except:
        #    pass
        #try:
        #    os.system("rd /s c:\\\\recycler")  #  Windows XP, Vista, or Server 2003
        #except:
        #    pass 
    else:
        print("DiskCleanUp - Platform NOT Recognized: " + _platform)
#
# ------------------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------------------   
#
# ------------------------------------------------
# Process ARGUMENTS if Present
# ------------------------------------------------ 
# 
# Retrieve ARGUMENTS - Total arguments
n = len(sys.argv)

print("System Maintenance - Total ARGS Passed: ", n)
 
_OPSYS = identify_OS()
    
if( n == 1 ):
    # ------------------------------------------------
    # Default Behavior - Process Disk/Memory CleanUp
    # ------------------------------------------------   
    print("System Maintenance - INIT DEFAULT BEHAVIOR - Disk Cleanup ...")
    
    if _OPSYS is None:
        print ("UNABLE to retrieve the Operating System: " + _OPSYS)
    else: 
        print ("Operating System: " + _OPSYS)   
        
        _OPSYS_LowerCase = _OPSYS.lower()
        
        #print ("Converted Operating System to LowerCase: " + _OPSYS_LowerCase) 
        print ("------------------------------------------------")
        
        # Windows Operating System
        if (_WIN_OS in _OPSYS_LowerCase) or (_WIN_OS_01 in _OPSYS_LowerCase):
             emptyTrashCan_Windows("win")
             emptyTempFolders_Windows("win")
             
        # Linux Operating System
        if (_LINUX_OS_01 in _OPSYS_LowerCase) or (_LINUX_OS_02 in _OPSYS_LowerCase) or (_LINUX_OS_03 in _OPSYS_LowerCase) or (_LINUX_OS_04 in _OPSYS_LowerCase) or \
           (_LINUX_OS_05 in _OPSYS_LowerCase) or (_LINUX_OS_06 in _OPSYS_LowerCase) or (_LINUX_OS_07 in _OPSYS_LowerCase) or (_LINUX_OS_08 in _OPSYS_LowerCase) or \
           (_LINUX_OS_09 in _OPSYS_LowerCase) or (_LINUX_OS_10 in _OPSYS_LowerCase) or (_UNIX_OS in _OPSYS_LowerCase):
             diskCleanup_Linux("linux")       
else:
    if ( n > 1 and n < 4 ):
        # ------------------------------------------------
        # Process ARGS1 & ARGS2 { HOSTNAME & EVENT }
        # ------------------------------------------------ 
        if (n >= 2):
            hostname = sys.argv[1]
        
            if hostname:
                #print("HOSTNAME - " + hostname)
            
                if (n == 3):        
                    event = sys.argv[2]
                    
                    if event:
                        #print("EVENT - " + event)
                        
                        print ("------------------------------------------------")
                        print (" - HostName and Event Received - " + hostname + " - " + event)  
                        
                        print (" - System Maintenance - INIT EVENT Processing - ") 
                        print ("------------------------------------------------")
                        
                        hostnameTrimmed = hostname.strip()
                        hostnameLowercase = hostnameTrimmed.lower()
                        
                        eventTrimmed = event.strip()
                        eventLowercase = eventTrimmed.lower()  


                        
                    else:
                        print("EVENT variable is NULL or BLANK in Value")
            else:
                print("HOSTNAME variable is NULL or BLANK in Value")              
    else:
        print("WELL we RICKED IT...Nothing to Do...Do not Understand....NO COMPHRENDE!!!")

             
         
    
    
