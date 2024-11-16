# Microservice Communication

The wishlist management service communicates via ZeroMQ and binds to port 5555. To accommodate other services, you can change the port the microservice binds to as required.
## Prerequisites
Prior to using the microservice you must have ZeroMQ installed on your system:
```bash
pip install zmq
```
## Files
wishlist_service.py is the microservice
test_wishlist.py is the test program shown in the video

## REQUESTING DATA:
First import zmq, set up ZeroMQ context, create and connect a request socket, and then send a request.
```python
import zmq

# ZeroMQ setup
context = zmq.Context()
wishlist_socket = context.socket(zmq.REQ)
wishlist_socket.connect("tcp://localhost:5555")

```
Once you have that set up, there are three commands that the service supports: display, add, and remove.
The add and remove command require card data, which will be added or removed from the wishlist.
The display command does not require any additional input since it's a read operation.

The following are examples showing how to send requests to the microservice using each of the commands.
```python
def add(self, card):
        wishlist_socket.send_json({
            'command': 'add',
            'name': card.name,
            'set_name': card.set_name,
            'year': card.year,
            'value': card.value
        })

def remove(self, card):
        wishlist_socket.send_json({
            'command': 'remove',
            'name': card.name,
            'set_name': card.set_name,
            'year': card.year,
            'value': card.value
        })

def display(self):
        wishlist_socket.send_json({
            'command': 'display',
        })
```
## RECEIVING DATA:
Receive a json object response from the microservice using the following code.
```python
response = wishlist_socket.recv_json()
message = response['message']
```
The display, add, and remove commands will send a json object in response to the request.
All three will contain a key 'message' which will have a string as a value.
The display command response will have an additional key 'cards' which will have a dictionary representing card objects as the value.
```python
cards = response['cards']
wishlist = []
for card in cards:
    wishlist.append(Card(card['name'], card['set_name'], card['year'], float(card['value'])))

```
The example code above builds a list of card objects received from the microservice response from the display command.

## UML DIAGRAM
![UML Diagram](https://github.com/emburyj/cardshop_microserviceA/blob/6b5061a1834703a97ad9601a2fe903ab75c187b0/UML%20Sequence%20Diagram.jpg)