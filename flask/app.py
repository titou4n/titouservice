import logging
from flask import Flask, request
from werkzeug.exceptions import BadRequest
from config import Config
import redis
import extensions as ext
from werkzeug.middleware.proxy_fix import ProxyFix

from blueprints.auth.register_login_manager import register_login_manager
from app_setup.context_processor import register_context_processors
from app_setup.blueprints import register_blueprints

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_app(config_object=Config):
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    app.config.from_object(obj=config_object)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
        x_prefix=0
    )

    @app.before_request
    def validate_host():
        allowed_hosts = config_object.ALLOWED_HOSTS
        if allowed_hosts and request.host not in allowed_hosts:
            logger.warning("Rejected request with invalid Host header: %s", request.host)
            raise BadRequest("Invalid Host header")

    # Extensions
    ext.csrf.init_app(app)
    ext.login_manager.init_app(app)
    ext.login_manager.login_view = "auth.login"
    ext.session_manager.init_app(app)
    ext.limiter.init_app(app)

    # redis
    try:
        redis_client = redis.from_url(app.config["REDIS_URL"])
        redis_client.ping()
        logger.info("Redis connected successfully")

    except Exception as e:
        logger.error("Redis connection failed: %s",str(e))
        raise RuntimeError("Unable to connect to Redis") from e

    # Configuration applicative
    register_login_manager()
    register_context_processors(app)
    register_blueprints(app)

    logger.info("Application initialized successfully")

    return app


if __name__ == '__main__' and not ext.config.ENV_PROD:
    try:
        app = create_app()
        logger.info("Starting development server on 127.0.0.1:8080")
        app.run(
            debug=ext.config.DEBUG,
            host="127.0.0.1",
            port=8080,
            use_reloader=False
        )
    except Exception as e:
        logger.error("Failed to start application: %s", str(e))
        raise
