# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(10000), nullable=False)

    def __repr__(self):
        return f'{self.username} {self.title} 추천 by {self.username}'

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    name = "hyouoo"
    motto = "live my own life"

    context = {
        "name": name,
        "motto": motto
    }
    return render_template("motto.html", data=context)

@app.route("/music/")
def music():
    song_list = Song.query.all()
    return render_template("music.html", data=song_list)

@app.route("/melon/")
def melon():
    url = "https://www.melon.com/chart/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    music_list = []
    for music in soup.select('table > tbody > tr'):
        rank = music.select_one('.rank').text
        title = music.select_one('.rank01 > span > a').text
        artist = music.select_one('.rank02 > a').text
        image = music.select_one('img')['src']

        context = {
            "rank": rank,
            "title": title,
            "artist": artist,
            "image": image
        }
        music_list.append(context)

    return render_template("melon.html", data=music_list)

@app.route("/music/create/")
def music_create():
    username_receive = request.args.get("username")
    title_receive = request.args.get("title")
    artist_receive = request.args.get("artist")
    image_receive = request.args.get("image_url")

    song = Song(username=username_receive, title=title_receive, artist=artist_receive, image_url=image_receive)
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('render_filtered_music', username=username_receive))

@app.route("/music_delete/<song_id>")
def music_delete(song_id):
    delete_song = Song.query.filter_by(title=song_id).first()
    db.session.delete(delete_song)
    db.session.commit()
    return redirect(url_for('music'))


@app.route("/music/<username>/")
def render_filtered_music(username):
    filter_list = Song.query.filter_by(username=username).all()
    return render_template("music.html", data=filter_list)

if __name__ == "__main__":
    app.run(debug=True, port=8080)