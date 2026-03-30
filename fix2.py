import sys

file_path = 'app/api/v1/endpoints/admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace import line to include cast and Date
content = content.replace(
    'from sqlalchemy import select, func, desc, text, String',
    'from sqlalchemy import select, func, desc, text, String, cast, Date'
)

# Replace func.date with cast(..., Date)
content = content.replace(
    'func.date(models.AuditLog.created_at - timedelta(hours=5))',
    'cast(models.AuditLog.created_at - timedelta(hours=5), Date)'
)

content = content.replace(
    'func.date(models.User.created_at - timedelta(hours=5))',
    'cast(models.User.created_at - timedelta(hours=5), Date)'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
    
print('Replaced func.date with cast(..., Date)!')
