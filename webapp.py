from flask import Flask, render_template, session, request, redirect
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.secret_key = "ABC"

# connected_users --> {username: ['room1 they're in', 'room2', 'room3']}
connected_users = {}

@app.route('/')
def index():
	user = session.get("user")   # "joel" or None
	# print "index: user=", user
	users_to_display = [u for u in connected_users if u != user]
	return render_template('index.html', 
		users = users_to_display,
		user=user)

@app.route('/login')
def login():
	return render_template("login.html")

@app.route('/logout')
def logout():
	# delete the current user from the connected_users dictionary
	global connected_users
	user = request.args.get("user")
	del connected_users[user]
	print "connected_users in logout: ", connected_users

	# delete the current user from the session
	del session["user"]
	print "session in logout ", session

	# reload the login page
	print "This is the list of connected users after %s has logged out" % user
	print connected_users
	return render_template("login.html")

@app.route("/set_session")
def set_session():
	global connected_users

	# get the current logged in user, and set that to the session
	user = request.args.get("user")
	print "set_session: user=", user
	session["user"] = user
	print session

	# add that user to the list of connected users
	connected_users.setdefault(session["user"], [])
	print "connected users in set_session", connected_users
	return redirect("/")

@app.route("/refresh_users")
def refresh_connected_users():
	"""Whenever a new user logs into the system, this is called to refresh all users' connected list"""
	global connected_users
	user = request.args.get("user")
	print "user in refresh_users", user
	return render_template("logged_in_users.html", user=user, users=[x for x in connected_users if x != user])



# socket functions

def send_message(message, room):
	emit('message to display', {'message': message, 'user': session['user']}, room=room)

def send_command(command, body, room):
	emit('interpret command', {'command': command, 'body': body}, room=room)

@socketio.on('refresh connected users', namespace='/chat')
def refresh_connecteduser_lists():
	"""tells every connected user to update their connected user list"""
	global connected_users
	print "These are the users being told to update: ", connected_users
	for key in connected_users:
		send_command('UL', "None", key)



# socket events

@socketio.on('my event', namespace='/chat')
def test_message(message):
	"""Called when a message is submitted, sends message back to the client to be displayed"""
	print message['data']
	send_message(message['data'], message['room'])

@socketio.on('receive command', namespace='/chat')
def receive_command(command):
	"""Sends any commands (join, update list, etc.) to a user's room to be interpreted"""
	print command
	send_command(command['command'], command['body'], command['room'])

@socketio.on('join room', namespace='/chat')
def on_join(data):
	global connected_users
	user = data['username']
	room = data['room']
	join_room(room)
	print "%s has joined room: %s" % (user, room)

	if room not in connected_users.get(user):
		connected_users.setdefault(user, []).append(room)
	print "connected users in join room", connected_users

	send_message("Success! Connected to %s" % room, room)
	refresh_connecteduser_lists()

@socketio.on('connect', namespace='/chat')
def test_connect():
	# check for awayness eventually
	print('Connected')
	emit('connected', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
	print('%s Client disconnected') % session.get("user")

if __name__ == '__main__':
    socketio.run(app)


# 