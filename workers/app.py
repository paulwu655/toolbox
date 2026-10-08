"""工具集服務入口。

啟動方式：
    ./venv/bin/python app.py

預設監聽 0.0.0.0:64102，可用環境變數 TOOL_PORT / TOOL_HOST 覆寫。
"""

import os

from flask import Flask

from tools import TOOLS

app = Flask(__name__)

for tool in TOOLS:
    app.register_blueprint(tool["blueprint"])

# 部署 Pages 後，把這裡換成實際網域（見 GitHub issue #7）
ALLOWED_ORIGIN = "https://toolbox-pages.stormyelbow.workers.dev"


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


if __name__ == "__main__":
    host = os.environ.get("TOOL_HOST", "0.0.0.0")
    port = int(os.environ.get("TOOL_PORT", "64102"))
    app.run(host=host, port=port, debug=True)
