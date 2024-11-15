import zmq
import csv
import os
import time



class WishlistService:
    def __init__(self, file_name="wishlist.csv"):
        self.file_name = file_name
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        self.initialize_wishlist()

    def initialize_wishlist(self):
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Set', 'Year', 'Value'])  # Header for wishlist

    def add_card_to_wishlist(self, card_data):
        print("Processing request to add card to wishlist...")
        time.sleep(2)  # Add a 2-second delay to simulate processing times

        with open(self.file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(card_data)

        print(f"Added card to wishlist: {card_data}")

    def get_current_wishlist(self):
        '''This method retrieves the current wishlist from file and
        returns a formatted string listing contents'''
        with open(self.file_name, 'r') as file:
            current_list = []
            for line in file:
                current_list.append(line)
        if len(current_list) == 1:
            return "You don't have anything in your wishlist yet!"

        wishlist = current_list[1].split(',')
        return (f"Here is your current wishlist:\n"
                  f"Card Name: {wishlist[0]}\n"
                  f"Set Name: {wishlist[1]}\n"
                  f"Year: {wishlist[2]}\n"
                  f"Value: ${wishlist[3]}\n"
                )

    def listen(self):
        print("Wishlist service is listening for requests...")
        while True:
            message = self.socket.recv_json()
            if message['command'] == 'display':
                response = self.get_current_wishlist()
                self.socket.send_string(response)

            elif message['command'] == 'add':
                card_data = [message['name'], message['set_name'], message['year'], message['value']]
                self.add_card_to_wishlist(card_data)
                self.socket.send_string("Card added to wishlist successfully!")
            # else if message['command'] == 'edit':
                # do something here


if __name__ == "__main__":
    service = WishlistService()
    service.listen()
