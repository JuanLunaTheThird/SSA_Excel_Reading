import pandas as pd
from datetime import datetime


class Student:

    def __init__(self, name):
        self.name = name
        self.days_worked = []
        self.tapped_in = []

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        # p1 == p2 calls p1.__eq__(p2)
        return self.name == other.name

    def tap_in(self, tap):
        self.tapped_in = tap

    def add_workday(self, work_day):
        append = True
        for x in self.days_worked:
            if work_day == x:
                append = False
        if append:
            self.days_worked.append(work_day)

    def update_student(self, student):
        for x in student.days_worked:
            if not self.works_that_day(x):
                self.days_worked.append(x)

    def works_that_day(self, day):
        for x in self.days_worked:
            if x == day:
                return True
        return False

    def print_tap(self):
        print(self.name + " was scheduled to work: ")
        for x in self.days_worked:
            print(x)
        print("and worked the days")
        for worked in self.tapped_in:
            print(worked)

    def to_string(self):
        string = self.name + " was scheduled to work: \n"
        for x in self.days_worked:
            string += convert_to_day(x) + '\n'
        string += "and didn't submit a shift log for these days: \n"
        count = 0
        for x in self.tapped_in:
            if not x[1]:
                string += x[0] + '\n'
                count += 1
        string += "Missing shift logs: " + str(count) + "/" + str(len(self.days_worked)) + " days" + "\n"
        return string

    def print_student(self):
        print(self.name)
        print("days worked: ")
        for x in self.days_worked:
            print(x)

        print("student printed")


class Schedule:
    def __init__(self):
        self.students = []
        self.days = []

    def add_schedule(self, student):
        self.students.append(student)

    def find_name(self, student_name):
        for x in self.students:
            if x.name == student_name:
                return x
        return None

    def update_student(self, student):
        new = True
        for x in self.students:
            if x.name == student.name:
                x.update_student(student)
                new = False
        if new:
            self.students.append(student)

    def load_schedule(self):
        schedule = read_schedule()
        dates = list(schedule.columns)
        dates = dates[3:10]
        for x in dates:
            self.days.append(x)

        for ind in schedule.index:
            if ind > 2:
                if not pd.isna(schedule['Name'][ind]):
                    student = schedule['Name'][ind]
                    if self.find_name(student) is None:
                        worker = Student(student)
                    else:
                        worker = self.find_name(student)
                    for x in dates:
                        entry = schedule[x][ind]
                        if not pd.isna(schedule[x][ind]):
                            if entry != "Off" and entry != "Vacation":
                                if not worker.works_that_day(x):
                                    worker.add_workday(x)
                    self.update_student(worker)

    def compare_with_shifts(self):
        shifts = pd.read_excel('shifts.xlsx', engine='openpyxl')

        for student in self.students:
            student.name = invert_name(student.name)
            indexes = get_indexes(shifts, student.name)
            days_worked = []
            for x in student.days_worked:
                day = convert_to_day(x)
                tup = (day, False)
                days_worked.append(tup)

            for day in days_worked:
                worked_that_day = False
                for idx in indexes:
                    index = idx[0]

                    compare = day[0] + " 00:00:00"
                    string_day = str(shifts["Today's Date:"][index])
                    if compare == string_day:
                        worked_that_day = True
                replace = days_worked.index(day)
                day = (day[0], worked_that_day)
                days_worked[replace] = day
            student.tap_in(days_worked)

    def print_who_tapped(self):
        for s in self.students:
            s.print_tap()
            print('\n')

    def write_to_file(self):
        txt = open("tapped_in.txt", "a")
        self.students = sorted(self.students)
        for s in self.students:
            txt.write(s.to_string())
            txt.write('\n')
        txt.close()

    def print_schedule(self):
        self.students = sorted(self.students)
        for s in self.students:
            s.print_student()
            print('\n')


def get_indexes(dfObj, value):
    listOfPos = []

    # isin() method will return a dataframe with
    # boolean values, True at the positions
    # where element exists
    result = dfObj.isin([value])

    # any() method will return
    # a boolean series
    seriesObj = result.any()

    # Get list of column names where
    # element exists
    columnNames = list(seriesObj[seriesObj == True].index)

    # Iterate over the list of columns and
    # extract the row index where element exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)

        for row in rows:
            listOfPos.append((row, col))

            # This list contains a list tuples with
    # the index of element in the dataframe
    return listOfPos


def convert_to_day(day):
    date = ""
    comma_pos = day.index(',')
    month = day[comma_pos + 2: comma_pos + 5]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    num_month = months.index(month) + 1
    day_of_month = day[comma_pos + 6:]

    if int(day_of_month) < 10:
        day_of_month = "0" + str(day_of_month)
    if num_month < 10:
        num_month = "0" + str(num_month)
    today = datetime.today()
    date = str(today.year) + "-" + str(num_month) + "-" + str(day_of_month)
    return date


def get_rid_of_middle_name(first_name):
    if ' ' in first_name:
        space_pos = first_name.index(' ')
        first_name = first_name[0:space_pos]
    return first_name


def invert_name(student_name):
    student_name = str(student_name)
    comma_pos = student_name.find(',')

    if comma_pos != -1:
        last_name = student_name[0:comma_pos]
        first_name = student_name[comma_pos + 1:]
        first_name = get_rid_of_middle_name(first_name[1:])
        name = first_name + " " + last_name
        return name
    return


def read_schedule():
    shifts = pd.read_excel('schedule.xlsx', engine='openpyxl')
    return shifts


def main():
    schedule = Schedule()
    schedule.load_schedule()
    schedule.compare_with_shifts()
    schedule.write_to_file()


if __name__ == '__main__':
    main()
