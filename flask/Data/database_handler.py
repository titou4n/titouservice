import sqlite3
import datetime
import os

from Data.init_db import DatabaseManager
from config import Config
from utils.hash_manager import HashManager
from utils.utils import Utils

class DatabaseHandler():
  def __init__(self):
    self.database_manager = DatabaseManager()
    self.hash_manager = HashManager()
    self.config = Config()
    self.utils = Utils()

    self.db_path = self.config.DATABASE_URL

    if not os.path.exists(self.config.DATABASE_URL):
        self.database_manager.init_database()

    if not self.config.ENV_PROD and not self.verif_username_exists(str(self.config.USERNAME_DEBUG)):
      role_id = self.get_role_id(role_name=self.config.ROLE_NAME_DEBUG)
      self.create_account(str(self.config.USERNAME_DEBUG), str(self.hash_manager.generate_password_hash(self.config.PASSWORD_DEBUG)), str(self.config.ROLE_NAME_DEBUG), role_id=role_id)

    if not self.verif_username_exists(str(self.config.USERNAME_VISITOR)):
      role_id = self.get_role_id(role_name=self.config.ROLE_NAME_VISITOR)
      self.create_account(str(self.config.USERNAME_VISITOR), str(self.hash_manager.generate_password_hash(self.config.PASSWORD_VISITOR)), str(self.config.NAME_VISITOR), role_id=role_id)

  def get_db_connection(self):
    conn = sqlite3.connect(self.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

  def get_number_account(self):
    conn = self.get_db_connection()
    query = f"SELECT id FROM account;"
    number_account = len(conn.execute(query).fetchall())
    conn.close()
    return number_account

  def insert_metadata(self, id:int, date_connected:datetime, ipv4:int):
    conn = self.get_db_connection()
    query = f"INSERT INTO metadata (date_connected, id, ipv4) VALUES (?,?,?);"
    conn.execute(query, (date_connected, id, ipv4))
    conn.commit()
    conn.close()

  def get_metadata(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT * FROM metadata WHERE id=?;"
    metadata = conn.execute(query, (id,)).fetchall()
    conn.close()
    return metadata
  
  ##########################################
  #________________ACCOUNT_________________#
  ##########################################

  def create_account(self, username:str, password:str, name:str, role_id:int):
    conn = self.get_db_connection()
    query = f"INSERT INTO account (username, password, name, role_id) VALUES (?, ?, ?, ?);"
    conn.execute(query, (username, password, name, role_id))
    conn.commit()
    conn.close()

  def get_user(self, user_id:int):
    conn = self.get_db_connection()
    query = f"SELECT id, role_id, username, password, name, email, email_verified, pay FROM account WHERE id=?"
    result = conn.execute(query, (user_id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result

  ##########################################
  #____________USER_PREFERENCES____________#
  ##########################################

  def insert_user_preferences(self, user_id:int):
    conn = self.get_db_connection()
    query = f"INSERT INTO user_preferences (user_id) VALUES (?);"
    conn.execute(query, (user_id,))
    conn.commit()
    conn.close()

  def get_user_preferences_2fa(self, user_id:int):
    conn = self.get_db_connection()
    query = f"SELECT twofa_enabled FROM user_preferences WHERE user_id=?;"
    result = conn.execute(query, (user_id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]

  def switch_user_preferences_2fa(self, user_id:int):
    switch_to = not self.get_user_preferences_2fa(user_id=user_id)
    conn = self.get_db_connection()
    query = f"UPDATE user_preferences SET twofa_enabled=? WHERE user_id=?;"
    conn.execute(query, (switch_to, user_id,))
    conn.commit()
    conn.close()

  ##########################################
  #___________PERMISSIONS/ROLES____________#
  ##########################################

  def get_all_couple_role_and_permissions_id(self):
    conn = self.get_db_connection()
    query = f"SELECT role_id, permission_id FROM role_permissions;"
    result = conn.execute(query,).fetchall()
    conn.close()
    if result is None:
        return None
    return result

  def get_list_permission_id(self, role_id:int) -> list:
    conn = self.get_db_connection()
    query = f"SELECT permission_id FROM role_permissions WHERE role_id=?;"
    result = conn.execute(query, (role_id,)).fetchall()
    conn.close()
    if result is None:
        return []
    list_result = []
    for permission_id_object in result:
      list_result.append(permission_id_object[0])
    return list_result
  
  def insert_permission(self, role_id:int, permission_id:int) -> None:
    conn = self.get_db_connection()
    query = f"INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?);"
    conn.execute(query, (role_id, permission_id))
    conn.commit()
    conn.close()

  def delete_role_from_role_permission(self, role_id:int) -> None:
    conn = self.get_db_connection()
    query = f"DELETE FROM role_permissions WHERE role_id=?;"
    conn.execute(query, (role_id,))
    conn.commit()
    conn.close()
  
  ##########################################
  #_____________PERMISSIONS________________#
  ##########################################

  def get_permission_id(self, permission_name:int):
    conn = self.get_db_connection()
    query = f"SELECT id FROM permissions WHERE name=?;"
    result = conn.execute(query, (permission_name,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]

  def get_permission_name(self, permission_id:int):
    conn = self.get_db_connection()
    query = f"SELECT name FROM permissions WHERE id=?;"
    result = conn.execute(query, (permission_id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]

  ##########################################
  #_________________ROLES__________________#
  ##########################################

  def get_all_role(self):
    conn = self.get_db_connection()
    query = f"SELECT * FROM roles;"
    result = conn.execute(query,).fetchall()
    conn.close()
    if result is None:
        return None
    return result

  def role_exists(self, role_name):
    conn = self.get_db_connection()
    query = "SELECT id FROM roles WHERE name=?"
    result = conn.execute(query, (role_name,)).fetchone()
    conn.close()
    return result is not None
  
  def insert_role(self, role_name:str):
    conn = self.get_db_connection()
    query = f"INSERT OR IGNORE INTO roles (name) VALUES (?);"
    conn.execute(query, (role_name,))
    conn.commit()
    conn.close()

  def update_role(self, role_id:int, role_name:str):
    conn = self.get_db_connection()
    query = f"UPDATE roles SET name=? WHERE id=?;"
    conn.execute(query, (role_name, role_id))
    conn.commit()
    conn.close()

  def delete_role(self, role_id:str):
    conn = self.get_db_connection()
    query = f"DELETE FROM roles WHERE id=?;"
    conn.execute(query, (role_id,))
    conn.commit()
    conn.close()
  
  def get_role_id(self, role_name:int):
    conn = self.get_db_connection()
    query = f"SELECT id FROM roles WHERE name=?;"
    result = conn.execute(query, (role_name,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]

  def get_role_name(self, role_id:int):
    conn = self.get_db_connection()
    query = f"SELECT name FROM roles WHERE id=?;"
    result = conn.execute(query, (role_id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]
  
  def update_user_role(self, role_id:int, user_id:int):
    conn = self.get_db_connection()
    query = f"UPDATE account SET role_id=? WHERE id=?;"
    conn.execute(query, (role_id, user_id))
    conn.commit()
    conn.close()

  ##########################################
  #_______________SESSIONS_________________#
  ##########################################

  def insert_session(self, session_id_hash:str, user_id:int, created_at:datetime, expires_at:datetime, ip_hash:str, user_agent_hash:str, is_revoked:bool):
    conn = self.get_db_connection()
    query = f"INSERT INTO sessions (session_id_hash, user_id, created_at, expires_at, last_used_at, ip_hash, user_agent_hash, is_revoked) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
    conn.execute(query, (session_id_hash, user_id, created_at, expires_at, created_at, ip_hash, user_agent_hash, is_revoked))
    conn.commit()
    conn.close()

  def update_session(self, session_id_hash:str, last_used_at:datetime):
    conn = self.get_db_connection()
    query = f"UPDATE sessions SET last_used_at=? WHERE session_id_hash=?;"
    conn.execute(query, (last_used_at, session_id_hash))
    conn.commit()
    conn.close()

  def get_session(self, session_id_hash:str):
    conn = self.get_db_connection()
    query = f"SELECT session_id_hash,user_id,created_at,expires_at,last_used_at,ip_hash,user_agent_hash,is_revoked FROM sessions WHERE session_id_hash=?;"
    result = conn.execute(query, (session_id_hash,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result
  
  def get_all_sessions_from_user_id(self, user_id:int):
    conn = self.get_db_connection()
    query = f"SELECT session_id_hash,user_id,created_at,expires_at,last_used_at,ip_hash,user_agent_hash,is_revoked FROM sessions WHERE user_id=?;"
    result = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    return result
  
  def revoke_session(self, session_id_hash:str):
    switch_to = 1
    conn = self.get_db_connection()
    query = f"UPDATE sessions SET is_revoked=? WHERE session_id_hash=?;"
    conn.execute(query, (switch_to, session_id_hash,))
    conn.commit()
    conn.close()

  def revoke_all_session_from_user_id(self, user_id:int):
    switch_to = 1
    conn = self.get_db_connection()
    query = f"UPDATE sessions SET is_revoked=? WHERE user_id=?;"
    conn.execute(query, (switch_to, user_id))
    conn.commit()
    conn.close()

  def delete_session(self, session_id_hash:str):
    conn = self.get_db_connection()
    query = f"DELETE FROM sessions WHERE session_id_hash=?;"
    conn.execute(query, (session_id_hash,))
    conn.commit()
    conn.close()

  def delete_all_session(self):
    conn = self.get_db_connection()
    query = f"DELETE FROM sessions;"
    conn.execute(query)
    conn.commit()
    conn.close()

  ##########################################
  #_________________2FA____________________#
  ##########################################

  def insert_two_factor_codes(self, user_id:int, code_hash:str, created_at:datetime):
    conn = self.get_db_connection()
    query = f"INSERT INTO two_factor_codes (user_id, code_hash, created_at) VALUES (?, ?, ?);"
    conn.execute(query, (user_id, code_hash, created_at))
    conn.commit()
    conn.close()

  def get_code_hash_from_user_id(self, user_id:int):
    used = 0
    max_attempts = 3
    conn = self.get_db_connection()
    query = f"SELECT id_two_factor_codes,code_hash,created_at,attempts, used FROM two_factor_codes WHERE user_id=? AND used=? AND attempts<=? ORDER BY created_at DESC;"
    result = conn.execute(query, (user_id, used, max_attempts)).fetchone()
    conn.close()
    if result is None:
        return None
    return result
  
  def add_attempts_two_factor_codes(self, id_two_factor_codes:int):
    conn = self.get_db_connection()
    query = f"UPDATE two_factor_codes SET attempts=attempts+1 WHERE id_two_factor_codes=?;"
    conn.execute(query, (id_two_factor_codes,))
    conn.commit()
    conn.close()
  
  def delete_old_code_hash_from_user_id(self, user_id:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM two_factor_codes WHERE user_id=?;"
    conn.execute(query, (user_id,))
    conn.commit()
    conn.close()

  def delete_old_code_hash(self):
    conn = self.get_db_connection()
    query = f"DELETE FROM two_factor_codes WHERE created_at < datetime('now', '-30 minutes');"
    conn.execute(query)
    conn.commit()
    conn.close()

  def update_twofa_code_to_used(self, id_two_factor_codes:int):
    used = 1
    conn = self.get_db_connection()
    query = f"UPDATE two_factor_codes SET used=? WHERE id_two_factor_codes=?;"
    conn.execute(query, (used, id_two_factor_codes,))
    conn.commit()
    conn.close()

  ##########################################
  #_______________ACCOUNT__________________#
  ##########################################

  def update_profile_picture_path_from_id(self, id:int, profile_picture_path:str):
    conn = self.get_db_connection()
    query = f"UPDATE account SET profile_picture_path=? WHERE id=?;"
    conn.execute(query, (profile_picture_path,id))
    conn.commit()
    conn.close()

  def get_id_from_username(self, username:str):
    conn = self.get_db_connection()
    query = f"SELECT id FROM account WHERE username=?;"
    result = conn.execute(query, (username,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]
  
  def get_id_from_name(self, name:str):
    conn = self.get_db_connection()
    query = f"SELECT id FROM account WHERE name=?;"
    result = conn.execute(query, (name,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]
  
  def get_username_from_user_id(self, user_id:int):
    conn = self.get_db_connection()
    query = f"SELECT username FROM account WHERE id=?;"
    result = conn.execute(query, (user_id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]
  
  def get_password(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT password FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]

  def get_name_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT name FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]
  
  def get_email_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT email FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]
  
  def get_email_verified_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT email_verified FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchone()
    conn.close()
    if result is None:
        return None
    return result[0]
  
  def get_profile_picture_path_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT profile_picture_path FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchone()
    if result is None:
        return None
    return result[0]

  def update_username(self, id:int, new_username:str):
    conn = self.get_db_connection()
    query = f"UPDATE account SET username=? WHERE id=?;"
    conn.execute(query, (new_username,id))
    conn.commit()
    conn.close()
  
  def update_password(self, id:int, new_password:str):
    conn = self.get_db_connection()
    query = f"UPDATE account SET password=?, nbpasswordchange=nbpasswordchange+1 WHERE id=?;"
    conn.execute(query, (new_password,id))
    conn.commit()
    conn.close()
  
  def update_name(self, id:int, new_name:str):
    conn = self.get_db_connection()
    query = f"UPDATE account SET name=? WHERE id=?;"
    conn.execute(query, (new_name,id))
    conn.commit()
    conn.close()

  def update_name_in_post(self, id:int, new_name:str):
    conn = self.get_db_connection()
    query = f"UPDATE posts SET name = ? WHERE id = ?"
    conn.execute(query, (new_name, id))
    conn.commit()
    conn.close()
  
  def update_email_from_id(self, id:int, email:str):
    conn = self.get_db_connection()
    query = f"UPDATE account SET email=? WHERE id=?;"
    conn.execute(query, (email,id))
    conn.commit()
    conn.close()

  def update_email_verified_from_id(self, id:int, switch_to:bool):
    conn = self.get_db_connection()
    query = f"UPDATE account SET email_verified=? WHERE id=?;"
    conn.execute(query, (switch_to, id,))
    conn.commit()
    conn.close()
  
  def verif_id_exists(self, id:int) -> bool:
    conn = self.get_db_connection()
    conn.row_factory = sqlite3.Row
    query = f"SELECT * FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchall()
    conn.close()
    return len(result)==1

  def verif_username_exists(self, username:str) -> bool:
    conn = self.get_db_connection()
    query = f"SELECT * FROM account WHERE username=?;"
    result = conn.execute(query, (username,)).fetchall()
    conn.close()
    return len(result)==1

  def verif_name_exists(self, name:str) -> bool:
    conn = self.get_db_connection()
    conn.row_factory = sqlite3.Row
    query = f"SELECT * FROM account WHERE name=?;"
    result = conn.execute(query, (name,)).fetchall()
    conn.close()
    return len(result)==1
  
  def delete_account(self, id:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM account WHERE id = ?;"
    conn.execute(query, (id,))
    conn.commit()
    conn.close()

  ##################################################
  #__________________Bank__________________________#
  ##################################################

  def get_pay(self, id:int) -> float:
    conn = self.get_db_connection()
    query = f"SELECT pay FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchall()
    conn.close()
    return dict(result[0])["pay"]

  def update_pay(self, id:int, new_pay:str):
    conn = self.get_db_connection()
    query = f"UPDATE account SET pay=? WHERE id=?;"
    conn.execute(query, (new_pay,id))
    conn.commit()
    conn.close()

  #### bank_transfers ####

  def insert_bank_transfer(self, id_sender:int, id_receiver:int, transfer_amount:int, transfer_date:datetime):
    conn = self.get_db_connection()
    query = f"INSERT INTO bank_transfers (id_sender, id_receiver, transfer_amount, transfer_date) VALUES (?,?,?,?);"
    conn.execute(query, (id_sender, id_receiver, transfer_amount, transfer_date))
    conn.commit()
    conn.close()

  def get_all_bank_transfer(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT * FROM bank_transfers WHERE id_sender=? OR id_receiver=?;"
    all_bank_transfer_from_id = conn.execute(query, (id, id,)).fetchall()
    conn.close()
    return all_bank_transfer_from_id
  
  #### stock_market_transfers ####

  def insert_stock_market_transfers(self, user_id:int, type:str, symbol:int, stock_number:float, stock_price:float, transfer_datetime:datetime):
    conn = self.get_db_connection()
    query = f"INSERT INTO stock_market_transfers (id_account, type, symbol, stock_number, stock_price, transfer_datetime) VALUES (?,?,?,?,?,?);"
    conn.execute(query, (user_id, type, symbol, stock_number, stock_price, transfer_datetime,))
    conn.commit()
    conn.close()

  def get_all_stock_market_transfers_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT * FROM stock_market_transfers WHERE id_account=?;"
    all_stock_market_transfers_from_id = conn.execute(query, (id,)).fetchall()
    conn.close()
    return all_stock_market_transfers_from_id
  
  def get_all_stock_market_transfers_from_id_symbol(self, id:int, symbol:str):
    conn = self.get_db_connection()
    query = f"SELECT * FROM stock_market_transfers WHERE id_account=? AND symbol=?;"
    all_stock_market_transfers_from_id_symbol = conn.execute(query, (id, symbol,)).fetchall()
    conn.close()
    return all_stock_market_transfers_from_id_symbol

  ##################################################
  #__________________Chatroom______________________#
  ##################################################
    
  def get_posts(self):
    conn = self.get_db_connection()
    query = f"SELECT * FROM posts;"
    posts = conn.execute(query).fetchall()
    conn.close()
    return posts
  
  def get_post_from_id(self, id_post:int):
      conn = self.get_db_connection()
      query = f"SELECT * FROM posts WHERE id_post = ?;"
      post = conn.execute(query, (id_post,)).fetchone()
      conn.close()
      return post
  
  def get_id_from_id_post(self, id_post:int):
      conn = self.get_db_connection()
      query = f"SELECT user_id FROM posts WHERE id_post = ?;"
      result = conn.execute(query, (id_post,)).fetchone()
      conn.close()
      return result[0]

  def create_post(self, user_id:int, title:str, content:str):
    conn = self.get_db_connection()
    query = f"INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?);"
    conn.execute(query,(user_id, title, content,))
    conn.commit()
    conn.close()

  def update_post(self, id_post:int, title:str, content:str):
    conn = self.get_db_connection()
    query = f"UPDATE posts SET title = ?, content = ? WHERE id_post = ?;"
    conn.execute(query, (title, content, id_post))
    conn.commit()
    conn.close()

  def delete_post(self, id_post:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM posts WHERE id_post = ?"
    conn.execute(query, (id_post,))
    conn.commit()
    conn.close()

  def delete_all_post_from_id(self, user_id:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM posts WHERE user_id = ?"
    conn.execute(query, (user_id,))
    conn.commit()
    conn.close()

  ##################################################
  #__________________API_Movies____________________#
  ##################################################

  def insert_movie_search(self, id:int, movie_title:str, date_movie_search:datetime):
    conn = self.get_db_connection()
    query = f"INSERT INTO movie_search (id, movie_title, date_movie_search) VALUES (?,?,?);"
    conn.execute(query, (id, movie_title, date_movie_search))
    conn.commit()
    conn.close()

  def get_movie_search(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT * FROM movie_search WHERE id=?;"
    movie_search = conn.execute(query, (id,)).fetchall()
    conn.close()
    return movie_search
  
  def movie_already_search(self, id:int, movie_title:str):
    conn = self.get_db_connection()
    query = f"SELECT * FROM movie_search WHERE id=? AND movie_title=?;"
    movie_search = conn.execute(query, (id, movie_title)).fetchall()
    conn.close()
    return len(movie_search) >= 1
  
  ##################################################
  #________________Social_Network__________________#
  ##################################################

  def create_link_social_network(self, id_follower:int, id_followed:int, date:datetime):
    conn = self.get_db_connection()
    query = f"INSERT INTO friends (id_follower, id_followed, date) VALUES (?, ?, ?);"
    conn.execute(query, (id_follower, id_followed, date,))
    conn.commit()
    conn.close()

  def get_all_followers_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT id_follower FROM friends WHERE id_followed=?;"
    list_id_follower = conn.execute(query, (id,)).fetchall()
    conn.close()
    return list_id_follower
  
  def get_all_followeds_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT id_followed FROM friends WHERE id_follower=?;"
    list_id_followed = conn.execute(query, (id,)).fetchall()
    conn.close()
    return list_id_followed
  
  def verif_id1_follow_id2(self, id1:int, id2:int) -> bool:
    conn = self.get_db_connection()
    query = f"SELECT * FROM friends WHERE id_follower=? AND id_followed=?;"
    result = conn.execute(query, (id1, id2,)).fetchall()
    conn.close()
    return len(result)>=1
  
  def delete_link_social_network_id1_id2(self, id_follower:int, id_followed:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM friends WHERE id_follower=? AND id_followed=?"
    conn.execute(query, (id_follower, id_followed,))
    conn.commit()
    conn.close()
  
  def insert_message(self, id_sender:int, id_receiver:int, message:str, datetime:datetime):
    conn = self.get_db_connection()
    query = f"INSERT INTO messages (id_sender, id_receiver, message, datetime) VALUES (?, ?, ?, ?);"
    conn.execute(query, (id_sender, id_receiver, message, datetime,))
    conn.commit()
    conn.close()

  def get_all_messages_between_id_sender_and_receiver(self, id_sender:int, id_receiver:int):
    conn = self.get_db_connection()
    query = f"SELECT * FROM messages WHERE id_sender=? AND id_receiver=?;"
    messages = conn.execute(query, (id_sender, id_receiver,)).fetchall()
    conn.close()
    return messages