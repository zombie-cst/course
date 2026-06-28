import hashlib
from db_connection import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username, password, role='Сотрудник'):
    conn = get_connection()
    if not conn:
        return False, "Ошибка подключения к БД"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "Пользователь с таким именем уже существует"
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash, role, email) VALUES (%s, %s, %s, %s)", (username, hashed_password, role, username + '@mail.ru'))
        conn.commit()
        return True, "Регистрация успешна"
    except Exception as e:
        return False, f"Ошибка при регистрации: {str(e)}"
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    conn = get_connection()
    if not conn:
        return False, "Ошибка подключения к БД", None
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute("SELECT id, role FROM users WHERE username = %s AND password_hash = %s",(username, hashed_password))
        user = cursor.fetchone()
        if not user:
            return False, "Неверный логин или пароль", None
        user_id, role = user
        return True, f"Добро пожаловать, {username}!", role
    except Exception as e:
        return False, f"Ошибка при входе: {str(e)}", None
    finally:
        cursor.close()
        conn.close()

def change_password(username, old_password, new_password):
    conn = get_connection()
    if not conn:
        return False, "Ошибка подключения к БД"
    try:
        cursor = conn.cursor()
        old_hashed = hash_password(old_password)
        cursor.execute("SELECT id FROM users WHERE username = %s AND password_hash = %s",(username, old_hashed))
        if not cursor.fetchone():
            return False, "Неверный текущий пароль"
        new_hashed = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s",(new_hashed, username))
        conn.commit()
        return True, "Пароль успешно изменен"
    except Exception as e:
        return False, f"Ошибка при смене пароля: {str(e)}"
    finally:
        cursor.close()
        conn.close()