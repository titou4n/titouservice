from flask import Flask
from config import Config
import extensions as ext

def create_app(config_object=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_object)

    # ── Extensions Flask ────────────────────────────────────────────────
    ext.csrf.init_app(app)
    ext.login_manager.init_app(app)
    ext.login_manager.login_view = "auth.login"
    ext.session_manager.init_app(app)

    # ── User loader ─────────────────────────────────────────────────────
    from models.user import User

    @ext.login_manager.user_loader
    def load_user(user_id):
        return User(int(user_id))

    # ── Context processor global ─────────────────────────────────────────
    @app.context_processor
    def inject_format_datetime():
        return dict(format_datetime=ext.utils.format_datetime)

    # ── Blueprints ───────────────────────────────────────────────────────
    from blueprints.main.routes             import bp as main_bp
    from blueprints.auth.routes             import bp as auth_bp
    from blueprints.admin.routes            import bp as admin_bp
    from blueprints.settings.routes         import bp as settings_bp
    from blueprints.bank.routes             import bp as bank_bp
    from blueprints.chatroom.routes         import bp as chatroom_bp
    from blueprints.social_network.routes   import bp as social_bp
    from blueprints.api.routes              import bp as api_bp
    from blueprints.job_tracker.routes      import bp as job_tracker_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,            url_prefix='/admin_panel')
    app.register_blueprint(settings_bp,         url_prefix='/settings')
    app.register_blueprint(bank_bp,             url_prefix='/bank')
    app.register_blueprint(chatroom_bp,         url_prefix='/chatroom')
    app.register_blueprint(social_bp,           url_prefix='/social_network')
    app.register_blueprint(api_bp,              url_prefix='/api')
    app.register_blueprint(job_tracker_bp,      url_prefix='/job_tracker')

    return app


if __name__ == '__main__' and not ext.config.ENV_PROD:
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)