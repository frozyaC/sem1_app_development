"""Скрипт для проверки таблицы order_reports в БД"""
import sqlite3

conn = sqlite3.connect('mydb.sqlite3')
cursor = conn.cursor()

# Список всех таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Таблицы в БД:")
for table in tables:
    print(f"  - {table}")

# Проверяем наличие order_reports
if 'order_reports' in tables:
    print("\n✓ Таблица order_reports существует")
    
    # Структура таблицы
    cursor.execute("PRAGMA table_info(order_reports)")
    columns = cursor.fetchall()
    print("\nСтруктура таблицы order_reports:")
    for col in columns:
        print(f"  {col[1]:20} {col[2]:10} nullable={not col[3]}")
    
    # Внешние ключи
    cursor.execute("PRAGMA foreign_key_list(order_reports)")
    fkeys = cursor.fetchall()
    if fkeys:
        print("\nВнешние ключи:")
        for fk in fkeys:
            print(f"  {fk[3]} -> {fk[2]}.{fk[4]}")
    
    # Проверяем количество записей
    cursor.execute("SELECT COUNT(*) FROM order_reports")
    count = cursor.fetchone()[0]
    print(f"\nКоличество записей в таблице: {count}")
else:
    print("\n✗ Таблица order_reports НЕ существует!")

conn.close()
