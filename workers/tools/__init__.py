"""工具集注册中心。

每新增一個工具：
1. 在 tools/ 下新建一個模組（例如 base64_tool.py），內含一個 Flask Blueprint。
2. 在下面的 TOOLS 清單中註冊 name / slug / description / blueprint。
app.py 會自動把所有工具的 blueprint 註冊進主程式，並在首頁列出。
"""

from .base64_tool import bp as base64_bp
from .xml_tool import bp as xml_bp

TOOLS = [
    {
        "slug": "base64",
        "name": "Base64 編碼 / 解碼",
        "description": '將文字轉換為 <span class="kw">Base64</span>，或將 <span class="kw">Base64</span> 還原成文字。',
        "blueprint": base64_bp,
    },
    {
        "slug": "xml",
        "name": "SAML / XML 解析",
        "description": '貼上 <span class="kw">SAML Response</span> 或 <span class="kw">XML</span>，自動判斷 Base64／Deflate 編碼並整理成欄位摘要與可展開樹狀結構。',
        "blueprint": xml_bp,
    },
]
