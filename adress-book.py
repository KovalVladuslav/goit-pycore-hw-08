from collections import UserDict
from datetime import datetime, timedelta
from colorama import init, Fore, Style
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
      
class Name(Field):
    def __init__(self, value):
        if not bool(value.strip()):
            raise ValueError(f"Invalid name: {value}. Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise Exception(f"Invalid phone number: {value}. Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_birthday(self, date):
      self.birthday = Birthday(date)

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))
        
    def edit_phone(self, old_number, new_number):
      for phone in self.phones:
          if phone.value == old_number:
            phone.value = new_number
            return True

      return False
    
    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        return f"Contact name: {Fore.YELLOW}{self.name.value}{Style.RESET_ALL}, phones: {Fore.YELLOW}{'; '.join(p.value for p in self.phones)}{Style.RESET_ALL}, birthday: {Fore.YELLOW}{self.birthday}{Style.RESET_ALL}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        
    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True

        return False
      
    def get_upcoming_birthdays(self):
        result = []

        for user in self.data:
            if "birthday" in user:
                birthday = datetime.strptime(user["birthday"], "%Y.%m.%d").date()
            
                currentDate = datetime.now().date()

                congratulationDate = birthday.replace(year=currentDate.year)

                if congratulationDate < currentDate:
                    congratulationDate = congratulationDate.replace(year=currentDate.year + 1)

                daysUntilBirthday = (congratulationDate - currentDate).days

                dayOfWeek = congratulationDate.weekday()
                #перевірка чи не на вихідних др
                if (dayOfWeek > 4):
                    holidayAfterBirthaday = 7 - dayOfWeek

                    congratulationDate = congratulationDate + timedelta(days=holidayAfterBirthaday)

                #в кого др ближчі 7 днів
                if (daysUntilBirthday <= 7):
                    result.append({ "name": user["name"], "congratulation_date": congratulationDate.strftime("%A, %d %B %Y")})
        
        return result
      

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            print(f"{Fore.RED}User not found{Style.RESET_ALL}")
        except ValueError:
            return f"{Fore.YELLOW}Enter the argument for the command.{Style.RESET_ALL}"
        except IndexError:
            print(IndexError)
            return f"{Fore.YELLOW}Enter the argument for the command.{Style.RESET_ALL}"
        except Exception as err:
            return f"{Fore.YELLOW}{err}{Style.RESET_ALL}"
    
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

@input_error
def change_contact(args, book: AddressBook):
    name, oldPhone, newPhone  = args
    
    record = book.find(name)

    if (record):
        record.edit_phone(oldPhone, newPhone)
 
        print(f"{Fore.GREEN}Contact changed.{Style.RESET_ALL}")
    else:
        raise KeyError

@input_error
def phone_user(args, book: AddressBook):
    [name] = args
    
    record = book.find(name)

    if record:
        print(record)
    else:
        raise KeyError
    
@input_error
def all_users(book: AddressBook):
    for record in book.data.values():
        print(record) 
        
@input_error
def add_birthday(args, book: AddressBook):
    name, date  = args
    
    record = book.find(name)
    
    if(record):
        record.add_birthday(date)
        print(f"{Fore.GREEN}Birthday added.{Style.RESET_ALL}")
    else:
        raise KeyError
    
@input_error
def show_birthday(args, book: AddressBook):
    [name] = args

    record = book.find(name)

    if record.birthday:
        print(f"{Fore.GREEN}{record.birthday}")
    else:
        print(f"{Fore.YELLOW}Not added birthday")
  
@input_error
def birthdays(book: AddressBook):
    date = book.get_upcoming_birthdays()
    print(date)
    for item in date:
        print(f"Name: {Fore.YELLOW}{item['name']}{Style.RESET_ALL}, Date: {Fore.YELLOW}{item['date']}{Style.RESET_ALL}")
    
def main(book):
    print(f"{Fore.GREEN}Welcome to the assistant bot!{Style.RESET_ALL}")
    
    print(f"{Fore.WHITE}Available commands:")
    print(f"{Fore.GREEN}\t add {Fore.YELLOW}[name] [phone]{Fore.WHITE} - add a new contact with name and phone number, or add another phone number.")
    print(f"{Fore.GREEN}\t change {Fore.YELLOW}[name] [old phone] [new phone]{Fore.WHITE} - change the phone number.")
    print(f"{Fore.GREEN}\t phone {Fore.YELLOW}[name]{Fore.WHITE} - show phone numbers.")
    print(f"{Fore.GREEN}\t all{Fore.WHITE} - show all contacts.")
    print(f"{Fore.GREEN}\t add-birthday {Fore.YELLOW}[name] [birthday] {Fore.WHITE}- add a birthday (DD.MM.YYYY).")
    print(f"{Fore.GREEN}\t show-birthday {Fore.YELLOW}[name] {Fore.WHITE}- show the birthday.")
    print(f"{Fore.GREEN}\t birthdays{Fore.WHITE} - show birthdays that will occur within the next week.")
    print(f"{Fore.GREEN}\t hello {Fore.WHITE}- get a greeting from the bot.")
    print(f"{Fore.GREEN}\t close {Fore.WHITE}or {Fore.GREEN}exit {Fore.WHITE}- close the program.")
    
    while True:
        user_input = input(f"{Fore.CYAN}Enter a command: {Style.RESET_ALL}"
)
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print(f"{Fore.MAGENTA}Good bye!{Style.RESET_ALL}")
            save_data(book)
            break

        elif command == "hello":
            print(f"{Fore.MAGENTA}How can I help you?{Style.RESET_ALL}")

        elif command == "add":
            add_contact(args, book)

        elif command == "change":
           change_contact(args, book)

        elif command == "phone":
            phone_user(args, book)

        elif command == "all":
            all_users(book)

        elif command == "add-birthday":
            add_birthday(args, book)

        elif command == "show-birthday":
            show_birthday(args, book)

        elif command == "birthdays":
            birthdays(book)
            
        else:
            print(f"{Fore.RED}Invalid command.{Style.RESET_ALL}")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

if __name__ == "__main__":
    book = load_data()
    
    main(book)
    
    
