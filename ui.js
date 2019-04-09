var express = require('express');
var bodyParser = require('body-parser')
var app = express();
var fs = require('fs');
const { spawn } = require("child_process");

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

var user;
var group;

app.get('/', function(req, res) {
  fs.readFile('html/home.html', function(err, data) {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.write(data);
    return res.end();
  })
})

app.get('/groups', function(req, res) {
  var pythonListGroups = spawn("python3", ["client.py", "list_groups", user]);
  pythonListGroups.stdout.on('data', (data) => {
    var groups = data;
    fs.readFile('html/groups.html', function(err, data) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      var page = data.toString().replace('{{data}}', groups);
      res.write(page);
      return res.end();
    })
  })
})

app.post('/signup', function(req, res) {
  user = req.body.user;
  var pythonSignUp = spawn("python3", ["client.py", "sign_up", user]);
  pythonSignUp.stdout.on('data', (data) => {
    var signedUp = JSON.parse(data);
    if (signedUp) {
      var pythonListGroups = spawn("python3", ["client.py", "list_groups", user]);
      pythonListGroups.stdout.on('data', (data) => {
        var groups = data;
        fs.readFile('html/groups.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', groups);
          res.write(page);
          return res.end();
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/signin', function(req, res) {
  user = req.body.user;
  var pythonSignIn = spawn("python3", ["client.py", "sign_in", user]);
  pythonSignIn.stdout.on('data', (data) => {
    var signedIn = JSON.parse(data);
    if (signedIn) {
      var pythonListGroups = spawn("python3", ["client.py", "list_groups", user]);
      pythonListGroups.stdout.on('data', (data) => {
        var groups = data;
        fs.readFile('html/groups.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', groups);
          res.write(page);
          return res.end();
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/createGroup', function(req, res) {
  group = req.body.group;
  var pythonCreate = spawn("python3", ["client.py", "create_group", user, group]);
  pythonCreate.stdout.on('data', (data) => {
    var created = JSON.parse(data);
    if (created) {
      var pythonListGroups = spawn("python3", ["client.py", "list_groups", user]);
      pythonListGroups.stdout.on('data', (data) => {
        var groups = data;
        fs.readFile('html/groups.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', groups);
          res.write(page);
          return res.end();
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/deleteGroup', function(req, res) {
  group = req.body.group;
  var pythonDelete = spawn("python3", ["client.py", "delete_group", user, group]);
  pythonDelete.stdout.on('data', (data) => {
    var deleted = JSON.parse(data);
    if (deleted) {
      var pythonListGroups = spawn("python3", ["client.py", "list_groups", user]);
      pythonListGroups.stdout.on('data', (data) => {
        var groups = data;
        fs.readFile('html/groups.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', groups);
          res.write(page);
          return res.end();
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/users', function(req, res) {
  group = req.body.group;
  var pythonUsers = spawn("python3", ["client.py", "list_users", user, group]);
  pythonUsers.stdout.on('data', (data) => {
    var users = data;
    fs.readFile('html/users.html', function(err, data) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      var page = data.toString().replace('{{data}}', users);
      res.write(page);
      return res.end()
    })
  })
})

app.post('/files', function(req, res) {
  group = req.body.group;
  var pythonFiles = spawn("python3", ["client.py", "list_files", user, group]);
  pythonFiles.stdout.on('data', (data) => {
    var files = data;
    fs.readFile('html/files.html', function(err, data) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      var page = data.toString().replace('{{data}}', files);
      res.write(page);
      return res.end()
    })
  })
})

app.post('/addUser', function(req, res) {
  var new_user = req.body.user;
  var pythonAdd = spawn("python3", ["client.py", "add_user", user, group, new_user]);
  pythonAdd.stdout.on('data', (data) => {
    var added = JSON.parse(data);
    if (added) {
      var pythonUsers = spawn("python3", ["client.py", "list_users", user, group]);
      pythonUsers.stdout.on('data', (data) => {
        var users = data;
        fs.readFile('html/users.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', users);
          res.write(page);
          return res.end()
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/removeUser', function(req, res) {
  var new_user = req.body.user;
  var pythonRemove = spawn("python3", ["client.py", "remove_user", user, group, new_user]);
  pythonRemove.stdout.on('data', (data) => {
    var removed = JSON.parse(data);
    if (removed) {
      var pythonUsers = spawn("python3", ["client.py", "list_users", user, group]);
      pythonUsers.stdout.on('data', (data) => {
        var users = data;
        fs.readFile('html/users.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', users);
          res.write(page);
          return res.end()
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/upload', function(req, res) {
  var file = req.body.file;
  var pythonUpload = spawn("python3", ["client.py", "upload_file", user, group, "upload/" + file]);
  pythonUpload.stdout.on('data', (data) => {
    var uploaded = JSON.parse(data);
    if (uploaded) {
      var pythonFiles = spawn("python3", ["client.py", "list_files", user, group]);
      pythonFiles.stdout.on('data', (data) => {
        var files = data;
        fs.readFile('html/files.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', files);
          res.write(page);
          return res.end()
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/download', function(req, res) {
  var file = req.body.file;
  var pythonDownload = spawn("python3", ["client.py", "download_file", user, group, file, "download"]);
  pythonDownload.stdout.on('data', (data) => {
    var downloaded = JSON.parse(data);
    if (downloaded) {
      var pythonFiles = spawn("python3", ["client.py", "list_files", user, group]);
      pythonFiles.stdout.on('data', (data) => {
        var files = data;
        fs.readFile('html/files.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', files);
          res.write(page);
          return res.end()
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})

app.post('/delete', function(req, res) {
  var file = req.body.file;
  var pythonDelete = spawn("python3", ["client.py", "delete_file", user, group, file]);
  pythonDelete.stdout.on('data', (data) => {
    var deleted = JSON.parse(data);
    if (deleted) {
      var pythonFiles = spawn("python3", ["client.py", "list_files", user, group]);
      pythonFiles.stdout.on('data', (data) => {
        var files = data;
        fs.readFile('html/files.html', function(err, data) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          var page = data.toString().replace('{{data}}', files);
          res.write(page);
          return res.end()
        })
      })
    }
    else {
      fs.readFile('html/home.html', function(err, data) {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.write(data);
        return res.end();
      })
    }
  })
})


var server = app.listen(8082, function() {
  var host = server.address().address
  var port = server.address().port
  console.log("Telecommunications project listening at http://%s:%s", host, port)
})
