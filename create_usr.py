import hashlib
import os
import mysql.connector

# Connect to your MySQL database
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',  # Replace with your MySQL password
    database='street_community_db'
)

cursor = db.cursor()

# Sample users to insert
users = [
    ('John Doe', '1234567890', '1@m.com', 30, 'Male', 'id_proof_john.pdf', 'Street 1', 'Member', 'password1'),
    ('Jane Smith', '0987654321', '2@m.com', 28, 'Female', 'id_proof_jane.pdf', 'Street 2', 'Member', 'password2'),
    ('Emily White', '1112223333', '3@m.com', 25, 'Female', 'id_proof_emily.pdf', 'Street 3', 'MaidMember', 'password3'),
    ('Michael Brown', '4445556666', '4@m.com', 35, 'Male', 'id_proof_michael.pdf', 'Street 1', 'MaidMember', 'password4'),
]

for user in users:
    salt = os.urandom(16)  # Generate a random salt
    print(f"Generating password for user: {user[0]}")  # Debugging output
    try:
        # Hash the password using scrypt with modified n value
        hashed_password = hashlib.scrypt(user[-1].encode(), salt=salt, n=16384, r=8, p=1)
        print(f"Hashed password for {user[0]}: {hashed_password.hex()}")
    except ValueError as e:
        print(f"Error hashing password for {user[0]}: {e}")
        continue  # Skip to the next user if there's an error

    password_store = f"scrypt:{len(salt)}:{salt.hex()}${hashed_password.hex()}"

    # Insert user into the database
    cursor.execute("INSERT INTO users (name, phone, email, age, gender, id_proof, street_name, user_type, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], password_store))

# Commit and close
db.commit()
cursor.close()
db.close()
