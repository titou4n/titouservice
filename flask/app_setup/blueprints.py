from flask import Flask
from blueprints.main.routes import bp as main_bp
from blueprints.auth.routes import bp as auth_bp
from blueprints.admin.routes import bp as admin_bp
from blueprints.settings.routes import bp as settings_bp
from blueprints.bank.routes import bp as bank_bp
from blueprints.chatroom.routes import bp as chatroom_bp
from blueprints.social_network.routes import bp as social_bp
from blueprints.movie_information.routes import bp as movie_information_bp
from blueprints.job_tracker.routes import bp as job_tracker_bp
from blueprints.emergency_information.routes import bp as emergency_information_bp


def register_blueprints(app:Flask):

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,                    url_prefix='/admin_panel')
    app.register_blueprint(settings_bp,                 url_prefix='/settings')
    app.register_blueprint(bank_bp,                     url_prefix='/bank')
    app.register_blueprint(chatroom_bp,                 url_prefix='/chatroom')
    app.register_blueprint(social_bp,                   url_prefix='/social_network')
    app.register_blueprint(movie_information_bp,        url_prefix='/movie_information')
    app.register_blueprint(job_tracker_bp,              url_prefix='/job_tracker')
    app.register_blueprint(emergency_information_bp,    url_prefix='/emergency_information')