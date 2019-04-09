import client
import json

user1 = "User1"
user2 = "User2"
group = "group"
file = "lemon.txt"

print(json.loads(client.main("sign_up", [user1])))
print(json.loads(client.main("sign_up", [user2])))
print(json.loads(client.main("sign_in", [user1])))

print(json.loads(client.main("create_group", [user1, group])))
group = json.loads(client.main("list_groups", [user1]))[0][0]

print(json.loads(client.main("upload_file",
                             [user1, group, "upload/test0.txt"])))
file = json.loads(client.main("list_files", [user1, group]))[0][0]
print(json.loads(client.main("add_user", [user1, group, user2])))
print(json.loads(client.main("download_file",
                             [user1, group, file, "download"])))
print(json.loads(client.main("download_file",
                             [user2, group, file, "download"])))
