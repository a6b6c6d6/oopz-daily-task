"""加密与签名原语（纯标准库实现，无第三方依赖）。

- rsa_oaep_encrypt: 登录时对密码做 RSA-OAEP(SHA-256) 加密。
- rsa_sign_sha256:  请求签名 RSA-PKCS1-v1.5-SHA256。
- oopz_sign:        生成 oopz-sign 请求签名头。
"""

import base64
import hashlib
import os

from . import keys


def mgf1(seed: bytes, length: int, hf=hashlib.sha256) -> bytes:
    """MGF1 掩码生成函数（OAEP 使用）。"""
    out, counter = b"", 0
    while len(out) < length:
        out += hf(seed + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:length]


def rsa_oaep_encrypt(msg: bytes) -> bytes:
    """RSA-OAEP(SHA-256) 加密，返回 256 字节密文。"""
    k = keys.RSA_KEY_BYTES
    hlen = hashlib.sha256().digest_size
    lhash = hashlib.sha256(b"").digest()
    ps = b"\x00" * (k - len(msg) - 2 * hlen - 2)
    db = lhash + ps + b"\x01" + msg

    seed = os.urandom(hlen)
    masked_db = bytes(a ^ b for a, b in zip(db, mgf1(seed, k - hlen - 1)))
    masked_seed = bytes(a ^ b for a, b in zip(seed, mgf1(masked_db, hlen)))
    em = b"\x00" + masked_seed + masked_db

    m = int.from_bytes(em, "big")
    c = pow(m, keys.PUB_E, keys.PUB_N)
    return c.to_bytes(k, "big")


def rsa_sign_sha256(data: bytes) -> bytes:
    """RSA-PKCS1-v1.5 签名（SHA-256），返回 256 字节签名。"""
    digest = hashlib.sha256(data).digest()
    prefix = bytes.fromhex("3031300d060960864801650304020105000420")
    digest_info = prefix + digest
    ps = b"\xff" * (keys.RSA_KEY_BYTES - len(digest_info) - 3)
    em = b"\x00\x01" + ps + b"\x00" + digest_info
    m = int.from_bytes(em, "big")
    s = pow(m, keys.RSA_D, keys.RSA_N)
    return s.to_bytes(keys.RSA_KEY_BYTES, "big")


def oopz_sign(path_with_query: str, body: str, timestamp_ms: str) -> str:
    """计算 oopz-sign 请求签名。

    oopz-sign = Base64( RSA-SHA256( UTF8( hex(MD5(path+query+body)) + 时间戳 ) ) )
    """
    md5hex = hashlib.md5((path_with_query + body).encode("utf-8")).hexdigest()
    payload = (md5hex + timestamp_ms).encode("utf-8")
    return base64.b64encode(rsa_sign_sha256(payload)).decode("ascii")


def encrypt_password(password: str) -> str:
    """登录用：返回密码的 RSA-OAEP 密文（Base64）。"""
    return base64.b64encode(rsa_oaep_encrypt(password.encode("utf-8"))).decode("ascii")
