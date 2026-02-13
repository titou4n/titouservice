# Import Externe
import requests
import os
import random

from flask import Flask, request, render_template, flash, redirect, send_file, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect
from io import BytesIO
from werkzeug.utils import secure_filename
from datetime import datetime

# Import Local
from Data.init_db import DatabaseManager
from Data.database_handler import DatabaseHandler
from config import Config
from utils.utils import Utils
from utils.session_manager import SessionManager
from utils.email_manager import EmailManager
from utils.hash_manager import HashManager
from utils.bank_manager import BankManager
from utils.twofa_manager import TwofaManager
from models.user import User

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

config = Config()
database_manager = DatabaseManager()
database_handler = DatabaseHandler()
session_manager = SessionManager(app_instance=app)
email_manager = EmailManager()
hash_manager = HashManager()
bank_manager = BankManager()
twofa_manager = TwofaManager()
user = None
utils = Utils()


@app.context_processor
def inject_format_datetime():
    return dict(format_datetime=utils.format_datetime)

@login_manager.user_loader
def load_user(user_id):
    return User(int(user_id))

@app.route('/')
def index():
    if session_manager.get_current_user_id() is None:
        return render_template('index.html')
    
    session_manager.insert_metadata()
    return redirect("/home/") 

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')
    
    username = str(request.form['username'])
    password = hash_manager.generate_password_hash(str(request.form['password']))

    if not username or username == None:
        flash('Username is required.')
        return redirect(url_for('login'))
    
    if not password or password == None:
        flash('Password is required.')
        return redirect(url_for('login'))

    if database_handler.get_id_from_username(username) is None:
        flash('Username is not correct.')
        return redirect(url_for('login'))
    
    user_id = database_handler.get_id_from_username(username)
    if password != database_handler.get_password(user_id):
        flash('Password is not correct.')
        return redirect(url_for('login'))

    session_manager.send_session(user_id=user_id)

    if database_handler.get_user_preferences_2fa(user_id=user_id):
        return redirect('/two_factor_authentication/')
    
    user = User(user_id)
    # Flask_login
    login_user(user)

    session_manager.insert_metadata()
    return redirect("/home/")         

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method != 'POST':
        return render_template('register.html')
    
    username        = str(request.form['username'])
    password        = hash_manager.generate_password_hash(str(request.form['password']))
    verif_password  = hash_manager.generate_password_hash(str(request.form['verif_password']))
    name            = str(request.form['name'])

    if database_handler.verif_username_exists(username):
        flash("Username is already used.")
        return redirect(url_for('register'))

    if database_handler.verif_name_exists(name):
        flash("Name is already used.")
        return redirect(url_for('register'))
    
    if password != verif_password:
        flash("Passwords must be identical.")
        return redirect(url_for('register'))
    
    role_id = database_handler.get_role_id(role_name="user")
    database_handler.create_account(username, password, name, role_id)
    user_id = database_handler.get_id_from_username(username)

    session_manager.send_session(user_id=user_id)
    database_handler.insert_user_preferences(user_id=user_id)

    user = User(user_id)
    # Flask_login
    login_user(user)

    session_manager.insert_metadata()
    return redirect("/home/")

@app.route('/forgot_password', methods=['GET', 'POST'])
@app.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    if session_manager.get_current_user_id() is not None:
        user_id = session_manager.get_current_user_id()
        session_manager.insert_metadata()
        return redirect("/home/")
    
    if request.method != 'POST':
        return render_template('forgot_password.html')
    
    username = str(request.form['username'])
    if not username or username == None:
        flash('Username is required.')
        return render_template('login.html')
    
    user_id = database_handler.get_id_from_username(username)
    if user_id is None:
        flash("Username doesn't exist.")
        return render_template('login.html')

    user_email = database_handler.get_email_from_id(user_id)
    if user_email is None:
        flash("No email has been added.")
        return render_template('login.html')
    
    email_verified = database_handler.get_email_verified_from_id(user_id)
    if email_verified is None or not email_verified:
        flash("No email has been verified.")
        return render_template('login.html')

    new_password = utils.generate_password(size=20)
    database_handler.update_password(user_id, new_password=hash_manager.generate_password_hash(new_password))
    email_manager.send_new_password_code_with_html(user_id=user_id, new_password=new_password)
    flash(f"An email containing a new password has been sent to {email_manager.get_hide_email(user_id=user_id)}.")
    return redirect(url_for('login'))         

@app.route('/two_factor_authentication', methods=['GET', 'POST'])
@app.route('/two_factor_authentication/', methods=['GET', 'POST'])
@login_required
def two_factor_authentication():
    
    user_id = session_manager.get_current_user_id()
    database_handler.delete_old_code_hash()

    if request.method == 'GET':
        if not twofa_manager.verif_code(user_id=user_id, code=code):
            twofa_manager.delete_old_code_hash(user_id=user_id)
            return redirect("/two_factor_authentication/")

        twofa_manager.send_code(user_id=user_id)
        flash(f"An email containing a two-factor authentication code has been sent to the following address: {email_manager.get_hide_email(user_id=user_id)} ")
        return render_template('two_factor_authentication.html')
    
    # request.method == 'POST' :

    code = str(request.form['code'])
    if not twofa_manager.verif_code(user_id=user_id, code=code):
        flash("Your two-factor authentication failed. Please try again.")
        return redirect("/two_factor_authentication/")

    flash("Your two-factor authentication sucess.")
    return redirect("/home/")

@app.route('/visitor', methods=['GET', 'POST'])
@app.route('/visitor/', methods=['GET', 'POST'])
@login_required
def continue_as_a_visitor():
    if session_manager.get_current_user_id() is not None:
        return redirect("/home/")
    
    username_visitor = config.USERNAME_VISITOR
    password_visitor = hash_manager.generate_password_hash(config.PASSWORD_VISITOR)

    if not username_visitor or username_visitor == None:
        flash('Username is required.')
        return render_template('login.html')
    
    if not password_visitor or password_visitor == None:
        flash('Password is required.')
        return render_template('login.html')
    
    if not database_handler.verif_username_exists(username_visitor) :
        flash('Username is not correct.')
        return render_template('login.html')

    if password_visitor != database_handler.get_password(database_handler.get_id_from_username(username_visitor)) :
        flash('Password is not correct.')
        return render_template('login.html')
     
    user_id = database_handler.get_id_from_username(username_visitor)
    session_manager.send_session(user_id=user_id)
    return redirect("/home/")

@app.route('/home')
@app.route('/home/')
@login_required
def home():
    user_id = session_manager.get_current_user_id()
    return render_template('home.html', id=user_id, name=database_handler.get_name_from_id(user_id))

@app.route('/logout')
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    session_manager.logout()
    return redirect("/")

##################################################
#__________________SETTINGS______________________#
##################################################

@app.route('/settings', methods=['GET', 'POST'])
@app.route('/settings/', methods=['GET', 'POST'])
@login_required
def settings_home():  
    user_id = session_manager.get_current_user_id()
    return render_template('settings_home.html',
                           id=user_id,
                           name=database_handler.get_name_from_id(user_id))

###################################
#_____________ACCOUNT_____________#
###################################

@app.route('/settings/account', methods=['GET', 'POST'])
@app.route('/settings/account/', methods=['GET', 'POST'])
@login_required
def account_home():
    user_id = session_manager.get_current_user_id()
    user = User(user_id)

    email = database_handler.get_email_from_id(user_id)
    user_has_email = not(email is None)
    email_verified = int(database_handler.get_email_verified_from_id(user_id))
    if email_verified == 0:
        email_verified = False
    else:
        email_verified = True

    return render_template('account_home.html',
                           id=user_id,
                           username=database_handler.get_username_from_user_id(user_id=user_id),
                           name=database_handler.get_name_from_id(user_id),
                           pay=database_handler.get_pay(user_id),
                           user_has_email = user_has_email,
                           email=email,
                           email_verified=email_verified,
                           role_name = user.role_name
                           )

@app.route('/settings/account/change_email', methods=['GET', 'POST'])
@app.route('/settings/account/change_email/', methods=['GET', 'POST'])
@login_required
def account_change_email():
    user_id=session_manager.get_current_user_id()
    if request.method != 'POST':
        email=database_handler.get_email_from_id(user_id)
        user_has_email = not(email is None)
        return render_template('account_change_email.html',
                               id=user_id,
                               user_has_email = user_has_email,
                               email=email)
    
    email = str(request.form['email'])
    if not email:
        flash('Email is required !')
        return redirect("/settings/account/change_email/")
    
    database_handler.update_email_from_id(user_id, email)
    flash('Your email has been updated')
    return redirect(url_for("account_home"))

@app.route('/settings/account/change_username', methods=['GET', 'POST'])
@app.route('/settings/account/change_username/', methods=['GET', 'POST'])
@login_required
def account_change_username():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return render_template('account_change_username.html', id=user_id, username=database_handler.get_username_from_user_id(user_id))
    
    new_username = str(request.form['new_username'])
    if not new_username:
        flash('Username is required !')
        return redirect(url_for("account_change_username"))
    
    if database_handler.verif_username_exists(new_username):
        flash('This username is already taken !')
        return redirect(url_for("account_change_username"))
    
    database_handler.update_username(user_id, new_username)
    flash('Your username has been updated')
    return redirect(url_for("account_home"))

@app.route('/settings/account/change_password', methods=['GET', 'POST'])
@app.route('/settings/account/change_password/', methods=['GET', 'POST'])
@login_required
def account_change_password():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return render_template('account_change_password.html', id=user_id)
    
    actual_password    = str(hash_manager.generate_password_hash(request.form['actual_password']))
    new_password       = str(hash_manager.generate_password_hash(request.form['new_password']))
    verif_new_password = str(hash_manager.generate_password_hash(request.form['verif_new_password']))

    if actual_password  != database_handler.get_password(user_id):
        flash('Password is not correct.')
        return redirect("/settings/account/change_password/")
    
    if new_password != verif_new_password:
        flash("Passwords must be identical.")
        return redirect("/settings/account/change_password/")
    
    database_handler.update_password(user_id, new_password)
    flash('Your password has been updated')
    return redirect(url_for("account_home"))

@app.route('/settings/account/change_name', methods=['GET', 'POST'])
@app.route('/settings/account/change_name/', methods=['GET', 'POST'])
@login_required
def account_change_name():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return render_template('account_change_name.html', id=user_id, name=database_handler.get_name_from_id(user_id))
    
    new_name = str(request.form['new_name'])
    if not new_name:
        flash('Name is required !')
        return redirect("/settings/account/change_name/")
    
    if database_handler.verif_name_exists(new_name):
        flash('This name is already taken !')
        return redirect("/settings/account/change_name/")
    
    database_handler.update_name(user_id, new_name)
    flash('Your name has been updated')
    return redirect(url_for("account_home"))

@app.route('/settings/account/upload_profile_picture', methods=['GET', 'POST'])
@app.route('/settings/account/upload_profile_picture/', methods=['GET', 'POST'])
@login_required
def upload_profile_picture():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return redirect(url_for("account_home"))
    
    #################################################

    @login_required
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS_PROFILE_PICTURE"]
    
    @login_required
    def get_file_extension(filename):
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else None
    
    #################################################

    if 'profile_picture' not in request.files:
        return redirect(url_for("account_home"))

    file = request.files['profile_picture']

    if file.filename == '':
        return redirect(url_for("account_home"))

    if not (file and allowed_file(file.filename)):
        return redirect(url_for("account_home"))
    
    filename = secure_filename(file.filename)
    extension = get_file_extension(filename)
    new_filename = f"user_{user_id}.{extension}"
    filepath = os.path.join(app.config['UPLOAD_PROFILE_PICTURE_FOLDER'], new_filename)
    

    old_path = database_handler.get_profile_picture_path_from_id(user_id)
    if old_path is not None and os.path.exists(old_path):
        os.remove(old_path)
    
    file.save(filepath)
    database_handler.update_profile_picture_path_from_id(user_id, filepath)
    return redirect(url_for("account_home"))

@app.route("/settings/profile_picture/<int:user_id>")
@login_required
def profile_picture(user_id):
    
    path = database_handler.get_profile_picture_path_from_id(user_id)

    if not path or not os.path.isfile(path):
        path = config.PATH_DEFAULT_PROFILE_PICTURE

    return send_file(path)

@app.route('/settings/account/delete_account', methods=['GET', 'POST'])
@app.route('/settings/account/delete_account/', methods=['GET', 'POST'])
@login_required
def delete_account():
    
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return redirect(url_for("account_home"))
    
    database_handler.delete_all_post_from_id(user_id)
    database_handler.delete_account(user_id)
    session_manager.logout()
    flash('Your account was successfully deleted!')
    return redirect("/")

###################################
#_____________SECURTY_____________#
###################################

@app.route('/settings/security', methods=['GET', 'POST'])
@app.route('/settings/security/', methods=['GET', 'POST'])
@login_required
def security_home():  
    user_id = session_manager.get_current_user_id()
    email = database_handler.get_email_from_id(user_id)
    sessions = database_handler.get_all_sessions_from_user_id(user_id=user_id)

    return render_template('security_home.html',
                           id=user_id,
                           username=database_handler.get_username_from_user_id(user_id=user_id),
                           name=database_handler.get_name_from_id(user_id),
                           pay=database_handler.get_pay(user_id),
                           user_has_email = not(email is None),
                           email=email,
                           email_verified=database_handler.get_email_verified_from_id(user_id),
                           twofa_enabled=database_handler.get_user_preferences_2fa(user_id=user_id),
                           session_id_hash=session_manager.get_current_session_id_hash(),
                           session_location=session_manager.get_location(),
                           ip_address=session_manager.get_ip_session(),
                           sessions=sessions)

@app.route('/settings/switch_2fa', methods=['GET', 'POST'])
@app.route('/settings/switch_2fa/', methods=['GET', 'POST'])
@login_required
def settings_switch_2fa():
    if request.method != 'POST':
        return redirect("/settings/security/")
    
    user_id = session_manager.get_current_user_id()

    if database_handler.get_email_from_id(user_id) is None:
        flash("Please add an email address first.")
        return redirect("/settings/account/change_email/")
    
    if not database_handler.get_email_verified_from_id(user_id):
        flash(f"Please verify your email address first - Click on 'Verify-it' link.")
        return redirect("/settings/security/")
    
    database_handler.switch_user_preferences_2fa(user_id=user_id)
    flash('Your preferences has been updated')
    return redirect("/settings/security/")

@app.route("/settings/logout_all", methods=['GET', 'POST'])
@app.route("/settings/logout_all/", methods=['GET', 'POST'])
@login_required
def settings_logout_all():  
    user_id = session_manager.get_current_user_id()
    session_manager.logout_user_from_all_devices(user_id=user_id)
    return redirect("/")

@app.route("/settings/logout_session/<string:session_id_hash>", methods=['POST'])
@login_required
def settings_logout_session(session_id_hash:str):
    session_manager.logout_session(session_id_hash=session_id_hash)
    return redirect(url_for('security_home'))

@app.route("/settings/delete_session/<string:session_id_hash>", methods=['POST'])
@login_required
def settings_delete_session(session_id_hash:str):
    session_manager.delete_session(session_id_hash=session_id_hash)
    return redirect(url_for('security_home'))

###################################
#_________NOTIFICATIONS___________#
###################################

@app.route('/settings/notifications', methods=['GET', 'POST'])
@app.route('/settings/notifications/', methods=['GET', 'POST'])
@login_required
def notifications_home():  
    user_id = session_manager.get_current_user_id()
    return render_template('notifications_home.html',
                           id=user_id)

#TODO
@app.route('/settings/notify_password_change', methods=['GET', 'POST'])
@app.route('/settings/notify_password_change/', methods=['GET', 'POST'])
@login_required
def settings_notify_password_change():
    flash("Not Implemented")
    if request.method != 'POST':
        return redirect("/settings/notifications/")
    
    return redirect("/settings/notifications/")

#TODO
@app.route('/settings/notify_twofa_change', methods=['GET', 'POST'])
@app.route('/settings/notify_twofa_change/', methods=['GET', 'POST'])
@login_required
def settings_notify_twofa_change():
    flash("Not Implemented")
    if request.method != 'POST':
        return redirect("/settings/notifications/")
    
    return redirect("/settings/notifications/")

###################################
#____________PRIVACY______________#
###################################

@app.route('/settings/privacy', methods=['GET', 'POST'])
@app.route('/settings/privacy/', methods=['GET', 'POST'])
@login_required
def privacy_home():
    user_id = session_manager.get_current_user_id()
    return render_template('privacy_home.html',
                           id=user_id)


@app.route('/settings/privacy/export_data', methods=['GET', 'POST'])
@app.route('/settings/privacy/export_data/', methods=['GET', 'POST'])
@login_required
def export_data():    
    user_id = session_manager.get_current_user_id()
    content = "=== PERSONALE DATA EXPORT ===\n"
    content += f"Date       : {utils.format_datetime(utils.get_datetime_isoformat())}\n"
    content += f"ID         : {user_id}\n"
    content += f"Username   : {database_handler.get_username_from_user_id(user_id)}\n"
    content += f"Name       : {database_handler.get_name_from_id(user_id)}\n"
    content += f"Pay        : {database_handler.get_pay(user_id)} TC\n\n"

    metadata = database_handler.get_metadata(user_id)
    content += "=== MÉTADONNÉES ===\n\n"
    for meta in metadata:
        content += f"{utils.format_datetime(meta['date_connected'])} - IP: {meta['ipv4']}\n"
    
    file = BytesIO(content.encode('utf-8'))
    return send_file(file, mimetype='text/plain', as_attachment=True, 
                     download_name=f'export_data_{user_id}.txt')


###################################
#___________APPEARANCE____________#
###################################

@app.route('/settings/appearance', methods=['GET', 'POST'])
@app.route('/settings/appearance/', methods=['GET', 'POST'])
@login_required
def appearance_home():      
    user_id = session_manager.get_current_user_id()
    return render_template('appearance_home.html',
                           id=user_id)


###################################
#_________ABOUT/SUPPORT___________#
###################################

@app.route('/settings/about_support', methods=['GET', 'POST'])
@app.route('/settings/about_support/', methods=['GET', 'POST'])
@login_required
def about_support_home():     
    user_id = session_manager.get_current_user_id()
    return render_template('about_support_home.html',
                           id=user_id)


##################################################
#__________________TitouBank_____________________#
##################################################

@app.route('/titoubank', methods=['GET', 'POST'])
@app.route('/titoubank/', methods=['GET', 'POST'])
@login_required
def titoubank():
    user_id = session_manager.get_current_user_id()
    return render_template('titoubank_home.html',
                           id=user_id,
                           pay=round(database_handler.get_pay(user_id),2),
                           all_transfer_history=database_handler.get_all_bank_transfer(user_id))
        
@app.route("/titoubank/withdrawl", methods=['GET', 'POST'])
@app.route("/titoubank/withdrawl/", methods=['GET', 'POST'])
@login_required
def withdrawl():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return render_template('titoubank_withdrawl.html', id=user_id)
    
    withdrawl = int(request.form['withdrawl'])
    if withdrawl <= 0:
        flash("Zero or negative withdrawal is impossible.")
        return redirect("/titoubank/withdrawl/")

    pay = database_handler.get_pay(user_id)
    if pay - withdrawl < 0:
        flash("Your Balance is not high enough.")
        return redirect("/titoubank/withdrawl/")
    
    new_pay_senders = pay - withdrawl
    database_handler.update_pay(user_id, new_pay_senders)
    flash('"{}" TC have been withdrawn from your account.'.format(withdrawl))
    return redirect("/titoubank/")     
    
@app.route('/titoubank/transfer', methods=['GET', 'POST'])
@app.route('/titoubank/transfer/', methods=['GET', 'POST'])
@login_required
def transfer():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return render_template('titoubank_transfer.html', id=user_id, all_transfer_history=database_handler.get_all_bank_transfer(user_id))
    
    transfer_value = int(request.form['transfer_value'])
    id_receiver = int(request.form['id_receiver'])

    if transfer_value <= 0:
        flash("Zero or negative transfer is impossible.")
        return redirect("/titoubank/transfer/")
    
    if not database_handler.verif_id_exists(id_receiver):
        flash("This ID does not exist.")
        return redirect("/titoubank/transfer/")
    
    pay = database_handler.get_pay(user_id)
    new_pay_senders = pay - transfer_value

    if pay - transfer_value < 0:
        flash("Your Balance is not high enough.")
        return redirect("/titoubank/transfer/")
    
    new_pay_receiver = database_handler.get_pay(id_receiver)+transfer_value
    database_handler.update_pay(user_id, new_pay_senders)
    database_handler.update_pay(id_receiver, new_pay_receiver)
    database_handler.insert_bank_transfer(user_id, id_receiver, transfer_value, utils.get_datetime_isoformat())
    receiver_name = database_handler.get_name_from_id(id_receiver)
    flash('"{}" TC have been sent to {}'.format(transfer_value, receiver_name))
    return redirect("/titoubank/")

@app.route('/titoubank/stock_market', methods=['GET', 'POST'])
@app.route('/titoubank/stock_market/', methods=['GET', 'POST'])
@login_required
def titoubank_stock_market():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        twelvedata_api_key = config.TWELVEDATA_API_KEY
        symbol = "BTC/USD"
        interval = "1day"
        output_size = 10
        #requestURL = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={twelvedata_api_key}"
        requestURL = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={output_size}&apikey={twelvedata_api_key}"
        r = requests.get(requestURL)
        result = r.json()

        if "status" in result and result["status"] == "error":  # run out api credits : result["code"] == 429
            #flash(result["message"])
            flash(f"You have run out of API credits for the current minute.")
            return redirect("/titoubank/")

        #result = {'meta': {'symbol': 'BTC/USD', 'interval': '1day', 'currency_base': 'Bitcoin', 'currency_quote': 'US Dollar', 'exchange': 'Coinbase Pro', 'type': 'Digital Currency'}, 'values': [{'datetime': '2026-01-20', 'open': '92559.65', 'high': '92807.99', 'low': '90558.99', 'close': '91255.19'}, {'datetime': '2026-01-19', 'open': '93630', 'high': '93630', 'low': '91935.3', 'close': '92559.66'}, {'datetime': '2026-01-18', 'open': '95109.99', 'high': '95485', 'low': '93559.78', 'close': '93633.53'}, {'datetime': '2026-01-17', 'open': '95503.99', 'high': '95600', 'low': '94980.12', 'close': '95109.99'}, {'datetime': '2026-01-16', 'open': '95578.2', 'high': '95830.49', 'low': '94229.04', 'close': '95504'}, {'datetime': '2026-01-15', 'open': '96954.02', 'high': '97176.42', 'low': '95066.19', 'close': '95587.65'}, {'datetime': '2026-01-14', 'open': '95385.59', 'high': '97963.62', 'low': '94518.63', 'close': '96955.16'}, {'datetime': '2026-01-13', 'open': '91188.08', 'high': '96250', 'low': '90925.17', 'close': '95384.23'}, {'datetime': '2026-01-12', 'open': '90878.51', 'high': '92406.3', 'low': '90003.46', 'close': '91188.09'}, {'datetime': '2026-01-11', 'open': '90387.36', 'high': '91173.12', 'low': '90109', 'close': '90872.01'}], 'status': 'ok'}
        
        pay_of_account = database_handler.get_pay(id=user_id)
        sum_stock_number = bank_manager.get_sum_transfers_from_id_symbol(user_id=user_id, symbol=symbol)

        ### GET PRICE ###
        twelvedata_api_key = config.TWELVEDATA_API_KEY
        requestURL = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={twelvedata_api_key}"
        r = requests.get(requestURL)
        current_price = r.json()

        coefficient = config.STOCK_MARKET_COEFFICIENT
        all_stock_market_transfers = database_handler.get_all_stock_market_transfers_from_id_symbol(id=user_id, symbol=symbol)

        return render_template("titoubank_stock_market.html",
                               id=user_id,
                               prices=result["values"],
                               pay_of_account=round(pay_of_account, 2),
                               sum_stock_number=sum_stock_number,
                               current_price=round(float(current_price["price"]), 2),
                               coefficient=coefficient,
                               all_stock_market_transfers=all_stock_market_transfers)
    return redirect("/titoubank/stock_market/")

@app.route('/titoubank/stock_market/sell', methods=['GET', 'POST'])
@app.route('/titoubank/stock_market/sell/', methods=['GET', 'POST'])
@login_required
def titoubank_stock_market_sell():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return redirect("/titoubank/stock_market/")
    
    stock_number = float(request.form['stock_number'])
    if stock_number <= 0:
        flash("Zero or negative stock is impossible.")
        return redirect("/titoubank/stock_market/")
    
    symbol = "BTC/USD"

    sum_stock_number = bank_manager.get_sum_transfers_from_id_symbol(user_id=user_id, symbol=symbol)
    if stock_number >= sum_stock_number:
        flash("You don't have enough stock.")
        return redirect("/titoubank/stock_market/")
    
    ### GET PRICE ###
    twelvedata_api_key = config.TWELVEDATA_API_KEY
    requestURL = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={twelvedata_api_key}"
    r = requests.get(requestURL)
    result = r.json()

    if "status" in result and result["status"] == "error":  # run out api credits : result["code"] == 429
        #flash(result["message"])
        flash(f"You have run out of API credits for the current minute.")
        return redirect("/titoubank/")

    current_price = float(result["price"])
    
    pay = database_handler.get_pay(user_id)
    #new_pay = pay + (stock_number*current_price)/int(config.STOCK_MARKET_COEFFICIENT)
    new_pay = pay + (stock_number*current_price)
    
    database_handler.update_pay(id, new_pay)
    database_handler.insert_stock_market_transfers(id=user_id,
                                                   type="sell",
                                                   symbol=symbol,
                                                   stock_number=stock_number,
                                                   stock_price=current_price,
                                                   transfer_datetime=utils.get_datetime_isoformat())
    flash('You have sell {} {} which is equivalent to {} TC'.format(stock_number, symbol, stock_number*current_price))
    return redirect("/titoubank/stock_market/")
    
@app.route('/titoubank/stock_market/sell_all', methods=['GET', 'POST'])
@app.route('/titoubank/stock_market/sell_all/', methods=['GET', 'POST'])
@login_required
def titoubank_stock_market_sell_all(): 
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return redirect("/titoubank/stock_market/")
    
    symbol = "BTC/USD"
    stock_number = bank_manager.get_sum_transfers_from_id_symbol(user_id=user_id, symbol=symbol)
    
    ### GET PRICE ###
    twelvedata_api_key = config.TWELVEDATA_API_KEY
    requestURL = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={twelvedata_api_key}"
    r = requests.get(requestURL)
    result = r.json()

    if "status" in result and result["status"] == "error":  # run out api credits : result["code"] == 429
        #flash(result["message"])
        flash(f"You have run out of API credits for the current minute.")
        return redirect("/titoubank/")

    current_price = float(result["price"])
    
    pay = database_handler.get_pay(user_id)
    #new_pay = pay + (stock_number*current_price)/int(config.STOCK_MARKET_COEFFICIENT)
    new_pay = pay + (stock_number*current_price)
    
    database_handler.update_pay(user_id, new_pay)
    database_handler.insert_stock_market_transfers(id=user_id,
                                                   type="sell",
                                                   symbol=symbol,
                                                   stock_number=stock_number,
                                                   stock_price=current_price,
                                                   transfer_datetime=utils.get_datetime_isoformat())
    flash('You have sell {} {} which is equivalent to {} TC'.format(stock_number, symbol, stock_number*current_price))
    return redirect("/titoubank/stock_market/")

@app.route('/titoubank/stock_market/buy', methods=['GET', 'POST'])
@app.route('/titoubank/stock_market/buy/', methods=['GET', 'POST'])
@login_required
def titoubank_stock_market_buy():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return redirect("/titoubank/stock_market/")
    
    stock_number = float(request.form['stock_number'])
    if stock_number <= 0:
        flash("Zero or negative stock is impossible.")
        return redirect("/titoubank/stock_market/")
    
    ### GET PRICE ###
    twelvedata_api_key = config.TWELVEDATA_API_KEY
    symbol = "BTC/USD"
    requestURL = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={twelvedata_api_key}"
    r = requests.get(requestURL)
    result = r.json()

    if "status" in result and result["status"] == "error":  # run out api credits : result["code"] == 429
        #flash(result["message"])
        flash(f"You have run out of API credits for the current minute.")
        return redirect("/titoubank/")

    current_price = float(result["price"])
    
    pay = database_handler.get_pay(user_id)
    #new_pay = pay - (stock_number*current_price)/int(config.STOCK_MARKET_COEFFICIENT)
    new_pay = pay - (stock_number*current_price)
    if new_pay < 0:
        flash("Your Balance is not high enough.")
        return redirect("/titoubank/stock_market/")

    database_handler.update_pay(user_id, new_pay)
    database_handler.insert_stock_market_transfers(id=user_id,
                                                   type="buy",
                                                   symbol=symbol,
                                                   stock_number=stock_number,
                                                   stock_price=current_price,
                                                   transfer_datetime=utils.get_datetime_isoformat())
    flash('You have buy {} {} which is equivalent to {} TC'.format(stock_number, symbol, stock_number*current_price))
    return redirect("/titoubank/stock_market/")

##################################################
#__________________Chatroom______________________#
##################################################

@app.route('/chatroom', methods=['GET'])
@app.route('/chatroom/', methods=['GET'])
@login_required
def chatroom():
    user_id = session_manager.get_current_user_id()
    posts = database_handler.get_posts()

    all_users_id = []
    for post in posts:
        all_users_id.append(post["user_id"])

    names = {}
    for post_user_id in all_users_id:
        names[post_user_id] = database_handler.get_name_from_id(post_user_id)

    return render_template('chatroom_home.html',id=user_id, posts=posts, names=names)      

@app.route('/chatroom/create_post', methods=['GET', 'POST'])
@app.route('/chatroom/create_post/', methods=['GET', 'POST'])
@login_required
def create_post():
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        return render_template('chatroom_create_post.html', id=user_id)
    
    title = str(request.form['title'])
    content = str(request.form['content'])

    if not title or not content:
        flash('Error: Title and Content is required')
        return redirect("/chatroom/create_post/")

    database_handler.create_post(user_id, title, content)
    return redirect("/chatroom/")

@app.route('/chatroom/edit_post/<int:id_post>', methods=['GET', 'POST'])
@app.route('/chatroom/edit_post/<int:id_post>/', methods=['GET', 'POST'])
@login_required
def edit_post(id_post):
    user_id = session_manager.get_current_user_id()
    if user_id != database_handler.get_id_from_id_post(id_post):
        flash("You cannot edit this post.")
        return redirect("/chatroom/")
    
    if request.method != 'POST':
        return render_template('chatroom_edit_post.html',id=user_id, post=database_handler.get_post_from_id(id_post))
    
    title = str(request.form['title'])
    content = str(request.form['content'])

    if not title or not content:
        flash('Error: Title and Content is required')
        return redirect("/create_post/")
    
    database_handler.update_post(id_post, title, content)
    return redirect("/chatroom/")    

@app.route('/chatroom/delete/<int:id_post>', methods=('POST',))
@app.route('/chatroom/delete/<int:id_post>/', methods=('POST',))
@login_required
def delete_post(id_post):
    if request.method != 'POST':
        return redirect("/edit_post/")
    
    post = database_handler.get_post_from_id(id_post)
    database_handler.delete_post(id_post)
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect("/chatroom/")    

##################################################
#_______________Social_Network___________________#
##################################################

@app.route('/social_network', methods=['GET', 'POST'])
@app.route('/social_network/', methods=['GET', 'POST'])
@login_required
def social_network_home():
    return render_template('social_network_home.html', id=session_manager.get_current_user_id())

@app.route('/social_network/friends', methods=['GET', 'POST'])
@app.route('/social_network/friends/', methods=['GET', 'POST'])
@login_required
def social_network_friends():
    
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':

        id_all_followers = database_handler.get_all_followers_from_id(user_id)
        all_followers = []
        for id_follower in id_all_followers:
            all_followers.append((id_follower["id_follower"], database_handler.get_name_from_id(id_follower["id_follower"])))

        id_all_followeds = database_handler.get_all_followeds_from_id(user_id)
        all_followeds = []
        for id_followed in id_all_followeds:
            all_followeds.append((id_followed["id_followed"], database_handler.get_name_from_id(id_followed["id_followed"])))

        return render_template("social_network_friends.html", id=user_id, all_followers=all_followers, all_followeds=all_followeds)
    
    friend_name = str(request.form["friend"])
    if friend_name is None or friend_name == "":
        flash("Name is required.")
        return redirect("/social_network/friends/")
    if not database_handler.verif_name_exists(friend_name):
        flash("This name doesn't exist.")
        return redirect("/social_network/friends/")

    id_followed = database_handler.get_id_from_name(friend_name)
    return redirect(f"/social_network/user_profile/{id_followed}")

@app.route('/social_network/user_profile/<int:id_account>', methods=['GET', 'POST'])
@app.route('/social_network/user_profile/<int:id_account>/', methods=['GET', 'POST'])
@login_required
def social_network_user_profile(id_account:int):
    user_id = session_manager.get_current_user_id()
    if user_id == id_account:
        return redirect(url_for('account_home'))
    
    id1_follow_id2 = database_handler.verif_id1_follow_id2(user_id, id_account)
    return render_template('social_network_user_profile.html',
                           id=user_id,
                           id1_follow_id2=id1_follow_id2,
                           user_profile_id=id_account,
                           name=database_handler.get_name_from_id(id_account),
                           pay=database_handler.get_pay(id_account))

@app.route('/social_network/follow_action/<int:id_followed>', methods=['GET', 'POST'])
@app.route('/social_network/follow_action/<int:id_followed>', methods=['GET', 'POST'])
@login_required
def social_network_follow_action(id_followed:int):
    user_id = session_manager.get_current_user_id()
    if id_followed == user_id:
        flash("You cannot follow yourself")
        return redirect("/social_network/friends/")

    if database_handler.verif_id1_follow_id2(user_id, id_followed):
        flash("You are already following this person")
        return redirect("/social_network/friends/")

    database_handler.create_link_social_network(user_id, id_followed, utils.get_datetime_isoformat())
    return redirect("/social_network/friends/")

@app.route('/social_network/unfollow_action/<int:id_unfollowed>', methods=['GET', 'POST'])
@app.route('/social_network/unfollow_action/<int:id_unfollowed>', methods=['GET', 'POST'])
@login_required
def social_network_unfollow_action(id_unfollowed:int): 
    user_id = session_manager.get_current_user_id()
    if id_unfollowed == user_id:
        flash("You cannot unfollow yourself")
        return redirect("/social_network/friends/")

    database_handler.delete_link_social_network_id1_id2(user_id, id_unfollowed)
    flash("You are no longer following this person")
    return redirect("/social_network/friends/")

@app.route('/social_network/chat', methods=['GET', 'POST'])
@app.route('/social_network/chat/', methods=['GET', 'POST'])
@login_required
def social_network_chat():
    user_id = session_manager.get_current_user_id()

    id_all_followeds = database_handler.get_all_followeds_from_id(user_id)
    all_followeds = []
    for id_followed in id_all_followeds:
        all_followeds.append((id_followed["id_followed"], database_handler.get_name_from_id(id_followed["id_followed"])))
    return render_template("social_network_chat.html", id=user_id, all_followeds=all_followeds)

@app.route('/social_network/chat/<int:id_receiver>', methods=['GET', 'POST'])
@app.route('/social_network/chat/<int:id_receiver>/', methods=['GET', 'POST'])
@login_required
def social_network_chat_selected(id_receiver:int):
    
    user_id = session_manager.get_current_user_id()

    id_all_followeds = database_handler.get_all_followeds_from_id(user_id)
    all_followeds = []
    for id_followed in id_all_followeds:
        all_followeds.append((id_followed["id_followed"], database_handler.get_name_from_id(id_followed["id_followed"])))

    messages = database_handler.get_all_messages_between_id_sender_and_receiver(user_id, id_receiver)
    return render_template('social_network_chat.html', id=user_id, all_followeds=all_followeds, id_receiver=id_receiver, messages=messages)

@app.route('/social_network/chat/send_message/<int:id_receiver>', methods=['GET', 'POST'])
@app.route('/social_network/chat/send_message/<int:id_receiver>/', methods=['GET', 'POST'])
@login_required
def social_network_send_message(id_receiver:int):
    
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        id_all_followeds = database_handler.get_all_followeds_from_id(user_id)
        all_followeds = []
        for id_followed in id_all_followeds:
            all_followeds.append((id_followed["id_followed"], database_handler.get_name_from_id(id_followed["id_followed"])))

        messages = database_handler.get_all_messages_between_id_sender_and_receiver(user_id, id_receiver)
        return render_template('social_network_chat.html', id=user_id, all_followeds=all_followeds, id_receiver=id_receiver, messages=messages)
    
    message = str(request.form['message'])
    if not message:
        flash('Message is required.')
        return redirect("/social_network/chat/")
    
    database_handler.insert_message(user_id, id_receiver, message, utils.get_datetime_isoformat())
    return redirect(f"/social_network/chat/{id_receiver}")

##################################################
#______________________API_______________________#
##################################################

@app.route('/api')
@app.route('/api/')
@login_required
def api_home():
    if session_manager.get_current_user_id() is None:
        return render_template('/')
    return render_template('api_home.html', id=session_manager.get_current_user_id())

@app.route('/api/search_movie', methods=['GET', 'POST'])
@app.route('/api/search_movie/', methods=['GET', 'POST'])
@login_required
def api_search_movie(movie_title=""):
    
    user_id = session_manager.get_current_user_id()
    if request.method != 'POST':
        all_movie_search=database_handler.get_movie_search(user_id)
        return render_template("api_search_movie.html",
                               id=user_id,
                               all_movie_search=all_movie_search)
    
    movie = str(request.form['movie'])
    if not movie or movie == None:
        flash('Movie is required.')
        return redirect(url_for('api_search_movie'))
    
    return redirect(url_for('api_infos_movie', movie_title=movie))

@app.route('/api/infos_movie/<string:movie_title>', methods=['GET', 'POST'])
@app.route('/api/infos_movie/<string:movie_title>/', methods=['GET', 'POST'])
@login_required
def api_infos_movie(movie_title=""):
    
    user_id = session_manager.get_current_user_id()

    movie = movie_title
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
    if not database_handler.movie_already_search(user_id, movie_title=movie_title):
        database_handler.insert_movie_search(user_id, movie_title, utils.get_datetime_isoformat())
    return render_template('api_infosmovie.html',   id=user_id,
                                                movie_title     = movie_title,
                                                movie_year      = infosMovie["Year"],
                                                movie_released  = infosMovie["Released"],
                                                movie_runtime   = infosMovie["Runtime"],
                                                movie_genre     = infosMovie["Genre"],
                                                movie_director  = infosMovie["Director"],
                                                movie_plot      = infosMovie["Plot"],
                                                movie_poster    = infosMovie["Poster"],
                                                movie_rating    = infosMovie["imdbRating"])

##################################################
#__________________Others________________________#
##################################################

@app.route('/conditions_uses')
@app.route('/conditions_uses/')
def conditions_uses():
    return render_template('conditions_uses.html', id=session_manager.get_current_user_id())

@app.route('/thank_you')
@app.route('/thank_you/')
def thank_you():
    return render_template('thank_you.html', id=session_manager.get_current_user_id())

if __name__ == "__main__" and not config.ENV_PROD:
    app.run(debug=True, use_reloader=False)