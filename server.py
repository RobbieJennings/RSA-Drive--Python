from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pymongo
import socket
import json

HOST = '127.0.0.1'  # localhost
PORT = 8080  # Proxy port
buffer_size = 1024  # Max Socket Buffer Size
valid_request = "telecommunications"


class Server:
    drive = None
    db = None

    def listen(self):
        # Initialize Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(1)

        print("Server started successfully")

        # Start listening for requests
        while True:
            try:
                conn, addr = sock.accept()  # Accept Conn from Client Browser
                data = conn.recv(buffer_size)  # Receive Client Data
                data = data.decode().split("\n\n\n\n")  # Decode received data
                request = data[0]  # Get request type

                if(request == valid_request):
                    # Get function call
                    function = data[1]
                    parameters = data[2].split("\n\n")
                    result = self.call_function(function, parameters)

                    # Send response back to client
                    reply = json.dumps(result).encode()
                    conn.send(reply)
                    conn.close()

            # User shutdown server
            except KeyboardInterrupt:
                sock.close()
                print("\nServer shut down successfully")
                return

    def call_function(self, function, parameters):
        # Display function call on terminal
        print("%s: %s" % (function, parameters))

        # List functions in dictionary
        functions = {"sign_up": self.sign_up,
                     "get_user_key": self.get_user_key,
                     "create_group": self.create_group,
                     "delete_group": self.delete_group,
                     "get_group_key": self.get_group_key,
                     "add_user": self.add_user,
                     "remove_user": self.remove_user,
                     "upload_file": self.upload_file,
                     "download_file": self.download_file,
                     "delete_file": self.delete_file,
                     "list_groups": self.list_groups,
                     "list_users": self.list_users,
                     "list_files": self.list_files}

        result = functions[function](*parameters)
        return result

    def init_drive(self):
        # Authenticate Drive client
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile("mycreds.txt")
        self.drive = GoogleDrive(gauth)

        return True

    def init_db(self):
        # Initialize MongoDB database
        client = pymongo.MongoClient("mongodb://localhost:27017")
        database = client["drive_database"]
        database["groups"]
        database["users"]
        self.db = database

        return True

    def sign_up(self, user, key):
        # Check user not already taken
        if self.db["users"].find_one({"id": user}) is not None:
            return False

        # Add user to database
        self.db["users"].insert_one({"id": user, "key": key})
        return True

    def get_user_key(self, user, other_user):
        # Check user is in database
        if self.db["users"].find_one({"id": user}) is None:
            return None

        # Check other user is in database
        if self.db["users"].find_one({"id": other_user}) is None:
            return None

        # Return user's public key
        return self.db["users"].find_one({"id": other_user}).get("key")

    def create_group(self, user, key, name):
        # Check user is in database
        if self.db["users"].find_one({"id": user}) is None:
            return False

        # Create a new folder in Drive
        folder = self.drive.CreateFile(
            {'title': name,
             'mimeType': "application/vnd.google-apps.folder"})
        folder.Upload()

        # Add group to database
        self.db["groups"].insert_one(
            {"id": folder['id'], "users": {user: key}})

        return True

    def delete_group(self, user, group):
        # Check group is in database
        if self.db["groups"].find_one({"id": group}) is None:
            return False

        # Check if user is in group
        if user not in self.db["groups"].find_one({"id": group}).get("users"):
            return False

        # Remove group from database
        self.db["groups"].delete_one({"id": group})

        # Delete folder from Drive
        folder = self.drive.CreateFile({"id": group})
        folder.Delete()

        return True

    def get_group_key(self, user, group):
        # Check group is in database
        if self.db["groups"].find_one({"id": group}) is None:
            return None

        # Check if user is in group
        if user not in self.db["groups"].find_one({"id": group}).get("users"):
            return None

        # Return users copy of symmetric key
        return self.db["groups"].find_one({"id": group}).get("users")[user]

    def add_user(self, user, group, new_user, new_key):
        # Check group is in database
        if self.db["groups"].find_one({"id": group}) is None:
            return False

        # Check if user is in group
        if user not in self.db["groups"].find_one({"id": group}).get("users"):
            return False

        # Add new user to group
        self.db["groups"].update(
            {'id': group}, {'$set': {'users.' + new_user: new_key}})

        return True

    def remove_user(self, user, group, removed_user):
        # Check group is in database
        if self.db["groups"].find_one({"id": group}) is None:
            return False

        # Check if user is in group
        if user not in self.db["groups"].find_one({"id": group}).get("users"):
            return False

        # Remove other user from group
        self.db["groups"].update({'id': group}, {'$unset':
                                                 {'users.' + removed_user: 1}})

        return True

    def upload_file(self, user, group, name, data):
        # Check group is in database
        if self.db["groups"].find_one({"id": group}) is None:
            return False

        # Check if user is in group
        if user not in self.db["groups"].find_one({"id": group}).get("users"):
            return False

        # Upload file to Drive
        file = self.drive.CreateFile(
            {"parents": [{"kind": "drive#fileLink", "id": group}],
             'title': name})
        file.SetContentString(data)
        file.Upload()

        return True

    def download_file(self, user, group, file):
        # Check group is in database
        if self.db["groups"].find_one({"id": group}) is None:
            return False

        # Check if user and file are in group
        if not any(file == entry[0] for entry in self.list_files(user, group)):
            return None

        # Download the file from Drive
        data = self.drive.CreateFile({"id": file})
        data = data.GetContentString()
        return data

    def delete_file(self, user, group, file):
        # Check group is in database
        if self.db["groups"].find_one({"id": group}) is None:
            return False

        # Check if user and file are in group
        if not any(file == entry[0] for entry in self.list_files(user, group)):
            return False

        # Remove from group's files and delete from Drive
        file = self.drive.CreateFile({"id": file})
        file.Delete()

        return True

    def list_groups(self, user):
        # Check user is in database
        if self.db["users"].find_one({"id": user}) is None:
            return False

        # Check if user is in each group
        groups = []
        for group in self.db["groups"].find({}):
            if user in group.get("users"):
                id = group.get("id")
                folder = self.drive.CreateFile({"id": id})
                name = folder['title']
                groups.append((id, name))

        return groups

    def list_users(self, user, group):
        # Check user is in database
        if self.db["users"].find_one({"id": user}) is None:
            return False

        # Check if user is in group
        if user not in self.db["groups"].find_one({"id": group}).get("users"):
            return None

        return list(self.db["groups"].find_one(
            {"id": group}).get("users").keys())

    def list_files(self, user, group):
        # Check user is in database
        if self.db["users"].find_one({"id": user}) is None:
            return False

        # Check if user is in group
        if user not in self.db["groups"].find_one({"id": group}).get("users"):
            return None

        # Get Drive folder
        folder = self.drive.ListFile(
            {'q': "'%s' in parents and trashed=false" % group}).GetList()

        # Return list of files
        files = []
        for file in folder:
            files.append((file["id"], file["title"]))
        return files


def main():
    server = Server()
    server.init_drive()
    server.init_db()
    server.listen()


if __name__ == "__main__":
    main()
