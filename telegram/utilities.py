import requests
x = requests.get('http://localhost:80/stats/ilVincio')
print(x.json())

x = ''

print(f'ciao {x}')