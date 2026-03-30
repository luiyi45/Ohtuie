import sys
file_path = 'app/api/v1/endpoints/admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('text("INTERVAL \'5 hours\'")', 'timedelta(hours=5)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print('Replaced!')
