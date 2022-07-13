import calendar
from django.utils import timezone


class Day:
    def __init__(self, number, past, month, year):
        self.number = number
        self.past = past
        self.month = month
        self.year = year

    # def __str__(self):
    #     return str(self.number)


class Calendar(calendar.Calendar):

    def __init__(self, year, month):
        super().__init__(firstweekday=6) # calendar 모듈의 Calendar 클래스에서 기본 인자로 firstweekday=0 이 설정되어 있다. 이것을 캘린더가 월요일부터 시작한다는 의미임. 
        self.year = year
        self.month = month
        self.day_names = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        self.months = (
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        )
    
    def get_days(self):
        weeks = self.monthdays2calendar(self.year, self.month)
        days = []
        for week in weeks:
            for day, _ in week:
                now = timezone.now()
                today = now.day
                this_month = now.month
                past = False # 날짜는 기본적으로 과거가 아닌 것으로 디폴트값 주기.
                if this_month == self.month: # 원리적으로 과거라는 것인 이번달인 경우만 해당됨으로. 다음달의 날짜는 비교 대상이 아님. 
                    if day < today:
                        past = True
                new_day = Day(number=day, past=past, month=self.month, year=self.year) # 날짜 하나하나를 배열로 담는 것이 아니라 Day 클래스 객체로 담아서 이 날짜가 오늘 대비 지난 과거인지 아닌지를 구분해서 담아 표현할 수 있다. 
                days.append(new_day)
        return days

    def get_month(self):
        return self.months[self.month-1]
