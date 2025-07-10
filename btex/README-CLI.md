# bTeX 命令行工具

bTeX 现在支持命令行模式，可以将 `.btx` 文件编译为 HTML 文件。

## 安装

```bash
# 安装依赖
npm install

# 编译项目
npm run build
```

## 使用方法

### 基本用法

```bash
# 编译单个文件
node dist/cli.js -i input.btx -o output.html

# 或者使用 npm 脚本
npm run cli -- -i input.btx -o output.html
```

### 全局安装（可选）

```bash
# 全局安装
npm install -g .

# 然后可以直接使用
btex -i input.btx -o output.html
```

### 命令行参数

- `-i, --input`: 输入的 btex 文件（必需）
- `-o, --output`: 输出的 HTML 文件（必需）
- `-p, --preamble`: 可选的 preamble 文件
- `--inline`: 启用内联模式
- `--equation-mode`: 启用公式模式
- `--inverse-search`: 启用反向搜索
- `--css`: 在输出中包含 KaTeX CSS（默认：true）
- `--title`: HTML 标题（默认：'bTeX Output'）
- `-h, --help`: 显示帮助信息
- `-v, --version`: 显示版本信息

### 示例

```bash
# 基本编译
node dist/cli.js -i test.btx -o test.html

# 使用 preamble
node dist/cli.js -i document.btx -p preamble.btx -o document.html

# 内联模式
node dist/cli.js -i inline.btx -o inline.html --inline

# 公式模式
node dist/cli.js -i equation.btx -o equation.html --equation-mode

# 不包含 CSS
node dist/cli.js -i content.btx -o content.html --css=false

# 自定义标题
node dist/cli.js -i report.btx -o report.html --title "我的报告"
```

### 测试

```bash
# 编译测试文件
node dist/cli.js -i test-cli.btx -o test-cli.html

# 查看结果
open test-cli.html  # macOS
xdg-open test-cli.html  # Linux
start test-cli.html  # Windows
```

## 错误处理

如果编译过程中出现错误，程序会：

1. 在控制台显示错误信息
2. 以非零退出码退出
3. 不会生成输出文件

## 警告

编译警告会显示在控制台，但不会阻止程序执行。

## 与服务器模式的区别

- **命令行模式**: 一次性编译，适合批量处理或集成到构建流程
- **服务器模式**: 持续运行，适合实时预览和开发

两种模式使用相同的编译引擎，输出结果一致。 