import zmq
import os
import csv

# Initialize ZeroMQ context and socket for the wishlist
context = zmq.Context()
wishlist_socket = context.socket(zmq.REQ)
wishlist_socket.connect("tcp://localhost:5555")

title = ("🏆 Welcome to the Ultimate Sports & Trading Cards Manager 🃏")
print(title)
print("     Keep track of your cards in a personal collection!")
print("+------------------------------------------------------------+")

class Card:
    def __init__(self, name, set_name, year, value):
        self.name = name
        self.set_name = set_name
        self.year = year
        self.value = value

    def __str__(self):
        return f"{self.name} - {self.year} {self.set_name} - ${self.value:.2f}"

class Collection:
    def __init__(self):
        self.cards = []
        self.load_from_file()

    def add_card(self, card):
        self.cards.append(card)
        print(f"\nAdded {card.name} to the collection.")
        self.save_to_file()

    def view_cards(self):
        if not self.cards:
            print("\nThe collection is empty.")
        else:
            print("\nYour Trading Card Collection:")
            for i, card in enumerate(self.cards, 1):
                print(f"\n{i}. {card}")

    def delete_card(self, index):
        if 0 <= index < len(self.cards):
            card_to_delete = self.cards[index]
            confirm = input(f"\nAre you sure you want to delete '{card_to_delete.name}'? "
                            f"\n*Removing item will result in lost card data* (y/n): ").lower()

            if confirm == 'y':
                self.cards.pop(index)
                print(f"\nRemoved {card_to_delete.name} from the collection.")
                self.save_to_file()
            else:
                print("\nDeletion cancelled.")
        else:
            print("\nInvalid input. Please try again.")

    def add_card_to_wishlist(self, card):
        wishlist_socket.send_json({
            'command': 'add', # added line
            'name': card.name,
            'set_name': card.set_name,
            'year': card.year,
            'value': card.value
        })
        message = wishlist_socket.recv_string()
        print(message)

    # added method
    def display_wishlist(self):
        '''This method opens a socket, sends a message to the
        Wishlist Microservice requesting to display the current wishlist.
        Then prints the wishlist to console'''
        wishlist_socket.send_json({
            'command': 'display',
        })
        message = wishlist_socket.recv_string()
        print(message)

    def save_to_file(self):
        with open('card_collection.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Year', 'Set', 'Value'])  # Write header
            for card in self.cards:
                writer.writerow([card.name, card.year, card.set_name, card.value])
        print("Collection saved to 'card_collection.csv'.")

    def load_from_file(self):
        if os.path.exists('card_collection.csv'):
            with open('card_collection.csv', 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) == 4:
                        try:
                            name_part = row[0].strip()
                            year = row[1].strip()
                            set_part = row[2].strip()
                            value = float(row[3].strip())
                            card = Card(name_part, set_part, year, value)
                            self.cards.append(card)
                        except ValueError:
                            print("Error loading card data; skipping entry.")
            print("Loaded existing collection from 'card_collection.csv'.")
        else:
            print("No existing collection found. Starting a new collection.")

    def add_cards_from_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) == 4:
                        try:
                            name_part = row[0].strip()
                            year = row[1].strip()
                            set_part = row[2].strip()
                            value = float(row[3].strip())
                            card = Card(name_part, set_part, year, value)
                            self.add_card(card)  # Use the existing add_card method
                        except ValueError:
                            print(f"Error converting value '{row[3]}'; skipping entry.")
        else:
            print(f"The file {file_path} does not exist.")

def display_menu():
    print()
    print("  Please enter the correlating number")
    print("  to proceed in the selected option.")
    print()
    print("1. Add a Card Manually")
    print("2. Add Cards from a CSV File")
    print("3. View Collection")
    print("4. Delete a Card")
    print("5. Add Card to Wishlist")  # New option
    print("6. Display Current Wishlist") # added new option
    print("7. About") # changed to 7
    print("8. Quit") # changed to 8

def show_about():
    print("\n+------------------- About -------------------+")
    print("  Welcome to the Ultimate Sports & Trading")
    print("  Cards Manager! This program helps you")
    print("  keep track of your valuable trading card")
    print("  collection by allowing you to add, view,")
    print("  and delete cards from your personal list.")
    print()
    print("  Features:")
    print("  - Add new cards to your collection with")
    print("    detailed information such as name, set,")
    print("    year, and value.")
    print("  - View all your cards in a user-friendly")
    print("    format to easily track your collection.")
    print("  - Delete cards from your collection with")
    print("    a confirmation prompt to prevent accidental")
    print("    deletions.")
    print("  - Automatic saving and loading of your")
    print("    collection data to/from 'card_collection.csv'.")
    print()
    print("  This program is ideal for collectors,")
    print("  enthusiasts, or anyone looking to manage")
    print("  their trading card collection effectively.")
    print()
    print("  Credits:")
    print("  Developed by Richard Phan")
    print("  Inspired by the love for trading card collecting!")
    print()
    print("  For feedback or suggestions, please contact:")
    print("  phanri@oregonstate.edu")
    print("+--------------------------------------------+")

def main():
    collection = Collection()

    while True:
        display_menu()
        choice = input("\nEnter your choice: ")

        if choice == "1":
            name = input("Card Name: ")
            set_name = input("Set Name: ")
            year = input("Year: ")
            value = float(input("Price Acquired: $"))

            card = Card(name, set_name, year, value)
            collection.add_card(card)

        elif choice == "2":
            file_path = input("Enter the path to the CSV file: ")
            collection.add_cards_from_file(file_path)

        elif choice == "3":
            collection.view_cards()

        elif choice == "4":
            collection.view_cards()
            try:
                index = int(input("\nEnter the card number to delete: ")) - 1
                collection.delete_card(index)
            except ValueError:
                print("\nPlease enter a valid number.")

        elif choice == "5":
            name = input("Card Name: ")
            set_name = input("Set Name: ")
            year = input("Year: ")
            value = float(input("Value: $"))
            card = Card(name, set_name, year, value)
            collection.add_card_to_wishlist(card)  # Send to wishlist service

        elif choice == "6": # added option to display wishlist
            collection.display_wishlist()

        elif choice == "7":
            show_about()

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("\nInvalid option, please try again.")

if __name__ == "__main__":
    main()