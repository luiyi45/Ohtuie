import requests
import sys

# URL del endpoint de login
url = "http://127.0.0.1:8000/api/v1/login/access-token"

# Credenciales del admin
payload = {
    "username": "admin@ohtuie.com",
    "password": "admin"
}

try:
    print(f"Enviando petición POST a {url}...")
    response = requests.post(url, data=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 500:
        print("¡Error 500 reproducido!")
        print("Por favor revisa la terminal donde corre uvicorn para ver el traceback.")
    elif response.status_code == 200:
        print("¡Login exitoso!")
        print(response.json())
    else:
        print("Otro error ocurrió.")

except Exception as e:
    print(f"Error de conexión: {e}")
