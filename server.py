from flask import Flask
import os

app = Flask(name)

@app.get("/")
def ok():
    return "OK"

if name == "main":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
