from datetime import datetime
import pandas as pd

INPUT_FILE = "addresses.txt"


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

    # Return address parts joined with space seperator
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
    directionals = ('N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SE')
    # Returns True if string is in directional tuple
    return f_string.upper().strip() in directionals


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
def datetime_name():
    dt = datetime.now()
    date = ".".join((str(dt.year), str(dt.month), str(dt.day)))
    time = ".".join((str(dt.hour), str(dt.minute), str(dt.second)))
    return f"address_{date}_{time}.csv"


def get_filename(f_prompt, f_default):
    print(f"{f_prompt} (blank for {f_default}): ", end='')
    f_in = input()
    if f_in == '':
        return f_default
    else:
        return f_in


# Main body of program
def main():
    # Display program introduction
    print("Address Conversion")
    print("- "*10)
    print("This program accepts a file with a list of normalized addresses.")
    print("It will output a CSV file of addresses split into component parts.")
    print()

    infile_name = get_filename("Enter the file name to import", INPUT_FILE)

    # Open the address file for reading
    try:
        with open(infile_name, "r", encoding='UTF-8') as in_file:
            # Build address list from file
            address_lines = [readline.rstrip() for readline in in_file]

    except FileNotFoundError:
        print(f"The file {infile_name} was not found.")
        input("Press <enter> to quit")
        quit()

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

        # Append each address as dictionary to the list
        address_list.append(add.address_parts())

    # Build a pandas data frame from the address list of dictionaries
    df = pd.DataFrame(address_list)

    # Remove duplicate rows from the data frame and count the difference
    file_len = df.shape[0]
    df.drop_duplicates(inplace=True)
    dup_len = file_len - df.shape[0]

    # Get output filename
    outfile_name = get_filename("Enter the file name to export", datetime_name())

    # Output the data frame to a csv file - Assign a heading to the index column
    df.to_csv(outfile_name, index_label='line_no')

    print()
    print("Conversion complete")
    print("- "*9)
    print(f"{df.shape[0]} Addresses have been converted.")
    print(f"{dup_len} duplicates have been removed.")
    print()
    input("Press <enter> to quit")

# Call main function
if __name__ == "__main__":
    main()
