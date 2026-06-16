from flask import Flask, request
import hashlib
import base64
from Crypto.Cipher import AES
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

# 从环境变量读取（Render 里设置），或硬编码
TOKEN = os.environ.get("WECHAT_TOKEN", "KLNYoW5n82nvGses")
ENCODING_AES_KEY = os.environ.get("WECHAT_AES_KEY", "X2OWIThYpZgN9GFlzGGJajeCjpAjKHSy46wAhKexwo1")
CORP_ID = os.environ.get("WECHAT_CORP_ID", "你的企业ID")

def verify_signature(token, timestamp, nonce, msg_encrypt):
    """验证消息签名"""
    sort_list = sorted([token, timestamp, nonce, msg_encrypt])
    sha1 = hashlib.sha1()
    sha1.update("".join(sort_list).encode())
    return sha1.hexdigest()

def decrypt_aes(ciphertext, aes_key):
    """解密企业微信消息"""
    key = base64.b64decode(aes_key + "=")
    cipher = AES.new(key, AES.MODE_CBC, key[:16])
    decrypted = cipher.decrypt(base64.b64decode(ciphertext))
    pad_len = decrypted[-1]
    content = decrypted[:-pad_len]
    return content[16:].decode()

@app.route('/wechat', methods=['GET', 'POST'])
def wechat_callback():
    # === GET请求：URL验证 ===
    if request.method == 'GET':
        signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        
        if not all([signature, timestamp, nonce, echostr]):
            return "参数缺失", 400
        
        # 验证签名
        if verify_signature(TOKEN, timestamp, nonce, echostr) == signature:
            result = decrypt_aes(echostr, ENCODING_AES_KEY)
            return result
        return "签名验证失败", 403
    
    # === POST请求：接收消息/事件 ===
    elif request.method == 'POST':
        # 这里可以处理企业微信推送的消息
        # 解密、处理业务逻辑...
        return "success"

@app.route('/')
def home():
    return "WeChat Bot is running!"

if __name__ == '__main__':
    # Render 会提供 PORT 环境变量
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
