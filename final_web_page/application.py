from flask import Flask,render_template
from bokeh.client import pull_session
from bokeh.embed import server_session
from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

# import real_time_ver_4_history

def create_app():
    app = Flask(__name__)
    

    @app.route("/",methods=['GET'])
    def index():
        
        # with pull_session(url="{}:5006/real_time_ver_4_history".format(bokeh_app_ip)) as session:
        
        # update or customize that session
            # session.document.roots[0].children[1].title.text = "Special Sliders For A Specific User!"

        # generate a script to load the customized session
        
        # script = autoload_server(None, url="10.17.15.225:5006/real_time_ver_4_history".format(app_ip), session_id=session.id)

        # script = server_document("{}:5006/real_time_ver_4_history".format(bokeh_app_ip))
        

        return render_template('index.html',temp='abcde', template="Flask")
    
    # def bk_worker():
    #     server = Server({'/bkapp': real_time_ver_4_history}, io_loop=IOLoop(), allow_websocket_origin=["localhost:5006"])
    #     server.start()
    #     server.io_loop.start()
    # from threading import Thread
    # Thread(target=bk_worker).start()

    
    from demo.views import demo_page
    app.register_blueprint(demo_page,url_prefix="/demo")

    return app
    
