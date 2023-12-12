from django.test import TestCase
from datetime import datetime, timedelta
from .models import *
# Create your tests here.
def check_time():
    time = datetime.now()
    time_star = time - timedelta(hours=2)
    time_end = time
    date_data = DsDatBan.objects.filter(thoi_gian_dat_ban__range=(time_star, time_end)).all()
    print(date_data)
if __name__== "__main__":
    check_time()