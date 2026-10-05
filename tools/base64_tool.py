"""Base64 編碼 / 解碼工具。"""

import base64
import binascii

from flask import Blueprint, jsonify, render_template, request

bp = Blueprint("base64_tool", __name__, url_prefix="/tools/base64")


@bp.route("/", methods=["GET"])
def index():
    return render_template("base64.html")


@bp.route("/api/encode", methods=["POST"])
def api_encode():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    result = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return jsonify({"result": result})


@bp.route("/api/decode", methods=["POST"])
def api_decode():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    try:
        decoded_bytes = base64.b64decode(text, validate=True)
        result = decoded_bytes.decode("utf-8")
    except (binascii.Error, ValueError):
        return jsonify({"error": "無效的 Base64 字串"}), 400
    except UnicodeDecodeError:
        return jsonify({"error": "解碼結果不是有效的 UTF-8 文字"}), 400
    return jsonify({"result": result})
