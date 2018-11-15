from flask import Blueprint,render_template,request,session,redirect,url_for,abort
from bokeh.client import pull_session
from bokeh.embed import server_session


demo_page = Blueprint('demo_page',__name__)


bokeh_app_ip='http://localhost:5100/real_time_ver_4_history'
# bokeh_app_ip='http://10.17.15.225:5100/real_time_ver_4_history'

@demo_page.route('/real_time',methods=['GET'])
def real_time():
    with pull_session(url=bokeh_app_ip) as session:
    # session = pull_session(url=bokeh_app_ip)
        script = server_session(session_id=session.id, url=bokeh_app_ip)
        return render_template('demo/real_time.html',script=script)
    
    # return render_template('demo/real_time.html')
    