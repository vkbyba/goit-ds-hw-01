from collections import defaultdict, UserDict
from datetime import date,datetime, timedelta

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)  
        self.__value = None
        self.value = value
    
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(self.value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
            self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if not phone:
            raise ValueError("Phone number not found.")
        self.add_phone(new_number)
        self.remove_phone(old_number)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def get_birthday(self):
        return self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "No birthday set"

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(phone.value for phone in self.phones)}, Birthday: {self.get_birthday()}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return "Contact deleted."
        return "Contact not found."

    def find_next_birthday(self, weekday):
        today = date.today()
        day_delta = (weekday - today.weekday() + 7) % 7
        next_weekday_date = today + timedelta(days=day_delta)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday and record.birthday.value.replace(year=today.year).date() == next_weekday_date:
                upcoming_birthdays.append(record)
        return upcoming_birthdays

    def get_upcoming_birthday(self, days=7):
        today = date.today()
        date_in_future = today + timedelta(days=days)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year).date()
                if today <= birthday_this_year <= date_in_future:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message



@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise IndexError("Not enough arguments. Usage: change <name> <old_phone> <new_phone>")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    return "Contact not found."


@input_error
def show_phones(args, book: AddressBook):
    if len(args) < 1:
        raise IndexError("Not enough arguments. Usage: phone <name>")
    name = args[0]
    record = book.find(name)
    if record:
        return f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}"
    return "Contact not found."


@input_error
def show_all(book: AddressBook):
    return "\n".join(str(record) for record in book.values())


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise IndexError("Not enough arguments. Usage: add-birthday <name> <birthday>")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."


@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise IndexError("Not enough arguments. Usage: show-birthday <name>")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.get_birthday()}"
    return "Birthday not set or contact not found."


@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else 7  
    upcoming_birthdays = book.get_upcoming_birthday(days)
    if upcoming_birthdays:
        return '\n'.join(f"{record.name.value}'s birthday is on {record.get_birthday()}" for record in upcoming_birthdays)
    return "No birthdays in the next {} days.".format(days)


def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0]
    args = parts[1:]
    return command, args





def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            if len(args) < 3:
                print("Not enough arguments. Usage: change <name> <old_phone> <new_phone>")
            else:
                name, old_phone, new_phone = args
                record = book.data.get(name)
                if record:
                    record.edit_phone(old_phone, new_phone)
                    print("Phone number updated.")
                else:
                    print("Contact not found.")

        elif command == "phone":
            if len(args) < 1:
                print("Not enough arguments. Usage: phone <name>")
            else:
                name = args[0]
                record = book.data.get(name)
                if record:
                    print(f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}")
                else:
                    print("Contact not found.")

        elif command == "all":
            for name, record in book.items():
                print(f"{name}: {record}")

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
