# -*- coding: utf-8 -*-
"""
激活码生成器 — 开发者工具
用法：
    python generate_code.py          # 生成 1 个激活码
    python generate_code.py 10       # 批量生成 10 个激活码
    python generate_code.py 5 vip    # 生成 5 个，备注 "vip"
"""
import hashlib
import random
import string
import sys

# 必须与 oracle_engine.py 中的 _SECRET 和 _DIFFICULTY 一致
SECRET = "ZhenRenOracle2026@Secret#Key!"
DIFFICULTY = 4


def generate_one() -> str:
    """暴力搜索一个有效激活码（约 10-60 秒）"""
    attempts = 0
    while True:
        attempts += 1
        code = "ZR-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
        raw = (code + SECRET).encode()
        if hashlib.sha256(raw).hexdigest().startswith("0" * DIFFICULTY):
            return code, attempts


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    note = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"难度: {DIFFICULTY} 个零前缀 | 密钥: {SECRET[:8]}...")
    print(f"生成 {count} 个激活码...\n")

    codes = []
    for i in range(count):
        code, attempts = generate_one()
        codes.append(code)
        print(f"  [{i+1}] {code}  (尝试 {attempts} 次)")

    print(f"\n=== 生成完毕 ===")
    if note:
        print(f"备注: {note}")
    print(f"\n发给用户时复制以下内容：")
    print("-" * 30)
    print("贞人占卜 · 激活码\n")
    for c in codes:
        print(f"  {c}")
    print(f"\n使用方法：打开App → 输入激活码 → 永久解锁")
    print("-" * 30)

    # 验证
    print("\n自检：")
    for c in codes:
        from oracle_engine import check_activation_code
        ok = check_activation_code(c)
        print(f"  {c} -> {'[OK] valid' if ok else '[FAIL] invalid - check SECRET!'}")

    if note:
        with open(f"codes_{note}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(codes))
        print(f"\n已保存到 codes_{note}.txt")


if __name__ == "__main__":
    main()
