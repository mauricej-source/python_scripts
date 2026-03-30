from os import strerror
from collections import Counter

srcname = input("Enter the source file name: ")
try:
    src = open(srcname, 'rt')
    lcnt = 0
    ccnt = 0
    
    letter_counts = Counter()
    
    line = src.readline()
    
    while line != '':
        lcnt += 1
        
        for ch in line:
            print(ch, end='')
            ch_lower = ch.lower()
            
            letter_counts[ch_lower] += 1
            
            ccnt += 1
        line = src.readline()
        
    src.close()
    
    result_dictionary = dict(letter_counts)
    
    print("\n\nCharacters in file:", ccnt)
    print("Lines in file:     ", lcnt)
    
    print("Number of Characters in the File:")
    for letter, count in sorted(result_dictionary.items()):
        print(f"'{letter}' -> {count}")
        
    sorted_items_desc_value = sorted(result_dictionary.items(),key=lambda item: item[1],reverse=True)

    # Convert back to a dictionary
    sorted_dict_desc_value = dict(sorted_items_desc_value)

    print("Sorted Number of Characters in the File:")
    for letter, count in sorted_dict_desc_value.items():
        print(f"'{letter}' -> {count}")
        
except IOError as e:
    print("Cannot open the source file: ", strerror(e.errno))
    exit(e.errno)