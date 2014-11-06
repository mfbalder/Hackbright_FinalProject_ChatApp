from flask import Flask, render_template, session, request, redirect
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.secret_key = "ABC"

room = None
user = None
connected_users = {}

@app.route('/')
def index():
	return render_template('index.html', users = connected_users)

@app.route('/login')
def login():
	return render_template("login.html")

@app.route("/set_session")
def set_session():
	user = request.args.get("user")
	session["user"] = user
	print session
	connected_users.setdefault(session["user"], {})
	print connected_users
	return redirect("/")

@socketio.on('my event', namespace='/chat')
def test_message(message):
	global user
	print message['data']
	emit('my response', {'data': message['data'], 'user': session['user']}, room=room)

@socketio.on('join', namespace='/chat')
def on_join(data):
	global room, user
	print data
	user = data['username']
	room = data['room']
	join_room(room)
	print "Room joined %s" % room
	emit('my response', {'data': "Success!", 'user': session['user']}, room=room)

@socketio.on('connect', namespace='/chat')
def test_connect():
	global connected_users
	print('Connected')
	emit('connected', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
	global connected_users
	del connected_users[session['user']]
	print(connected_users)
	print('%s Client disconnected') % session['user']

if __name__ == '__main__':
    socketio.run(app)


# 