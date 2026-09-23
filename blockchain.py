# blockchain.py

import hashlib
import mysql.connector

class Blockchain:
    def __init__(self, db):
        self.db = db

    def get_last_hash(self):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT current_hash FROM blockchain ORDER BY block_id DESC LIMIT 1")
        last = cursor.fetchone()
        return last['current_hash'] if last else '0'*64

    def add_block(self, certificate_id):
        cursor = self.db.cursor()
        # Get certificate data
        cursor.execute("SELECT certificate_data FROM certificates WHERE id=%s", (certificate_id,))
        cert = cursor.fetchone()
        if not cert:
            return False
        cert_data = cert[0]
        previous_hash = self.get_last_hash()
        # FIX: The hash calculation is corrected here to use only the certificate_data.
        current_hash = hashlib.sha256(cert_data.encode()).hexdigest()
        # Insert into blockchain
        cursor.execute("""
            INSERT INTO blockchain (certificate_id, previous_hash, current_hash)
            VALUES (%s,%s,%s)
        """, (certificate_id, previous_hash, current_hash))
        self.db.commit()
        return True