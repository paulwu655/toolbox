"""SAML / XML 解析工具。

貼上的內容可能是三種形態：
    1. 原始 XML（例如 acs_catcher.py 已經印出來的明文）
    2. Base64（POST binding 的 SAMLResponse 參數值）
    3. Base64 + raw-deflate（Redirect binding，常見於 SLO 的 LogoutRequest/Response）
依序嘗試解碼，不需要使用者自己指定來源格式。
"""

import base64
import binascii
import zlib
import xml.etree.ElementTree as ET

from flask import Blueprint, jsonify, render_template, request

bp = Blueprint("xml_tool", __name__, url_prefix="/tools/xml")


def _local(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def _text(elem):
    if elem is None:
        return None
    value = (elem.text or "").strip()
    return value or None


def _iter_all(root, name):
    return [e for e in root.iter() if _local(e.tag) == name]


def _first(root, name):
    for e in root.iter():
        if _local(e.tag) == name:
            return e
    return None


def decode_input(text):
    text = text.strip()
    if not text:
        raise ValueError("請先貼上內容")

    try:
        return ET.fromstring(text), "原始 XML"
    except ET.ParseError:
        pass

    try:
        decoded = base64.b64decode(text, validate=False)
    except (binascii.Error, ValueError):
        decoded = None

    if decoded is not None:
        try:
            return ET.fromstring(decoded.decode("utf-8")), "Base64 解碼"
        except (ET.ParseError, UnicodeDecodeError):
            pass

        try:
            inflated = zlib.decompress(decoded, -15)
            return ET.fromstring(inflated.decode("utf-8")), "Base64 + Deflate 解碼"
        except (zlib.error, ET.ParseError, UnicodeDecodeError):
            pass

    raise ValueError("無法解析：不是合法的 XML，也不是 Base64 / Base64+Deflate 編碼的 XML")


def build_summary(root):
    rows = []

    def add(label, value):
        if value:
            rows.append({"label": label, "value": value})

    add("訊息類型", _local(root.tag))
    add("ID", root.attrib.get("ID"))
    add("IssueInstant", root.attrib.get("IssueInstant"))
    add("Destination", root.attrib.get("Destination"))
    add("InResponseTo", root.attrib.get("InResponseTo"))

    issuer_el = next((c for c in root if _local(c.tag) == "Issuer"), None) or _first(root, "Issuer")
    add("Issuer", _text(issuer_el))

    status_code_el = _first(root, "StatusCode")
    if status_code_el is not None:
        value = status_code_el.attrib.get("Value", "")
        add("StatusCode", value.rsplit(":", 1)[-1] if value else None)
    add("StatusMessage", _text(_first(root, "StatusMessage")))

    nameid_el = _first(root, "NameID")
    if nameid_el is not None:
        fmt = nameid_el.attrib.get("Format", "")
        suffix = f"（{fmt.rsplit(':', 1)[-1]}）" if fmt else ""
        add("NameID", f"{_text(nameid_el) or ''}{suffix}")

    authn_stmt = _first(root, "AuthnStatement")
    session_indexes = []
    if authn_stmt is not None and authn_stmt.attrib.get("SessionIndex"):
        session_indexes.append(authn_stmt.attrib["SessionIndex"])
    session_indexes += [t for e in _iter_all(root, "SessionIndex") if (t := _text(e))]
    if session_indexes:
        add("SessionIndex", ", ".join(dict.fromkeys(session_indexes)))

    if authn_stmt is not None:
        add("AuthnInstant", authn_stmt.attrib.get("AuthnInstant"))
    add("AuthnContextClassRef", _text(_first(root, "AuthnContextClassRef")))

    conditions_el = _first(root, "Conditions")
    if conditions_el is not None:
        nb = conditions_el.attrib.get("NotBefore")
        noa = conditions_el.attrib.get("NotOnOrAfter")
        if nb or noa:
            add("有效期間", f"{nb or '?'} ~ {noa or '?'}")

    audiences = [t for e in _iter_all(root, "Audience") if (t := _text(e))]
    if audiences:
        add("Audience", ", ".join(audiences))

    attributes = []
    for attr_el in _iter_all(root, "Attribute"):
        name = attr_el.attrib.get("Name") or attr_el.attrib.get("FriendlyName") or "(未命名)"
        values = [t for v in attr_el if _local(v.tag) == "AttributeValue" and (t := _text(v))]
        attributes.append({"name": name, "values": values})

    return rows, attributes


def build_tree(elem):
    attrs = [{"name": _local(k), "value": v} for k, v in elem.attrib.items()]
    return {
        "tag": _local(elem.tag),
        "label_suffix": elem.attrib.get("Name"),
        "attrs": attrs,
        "text": _text(elem),
        "children": [build_tree(c) for c in elem],
    }


@bp.route("/", methods=["GET"])
def index():
    return render_template("xml_tool.html")


@bp.route("/api/parse", methods=["POST"])
def api_parse():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    try:
        root, decode_method = decode_input(text)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    summary, attributes = build_summary(root)
    tree = build_tree(root)
    return jsonify(
        {
            "decode_method": decode_method,
            "summary": summary,
            "attributes": attributes,
            "tree": tree,
        }
    )
