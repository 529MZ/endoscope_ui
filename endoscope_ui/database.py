import pymysql

def connect_to_database():
    """连接到MySQL数据库"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='jzy20020206',
            database='database',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Successfully connected to the database.")
        return connection
    except pymysql.Error as e:
        print(f"Failed to connect to the database: {e}")
        return None

def insert_data(connection, name, gender, age, id):

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO patient (name, gender, age, id) VALUES (%s, %s, %s, %s);"
            cursor.execute(sql, (name, gender, age, id))
            connection.commit()
            print(f"Successfully inserted {cursor.rowcount} records.")
    except Exception as e:
        print(f"Failed to insert data: {e}")

def insert_data_1(connection, num, pic, txt):

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO image (patient_num, address_pic, address_txt) VALUES (%s, %s, %s);"
            cursor.execute(sql, (num, pic, txt))
            connection.commit()
            print(f"Successfully inserted {cursor.rowcount} records.")
    except Exception as e:
        print(f"Failed to insert data: {e}")


def delete_data(connection, id):
    
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM information WHERE id = %s;"
            cursor.execute(sql, (id,))
            connection.commit()
            print(f"Successfully deleted {cursor.rowcount} records.")
    except Exception as e:
        print(f"Failed to delete data: {e}")

def update_data(connection, name, age, id):
    """更新数据库中的数据"""
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE information SET name = %s, age = %s WHERE id = %s;"
            cursor.execute(sql, (name, age, id))
            connection.commit()
            print(f"Successfully updated {cursor.rowcount} records.")
    except Exception as e:
        print(f"Failed to update data: {e}")

def query_data(connection, name):
    """从数据库查询数据"""
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM patient WHERE name = %s;"
            cursor.execute(sql, (name,))
            result = cursor.fetchone()
            if result:
                return result['id'], result['num']  # 返回查询结果的第一个值,即id
            else:
                return None
    except Exception as e:
        print(f"Failed to query data: {e}")

def query_data_2(connection, num):
    """从数据库查询数据"""
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM patient WHERE num = %s;"
            cursor.execute(sql, (num,))
            result = cursor.fetchone()
            if result:
                """print(f"Patient Information:")
                print(f"ID: {result['id']}")
                print(f"Num: {result['num']}")
                print(f"Name: {result['name']}")
                print(f"Age: {result['age']}")
                print(f"Gender: {result['gender']}")"""
                patient_info = f"Patient Information:\nName: {result['name']}\nAge: {result['age']}\nGender: {result['gender']}\nID: {result['id']}"
                return patient_info
            else:
                return None
    except Exception as e:
        print(f"Failed to query data: {e}")

def disconnect_from_database(connection):
    """断开与MySQL数据库的连接"""
    try:
        connection.close()
        print("Successfully disconnected from the database.")
    except Exception as e:
        print(f"Failed to disconnect from the database: {e}")

# 示例用法
"""connection = connect_to_database()
insert_data(connection, 'John Doe', 25, 1)
insert_data(connection, 'Jane Smith', 30, 2)
query_data(connection)
update_data(connection, 'John Doe', 26, 1)
delete_data(connection, 2)
query_data(connection)
disconnect_from_database(connection)"""