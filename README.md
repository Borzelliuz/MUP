# MUD - Secure Chat Application

MUD is a Python-based secure chat application that combines TCP client/server communication, UDP user discovery, and encrypted messaging. The project was developed to practice computer networking concepts, socket programming, secure key exchange, and terminal-based user interfaces.

## Features

- TCP-based client/server messaging
- UDP broadcast system for discovering active users on the network
- Secure chat using Diffie-Hellman key exchange
- Triple DES encryption for encrypted communication
- Chat history support
- Username storage using username.txt
- Terminal interface using the Rich library
- Active user listing
- Basic local network communication

## Technologies Used

- Python
- Socket Programming
- TCP
- UDP Broadcast
- Diffie-Hellman Key Exchange
- Triple DES Encryption
- Rich Console UI
- File Handling

## Project Structure

MUD/
- MUD.py
- username.txt
- README.md
- requirements.txt

## Requirements

This project requires Python 3.

Required Python libraries:

- rich
- pyDes

Install dependencies:

pip install rich pyDes

Or with requirements.txt:

pip install -r requirements.txt

Example requirements.txt:

rich  
pyDes

## How to Run

Clone the repository:

git clone https://github.com/Borzelliuz/MUP.git

Go into the project directory:

cd your-repository-name

Install dependencies:

pip install rich pyDes

Run the application:

python MUD.py

## How It Works

The application uses both TCP and UDP networking methods.

UDP is used to broadcast and discover active users on the local network. This allows users to see who is currently available.

TCP is used for direct message communication between users. For secure communication, the application uses Diffie-Hellman key exchange to create a shared secret key between two users. This shared secret is then used with Triple DES encryption to encrypt and decrypt messages.

The Rich library is used to make the terminal interface cleaner and easier to use.

## Security Concept

This project includes a basic secure messaging mechanism:

1. Two users establish communication.
2. Diffie-Hellman key exchange is used to generate a shared secret.
3. The shared secret is converted into a usable encryption key.
4. Messages are encrypted using Triple DES.
5. The receiver decrypts the message using the same shared key.

This project is mainly educational and should not be used as a production-level secure communication tool.

## What I Learned

- How TCP and UDP communication work in Python
- How to create a basic client/server architecture
- How UDP broadcast can be used for local network discovery
- How Diffie-Hellman key exchange works
- How encrypted messaging can be implemented
- How to design a terminal-based user interface
- How to manage chat history and user data locally

## Future Improvements

- Add a graphical user interface
- Improve encryption method with modern cryptographic libraries
- Add user authentication
- Add better error handling
- Add support for multiple chat rooms
- Improve message history management
- Add file transfer support

## Author

Alperen Çelik  
Computer Engineering Student
