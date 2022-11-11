from datetime import datetime
import string
import pandas as pd

INPUT_FILE = "addresses.txt"
OUTPUT_FILE = "address_list.csv"


# Creates objects to hold a mailing address
class Address(str):
    def __init__(self, base_address):
        self.address = base_address
        self.number = ""
        self.prefix = ""
        self.street = ""
        self.suffix = ""
        self.city = ""
        self.state = ""
        self.postcode = ""

    # Return all address parts joined with space seperator
    def normal_address(self):
        return " ".join((self.number, self.prefix, self.street, self.suffix,
                         self.city, self.state, self.postcode)).replace("  ", " ").replace("  ", " ")

    # Return address parts in a dictionary
    def address_parts(self):
        return {'number': self.number, 'prefix': self.prefix, 'street': self.street,
                'suffix': self.suffix, 'city': self.city,
                'state': self.state, 'postcode': self.postcode}


# Determine if a string is a standard directional abbreviation
def is_directional(f_string):
    # Returns True if string is in directional tuple
    return f_string.upper().strip() in ('N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SE')


# Determine if a string matches standard Zip Code format
def is_postalcode(f_string):
    # Five-digit zip code
    if len(f_string) == 5:
        if f_string.isnumeric():
            return True
    # Zip+4 zip code
    elif len(f_string) == 10:
        # starts with 5 digits - ends with 4 digits
        if (f_string[:5] + f_string[6:]).isnumeric():
            if f_string.find('-') == 5:
                return True
    return False


# Get a unique output filename based on the date and time
def outfile_name():
    dt = datetime.now()
    date = ".".join((str(dt.year), str(dt.month), str(dt.day)))
    time = ".".join((str(dt.hour), str(dt.minute), str(dt.second)))
    return f"address_{date}_{time}.csv"


def main():
    # Open the address file for reading
    with open(INPUT_FILE, "r", encoding='UTF-8') as in_file:
        # Build address list from file
        address_lines = [readline.rstrip() for readline in in_file]

    # Initiate empty address list
    address_list = []

    # Process each line in the list
    for line in address_lines:
        # Create an Address object for each address
        add = Address(line.upper())

        # Split the address line at white space
        add_split = add.split()

        # First part of string is house number
        add.number = add_split.pop(0)

        # After removing house number, move from right to left
        # Last part of string is postal code
        if is_postalcode(add_split[-1]):
            add.postcode = add_split.pop()

        # Next is State name
        add.state = add_split.pop()

        # City
        add.city = add_split.pop().rstrip(",")

        # Consider commas as address/city separator
        # Add each word to city name until comma is reached
        while len(add_split) > 0 and add_split[-1].find(",") < 1:
            add.city = add_split.pop() + " " + add.city

        # Separate directional suffix if found
        if is_directional(add_split[-1].rstrip(",")):
            add.suffix = add_split.pop().rstrip(",")

        # Main address part
        add.street = add_split.pop().rstrip(",")

        while len(add_split) > 0 and add_split[-1].find(",") < 1:
            # If a directional prefix is found, consider main address found
            if is_directional(add_split[-1].rstrip(",")):
                add.prefix = add_split.pop().rstrip(",")
                break
            # Add remaining words to main address string
            else:
                add.street = add_split.pop() + " " + add.street

        address_list.append(add.address_parts())

    df = pd.DataFrame(address_list)
    df.to_csv(outfile_name())


if __name__ == "__main__":
    main()
