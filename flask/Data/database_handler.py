import sqlite3
import datetime
import os

class DatabaseHandler():
  def __init__(self):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    self.db_path = os.path.join(base_dir, "database.db")

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

  def get_id(self, username:str):
    conn = self.get_db_connection()
    query = f"SELECT id FROM account WHERE username=?;"
    result = conn.execute(query, (username,)).fetchall()
    conn.close()
    return dict(result[0])["id"]

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

  def get_password(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT password FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchall()
    conn.close()
    return dict(result[0])["password"]

  def get_name(self, id:int):
    conn = self.get_db_connection()
    query = f"SELECT name FROM account WHERE id=?;"
    result = conn.execute(query, (id,)).fetchall()
    conn.close()
    return dict(result[0])["name"]
  
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

  def get_pay(self, id:int) -> bool:
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