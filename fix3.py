import sys

file_path = 'app/api/v1/endpoints/admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace AuditLog group by
content = content.replace(
    '.group_by(cast(models.AuditLog.created_at - timedelta(hours=5), Date))\n        .order_by(cast(models.AuditLog.created_at - timedelta(hours=5), Date))',
    '.group_by(text("1"))\n        .order_by(text("1"))'
)

# Replace User group by
content = content.replace(
    '.group_by(cast(models.User.created_at - timedelta(hours=5), Date))\n        .order_by(cast(models.User.created_at - timedelta(hours=5), Date))',
    '.group_by(text("1"))\n        .order_by(text("1"))'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced all cast(Date) group_by to text('1')")
