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
    '''Class to represent a card object'''
    def __init__(self, name, set_name, year, value):
        self.name = name
        self.set_name = set_name
        self.year = year
        self.value = value

    def __str__(self):
        return f"{self.name} - {self.year} {self.set_name} - ${self.value:.2f}"

class Collection:
    '''Class to represent a collection of card objects'''
    def __init__(self):
        self.wishlist = [] # list of card objects

    def add_card_to_wishlist(self, card):
        '''This method opens a socket, sends a message to the
        Wishlist Microservice requesting to add the specified
        card to the wishlist.
        Updates the wishlist data member.
        :return: List of card objects in wishlist
        '''
        self.wishlist.append(card)
        wishlist_socket.send_json({
            'command': 'add',
            'name': card.name,
            'set_name': card.set_name,
            'year': card.year,
            'value': card.value
        })
        response = wishlist_socket.recv_json() # response is a json object
        print(response['message'])

    def remove_card_from_wishlist(self, card):
        '''This method opens a socket, sends a message to the
        Wishlist Microservice requesting to remove the specified
        card from the wishlist.
        Then prints if/what card was removed from wishlist.
        Updates the wishlist data member.
        :return: List of card objects in wishlist
        '''
        self.wishlist.remove(card)
        wishlist_socket.send_json({
            'command': 'remove', # added line
            'name': card.name,
            'set_name': card.set_name,
            'year': card.year,
            'value': card.value
        })
        response = wishlist_socket.recv_json() # response is a json object
        print(response['message'])

    def display_wishlist(self):
        '''This method opens a socket, sends a message to the
        Wishlist Microservice requesting to display the current wishlist.
        Then prints the wishlist to console
        :return: List of card objects in wishlist
        '''
        wishlist_socket.send_json({
            'command': 'display',
        })
        response = wishlist_socket.recv_json() # response is json object
        # response contains:
        # -'message' string
        # -'cards' list of dicts representing cards
        print(response['message'])
        wishlist_data = response['cards']
        # update wishlist data member
        self.wishlist = []
        for card in wishlist_data:
            self.wishlist.append(Card(card['name'], card['set_name'], card['year'], float(card['value'])))
        return wishlist_data

    def edit_wishlist(self, new_data):
        wishlist_socket.send_json({
            'command': 'edit',
            'old_name': new_data[0],
            'name': new_data[1],
            'set_name': new_data[2],
            'year': new_data[3],
            'value': new_data[4]
        })
        response = wishlist_socket.recv_json()
        print("\n" + response['message'])

def display_menu():
    print()
    print("  Please enter the correlating number")
    print("  to proceed in the selected option.")
    print()
    print("1. Display Current Wishlist")
    print("2. Add Card to Wishlist")
    print("3. Remove Card from Wishlist")
    print("4. Edit Card in Wishlist")
    print("5. Quit")


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
            wishlist = collection.display_wishlist()
            edit_card_choice = int(input("Enter which card number would you like to edit: "))
            card_to_edit = wishlist[edit_card_choice - 1]
            print("Enter new values for your selected card (or leave blank to keep)")
            card_data = []
            card_data.append(card_to_edit['name'])
            params = ["Name: ", "Set Name: ", "Year: ", "Value: $"]
            for item in params:
                current_input = input(f"Enter New {item}")
                card_data.append(current_input)
            collection.edit_wishlist(card_data)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("\nInvalid option, please try again.")
        print("+------------------------------------------------------------+")

if __name__ == "__main__":
    main()