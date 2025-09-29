import math

def is_prime(num):
#
# Write your code here.
#
    result = True
    
    if(num >= 2):
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                result = False
                break
            
    return result
    
for i in range(1, 20):
	if is_prime(i + 1):
			print(i + 1, end=" ")
print()

for i in range(10, 50):
	if is_prime(i + 1):
			print(i + 1, end=" ")
print()
