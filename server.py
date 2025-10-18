from flask import Flask
import os

app = Flask(name)

@app.get("/")
def ok():
    # healthcheck для Railway
    return "OK"

if name == "main":
    # Railway сам передает порт через переменную PORT
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
