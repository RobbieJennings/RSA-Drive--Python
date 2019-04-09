from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto import Random
import socket
import json
import os
import sys

HOST = '127.0.0.1'  # localhost
PORT = 8081  # Client port
SERVER_PORT = 8080  # Server port
buffer_size = 1024  # Max Socket Buffer Size
valid_request = "telecommunications"


class Client():
    def call_function(self, function, parameters):
        # List functions in dictionary
        functions = {"sign_up": self.sign_up,
                     "sign_in": self.sign_in,
                     "create_group": self.create_group,
                     "delete_group": self.delete_group,
                     "add_user": self.add_user,
                     "remove_user": self.remove_user,
                     "upload_file": self.upload_file,
                     "download_file": self.download_file,
                     "delete_file": self.delete_file,
                     "list_groups": self.list_groups,
                     "list_users": self.list_users,
                     "list_files": self.list_files}

        return functions[function](*parameters)

    def make_request(self, function, parameters):
        # Load parameters into string
        paramater_string = ""
        for paramater in range(len(parameters)):
            if(paramater == len(parameters) - 1):
                paramater_string += parameters[paramater]
            else:
                paramater_string += "%s\n\n" % parameters[paramater]

        # Encode request
        data = "%s\n\n\n\n%s\n\n\n\n%s" % (
            valid_request, function, paramater_string)
        data = data.encode()

        # Initialize socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))

        # Send request to server
        sock.connect((HOST, SERVER_PORT))
        sock.send(data)

        # Receive reply from server
        reply = sock.recv(buffer_size)
        sock.close()

        # Decode and return result
        return json.loads(reply.decode())

    def sign_up(self, user):
        # Check user does not exist in database:
        if(self.get_user_key(user, user) is not None):
            return False

        # Make a keys folder if none already exists
        if not os.path.exists('keys'):
            os.makedirs('keys')

        # Generate keys
        random_generator = Random.new().read
        private_key = RSA.generate(1024, random_generator)
        public_key = private_key.publickey()

        # Serialize and save private key
        with open("keys/" + user + ".pem", 'wb') as f:
            f.write(private_key.exportKey('PEM'))
            f.close()

        # Serialize and upload public key
        pem = public_key.exportKey('PEM').decode()
        return self.make_request("sign_up", [user, pem])

    def sign_in(self, user):
        # Check user exists in database
        result = self.make_request("get_user_key", [user, user])
        if result is None:
            return False

        # Check private key exists
        if not os.path.exists("keys/%s.pem" % (user)):
            return False

        return True

    def get_keys(self, user):
        # Load public and private key
        with open("keys/" + user + ".pem", "rb") as f:
            private_key = RSA.importKey(f.read())
            f.close()
        public_key = private_key.publickey()

        return private_key, public_key

    def get_user_key(self, user, other_user):
        # Load users public key
        key = self.make_request("get_user_key", [user, other_user])
        if key is None:
            return None

        key = RSA.importKey(key)
        return key

    def create_group(self, user, name):
        # Get public key
        _, public_key = self.get_keys(user)
        if public_key is None:
            return False

        # Generate and encrypt symmetric key
        key = Fernet.generate_key()
        key = public_key.encrypt(key, 32)[0]
        key = key.decode('latin-1')

        # Create group
        return self.make_request("create_group", [user, key, name])

    def delete_group(self, user, group):
        return self.make_request("delete_group", [user, group])

    def get_group_key(self, user, group):
        # Get private key
        private_key, _ = self.get_keys(user)
        if private_key is None:
            return False

        # Get symmetric key and decrypt
        key = self.make_request("get_group_key", [user, group])
        key = key.encode('latin-1')
        return private_key.decrypt(key)

    def add_user(self, user, group, new_user):
        # Check new user exists
        if self.get_user_key(user, new_user) is None:
            return False

        # Get user key
        user_key = self.get_user_key(user, new_user)
        if user_key is None:
            return False

        # Get symmetric key
        symmetric_key = self.get_group_key(user, group)
        if symmetric_key is None:
            return False

        # Encrypt symmetric key with user key
        symmetric_key = user_key.encrypt(symmetric_key, 32)[0]
        symmetric_key = symmetric_key.decode('latin-1')

        # Add user
        return self.make_request("add_user", [user, group, new_user,
                                              symmetric_key])

    def remove_user(self, user, group, removed_user):
        return self.make_request("remove_user", [user, group, removed_user])

    def upload_file(self, user, group, path):
        # Get symmetric key from server
        key = self.get_group_key(user, group)
        if key is None:
            return False

        # Read data from file
        with open(path, 'rb') as f:
            data = f.read()
            name = path.split("/").pop()
        f.close()

        # Encrypt data
        cipher_suite = Fernet(key)
        data = cipher_suite.encrypt(data).decode()

        # Upload encrypted file to server
        return self.make_request("upload_file", [user, group, name, data])

    def download_file(self, user, group, file, destination):
        # Get symmetric key from server
        key = self.get_group_key(user, group)
        if key is None:
            return False

        # download file from server
        data = self.make_request("download_file", [user, group, file]).encode()
        if data is None:
            return False

        # Decrypt file
        cipher_suite = Fernet(key)
        data = cipher_suite.decrypt(data)

        # Write back decrypted file
        name = [entry[1] for entry in self.list_files(
            user, group) if entry[0] == file][0]
        with open("%s/%s" % (destination, name), 'wb') as f:
            f.write(data)
        f.close()

        return True

    def delete_file(self, user, group, file):
        return self.make_request("delete_file", [user, group, file])

    def list_groups(self, user):
        return self.make_request("list_groups", [user])

    def list_users(self, user, group):
        return self.make_request("list_users", [user, group])

    def list_files(self, user, group):
        return self.make_request("list_files", [user, group])


def main(function, parameters):
    client = Client()
    return json.dumps(client.call_function(function, parameters))


if __name__ == "__main__":
    function = sys.argv[1]
    parameters = sys.argv[2:]
    print(main(function, parameters))
