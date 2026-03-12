#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量透明边裁剪工具（独立版）
- 遍历同目录下 img/ 里所有 PNG，按非透明像素计算包围框，裁掉透明边
- 裁剪结果保存到 img_trimmed/，保持文件名一致
- 不导出任何元数据/相对位置，仅做图片切割
"""

from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("请先安装依赖: pip install Pillow numpy")
    raise SystemExit(1)

# 与常见逻辑一致：alpha 大于此值视为不透明
ALPHA_THRESHOLD = 10

# 脚本所在目录 = 工作目录
BASE = Path(__file__).resolve().parent
IMG_DIR = BASE / "img"
OUT_DIR = BASE / "img_trimmed"


def get_content_bbox(im):
    """根据 alpha 通道得到非透明区域的 (left, top, right, bottom)。"""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    a = np.array(im)[:, :, 3]
    rows = np.any(a > ALPHA_THRESHOLD, axis=1)
    cols = np.any(a > ALPHA_THRESHOLD, axis=0)
    if not np.any(rows) or not np.any(cols):
        return None
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return (int(cmin), int(rmin), int(cmax) + 1, int(rmax) + 1)


def trim_one(path: Path):
    """裁剪一张图，返回裁剪后的 PIL Image。"""
    im = Image.open(path).convert("RGBA")
    w0, h0 = im.size
    bbox = get_content_bbox(im)
    if not bbox:
        return im  # 全透明，不裁，直接返回原图
    left, top, right, bottom = bbox
    return im.crop((left, top, right, bottom))


def main():
    if not IMG_DIR.is_dir():
        print(f"找不到目录: {IMG_DIR}")
        print("请在本工具同目录下创建 img 文件夹，并放入要裁剪的 PNG 图片。")
        input("按回车键退出...")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(IMG_DIR.glob("*.png")) + sorted(IMG_DIR.glob("*.PNG"))
    seen = set()
    unique_paths = []
    for p in sorted(paths, key=lambda x: x.name.lower()):
        if p.name not in seen:
            seen.add(p.name)
            unique_paths.append(p)

    if not unique_paths:
        print(f"img 文件夹内没有 PNG 图片。")
        input("按回车键退出...")
        return

    ok = 0
    for path in unique_paths:
        name = path.name
        try:
            cropped = trim_one(path)
            out_path = OUT_DIR / name
            cropped.save(out_path, "PNG")
            ok += 1
            print(f"OK  {name} -> {cropped.size[0]}x{cropped.size[1]}")
        except Exception as e:
            print(f"SKIP  {name}: {e}")

    print(f"\n完成：共处理 {ok}/{len(unique_paths)} 张，结果在 {OUT_DIR}")
    input("按回车键退出...")


if __name__ == "__main__":
    main()
