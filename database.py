import pymysql
import datetime

def insert(nama_file: str, jenis: str, kendaraan: str):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='violation_db',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor # type: ignore
    )

    try:
        with conn.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO record_pelanggaran (jenis_pelanggaran, nama_file, kendaraan) VALUES (%s, %s, %s)"
            cursor.execute(sql, (f'{jenis}', f'{nama_file}', f'{kendaraan}'))

       # Commit change
        conn.commit()

        print("Record inserted successfully")
    finally:
        conn.close()