import pyodbc

def init_database():
    try:
        # Connect to master database to check/create the target database
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=master;Trusted_Connection=yes', 
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Check if MarketplaceDb exists
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'MarketplaceDb'")
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("CREATE DATABASE MarketplaceDb")
            print("Database 'MarketplaceDb' created successfully in SQL Server.")
        else:
            print("Database 'MarketplaceDb' already exists in SQL Server.")
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")

if __name__ == '__main__':
    init_database()
