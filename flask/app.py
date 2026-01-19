# Import Externe
import datetime
import requests
import os

from flask import Flask, render_template, session, request, flash, redirect, send_file, jsonify
from flask_session import Session
from io import BytesIO
from werkzeug.utils import secure_filename

# Import Local
from Data.database_handler import DatabaseHandler
from config import Config
from utils.hashlib_blake2b import hashlib_blake2b
from utils.ipv4_address import ipv4_address

###########################################
#_____DO_NOT_FORGET_TO_REMOVE_APP_RUN_____#
###########################################

database_handler=DatabaseHandler()
config = Config()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)
Session(app)

@app.route('/')
def index():
    if "id" not in session:
        return render_template('index.html')
    
    database_handler.insert_metadata(session["id"], datetime.datetime.now(), ipv4_address())
    return redirect("/home/") 

@app.route('/login', methods=('GET', 'POST'))
@app.route('/login/', methods=('GET', 'POST'))
def login():
    if "id" in session:
            id = session["id"]
            return redirect("/home/")
    
    if request.method != 'POST':
        return render_template('login.html')
    
    username = str(request.form['username'])
    password = hashlib_blake2b(str(request.form['password']))

    if not username or username == None:
        flash('Username is required.')
        return render_template('login.html')
    
    if not password or password == None:
        flash('Password is required.')
        return render_template('login.html')
    
    if not database_handler.verif_user_exists(username) :
        flash('Username is not correct.')
        return render_template('login.html')

    if password != database_handler.get_password(database_handler.get_id_from_username(username)) :
        flash('Password is not correct.')
        return render_template('login.html')
     
    session["id"]=database_handler.get_id_from_username(username)
    database_handler.insert_metadata(session["id"], datetime.datetime.now(), ipv4_address())
    return redirect("/home/")         

@app.route('/register', methods=('GET', 'POST'))
@app.route('/register/', methods=('GET', 'POST'))
def register():
    if "id" in session:
        return redirect("/home/")
    
    if request.method != 'POST':
        return render_template('register.html')
    
    username        = str(request.form['username'])
    password        = hashlib_blake2b(str(request.form['password']))
    verif_password  = hashlib_blake2b(str(request.form['verif_password']))
    name            = str(request.form['name'])

    if database_handler.verif_user_exists(username):
        flash("Username is already used.")
        return render_template('register.html')

    if database_handler.verif_name_exists(name):
        flash("Name is already used.")
        return render_template('register.html')
    
    if password != verif_password:
        flash("Passwords must be identical.")
        return render_template('register.html')
    
    database_handler.create_account(username, password, name)
    session["id"] = database_handler.get_id_from_username(username)
    database_handler.insert_metadata(session["id"], datetime.datetime.now(), ipv4_address())
    return redirect("/home/")

@app.route('/home')
@app.route('/home/')
def home():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    return render_template('home.html', id=id, name=database_handler.get_name_from_id(id))
    
@app.route("/logout")
@app.route("/logout/")
def logout():
    session.clear()
    return redirect("/")

##################################################
#____________Personal_Information________________#
##################################################

@app.route('/personal_information', methods=('GET', 'POST'))
@app.route('/personal_information/', methods=('GET', 'POST'))
def personal_information():
    if "id" not in session:
        return redirect("/")
        
    id=session["id"]
    return render_template('personal_information.html',
                           id=id,
                           name=database_handler.get_name_from_id(id),
                           pay=database_handler.get_pay(id))   

@app.route('/personal_information/change_password', methods=('GET', 'POST'))
@app.route('/personal_information/change_password/', methods=('GET', 'POST'))
def change_password():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if request.method != 'POST':
        return render_template('change_password.html', id=id)
    
    actual_password    = hashlib_blake2b(request.form['actual_password'])
    new_password       = hashlib_blake2b(request.form['new_password'])
    verif_new_password = hashlib_blake2b(request.form['verif_new_password'])

    if actual_password  != database_handler.get_password(id):
        flash('Password is not correct.')
        return render_template('change_password.html', id=id)
    
    if new_password != verif_new_password:
        flash("Passwords must be identical.")
        return render_template('change_password.html', id=id)
    
    database_handler.update_password(id, new_password)
    flash('Your password has been updated')
    return redirect("/personal_information/")

@app.route('/personal_information/change_name', methods=('GET', 'POST'))
@app.route('/personal_information/change_name/', methods=('GET', 'POST'))
def change_name():
    if "id" not in session:
        return redirect("/")
    
    id=session["id"]
    if request.method != 'POST':
        return render_template('change_name.html', id=id, name=database_handler.get_name_from_id(id))
    
    new_name = str(request.form['new_name'])
    if not new_name:
        flash('Name is required !')
        return redirect("/personal_information/change_name/")
    
    if database_handler.verif_name_exists(new_name):
        flash('This name is already taken !')
        return redirect("/personal_information/change_name/")
    
    database_handler.update_name(id, new_name)
    database_handler.update_name_in_post(id, new_name)
    flash('Your name has been updated')
    return redirect("/personal_information/")

@app.route('/personal_information/upload_profile_picture', methods=('GET', 'POST'))
@app.route('/personal_information/upload_profile_picture/', methods=('GET', 'POST'))
def upload_profile_picture():
    if "id" not in session:
        return redirect("/")
    
    id=session["id"]
    if request.method != 'POST':
        return redirect("/personal_information/")
    
    #################################################

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS_PROFILE_PICTURE"]
    
    def get_file_extension(filename):
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else None
    
    #################################################

    if 'profile_picture' not in request.files:
        return redirect("/personal_information/")

    file = request.files['profile_picture']

    if file.filename == '':
        return redirect("/personal_information/")

    if not (file and allowed_file(file.filename)):
        return redirect("/personal_information/")
    
    filename = secure_filename(file.filename)
    extension = get_file_extension(filename)
    new_filename = f"user_{id}.{extension}"
    filepath = os.path.join(app.config['UPLOAD_PROFILE_PICTURE_FOLDER'], new_filename)
    

    old_path = database_handler.get_profile_picture_path_from_id(id)
    if old_path is not None and os.path.exists(old_path):
        os.remove(old_path)
    
    file.save(filepath)
    database_handler.update_profile_picture_path_from_id(id, filepath)
    return redirect("/personal_information/")

@app.route("/profile_picture/<int:user_id>")
def profile_picture(user_id):
    if "id" not in session:
        return redirect("/")
    
    path = database_handler.get_profile_picture_path_from_id(user_id)

    if not path or not os.path.isfile(path):
        path = config.PATH_DEFAULT_PROFILE_PICTURE
    
    print(path)
    return send_file(path)

@app.route('/personal_information/delete_account', methods=('GET', 'POST'))
@app.route('/personal_information/delete_account/', methods=('GET', 'POST'))
def delete_account():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if request.method != 'POST':
        return redirect("/personal_information/")
    
    database_handler.delete_all_post_from_id(id)
    database_handler.delete_account(id)
    session.clear()
    flash('Your account was successfully deleted!')
    return redirect("/")

@app.route('/personal_information/export_data', methods=('GET', 'POST'))
@app.route('/personal_information/export_data/', methods=('GET', 'POST'))
def export_data():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    content = "=== PERSONALE DATA EXPORT ===\n"
    content += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"ID  : {id}\n"
    content += f"Nom : {database_handler.get_name_from_id(id)}\n"
    content += f"Pay : {database_handler.get_pay(id)} TC\n\n"

    metadata = database_handler.get_metadata(id)
    content += "=== MÉTADONNÉES ===\n\n"
    for meta in metadata:
        content += f"Date: {meta['date_connected']} - IP: {meta['ipv4']}\n"
    
    file = BytesIO(content.encode('utf-8'))
    return send_file(file, mimetype='text/plain', as_attachment=True, 
                     download_name=f'export_data_{id}.txt')

##################################################
#__________________TitouBank_____________________#
##################################################

@app.route('/titoubank', methods=('GET', 'POST'))
@app.route('/titoubank/', methods=('GET', 'POST'))
def titoubank():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    return render_template('titoubank.html', id=id, pay=database_handler.get_pay(id), all_transfer_history=database_handler.get_all_bank_transfer(id))
        
@app.route("/titoubank/withdrawl", methods=('GET', 'POST'))
@app.route("/titoubank/withdrawl/", methods=('GET', 'POST'))
def withdrawl():
    if "id" not in session:
        return redirect("/")

    id = session["id"]
    if request.method != 'POST':
        return render_template('withdrawl.html', id=id)
    
    withdrawl = int(request.form['withdrawl'])
    if withdrawl <= 0:
        flash("Zero or negative withdrawal is impossible.")
        return redirect("/titoubank/withdrawl/")

    pay = database_handler.get_pay(id)
    if pay - withdrawl < 0:
        flash("Your Balance is not high enough.")
        return redirect("/titoubank/withdrawl/")
    
    new_pay_senders = pay - withdrawl
    database_handler.update_pay(id, new_pay_senders)
    flash('"{}" TC have been withdrawn from your account.'.format(withdrawl))
    return redirect("/titoubank/")     
    
@app.route('/titoubank/transfer', methods=('GET', 'POST'))
@app.route('/titoubank/transfer/', methods=('GET', 'POST'))
def transfer():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if request.method != 'POST':
        return render_template('transfer.html', id=id, all_transfer_history=database_handler.get_all_bank_transfer(id))
    
    transfer_value = int(request.form['transfer_value'])
    id_receiver = int(request.form['id_receiver'])

    if transfer_value <= 0:
        flash("Zero or negative transfer is impossible.")
        return redirect("/titoubank/transfer/")
    
    if not database_handler.verif_id_exists(id_receiver):
        flash("This ID does not exist.")
        return redirect("/titoubank/transfer/")
    
    pay = database_handler.get_pay(id)
    new_pay_senders = pay - transfer_value

    if pay - transfer_value < 0:
        flash("Your Balance is not high enough.")
        return redirect("/titoubank/transfer/")
    
    new_pay_receiver = database_handler.get_pay(id_receiver)+transfer_value
    database_handler.update_pay(id, new_pay_senders)
    database_handler.update_pay(id_receiver, new_pay_receiver)
    database_handler.insert_bank_transfer(id, id_receiver, transfer_value, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    receiver_name = database_handler.get_name_from_id(id_receiver)
    flash('"{}" TC have been sent to {}'.format(transfer_value, receiver_name))
    return redirect("/titoubank/")

##################################################
#__________________Chatroom______________________#
##################################################

@app.route('/chatroom', methods=('GET', 'POST'))
@app.route('/chatroom/', methods=('GET', 'POST'))
def chatroom():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    return render_template('chatroom.html',id=id, posts=database_handler.get_posts())      

@app.route('/chatroom/create_post', methods=('GET', 'POST'))
@app.route('/chatroom/create_post/', methods=('GET', 'POST'))
def create_post():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if request.method != 'POST':
        return render_template('create_post.html', id=id)
    
    title = str(request.form['title'])
    content = str(request.form['content'])
    if not title or not content:
        flash('Error: Title and Content is required')
        return render_template('create_post.html', id=id)
    
    name=database_handler.get_name_from_id(id)
    database_handler.create_post(id, name, title, content)
    return redirect("/chatroom/")      

@app.route('/chatroom/edit_post/<int:id_post>', methods=('GET', 'POST'))
@app.route('/chatroom/edit_post/<int:id_post>/', methods=('GET', 'POST'))
def edit_post(id_post):
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if id != database_handler.get_id_from_id_post(id_post):
        flash("You cannot edit this post.")
        return redirect("/chatroom/")
    
    if request.method != 'POST':
        return render_template('edit_post.html',id=id, post=database_handler.get_post_from_id(id_post))
    
    title = str(request.form['title'])
    content = str(request.form['content'])
    if not title or not content:
        flash('Error: Title and Content is required')
        return redirect("/create_post/")

    name = database_handler.get_name_from_id(id)
    database_handler.update_post(id_post, name, title, content)
    return redirect("/chatroom/")    

@app.route('/chatroom/delete/<int:id_post>', methods=('POST',))
@app.route('/chatroom/delete/<int:id_post>/', methods=('POST',))
def delete_post(id_post):
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if request.method != 'POST':
        return redirect("/edit_post/")
    
    post = database_handler.get_post_from_id(id_post)
    database_handler.delete_post(id_post)
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect("/chatroom/")    

##################################################
#_______________Social_Network___________________#
##################################################

@app.route('/social_network', methods=('GET', 'POST'))
@app.route('/social_network/', methods=('GET', 'POST'))
def social_network_home():
    if "id" not in session:
        return redirect("/")
    return render_template('social_network_home.html', id=session["id"])

@app.route('/social_network/friends', methods=('GET', 'POST'))
@app.route('/social_network/friends/', methods=('GET', 'POST'))
def social_network_friends():
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if request.method != 'POST':

        id_all_followers = database_handler.get_all_followers_from_id(id)
        all_followers = []
        for id_follower in id_all_followers:
            all_followers.append((id_follower["id_follower"], database_handler.get_name_from_id(id_follower["id_follower"])))

        id_all_followeds = database_handler.get_all_followeds_from_id(id)
        all_followeds = []
        for id_followed in id_all_followeds:
            all_followeds.append((id_followed["id_followed"], database_handler.get_name_from_id(id_followed["id_followed"])))

        return render_template("social_network_friends.html", id=id, all_followers=all_followers, all_followeds=all_followeds)
    
    friend_name = str(request.form["friend"])
    if friend_name is None or friend_name == "":
        flash("Name is required.")
        return redirect("/social_network/friends/")
    if not database_handler.verif_name_exists(friend_name):
        flash("This name doesn't exist.")
        return redirect("/social_network/friends/")

    id_followed = database_handler.get_id_from_name(friend_name)

    if id_followed == id:
        flash("You cannot follow yourself")
        return redirect("/social_network/friends/")

    if id_followed in database_handler.get_all_followeds_from_id(id):
        flash("You are already following this person")
        return redirect("/social_network/friends/")

    database_handler.create_link_social_network(id, id_followed, datetime.date.today())
    return redirect("/social_network/friends/")

##################################################
#______________________API_______________________#
##################################################

@app.route('/api')
@app.route('/api/')
def api():
    if "id" not in session:
        return render_template('/')
    return render_template('api.html', id=session["id"])

@app.route('/api/search_movie', methods=('GET', 'POST'))
@app.route('/api/search_movie/', methods=('GET', 'POST'))
def search_movie(movie_title=""):
    if "id" not in session:
        return redirect("/")
    
    id = session["id"]
    if request.method != 'POST':
        return render_template("search_movie.html", id=id, all_movie_search=database_handler.get_movie_search(id))
    
    movie = str(request.form['movie'])
    if not movie or movie == None:
        flash('Movie is required.')
        return redirect("/api/search_movie/")

    omdb_api_key = app.config['OMDB_API_KEY']
    requestURL = "http://www.omdbapi.com/?apikey=" + omdb_api_key + "&t=" + movie
    r = requests.get(requestURL)
    infosMovie = r.json()
    if infosMovie["Response"] == "False":
        infos_movie_error = infosMovie["Error"]
        flash('"{}"'.format(infos_movie_error))
        return redirect("/api/search_movie/")
    
    movie_title = infosMovie["Title"]
    database_handler.insert_movie_search(id, movie_title, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return render_template('infosmovie.html',   id=id,
                                                movie_title     = movie_title,
                                                movie_year      = infosMovie["Year"],
                                                movie_released  = infosMovie["Released"],
                                                movie_runtime   = infosMovie["Runtime"],
                                                movie_genre     = infosMovie["Genre"],
                                                movie_director  = infosMovie["Director"],
                                                movie_plot      = infosMovie["Plot"],
                                                movie_poster    = infosMovie["Poster"],
                                                movie_rating    = infosMovie["imdbRating"],
                                                )

##################################################
#__________________Others________________________#
##################################################

@app.route('/conditions_uses')
@app.route('/conditions_uses/')
def conditions_uses():
    return render_template('conditions_uses.html')

@app.route('/thank_you', methods=('GET', 'POST'))
@app.route('/thank_you/', methods=('GET', 'POST'))
def thank_you():
    return render_template('thank_you.html')

if __name__ == "__main__":
    app.run(debug=True)