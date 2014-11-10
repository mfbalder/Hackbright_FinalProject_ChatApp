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

@app.route("/logout")
def logout():
	# delete the current user from the connected_users dictionary
	global connected_users
	del connected_users[session["user"]]
	print "connected_users: ", connected_users

	# delete the current user from the session
	del session["user"]
	print "session ", session

	# reload the login page
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
	return render_template("logged_in_users.html", user=user, users=[x for x in connected_users if x != user])


@socketio.on('my event', namespace='/chat')
def test_message(message):
	"""Called when a message is submitted, sends message back to the client to be displayed"""
	print message['data']
	emit('message to display', {'message': message['data'], 'user': session['user']}, room=message['room'])


@socketio.on('receive command', namespace='/chat')
def receive_command(command):
	"""Sends any commands (join, update list, etc.) to a user's room to be interpreted"""
	print command
	emit('interpret command', {'command': command['command'], 'body': command['body']}, room=command['room'])

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
	emit('message to display', {'message': "Success! Connected to %s" % room, 'user': session['user']}, room=room)
	for key in connected_users:
		print key
		emit('interpret command', {'command': 'UL', 'body': "None"}, room=key)

@socketio.on('connect', namespace='/chat')
def test_connect():
	# check for awayness
	print('Connected')
	emit('connected', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
	# global connected_users
	# room = session['user']
	# connected_users[session['user']].remove(room)
	# print connected_users
	print('%s Client disconnected') % session["user"]

if __name__ == '__main__':
    socketio.run(app)


# 