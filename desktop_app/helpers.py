import datetime
import json

def load_dst_dates():
    """
    opens the daylight_savings.json file to gain access to the start and end dates of daylight savings storred there
    """
    with open("daylight_savings.json", 'r') as file:
        return json.load(file)
    
def hour_change(calender_date, region):
    """
    takes as argument a calender date and region and returns end if the clock goes back an hour (3am becomes 2am),
    start if the clock goes foward an hour (2 am becomes 3am)
    or none for all the days the clocks do not change
    """
    year, month, day = map(int, calender_date.split('-'))
    if region == "melbourne" or region == "sydney":
        daylight_savings_data = load_dst_dates()
        if str(year) in daylight_savings_data['AEST']:
            start_date = daylight_savings_data['AEST'][str(year)]['start']
            end_date = daylight_savings_data['AEST'][str(year)]['end']

            start_month, start_day = map(int, start_date.split('-'))
            end_month, end_day = map(int, end_date.split('-'))

            if start_month == month and start_day == day:
                return "START"
            if end_month == month and end_day == day:
                return "END"
    return None

def get_offset(date, region="melbourne"):
    """
    takes 2 arguments: date in the format "yyyy-mm-dd" and a region (city name) default melbourne then returns 
    the offset from utc to support timezones
    """
    year, month, day = map(int, date.split('-'))
    if region == "melbourne" or region == "sydney":
        daylight_savings_data = load_dst_dates()
        if str(year) in daylight_savings_data['AEST']:
            start_date = daylight_savings_data['AEST'][str(year)]['start']
            end_date = daylight_savings_data['AEST'][str(year)]['end']

            start_month, start_day = map(int, start_date.split('-'))
            end_month, end_day = map(int, end_date.split('-'))

            start_datetime = datetime.datetime(year, start_month, start_day)
            end_datetime = datetime.datetime(year, end_month, end_day)
            current_datetime = datetime.datetime(year, month, day)

            if start_datetime <= current_datetime or current_datetime <= end_datetime:
                return 11
        return 10
    
    if region == "perth":
        return 8

def get_timestamp(date, location="melbourne", h=0, m=0):
    """
    takes the date and the desired time and calculates the timestamp 
    (seconds since epoch <01/01/1970 00:00>) if the date. takes as 
    arguments: the date in format "yyyy-mm-dd" and the offset for the
    desired timezone. optional arguments for the time, h=hour and m=minute
    time is 00:00 by default
    """
    specific_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    offset = get_offset(date, location)

    # Create a new datetime object for 6 AM on the specified date
    six_am_date = specific_date.replace(hour=h, minute=m, second=0)
    timezone = datetime.timezone(datetime.timedelta(hours=offset, minutes=0))
    six_am_date = six_am_date.replace(tzinfo=timezone)

    # Get the time difference in seconds since the epoch (January 1, 1970)
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    seconds_since_epoch = (six_am_date - epoch).total_seconds()

    return seconds_since_epoch

def get_gaming_day_base(date, location):
    """
    returns the timestamp of 6 am of the specified date and location, 6am being the start of the gaming day
    """
    return get_timestamp(date, location, h=6, m=0)

if __name__=="__main__":
    print(get_gaming_day_base("2023-12-26", "melbourne"))