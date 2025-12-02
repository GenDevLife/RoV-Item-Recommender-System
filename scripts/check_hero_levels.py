import sqlite3

conn = sqlite3.connect('data/rov_data.db')
cursor = conn.cursor()

# Check available levels
cursor.execute('SELECT DISTINCT level FROM hero_scaling ORDER BY level')
levels = cursor.fetchall()
print('Available levels:', [l[0] for l in levels])

# Check Tachi's data
cursor.execute('''
    SELECT level, base_hp, base_atk, base_def 
    FROM hero_scaling 
    WHERE hero_id=(SELECT hero_id FROM heroes WHERE code_name='tachi') 
    LIMIT 5
''')
data = cursor.fetchall()
print('\nTachi stats:')
for d in data:
    print(f'Level {d[0]}: HP={d[1]}, ATK={d[2]}, DEF={d[3]}')

conn.close()
