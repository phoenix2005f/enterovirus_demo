from flask import Flask,render_template
from bokeh.client import pull_session
from bokeh.embed import server_session

app = Flask(__name__)

bokeh_app_ip = 'http://140.115.80.90:5006/real_time_ver_4_history'

@app.route("/",methods=['GET'])
def index():
	with pull_session(url=bokeh_app_ip) as session:
		script = server_session(session_id=session.id, url=bokeh_app_ip)
		return render_template('index.html',script=script)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5566)
