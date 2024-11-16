import zmq
import os
import csv

# Initialize ZeroMQ context and socket for the wishlist
context = zmq.Context()
wishlist_socket = context.socket(zmq.REQ)
wishlist_socket.connect("tcp://localhost:5555")

title = ("Wishlist manager - Test Program")
print("+------------------------------------------------------------+")
print(title)
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
        self.wishlist = []
        # self.load_from_file()

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

    def add_card_to_wishlist(self, card):
        wishlist_socket.send_json({
            'command': 'add',
            'name': card.name,
            'set_name': card.set_name,
            'year': card.year,
            'value': card.value
        })
        message = wishlist_socket.recv_string()
        print(message)

    def remove_card_from_wishlist(self, card):
        self.wishlist.remove(card)
        wishlist_socket.send_json({
            'command': 'remove', # added line
            'name': card.name,
            'set_name': card.set_name,
            'year': card.year,
            'value': card.value
        })
        message = wishlist_socket.recv_string()
        print(message)

    def display_wishlist(self):
        '''This method opens a socket, sends a message to the
        Wishlist Microservice requesting to display the current wishlist.
        Then prints the wishlist to console
        :return: List of card objects in wishlist
        '''
        wishlist_socket.send_json({
            'command': 'display',
        })
        response = wishlist_socket.recv_json()
        print(response['message'])
        wishlist_data = response['cards']
        # update wishlist data member
        self.wishlist = []
        for card in wishlist_data:
            self.wishlist.append(Card(card['name'], card['set_name'], card['year'], float(card['value'])))

def display_menu():
    print()
    print("  Please enter the correlating number")
    print("  to proceed in the selected option.")
    print()
    print("1. Display Current Wishlist")
    print("2. Add Card to Wishlist")
    print("3. Remove Card from Wishlist")
    print("4. Quit")


def main():
    collection = Collection()

    while True:
        display_menu()
        choice = input("\nEnter your choice: ")

        if choice == "1":
            collection.display_wishlist()

        elif choice == "2":
            name = input("Card Name: ")
            set_name = input("Set Name: ")
            year = input("Year: ")
            value = float(input("Value: $"))
            card = Card(name, set_name, year, value)
            collection.add_card_to_wishlist(card)

        elif choice == "3":
            collection.display_wishlist()
            delete_card = int(input("Enter which card number would you like to delete: "))
            collection.remove_card_from_wishlist(collection.wishlist[delete_card - 1])

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("\nInvalid option, please try again.")
        print("+------------------------------------------------------------+")

if __name__ == "__main__":
    main()