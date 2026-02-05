import sqlite3
import datetime
import os

from Data.init_db import DatabaseManager
from config import Config
from utils.hash_manager import HashManager


database_manager = DatabaseManager()
hash_manager = HashManager()
config = Config()

class DatabaseHandler():
  def __init__(self):
    if not os.path.exists(config.DATABASE_URL):
        database_manager.init_database()
    self.db_path = config.DATABASE_URL

    if not self.verif_username_exists(str(config.USERNAME_VISITOR)):
      self.create_account(str(config.USERNAME_VISITOR), str(hash_manager.generate_password_hash(config.PASSWORD_VISITOR)), str(config.NAME_VISITOR))

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

  def create_account(self, username:str, password:str, name:str):
    conn = self.get_db_connection()
    query = f"INSERT INTO account (username, password, name) VALUES (?, ?, ?);"
    conn.execute(query, (username, password, name))
    conn.commit()
    conn.close()

  #_____two_factor_codes_____#

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
    query = f"DELETE FROM two_factor_codes WHERE created_at < datetime('now', '-10 minutes');"
    conn.execute(query)
    conn.commit()
    conn.close()

  def update_profile_picture_path_from_id(self, id:int, profile_picture_path:str):
    conn = self.get_db_connection()
    query = f"UPDATE account SET profile_picture_path=? WHERE id=?;"
    conn.execute(query, (profile_picture_path,id))
    conn.commit()
    conn.close()

  def get_id_from_username(self, username:str):
    conn = self.get_db_connection()
    query = f"SELECT id FROM account WHERE username=?;"
    result = conn.execute(query, (username,)).fetchall()
    conn.close()
    return dict(result[0])["id"]
  
  def get_id_from_name(self, name:str):
    conn = self.get_db_connection()
    query = f"SELECT id FROM account WHERE name=?;"
    result = conn.execute(query, (name,)).fetchall()
    conn.close()
    return dict(result[0])["id"]
  
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
    result = conn.execute(query, (id,)).fetchall()
    conn.close()
    return dict(result[0])["password"]

  def get_name_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT name FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchall()
    conn.close()
    return dict(result[0])["name"]
  
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

  def update_email_verified_from_id(self, id:int):
    switch_to = 1
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

  def insert_stock_market_transfers(self, id:int, type:str, symbol:int, stock_number:float, stock_price:float, transfer_datetime:datetime):
    conn = self.get_db_connection()
    query = f"INSERT INTO stock_market_transfers (id_account, type, symbol, stock_number, stock_price, transfer_datetime) VALUES (?,?,?,?,?,?);"
    conn.execute(query, (id, type, symbol, stock_number, stock_price, transfer_datetime,))
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
      query = f"SELECT id FROM posts WHERE id_post = ?;"
      result = conn.execute(query, (id_post,)).fetchone()
      conn.close()
      return result[0]

  def create_post(self, id:int, name:str, title:str, content:str):
    conn = self.get_db_connection()
    query = f"INSERT INTO posts (id, name, title, content) VALUES (?, ?, ?, ?);"
    conn.execute(query,(id, name, title, content))
    conn.commit()
    conn.close()

  def update_post(self, id_post:int, name:str, title:str, content:str):
    conn = self.get_db_connection()
    query = f"UPDATE posts SET name = ?, title = ?, content = ? WHERE id_post = ?;"
    conn.execute(query, (name, title, content, id_post))
    conn.commit()
    conn.close()

  def delete_post(self, id_post:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM posts WHERE id_post = ?"
    conn.execute(query, (id_post,))
    conn.commit()
    conn.close()

  def delete_all_post_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM posts WHERE id = ?"
    conn.execute(query, (id,))
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