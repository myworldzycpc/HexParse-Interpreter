# HexParse Interpreter

一个可以模拟执行 [HexParse](https://modrinth.com/mod/hexparse) 代码的解释器

## 运行方式

提供两种语言的实现：

### Web可视化版本 `index.html`

这是目前功能较完善的版本，支持步进、逐步运行、实时栈和变量查看、世界视图3D渲染等。

- 方式1：直接访问GitHub Pages: https://myworldzycpc.top/HexParse-Interpreter/
- 方式2：克隆项目，直接用浏览器打开index.html即可

### Python命令行版本 `main.py`

#### CLI 接口

```bash
# 启动 REPL（默认交互模式）
python main.py

# 运行单个脚本文件
python main.py script.hexparse

# 依次运行多个文件（共享同一个栈环境）
python main.py a.hex b.hex c.hex

# 直接执行命令字符串
python main.py -c "num_1 num_2 add print"

# 运行文件后进入交互模式
python main.py -i script.hexparse

# 安静模式（隐藏执行提示，仅显示错误和 print 输出）
python main.py -q script.hexparse
```

#### 参数说明

| 参数 | 说明 |
|------|------|
| `files` | 要运行的脚本文件（可多个，依次执行，共享栈） |
| `-c` / `--command` | 直接执行命令字符串 |
| `-i` / `--interactive` | 运行后进入 REPL 交互模式 |
| `-q` / `--quiet` | 安静模式，隐藏执行提示 |

## 命令列表

### 实体操作

| 命令 | 功能 | 入栈 | 出栈 |
|------|------|------|------|
| `get_caster` | 获取 caster 实体 | - | `Entity` |
| `entity_pos/eye` | 获取实体眼部坐标 | `Entity` | `Vector` |
| `entity_pos/foot` | 获取实体脚部坐标 | `Entity` | `Vector` |

### 栈操作

| 命令          | 功能 | 入栈 | 出栈             |
|-------------|------|------|----------------|
| `duplicate` | 复制栈顶元素 | `a` | `a, a`         |
| `swap`      | 交换栈顶两个元素 | `a, b` | `b, a`         |
| `over`      | 复制倒数第二个元素到栈顶 | `a, b` | `a, b, a`      |
| `mask_*`    | 选择性擦除栈顶元素 | 一个或多个元素               | 按掩码提取          |
| `stack_len` | 栈长度压栈| - | `float`        |
|  `2dup`     | 复制栈顶两个元素| `a, b`|  `a, b, a, b`  |

### 常量

| 命令 | 功能 | 入栈 | 出栈 |
|------|------|------|------|
| `const/true` | 布尔值 true | - | `true` |
| `const/false` | 布尔值 false | - | `false` |
| `const/double/pi` | 圆周率 π | - | `float` |
| `const/double/tau` | 双倍圆周率 τ (2π) | - | `float` |
| `num_*` | 数字字面量（如 `num_42`） | - | `float` |

### 数学运算

| 命令 | 功能 | 入栈 | 出栈 |
|------|------|------|------|
| `add` | 加法 / 向量加法 | `a, b` | `a + b` |
| `sub` | 减法 / 向量减法 | `a, b` | `a - b` |
| `mul_dot` | 乘法 / 点积 / 数乘 | `a, b` | `a * b` |
| `div_cross` | 除法 / 叉积 | `a, b` | `a / b` |
| `sin` | 正弦值（弧度制） | `float` | `float` |
| `cos` | 余弦值（弧度制） | `float` | `float` |
| `tan` | 正切值（弧度制） | `float` | `float` |
| `less` | 小于比较 | `a, b` | `boolean` |
| `greater` | 大于比较 | `a, b` | `boolean` |

### 向量操作

| 命令 | 功能        | 入栈                    | 出栈 |
|------|-----------|-----------------------|------|
| `construct_vec` | 构造三维向量    | `float, float, float` | `Vector` |

### 列表操作

| 命令                | 功能           | 入栈                 | 出栈               |
|-------------------|--------------|--------------------|------------------|
| `last_n_list`     | 栈顶 n 个元素组成列表 | `..., n`           | `list`           |
| `splat`           | 列表展开压栈       | `list`             | `...elements`    |
| `index`           | 按索引取元素       | `list, n`          | `element / NULL` |
| `slice`           | 列表切片         | `list, start, end` | `list`           |
| `append`          | 末尾追加元素       | `list, item`       | `new_list`       |
| `concat`          | 拼接两个列表       | `l1, l2`           | `new_list`       |
| `empty_list`      | 空列表          | -                  | `[]`             |
| `singleton`       | 单元素列表        | `item`             | `[item]`         |
| `list_size`       | 列表长度         | `list`             | `float`          |
| `reverse_list`    | 反转列表         | `list`             | `reversed`       |
| `index_of`        | 查找元素索引       | `list, item`       | `float` (-1未找到)   |
| `list_remove`     | 按索引删除        | `list, n`          | `new_list`       |
| `modify_in_place` | 按索引修改        | `list, n, item`    | `new_list`       |
| `construct`       | 头部添加元素       | `list, item`       | `[item, ...list]` |
| `deconstruct`     | 拆分头部和剩余      | `list`             | `rest, first`    |


### 局部变量

| 命令 | 功能 | 入栈 | 出栈 |
|------|------|------|------|
| `write/local` | 写入局部变量 | `value` | - |
| `read/local` | 读取局部变量 | - | `value` |

### 内省与元编程

| 命令 | 功能        | 入栈                      | 出栈     |
|------|-----------|-------------------------|--------|
| `(` | 开始收集命令列表  | -                       | -      |
| `)` | 结束收集并压入列表 | -                       | `list` |
| `eval` | 执行栈顶的命令列表 | `list \| Command`  | 执行结果   |
| `if` | 条件选择      | `cond, then, else`      | 结果     |
| `for_each` | 遍历列表执行命令  |	`commands, iterable` | 结果列表 |

### 世界操作

| 命令 | 功能 | 入栈       | 出栈 |
|------|------|----------|------|
| `place_block` | 在位置放置方块 | `Vector` | - |
| `break_block` | 移除位置的方块 | `Vector`    | - |

### 控制流

| 命令 | 功能 | 入栈 | 出栈 |
|------|------|------|------|
| `halt` | 暂停执行 | - | - |
| `print` | 打印栈顶元素（不弹出） | `value` | `value` |

## 辅助命令（斜杠命令）

| 命令             | 功能                   |
|----------------|----------------------|
| `/stack`       | 查看当前栈内容              |
| `/clear`       | 清空栈                  |
| `/clear_world` | 清空世界                 |
| `/local`       | 查看局部变量               |
| `/verbose`     | 开启详细模式（显示所有执行提示）     |
| `/quiet`       | 开启安静模式（仅显示错误和 print） |
| `/get_block`   | 获取指定位置的方块            |
| `/get_blocks`  | 列出所有已放置的方块           |

## 注释语法

```
// 这是单行注释

/* 这是多行注释
   可以跨越多行 */
```

## Verbose 模式

- **详细模式（默认）**：显示所有执行过程，包括 `push`、`pop`、`run_program>`、`eval>` 等提示
- **安静模式**：仅显示 Accident 错误、`print` 命令输出、斜杠命令输出

运行时可通过 `/verbose` 和 `/quiet` 随时切换。
