# HexParse Interpreter

一个可以模拟执行 [HexParse](https://modrinth.com/mod/hexparse) 代码的解释器

## 目前支持的图案类型

### 基本图案

- `get_caster`： **意识之精思** ：获取施法者
- `entity_pos/eye`： **指南针之纯化** ：获取实体眼部坐标
- `entity_pos/foot`： **指南针之纯化（第二型）** ：获取实体脚部坐标
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

### 法术

- `break_block`
- `place_block`

## 辅助命令

- `/stack`
- `/clear`
- `/local`
- `/get_block`
- `/get_blocks`