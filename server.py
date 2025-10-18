from flask import Flask
import os

app = Flask(name)

@app.get("/")
def ok():
    # Healthcheck для Railway
    return "OK"

if name == "main":
    # Railway передает порт в переменной PORT
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
