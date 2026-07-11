# HexParse Interpreter

一个可以模拟执行 [HexParse](https://modrinth.com/mod/hexparse) 代码的解释器

## 运行方式

提供两种语言的实现：

### Web可视化版本 `index.html`：

这是目前功能较完善的版本，支持步进、逐步运行、实时栈和变量查看、世界视图等。

- 方式1：直接访问GitHub Pages: https://github.com/myworldzycpc/HexParse-Interpreter
- 方式2：克隆项目，直接用浏览器打开index.html即可

### Python命令行版本 `main.py`：

运行文件可启动REPL，支持输入HexParse代码并执行。CLI接口正在开发中。

## 目前支持的图案类型

### 基本图案

- `get_caster`：获取 `caster`
- `entity_pos/eye`：获取实体眼部坐标
- `entity_pos/foot`：获取实体脚部坐标
- `print`
- `const/true`
- `const/false`
- `const/double/tau`
- `const/double/pi`
- `read/local`
- `write/local`
- `num_*`
- `mask_*`
- `add`
- `sub`
- `mul_dot`
- `div_cross`
- `duplicate`
- `over`
- `swap`
- `construct_vec`
- `less`
- `greater`
- `cos`
- `sin`
- `tan`
- `(`、`)`
- `if`
- `eval`
- `halt`

### 世界操作

- `break_block`
- `place_block`

## 辅助命令

- `/stack`
- `/clear`
- `/local`
- `/get_block`
- `/get_blocks`