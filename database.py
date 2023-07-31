import pymysql
import datetime

def insert(tanggal: str, jenis: str):
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
            sql = "INSERT INTO `pelanggar` (`tanggal`, `jenis_pelanggaran`) VALUES (%s, %s)"
            cursor.execute(sql, (f'{tanggal}', f'{jenis}'))

        # Commit changes
        conn.commit()

        print("Record inserted successfully")
    finally:
        conn.close()