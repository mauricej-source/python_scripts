from os import strerror
from collections import Counter

srcname = input("Enter the source file name: ")
try:
    src = open(srcname, 'rt')
    
    student_counts = Counter()
    
    line = src.readline()
    
    while line != '':
        line_string_array = line.split()
        
        content_index = 0
        student_fullname = ""
        
        for content in line_string_array:
            #print(content, end='')
            
            if content_index == 0 or content_index == 1:
                student_fullname = student_fullname + content + " "
                content_index = content_index + 1
            else:
                student_counts[student_fullname] += float(content)
                content_index = 0
                student_fullname = ""                
            
        line = src.readline()
        
    src.close()
    
    result_dictionary = dict(student_counts)
    
    print(result_dictionary)
        
except IOError as e:
    print("Cannot open the source file: ", strerror(e.errno))
    exit(e.errno)