import re

content = open('main.py', 'r', encoding='utf-8').read()
base = 'https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_'

for i in range(1, 71):
    content = re.sub(
        r'("id":\s*' + str(i) + r'[^}]*?)"image":\s*"[^"]*"',
        r'\1"image": "' + base + str(i) + '.jpg"',
        content,
        flags=re.DOTALL
    )

open('main.py', 'w', encoding='utf-8').write(content)
print('Done! main.py updated with Cloudinary URLs!')