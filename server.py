from flask import Flask
import os

# имя приложения задаём строкой, чтобы не использовать name
app = Flask("server")

@app.get("/")
def ok():
    return "OK"

# запускаем сразу (без if name == "main")
port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
