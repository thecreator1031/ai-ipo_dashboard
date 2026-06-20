import sqlite3
import pandas as pd
import requests
import time

# 1. Database Initialization
def setup_database():
    """Creates the SQLite database and the core IPO table."""
    conn = sqlite3.connect('ipo_engine.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_gmp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ipo_name TEXT,
            price_band TEXT,
            gmp TEXT,
            est_listing TEXT,
            ipo_size TEXT,
            lot_size TEXT,
            open_date TEXT,
            close_date TEXT,
            boast_status TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

# 2. The Extraction Pipeline
def scrape_live_gmp():
    """Bypasses basic security and extracts the HTML table into a DataFrame."""
    url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    print("[*] Initiating secure connection to market data...")
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print("[+] Connection successful. Parsing financial tables...")
        # Pandas reads all HTML tables; the primary GMP table is usually index 0
        tables = pd.read_html(response.text)
        df = tables[0]
        
        # Clean column names to make them database-friendly
        df.columns = ['ipo_name', 'price_band', 'gmp', 'est_listing', 'ipo_size', 'lot_size', 'open_date', 'close_date', 'boast_status']
        
        # Drop the header row if it gets duplicated inside the data
        df = df[df['ipo_name'] != 'IPO'] 
        
        print(f"[+] Extracted {len(df)} active/upcoming IPO records.")
        return df
    else:
        print(f"[-] Blocked by server. HTTP Status: {response.status_code}")
        return None

# 3. Execution & Storage
if __name__ == "__main__":
    print("--- QUANT IPO ENGINE V1.0 ---")
    conn = setup_database()
    
    ipo_data = scrape_live_gmp()
    
    if ipo_data is not None:
        print("[*] Writing data to local SQLite database (ipo_engine.db)...")
        # Write the dataframe directly to SQL
        ipo_data.to_sql('live_gmp', conn, if_exists='append', index=False)
        print("[SUCCESS] Engine cycle complete. Data secured.")
    
    conn.close()
    