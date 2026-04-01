#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T12焊台OLED显示中文精简字库生成工具
从HZK16字库提取所需汉字的点阵数据，生成C语言头文件
"""

import os
import sys
import struct

# 默认汉字列表（如果未提供文件）
DEFAULT_CHINESE_CHARS = (
    # 主屏幕状态和基本文字
    "设 置 错 误 关 闭 休 眠 增 强 工 作 加 热 保 持 "
    # 菜单相关
    "菜 单 焊 嘴 温 度 定 时 器 控 制 类 型 调 谐 语 言 蜂 鸣 返 回 "
    # 焊嘴操作
    "更 换 校 准 重 命 名 删 除 添 加 新 "
    # PID调谐
    "激 进 保 守 "
    # 其他选项
    "直 接 大 数 字 多 信 息 否 是 存 储 确 认 "
    # 时间和单位
    "分 钟 秒 "
    # 警告消息
    "警 告 你 不 能 的 最 后 已 达 最 大 数 量 "
    # 校准和输入
    "步 骤 测 量 请 等 待 输 入 名 称 "
    # 信息屏幕
    "固 件 电 源"
)

# 从文件读取汉字列表
def load_chars_from_file(filename="chinese_chars.txt"):
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在，使用默认汉字列表")
        return DEFAULT_CHINESE_CHARS

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有汉字（中文字符的Unicode范围）
        chars = []
        for char in content:
            # 判断是否为中文字符（基本范围）
            if '\u4e00' <= char <= '\u9fff' or char == '°':
                chars.append(char)

        if not chars:
            print(f"文件 {filename} 中未找到汉字，使用默认列表")
            return DEFAULT_CHINESE_CHARS

        # 转换为空格分隔的字符串
        chars_str = ' '.join(chars)
        print(f"从文件 {filename} 读取到 {len(chars)} 个汉字")
        return chars_str

    except Exception as e:
        print(f"读取文件 {filename} 失败: {e}，使用默认列表")
        return DEFAULT_CHINESE_CHARS

# 转换为无空格字符串并去重
def get_unique_chars(chars_str):
    # 移除空格并去重，保持顺序
    seen = set()
    unique_chars = []
    for char in chars_str:
        if char != ' ' and char not in seen:
            seen.add(char)
            unique_chars.append(char)
    return ''.join(unique_chars)

# 汉字转GB2312编码
def char_to_gb2312(char):
    try:
        # 获取GB2312编码（2字节）
        gb_bytes = char.encode('gb2312')
        if len(gb_bytes) != 2:
            return None
        return gb_bytes
    except:
        return None

# 从HZK16读取汉字点阵
def read_char_from_hzk16(hzk_file, gb_bytes, font_size=16):
    if len(gb_bytes) != 2:
        return None

    # 计算HZK16中的位置
    # 区码 = byte1 - 0xA1，位码 = byte2 - 0xA1
    zone = gb_bytes[0] - 0xA1
    pos = gb_bytes[1] - 0xA1

    # 每个汉字点阵大小：16x16 = 256 bits = 32 bytes
    char_size = 32  # 16x16点阵
    offset = (zone * 94 + pos) * char_size

    try:
        hzk_file.seek(offset)
        data = hzk_file.read(char_size)
        if len(data) != char_size:
            return None
        return data
    except:
        return None

# 生成C语言头文件
def generate_header_file(chars, font_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("/*\n")
        f.write(" * T12焊台OLED中文精简字库\n")
        f.write(" * 生成时间: 2026-04-01\n")
        f.write(" * 包含汉字: {}个\n".format(len(chars)))
        f.write(" * 点阵格式: 16x16，纵向取模，字节倒序\n")
        f.write(" */\n\n")

        f.write("#ifndef CHINESE_FONT_H\n")
        f.write("#define CHINESE_FONT_H\n\n")

        f.write("#include <stdint.h>\n\n")

        f.write("// 字库信息\n")
        f.write("#define FONT_WIDTH 16\n")
        f.write("#define FONT_HEIGHT 16\n")
        f.write("#define FONT_CHAR_SIZE 32  // 16x16/8 = 32 bytes\n")
        f.write("#define FONT_CHAR_COUNT {}\n\n".format(len(chars)))

        f.write("// 汉字点阵数据\n")
        f.write("const uint8_t chinese_font_data[{}][{}] PROGMEM = {{\n".format(
            len(chars), 32))

        for i, (char, data) in enumerate(zip(chars, font_data)):
            if data:
                f.write("  {{  // {} (索引:{}) {:#04x} {:#04x}\n".format(
                    char, i, ord(char) >> 8, ord(char) & 0xFF))

                # 每行显示8字节
                for row in range(16):  # 16行
                    start = row * 2    # 每行2字节
                    end = start + 2
                    row_bytes = data[start:end]
                    hex_str = ', '.join(['0x{:02x}'.format(b) for b in row_bytes])
                    f.write("    {}, ".format(hex_str))

                    # 在右侧显示点阵预览（可选）
                    preview = ''
                    for byte in row_bytes:
                        for bit in range(8):
                            preview += '█' if byte & (0x80 >> bit) else ' '
                    f.write("// {}\n".format(preview))

                f.write("  }")
                if i < len(chars) - 1:
                    f.write(",\n\n")
                else:
                    f.write("\n")

        f.write("};\n\n")

        f.write("// 汉字Unicode编码索引表\n")
        f.write("const uint16_t chinese_font_index[{}] PROGMEM = {{\n".format(len(chars)))
        f.write("  ")
        for i, char in enumerate(chars):
            f.write("0x{:04x}".format(ord(char)))
            if i < len(chars) - 1:
                f.write(", ")
                if (i + 1) % 8 == 0:
                    f.write("\n  ")
        f.write("\n};\n\n")

        f.write("// 查找汉字点阵数据\n")
        f.write("const uint8_t* find_chinese_char(uint16_t unicode) {\n")
        f.write("  for (uint16_t i = 0; i < FONT_CHAR_COUNT; i++) {\n")
        f.write("    if (pgm_read_word(&chinese_font_index[i]) == unicode) {\n")
        f.write("      return chinese_font_data[i];\n")
        f.write("    }\n")
        f.write("  }\n")
        f.write("  return NULL;  // 未找到\n")
        f.write("}\n\n")

        f.write("#endif // CHINESE_FONT_H\n")

        print("生成头文件: {}".format(output_file))
        print("包含汉字: {}".format(''.join(chars)))
        print("汉字数量: {}".format(len(chars)))

def main():
    # 加载汉字列表（从文件或默认）
    chars_str = load_chars_from_file("chinese_chars.txt")

    # 获取去重后的汉字
    chars = get_unique_chars(chars_str)
    print("需要生成的汉字: {}".format(chars))
    print("汉字数量: {}".format(len(chars)))

    # HZK16文件路径（常见位置）
    hzk_paths = [
        'HZK16',
        'hzk16',
        '/usr/share/fonts/chinese/HZK16',
        'C:/Windows/Fonts/HZK16',
        './HZK16'
    ]

    hzk_file = None
    hzk_path = None

    # 查找HZK16文件
    for path in hzk_paths:
        if os.path.exists(path):
            hzk_path = path
            break

    if not hzk_path:
        print("错误: 未找到HZK16字库文件")
        print("请将HZK16文件放置在以下位置之一:")
        for path in hzk_paths:
            print("  - {}".format(path))
        print("\n您可以从以下位置获取HZK16文件:")
        print("1. 网上搜索下载HZK16字库")
        print("2. 从Windows系统目录C:/Windows/Fonts/复制")
        print("3. 从Linux系统/usr/share/fonts/chinese/目录复制")
        return 1

    print("找到HZK16字库: {}".format(hzk_path))

    # 读取HZK16并提取点阵
    font_data = []
    missing_chars = []

    try:
        with open(hzk_path, 'rb') as f:
            for char in chars:
                gb_bytes = char_to_gb2312(char)
                if not gb_bytes:
                    print("警告: 汉字'{}'无法转换为GB2312编码".format(char))
                    missing_chars.append(char)
                    font_data.append(None)
                    continue

                data = read_char_from_hzk16(f, gb_bytes)
                if not data:
                    print("警告: 汉字'{}'在HZK16中未找到".format(char))
                    missing_chars.append(char)
                    font_data.append(None)
                    continue

                font_data.append(data)
                print("提取: {} (GB:{:02X}{:02X})".format(char, gb_bytes[0], gb_bytes[1]))

    except Exception as e:
        print("读取HZK16文件失败: {}".format(e))
        return 1

    # 检查是否所有汉字都成功提取
    success_count = len([d for d in font_data if d is not None])
    print("\n提取结果: {}/{} 个汉字成功".format(success_count, len(chars)))

    if missing_chars:
        print("缺失的汉字: {}".format(''.join(missing_chars)))
        print("这些汉字可能不在GB2312字符集中，或者HZK16字库不完整")

    if success_count == 0:
        print("错误: 未能提取任何汉字点阵")
        return 1

    # 生成头文件
    output_file = "chinese_font.h"
    generate_header_file(chars, font_data, output_file)

    # 生成使用说明
    print("\n" + "="*60)
    print("使用说明:")
    print("1. 将生成的 chinese_font.h 添加到Arduino项目中")
    print("2. 在代码中包含头文件: #include \"chinese_font.h\"")
    print("3. 使用 find_chinese_char(unicode) 函数获取汉字点阵")
    print("4. 需要实现自定义显示函数来绘制汉字")
    print("\n示例代码:")
    print("  const uint8_t* font_data = find_chinese_char(0x8BBE); // '设'")
    print("  if (font_data) {")
    print("    // 使用点阵数据绘制汉字")
    print("  }")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())