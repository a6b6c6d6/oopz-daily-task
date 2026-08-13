"""oopz 前端硬编码的密钥常量。

说明：以下密钥均硬编码在 web.oopz.cn 的公开前端 JS（main.dart.js）中，
由所有客户端共用，任何人加载页面即可提取，因此**不属于个人机密**。
真正的隐私信息（手机号、密码）在 config.py 中从环境变量读取。
"""

import base64

# 密码加密公钥（RSA-OAEP-256）。用于登录时加密密码，服务端用对应私钥解密。
# JWK: {kty:"RSA", n:<PUB_N_B64URL>, e:"AQAB", alg:"RSA-OAEP-256"}
PUB_N_B64URL = (
    "wf935Evk12yBMDq5u-2WGXG7rI80-WTu5BQXVnMm2HRZWKmOEdjW5XG4WhsbidDF2hhxO4emVqRlEE-EAZ8Ro936fk-oDvuYcLGbe_AUhgkb_uCldl32inF7dYXuONb-eigNSlGjapv8Ef__rFi0srg1dJg7_j8IQBm2RC5Hgd98-7QKokpjZHQmi-WpYAyaW7rZk1s6Ac6vZiAAq8HEa-eaEFTeQBcxrgYMwL65FfNFomh3Xvd1tMMtTx-dp4dfARfJB8UHhC8_xsUlHp14KYg4YRq9eRelnM_pV1ZXEAjPCbl6hwEsGrxWz40m-OeVsEZy-XGcoeeZfZ5dbTsicQ"
)
PUB_N = int.from_bytes(base64.urlsafe_b64decode(PUB_N_B64URL + "=="), "big")
PUB_E = 65537

# 请求签名私钥（RSA-PKCS1-v1.5-SHA256）。用于计算 oopz-sign 请求签名头。
# 同样硬编码在前端，全网共用，非个人机密。
RSA_N = int(
    "bf75b4b1d246a03d19a105d684c45ecf3d3af8084734c0d13fa594178d9c0822"
    "2686aee2a0c387cf4bfb2d78d64b98ba3fdb6ddc51c5b5ed5cdafe186f858f5b"
    "c8fe2ca6af5a1067548c36071f20729e55184dd91b7189b621e0909d0f7db993"
    "8fbcbfd9e9b2485545df0a9d88fbc873b252bb6888cd81fd7961f1d7762e8c3e"
    "273eea5142624dfc44af8e29796ae236711ef3388a057125c0b053e74fd43d18"
    "f43fe77b85888a3488cfd1d3c7d00d73761e47873137df25a28f73735d5c47ae"
    "fb9a2764dd9e909f406c1de438f30b73f25d4b81850589a40a512ecb6ed6e47d"
    "83870430d1322e074314d99b1877e7b8da7813517a9e058a3d9d52ab64735951",
    16,
)
RSA_D = int(
    "51012c0250453166a88148470ac54a97c4003f10c18fc044c7f8f63f40dad3561"
    "f96bc47865d3408b0cd04e02b4ab0c39c60ea8a5cce99ba639f0402b2ac7f8b05"
    "ef045541bb89552ea063fb7f5feb1eb242262dc53eb4552ae0284f4b4e9645a87"
    "ae370ff3f3efb552499092dfbd9439a1f06cba395cf79bef181b0f77f9a35b62c"
    "f734faa60632f4aec9242e0a6b32e631c0f732e7e9336002e0ba7438637c3f28b"
    "cd90f52dec1427e8bcaf063f99bb7998cd54833ba699732ccf7b885a9309c51d0"
    "fc10e980bbaff8928a1e174a6c972c817fb4d285460d386a8af2aa63b322c9020"
    "e12f3bf0192154d52325f061fb186548389e8821a4ea2ad801098bf41",
    16,
)
RSA_KEY_BYTES = 256
