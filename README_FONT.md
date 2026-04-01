# T12焊台OLED中文精简字库生成工具

## 文件说明

### 1. 主要文件
- `generate_font.py` - Python字库生成脚本
- `chinese_chars.txt` - 汉字列表文件（可编辑）
- `README_FONT.md` - 本说明文件

### 2. 输出文件（运行后生成）
- `chinese_font.h` - C语言头文件，包含汉字点阵数据

## 所需汉字列表

当前`chinese_chars.txt`文件中包含的汉字（共73个）：

```
设 置 错 误 关 闭 休 眠 增 强 工 作 加 热 保 持 菜 单 焊 嘴 温 度 定 时 器 控 制 类 型 调 谐 语 言 蜂 鸣 返 回 更 换 校 准 重 命 名 删 除 添 加 新 激 进 保 守 直 接 大 数 字 多 信 息 否 是 存 储 确 认 分 钟 秒 警 告 你 不 能 的 最 后 已 达 最 大 数 量 步 骤 测 量 请 等 待 输 入 名 称 固 件 电 源
```

这些汉字覆盖了T12焊台固件的所有界面翻译需求。

## 使用步骤

### 步骤1：获取HZK16字库文件

HZK16是16×16点阵汉字字库文件，您可以从以下位置获取：

1. **Windows系统**：复制 `C:\Windows\Fonts\HZK16`（如果存在）
2. **Linux系统**：通常在 `/usr/share/fonts/chinese/HZK16`
3. **在线下载**：搜索"HZK16字库下载"
4. **备用方案**：使用其他点阵字库文件，如HZK12（12×12）

**最简单的方法**：将HZK16文件复制到当前目录（`/Users/liyong/Downloads/T12-SolderingStation/`）

### 步骤2：运行生成脚本

```bash
# 确保在项目目录中
cd /Users/liyong/Downloads/T12-SolderingStation/

# 运行Python脚本（需要Python 3）
python3 generate_font.py
```

或直接执行：
```bash
./generate_font.py
```

### 步骤3：检查输出

脚本运行成功后，将生成 `chinese_font.h` 文件，包含：
- 73个汉字的16×16点阵数据
- 汉字索引表（Unicode编码）
- 查找函数 `find_chinese_char(unicode)`

## 自定义汉字列表

如果需要修改汉字列表，编辑 `chinese_chars.txt` 文件：

1. 每行可以包含注释（以#开头）
2. 汉字可以用空格分隔或连续书写
3. 支持特殊字符如°（度符号）
4. 脚本会自动去重

示例：
```txt
# 添加新汉字
设 置 温 度 控 制
# 下一行
校准 测量 步骤
```

## 在Arduino项目中使用

### 1. 添加文件到项目
将生成的 `chinese_font.h` 复制到Arduino项目目录。

### 2. 包含头文件
在需要显示中文的代码文件中添加：
```cpp
#include "chinese_font.h"
```

### 3. 实现汉字显示函数
需要编写自定义函数来绘制汉字点阵：

```cpp
// 示例：绘制一个汉字
void drawChineseChar(uint8_t x, uint8_t y, uint16_t unicode) {
  const uint8_t* font_data = find_chinese_char(unicode);
  if (font_data) {
    // 16×16点阵，每行2字节，共32字节
    for (uint8_t row = 0; row < 16; row++) {
      uint8_t byte1 = pgm_read_byte(font_data + row * 2);
      uint8_t byte2 = pgm_read_byte(font_data + row * 2 + 1);
      
      // 绘制每个像素点
      for (uint8_t col = 0; col < 16; col++) {
        uint8_t pixel;
        if (col < 8) {
          pixel = byte1 & (0x80 >> col);
        } else {
          pixel = byte2 & (0x80 >> (col - 8));
        }
        
        if (pixel) {
          u8g.drawPixel(x + col, y + row);
        }
      }
    }
  }
}

// 示例：绘制中文字符串（UTF-8编码）
void drawChineseString(uint8_t x, uint8_t y, const char* str) {
  uint8_t currentX = x;
  
  while (*str) {
    // 判断是否为中文字符（UTF-8编码）
    if ((*str & 0xE0) == 0xE0) {  // 3字节UTF-8
      // 提取Unicode编码
      uint16_t unicode = ((str[0] & 0x0F) << 12) |
                        ((str[1] & 0x3F) << 6) |
                         (str[2] & 0x3F);
      
      drawChineseChar(currentX, y, unicode);
      currentX += 16;  // 汉字宽度
      str += 3;
    } else {  // 英文字符
      char eng_str[2] = {*str, '\0'};
      u8g.drawStr(currentX, y, eng_str);
      currentX += 6;  // 英文字符宽度
      str++;
    }
  }
}
```

### 4. 集成到多语言系统
结合之前的语言切换功能：

```cpp
// 根据当前语言选择字符串
const char* getString(StringID id) {
  if (currentLanguage == LANGUAGE_CHINESE) {
    return cn_strings[id];
  } else {
    return en_strings[id];
  }
}

// 绘制多语言字符串
void drawMultiLangStr(uint8_t x, uint8_t y, StringID id) {
  const char* str = getString(id);
  
  if (currentLanguage == LANGUAGE_CHINESE) {
    drawChineseString(x, y, str);
  } else {
    u8g.drawStr(x, y, str);
  }
}
```

## 点阵格式说明

生成的 `chinese_font.h` 使用以下格式：
- **尺寸**: 16×16像素
- **取模方式**: 纵向取模，字节倒序
- **字节排列**: 每行2字节（16像素），共32字节
- **存储方式**: PROGMEM（Flash存储）

## 常见问题

### Q1: 找不到HZK16文件怎么办？
A: 可以从以下网址下载：
   - https://github.com/soonuse/text-font-database/tree/master/fonts
   - 或搜索"HZK16字库下载"

### Q2: 汉字显示不完整或错位？
A: 检查点阵格式是否匹配显示函数。可能需要调整取模方式。

### Q3: 固件空间不足？
A: 考虑以下优化：
   - 使用12×12点阵（需修改脚本）
   - 减少汉字数量
   - 使用压缩算法

### Q4: 如何添加新汉字？
A: 编辑 `chinese_chars.txt`，添加所需汉字，重新运行脚本。

### Q5: 度符号(°)如何显示？
A: 度符号不是汉字，需要使用特殊处理或英文字体。

## 下一步工作

1. **实现显示函数**：在固件中添加汉字显示功能
2. **创建字符串资源表**：将中英文字符串分离到单独文件
3. **替换所有显示调用**：将 `u8g.drawStr()` 替换为多语言版本
4. **测试和优化**：确保显示效果和性能

## 联系与支持

如有问题，请参考代码注释或联系开发者。

---
*生成时间: 2026-04-01*  
*版本: v1.0*