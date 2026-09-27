import sqlite3

db = sqlite3.connect("serpguard.db")

print("\nDATABASE TABLES")
print("=" * 40)

tables = db.execute(
    'SELECT name FROM sqlite_master WHERE type="table"'
).fetchall()

for table in tables:
    table_name = table[0]

    print(f"\nTable: {table_name}")
    print("-" * 40)

    columns = db.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    for column in columns:
        print(f"  {column[1]} | {column[2]}")

db.close()