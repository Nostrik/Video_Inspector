import re


class NumberChecker:

    def __init__(self) -> None:
        self.previous_number = None

    def check_number(self, number):
        if number is not None:
            number = int(number)
            if self.previous_number is None or number == self.previous_number + 1:
                self.previous_number = number
                return True
            else:
                self.previous_number = None
                return False


def current_frame_to_single_frame(value):
    if value:
        a = round(float(value)/24, 3)
        b = round((a % 1), 2)
        if 0 < b < 0.05:
            return 1
        elif  0.05 < b < 0.1:
            return 2
        elif  0.1 < b < 0.15:
            return 3
        elif 0.15 < b < 0.2:
            return 4
        elif 0.2 < b < 0.25:
            return 5
        elif 0.24 < b < 0.26:
            return 6
        elif 0.25 < b < 0.3:
            return 7
        elif 0.3 < b < 0.35:
            return 8
        elif 0.35 < b < 0.4:
            return 9   
        elif 0.4 < b < 0.45:
            return 10
        elif 0.45 < b < 0.5:
            return 11
        elif 0.49 < b < 0.51:
            return 12
        elif 0.5 < b < 0.55:
            return 13
        elif 0.55 < b < 0.6:
            return 14
        elif 0.6 < b < 0.65:
            return 15
        elif 0.65 < b < 0.7:
            return 16
        elif 0.7 < b < 0.75:
            return 17
        elif 0.74 < b < 0.76:
            return 18
        elif 0.75 < b < 0.8:
            return 19
        elif 0.8 < b < 0.85:
            return 20
        elif 0.85 < b < 0.9:
            return 21
        elif 0.9 < b < 0.95:
            return 22
        elif 0.95 < b < 1:
            return 23
        elif -0.1 < b < 0.1:
            return 24


def check_number(number):
    if number is not None:
        number = int(number)
        if previous_number is None or number == previous_number + 1:
            previous_number = number
            return True
        else:
            previous_number = None
            return False


# if __name__ == "__main__":
#     for i in range(1, 145):
#         print(f"{i} = > {current_frame_to_single_frame(i)}")