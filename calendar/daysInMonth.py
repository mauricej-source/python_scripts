import calendar

def is_year_leap(year):
#
# Your code from LAB 4.3.1.6.
#
    result = False
    
    if(year > 0):
        if((year % 400) == 0):
            result = True
        elif((year % 100) == 0):
            result = False
        elif((year % 4) == 0):
            result = True
        else:
            result = False
            
    return result
    
def days_in_month(year, month):
#
# Write your new code here.
#
    day_in_month_leapyear = 29
    day_in_month = 28
    
    result_day_in_month = 0
    
    if(year > 0 and month > 0):
        if(is_year_leap(year) and month == 2):
            result_day_in_month = day_in_month_leapyear
        elif(is_year_leap(year) == False and month == 2):
            result_day_in_month = day_in_month
        else:
            result_day_in_month = calendar.monthrange(year, month)[1]
    
    return result_day_in_month
    
test_years = [1900, 2000, 2016, 1987]
test_months = [2, 2, 1, 11]
test_results = [28, 29, 31, 30]

for i in range(len(test_years)):
	yr = test_years[i]
	mo = test_months[i]
	
	print(yr, mo, "->", end="")
	
	result = days_in_month(yr, mo)
	
	if result == test_results[i]:
		print("OK")
	else:
		print("Failed")
