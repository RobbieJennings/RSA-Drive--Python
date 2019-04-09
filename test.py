import client
import json
import os

num_groups = 5
user1 = "User1"
user2 = "User2"

# Make directories
if not os.path.exists('user1'):
    os.makedirs('user1')
if not os.path.exists('user2'):
    os.makedirs('user2')

# Sign up some users
print(json.loads(client.main("sign_up", [user1])))
print(json.loads(client.main("sign_up", [user2])))

# Sign in to user1
print(json.loads(client.main("sign_in", [user1])))
user = user1

# Create some groups
for i in range(num_groups):
    print(json.loads(client.main("create_group", [user, "group%d" % i])))

# Upload some test files
i = 0
groups = json.loads(client.main("list_groups", [user]))
for entry in groups:
    group = entry[0]
    print(json.loads(client.main("upload_file",
                                 [user, group, "upload/test%d.txt" % i])))
    i += 1

# Delete a group
group = json.loads(client.main("list_groups", [user]))[1][0]
print(json.loads(client.main("delete_group", [user, group])))

# Delete a file
group = json.loads(client.main("list_groups", [user]))[2][0]
file = json.loads(client.main("list_files", [user, group]))[0][0]
print(json.loads(client.main("delete_file", [user, group, file])))

# Download some test files
groups = json.loads(client.main("list_groups", [user]))
for entry in groups:
    group = entry[0]
    files = json.loads(client.main("list_files", [user, group]))
    for entry in files:
        file = entry[0]
        print(json.loads(client.main("download_file",
                                     [user, group, file, "user1"])))

# Add a user
group = json.loads(client.main("list_groups", [user]))[1][0]
print(json.loads(client.main("add_user", [user, group, user2])))
print(json.loads(client.main("upload_file", [user, group,
                                             "upload/test0.txt"])))
file = json.loads(client.main("list_files", [user, group]))[0][0]
# user = user2
print(json.loads(client.main("download_file", [user1, group, file, "user2"])))

# Remove a user
group = json.loads(client.main("list_groups", [user]))[1][0]
print(json.loads(client.main("remove_user", [user, group, user1])))
files = json.loads(client.main("list_files", [user, group]))
print("user1 files: ", files)
json.loads(client.main("sign_in", [user2]))
user = user2
files = json.loads(client.main("list_files", [user, group]))
print("user2 files: ", files)

# Show groups
json.loads(client.main("sign_in", [user1]))
user = user1
print("user1 groups", json.loads(client.main("list_groups", [user])))
json.loads(client.main("sign_in", [user2]))
user = user2
print("user1 groups", json.loads(client.main("list_groups", [user])))

# Show users in a group
json.loads(client.main("sign_in", [user1]))
user = user1
group = json.loads(client.main("list_groups", [user]))[2][0]
print(json.loads(client.main("add_user", [user, group, user2])))
user = user2
print(json.loads(client.main("list_users", [user, group])))
