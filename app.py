from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from flask_session import Session
import os
import datetime

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

socketio = SocketIO(app, manage_session=False)

Session(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if (request.method=='POST'):
        username = request.form['username']
        room = request.form['room']

        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session=session, username=username, room=room)

    elif(session.get('username') is not None):
        return render_template('chat.html', session=session)
    else:
        return redirect(url_for('index'))


@socketio.on('join', namespace='/chat')
def join(data):
    if data['username'] is not None:
        username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': "has entered the chat. Welcome !", 'user': "&#160&#160 "+username}, room=room)

@socketio.on('text', namespace='/chat')
def text(message):
    room = message['room']
    emit('message', {'msg':message['msg'], 'user':message['username']}, room=room)

@socketio.on('left', namespace='/chat')
def left(data):
    room = data['room']
    username= data['username']
    leave_room(room)
    session.clear()
    emit('status', {'msg':' has left the chat.', 'user': "&#160&#160"+username}, room=room)
    



if __name__ == '__main__':
    socketio.run(app)