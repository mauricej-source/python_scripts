# Importing required module 
import os
import winshell 

def diskCleanup(_platform):
    """Empty trash folder.

    """
    print(_platform)
    
    text = "[tl] Empty the trash"
    
    if _platform == "linux" or _platform == "linux2":
        print('linux: %s' % text)
        os.system("rm -rf ~/.local/share/Trash/*")
    elif _platform == "darwin":
        print('OS X: %s' % text)
        os.system("sudo rm -rf ~/.Trash/*")
    elif _platform == "nt":
        print('Windows: %s' % text)
        
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
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
    elif _platform == "win64":
        print('Windows: %s' % text)
        try:
            os.system("rd /s c:\\\\$Recycle.Bin")  # newer Windows..
        except:
            pass
        try:
            os.system("rd /s c:\\\\recycler")  #  Windows XP, Vista, or Server 2003
        except:
            pass        
    elif _platform == "win32":
        print('Windows: %s' % text)
        try:
            os.system("rd /s c:\\\\$Recycle.Bin")  # Windows 7 or Server 2008
        except:
            pass
        try:
            os.system("rd /s c:\\\\recycler")  #  Windows XP, Vista, or Server 2003
        except:
            pass
    else:
        print(_platform)

# 

diskCleanup(os.name)

