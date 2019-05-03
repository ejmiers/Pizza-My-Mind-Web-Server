from datetime import datetime

class Date():
    def __init__(self):
        self.currentDay = datetime.today
        self.currentTime = datetime.now()
        self.stringDate = datetime.now().strftime("%m_%d_%Y")
        self.month = datetime.now().month
        self.year = datetime.now().year

        fallMonths = [8, 9, 10, 11, 12]
        springMonths = [1, 2, 3, 4, 5]


        if (datetime.now().month in fallMonths):
            self.season = 'Fall'
        elif (datetime.now().month in springMonths):
            self.season = 'Spring'
        else:
            self.season = 'Summer'

    def __repr__(self):
        return f"Date('{self.stringDate}', '{self.month}', '{self.year}','{self.season}')"
