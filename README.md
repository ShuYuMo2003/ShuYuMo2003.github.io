# 个人学术主页生成器

这是一个最小化的静态主页生成脚本。

页面样式已经固定在模板里，你只需要修改内容数据，然后重新生成 `index.html`。

## 文件说明

- `site_content.py`：主页内容数据，后续主要修改这个文件
- `generate_site.py`：生成脚本
- `templates/index.html.j2`：HTML 模板
- `index.html`：生成后的主页文件
- `environment.yml`：conda 环境配置

## 使用方法

### 1. 创建环境

```bash
conda env create -f environment.yml
conda activate academic_site_py312
```

### 2. 修改内容

编辑 `site_content.py`，按里面的类和示例数据填写你自己的信息，例如：

- 个人简介
- 新闻
- 论文
- 教育/经历
- 奖项

图片路径也在 `site_content.py` 里直接填写。

### 3. 生成网页

```bash
python generate_site.py
```

生成完成后，会更新根目录下的 `index.html`。

## 日常更新流程

```bash
conda activate academic_site_py312
python generate_site.py
```

如果只是改内容，通常只需要：

1. 修改 `site_content.py`
2. 运行 `python generate_site.py`