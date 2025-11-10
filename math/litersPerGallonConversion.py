def liters_100km_to_miles_gallon(liters):
#
# Write your code here.
#
    number_of_kilometers = 100
    one_mile_is_kilometer = 1.609344
    one_gallon_is_liters = 3.785411784
    
    number_of_gallons = liters / one_gallon_is_liters
    number_of_miles = number_of_kilometers / one_mile_is_kilometer
    
    return number_of_miles / number_of_gallons
    
    

def miles_gallon_to_liters_100km(milespergallon):
#
# Write your code here
#
    number_of_kilometers = 100
    one_mile_is_kilometer = 1.609344
    one_gallon_is_liters = 3.785411784
    
    number_of_kilometers = milespergallon * one_mile_is_kilometer
    
    return (one_gallon_is_liters / number_of_kilometers)*100
    
print(liters_100km_to_miles_gallon(3.9))
print(liters_100km_to_miles_gallon(7.5))
print(liters_100km_to_miles_gallon(10.))

print(miles_gallon_to_liters_100km(60.3))
print(miles_gallon_to_liters_100km(31.4))
print(miles_gallon_to_liters_100km(23.5))
