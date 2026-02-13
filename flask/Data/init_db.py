import sqlite3
import os
from config import Config

class DatabaseManager():
    def __init__(self):
        self.config = Config()
        self.db_path = self.config.DATABASE_URL
        if not os.path.exists(self.config.DATABASE_URL):
            self.init_database()
            self.get_plan_database()
            return

        #self.reset_all_table_except_account()

    def init_database(self):
        self.create_table_account()
        
        self.create_table_roles()
        self.create_table_permissions()
        self.create_table_role_permissions()

        self.create_table_user_preferences()
        self.create_table_sessions()
        self.create_table_two_factor_codes()
        self.create_table_metadata()
        self.create_table_bank_transfers()
        self.create_table_stock_market_transfers()
        self.create_table_friends()
        self.create_table_messages()
        self.create_table_posts()
        self.create_table_movie_search()

        self.init_role_permissions()
        print("-> Base de données initialisée avec succès.")

    def init_role_permissions(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        #____________Roles____________#
        
        roles = self.config.LIST_ROLES
        for role in roles:
            cursor.execute(
                "INSERT OR IGNORE INTO roles (name) VALUES (?);",
                (role,)
            )

        #____________Permissions____________#
        permissions = self.config.LIST_PERMISSIONS
        for perm in permissions:
            cursor.execute(
                "INSERT OR IGNORE INTO permissions (name) VALUES (?);",
                (perm,)
            )

        #____________Roles/Permissions____________#

        # super_admin -> all permissions
        cursor.execute("SELECT id FROM roles WHERE name = 'super_admin'")
        super_admin_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM permissions")
        all_permissions = cursor.fetchall()
        for perm in all_permissions:
            cursor.execute(
                "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                (super_admin_id, perm[0])
            )

        role_permissions_map = {
            "admin": self.config.LIST_ADMIN_PERMS,
            "user": self.config.LIST_USER_PERMS,
            "visitor": self.config.LIST_VISITOR_PERMS
        }

        for role_name, perms_list in role_permissions_map.items():

            cursor.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
            role_id = cursor.fetchone()[0]

            for perm_name in perms_list:
                cursor.execute("SELECT id FROM permissions WHERE name = ?", (perm_name,))
                perm_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                    (role_id, perm_id)
                )


        conn.commit()
        conn.close()


    def verif_table_exist(self, table_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
        """
        cursor.execute(query, (table_name,))
        result = cursor.fetchone()

        conn.close()
        return result is not None
    
    ########################################
    #________________TABLE_________________#
    ########################################

    def create_table_account(self):

        if self.verif_table_exist("account"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE account
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            role_id INTEGER NOT NULL,
            username STRING NOT NULL UNIQUE,
            password STRING NOT NULL,
            name STRING NOT NULL UNIQUE,
            email VARCHAR(255),
            email_verified BOOLEAN DEFAULT 0,
            profile_picture_path STRING,
            pay DECIMAL DEFAULT {self.config.BANK_DEFAULT_PAY},
            nbpasswordchange INTEGER DEFAULT 0,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'account' created with success.")

    def create_table_roles(self):

        if self.verif_table_exist("roles"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = f"""
        CREATE TABLE roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'roles' created with success.")

    def create_table_permissions(self):

        if self.verif_table_exist("permissions"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = f"""
        CREATE TABLE permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'permissions' created with success.")

    def create_table_role_permissions(self):

        if self.verif_table_exist("role_permissions"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = f"""
        CREATE TABLE role_permissions (
            role_id INTEGER,
            permission_id INTEGER,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (permission_id) REFERENCES permissions(id)
        );
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'role_permissions' created with success.")

    def create_table_user_preferences(self):

        if self.verif_table_exist("user_preferences"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE user_preferences
        # =========================
        query = f"""
        CREATE TABLE user_preferences (
            user_id INTEGER PRIMARY KEY,
            twofa_enabled BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES account(id) ON DELETE CASCADE
        );
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'user_preferences' created with success.")

    def create_table_sessions(self):

        if self.verif_table_exist("sessions"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE sessions
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id_hash TEXT PRIMARY KEY NOT NULL,
            user_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL,
            expires_at DATETIME NOT NULL,
            last_used_at DATETIME NOT NULL,
            ip_hash TEXT,
            user_agent_hash TEXT,
            is_revoked BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'sessions' created with success.")

    def create_table_two_factor_codes(self):

        if self.verif_table_exist("two_factor_codes"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE two_factor_codes
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS two_factor_codes (
            id_two_factor_codes INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code_hash TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            attempts INTEGER DEFAULT 0,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'two_factor_codes' created with success.")

    def create_table_metadata(self):

        if self.verif_table_exist("metadata"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE metadata
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS metadata (
            id_metadata INTEGER PRIMARY KEY AUTOINCREMENT,
            id INTEGER NOT NULL,
            date_connected DATETIME NOT NULL,
            ipv4 INTEGER NOT NULL,
            FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'metadata' created with success.")

    def create_table_bank_transfers(self):

        if self.verif_table_exist("bank_transfers"):
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE bank_transfers
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS bank_transfers (
            id_bank_transfer INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sender INTEGER NOT NULL,
            id_receiver INTEGER NOT NULL,
            transfer_amount DECIMAL NOT NULL,
            transfer_date DATETIME NOT NULL,
            FOREIGN KEY (id_sender) REFERENCES account(id) ON DELETE CASCADE,
            FOREIGN KEY (id_receiver) REFERENCES account(id) ON DELETE CASCADE
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'bank_transfers' created with success.")

    def create_table_stock_market_transfers(self):

        if self.verif_table_exist("stock_market_transfers"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE stock_market_transfers
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS stock_market_transfers (
            id_stock_market_transfer INTEGER PRIMARY KEY AUTOINCREMENT,
            id_account INTEGER NOT NULL,
            type STRING NOT NULL,
            symbol STRING NOT NULL,
            stock_number DECIMAL NOT NULL,
            stock_price DECIMAL NOT NULL,
            transfer_datetime DATETIME NOT NULL,
            FOREIGN KEY (id_account) REFERENCES account(id)
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'stock_market_transfers' created with success.")

    def create_table_friends(self):

        if self.verif_table_exist("friends"):
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # =========================
        # TABLE friends
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_follower INTEGER NOT NULL,
            id_followed INTEGER NOT NULL,
            date DATETIME NOT NULL,
            FOREIGN KEY (id_follower) REFERENCES account(id) ON DELETE CASCADE,
            FOREIGN KEY (id_followed) REFERENCES account(id) ON DELETE CASCADE
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'friends' created with success.")

    def create_table_messages(self):

        if self.verif_table_exist("messages"):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE messages
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS messages (
            id_message INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sender INTEGER NOT NULL,
            id_receiver INTEGER NOT NULL,
            message STRING NOT NULL,
            datetime DATETIME NOT NULL,
            FOREIGN KEY (id_sender) REFERENCES account(id) ON DELETE CASCADE,
            FOREIGN KEY (id_receiver) REFERENCES account(id) ON DELETE CASCADE
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'messages' created with success.")

    def create_table_posts(self):

        if self.verif_table_exist("posts"):
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE posts
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS posts (
            id_post INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title STRING NOT NULL,
            content STRING NOT NULL,
            created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES account(id) ON DELETE CASCADE
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'posts' created with success.")

    def create_table_movie_search(self):

        if self.verif_table_exist("movie_search"):
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # =========================
        # TABLE movie_search
        # =========================
        query = f"""
        CREATE TABLE IF NOT EXISTS movie_search (
            id_movie_search INTEGER PRIMARY KEY AUTOINCREMENT,
            id INTEGER NOT NULL,
            movie_title STRING NOT NULL,
            date_movie_search DATETIME NOT NULL,
            FOREIGN KEY (id) REFERENCES account(id) ON DELETE CASCADE
        );
        """

        cursor.execute(query)
        conn.commit()
        conn.close()
        print("-> TABLE 'movie_search' created with success.")

    ########################################
    #________________OTHER_________________#
    ########################################

    def get_plan_database(self):
        print("Get plan database....")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
        for row in cursor.fetchall():
            print(row[0])

        conn.close()

    def reset_all_table_except_account(self):
        print("_________Reset all table except account__________")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            AND name != 'account'
            AND name NOT LIKE 'sqlite_%'
        """)

        tables = cursor.fetchall()

        for (table_name,) in tables:
            cursor.execute(f'DROP TABLE "{table_name}"')
            print(f"The {table_name} table has been successfully deleted.")

        conn.commit()
        conn.close()

        self.init_database()

    def reset_database(self):
        """
        Supprime l'ancienne base de données et la recrée avec toutes les tables.
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print("-> Ancienne base de données supprimée.")
        
        self.init_database()