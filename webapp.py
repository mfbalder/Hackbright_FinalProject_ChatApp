from flask import Flask, render_template, session, request, redirect
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.secret_key = "ABC"

room = None
# connected_users --> {username: ['room1 they're in', 'room2']}
connected_users = {}

@app.route('/')
def index():
	user = session.get("user")   # "joel" or None
	print "index: user=", user
	return render_template('index.html', 
		users = connected_users,
		user=user)

@app.route('/login')
def login():
	return render_template("login.html")

@app.route("/set_session")
def set_session():
	global conn
	# get the user's login name, and set that to the session
	user = request.args.get("user")
	print "set_session: user=", user
	session["user"] = user
	print session

	# add that user to the list of connected users
	connected_users.setdefault(session["user"], [])
	print "connected users in set_session", connected_users
	return redirect("/")


@socketio.on('my event', namespace='/chat')
def test_message(message):
	global room
	print message['data']
	emit('my response', {'data': message['data'], 'user': session['user']}, room="bkinkeadmfbalder")


@socketio.on('receive command', namespace='/chat')
def receive_command(command):
	print command
	emit('interpret command', {'command': command['command'], 'body': command['body']}, room=command['room'])

# @socketio.on('get command', namespace='/chat')
# def get_command(data):
# 	# global room
# 	other_user = data['other_user']
# 	command = data['command']
# 	self = session['user']
# 	connected_room = other_user + self
# 	print "********** self: %s, other_user: %s, command: %s, connected room: %s" % (self, other_user, command, connected_room)
# 	if command == "join":
# 		emit('send command', {'room': connected_room}, room=self)
# 		emit('send command', {'room': connected_room}, room=other_user)

@socketio.on('join room', namespace='/chat')
def on_join(data):
	# global connected_users
	user = data['username']
	room = data['room']
	join_room(room)
	print "%s has joined room: %s" % (user, room)
	connected_users.setdefault(user, []).append(room)
	print "connected users in join room", connected_users
	# print "I am %s" % session["user"]
	emit('my response', {'data': "Success! Connected to %s" % room, 'user': session['user']}, room="bkinkeadmfbalder")

# @socketio.on('link users', namespace='/chat')
# def link_users(data):
# 	connecting_user = data["connecting_user"] # ben
# 	receiving_user = data["receiving_user"] # micki
# 	new_room = data["new_room"] # mfbalderbkinkead
# 	emit('make connection', {'connecting_user': connecting_user, 'receiving_user': receiving_user, 'new_room': new_room}, room=receiving_user)

@socketio.on('connect', namespace='/chat')
def test_connect():
	# global connected_users
	print('Connected')
	emit('connected', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
	print('%s Client disconnected') % session["user"]

if __name__ == '__main__':
    socketio.run(app)


# 