import zmq
import csv
import os
import time

class WishlistService:
    '''Wishlist Service class represents an object for manipulating wishlist data
    contained in a .csv file.
    '''
    def __init__(self, file_name="wishlist.csv"):
        self.file_name = file_name
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        self.initialize_wishlist()

    def initialize_wishlist(self):
        '''Method to create wishlist.csv file if it doesn't already exist'''
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Set', 'Year', 'Value'])  # Header for wishlist

    def add_card_to_wishlist(self, card_data):
        '''Method to add a line, containing card data, to the wishlist file.'''
        print("Processing request to add card to wishlist...")
        with open(self.file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(card_data)

        print(f"Added card to wishlist: {card_data}")

    def get_current_wishlist(self):
        '''This method returns a List of Lists containing card data in wishlist'''
        with open(self.file_name, 'r') as file:
            current_list = []
            for line in file:
                current_list.append(line.strip())
        if len(current_list) == 1:
            return []
        wishlist = []
        for i in range(1, len(current_list)):
            line = current_list[i].split(',')
            line = [item.strip() for item in line] # remove whitespace from items
            wishlist.append(line)

        return wishlist

    def print_current_wishlist(self):
        '''This method retrieves the current wishlist from file and
        returns a formatted string listing contents'''
        current_list = self.get_current_wishlist()
        if len(current_list) == 0:
            return "You don't have anything in your wishlist yet!\n"

        wishlist_string = f"Here is your current wishlist:\n\n"
        for i, item in enumerate(current_list):
            wishlist_string += f"{i + 1}. {item[0]} - {item[2]} {item[1]} - ${float(item[3]):.2f}\n\n"

        return wishlist_string

    def remove_from_wishlist(self, card_data):
        '''This method removes a card from the wishlist
        :param card_data: Object of type List containing data of card to remove.
        :return: String to indicate if/what was removed from wishlist.
        '''
        current_list = self.get_current_wishlist()
        ritem = None
        with open(self.file_name, 'w') as file:
            file.write("Name, Set, Year, Value\n")
            for item in current_list:
                item = [param.strip() for param in item]
                if item == card_data:
                    ritem = item
                else:
                    file.write(f"{item[0]}, {item[1]}, {item[2]}, {item[3]}\n")
        if ritem:
            response = "The following card has been removed from wishlist:\n"
            response += f"{ritem[0]} - {ritem[1]} {ritem[2]} - ${float(ritem[3]):.2f}\n"
            return response

        return "The card you are trying do delete is not in the wishlist"

    def listen(self):
        print("Wishlist service is listening for requests...")
        while True:
            message = self.socket.recv_json()
            if message['command'] == 'display':
                response = self.print_current_wishlist()
                card_data = self.get_current_wishlist()
                cards = []
                for card in card_data:
                    current_card = {}
                    current_card['name'] = card[0].strip()
                    current_card['set_name'] = card[1].strip()
                    current_card['year'] = card[2].strip()
                    current_card['value'] = card[3].strip()
                    cards.append(current_card)

                self.socket.send_json({
                    'message': response,
                    'cards': cards,
                    })

            elif message['command'] == 'add':
                card_data = [message['name'], message['set_name'], message['year'], message['value']]
                self.add_card_to_wishlist(card_data)
                self.socket.send_json({'message': "Card added to wishlist successfully!"})

            elif message['command'] == 'remove':
                card_data = [message['name'], message['set_name'], message['year'], str(message['value'])]
                response = self.remove_from_wishlist(card_data)
                self.socket.send_json({'message': response})

if __name__ == "__main__":
    service = WishlistService()
    service.listen()
