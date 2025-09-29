import calendar
from datetime import date

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

def day_of_year(year, month, day):
#
# Write your new code here.
#
    result_days_in_year = 0
    
    if(year > 0 and month > 0 and day > 0):
        # 1. Create a date object for the input date
        input_date = date(year, month, day)
    
        # 2. Convert the date object to a time tuple
        time_tuple = input_date.timetuple()
    
        # 3. Access the tm_yday attribute, which is the Day of the Year
        # (January 1st is 1, January 31st is 31, February 1st is 32, etc.)
        result_days_in_year = time_tuple.tm_yday
        
    return result_days_in_year

print(day_of_year(2000, 12, 31))
