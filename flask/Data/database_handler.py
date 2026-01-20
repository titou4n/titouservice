import sqlite3
import datetime
import os

from Data.init_db import init_database
from config import Config

conf = Config()

class DatabaseHandler():
  def __init__(self):
    if not os.path.exists(conf.DATABASE_URL):
        init_database()
    self.db_path = conf.DATABASE_URL

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

  def create_account(self, username:str, password:str, name:str):
    conn = self.get_db_connection()
    query = f"INSERT INTO account (username, password, name) VALUES (?, ?, ?);"
    conn.execute(query, (username, password, name))
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
  
  def get_profile_picture_path_from_id(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT profile_picture_path FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchone()
    if result is None:
        return None
    return result[0]

  def delete_account(self, id:int):
    conn = self.get_db_connection()
    query = f"DELETE FROM account WHERE id = ?;"
    conn.execute(query, (id,))
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
    query = f"UPDATE account SET name=?, nbnamechange=nbnamechange+1 WHERE id=?;"
    conn.execute(query, (new_name,id))
    conn.commit()
    conn.close()

  def update_name_in_post(self, id:int, new_name:str):
    conn = self.get_db_connection()
    query = f"UPDATE posts SET name = ? WHERE id = ?"
    conn.execute(query, (new_name, id))
    conn.commit()
    conn.close()
  
  def verif_id_exists(self, id:int) -> bool:
    conn = self.get_db_connection()
    conn.row_factory = sqlite3.Row
    query = f"SELECT * FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchall()
    conn.close()
    return len(result)==1

  def verif_user_exists(self, username:str) -> bool:
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