#!/usr/bin/env python3
"""
Test script to verify MySQL database connection
"""
import mysql.connector as sk

print("Testing MySQL Database Connection...")
print("=" * 50)

try:
    # Test connection with the credentials
    connection = sk.connect(
        host="localhost",
        user="dr_user",
        password="dr_password_2024",
        database="diabetic_retinopathy_db"
    )
    
    print("✅ SUCCESS: Connected to database!")
    
    # Create cursor
    cursor = connection.cursor()
    
    # Test query
    cursor.execute("SELECT * FROM THEGREAT")
    results = cursor.fetchall()
    
    print(f"✅ Table 'THEGREAT' has {len(results)} users")
    print("\nCurrent users in database:")
    print("-" * 50)
    for row in results:
        print(f"  Username: {row[0]} | Password: {row[1]} | Predict: {row[2]}")
    
    # Close connection
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 50)
    print("✅ Database connection test PASSED!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nConnection failed. Please check:")
    print("1. MySQL server is running")
    print("2. User 'dr_user' exists with correct password")
    print("3. Database 'diabetic_retinopathy_db' exists")
