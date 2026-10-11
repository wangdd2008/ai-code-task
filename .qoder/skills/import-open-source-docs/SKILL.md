---
name: import-open-source-docs
description: 自动解压开源项目压缩包，提取 docs 文档内容，按版本号归档到对应版本目录。当用户需要引入新的开源项目文档或更新现有项目文档时触发。
---

# Import Open Source Docs

自动处理开源项目压缩包，保留 docs 内容并按版本归档。

## 触发条件

- 用户提到"引入开源项目文档"
- 用户上传了 `.zip` 压缩包到 `002-open-source-docs/` 目录
- 用户说"更新某个项目的文档"
- 用户在 `002-open-source-docs/` 目录下新增压缩包文件

## 标准流程

### 1. 扫描待处理压缩包

扫描 `src/002-open-source-docs/` 及各项目子目录中的 `.zip` 文件。

```powershell
Get-ChildItem -Path "src/002-open-source-docs" -Recurse -Filter "*.zip"
```

### 2. 确定项目归属

根据压缩包名称或所在目录判断属于哪个项目：
- 如果在 `src/002-open-source-docs/` 根目录，根据文件名前缀匹配项目目录
- 如果在某个项目子目录下，直接在该项目下处理

### 3. 解压压缩包

解压到临时目录：
```powershell
Expand-Archive -Path "<zip-path>" -DestinationPath "<temp-dir>" -Force
```

### 4. 提取版本号

按优先级查找版本信息：
1. **`package.json`** 中的 `"version"` 字段
2. **`CHANGELOG.md`** 第一行或 `# Changelog` 后的第一个版本号
3. **压缩包文件名**中的版本标识（如 `project-v1.2.3.zip`）
4. 如果都查不到，使用当前日期作为版本号（格式 `YYYY-MM-DD`）

### 5. 定位 docs 目录

在解压后的目录中递归查找 `docs/` 目录。常见路径：
- `<repo>/docs/`
- `<repo>/<sub-project>/docs/`

如果找到多个 `docs/`，优先选择最顶层的那个。

### 6. 创建版本目录并迁移内容

```
src/002-open-source-docs/
├── <project-name>/
│   ├── v<x.x.x>/          ← 版本目录
│   │   └── ...docs 内容
│   └── v<y.y.y>/          ← 其他版本
```

操作步骤：
1. 创建版本目录：`<project-name>/v<version>/`
2. 将 `docs/` 下的**所有内容**移入版本目录
3. 如果版本目录已存在，提示用户是否覆盖或选择其他版本号

### 7. 清理临时文件

```powershell
# 删除压缩包
Remove-Item -Path "<zip-path>" -Force

# 删除临时解压目录
Remove-Item -Recurse -Path "<temp-dir>" -Force
```

### 8. 验证结果

确认最终目录结构：
```
src/002-open-source-docs/
├── <project-name>/
│   └── v<version>/
│       └── ...docs 文件和目录
```

## 版本号处理规则

- 标准语义化版本：`v1.2.3`
- 如果不以 `v` 开头，自动添加 `v` 前缀
- 如果版本号重复，提示用户确认（覆盖 / 重命名 / 取消）

## 示例

**场景**：用户上传了 `Fission-AI-OpenSpec-v1.14.0.zip`

```
1. 解压到临时目录
2. 读取 package.json → "version": "1.14.0"
3. 找到 docs/ 目录
4. 创建 Fission-AI-OpenSpec/v1.14.0/
5. 将 docs/ 内容移入 v1.14.0/
6. 删除压缩包和临时目录
```

最终结构：
```
src/002-open-source-docs/
├── Fission-AI-OpenSpec/
│   ├── v1.13.2/
│   └── v1.14.0/          ← 新增
└── mattpocock-skills/
    └── v1.3.1/
```

## 注意事项

- 只保留 `docs/` 目录的内容，其他源码、配置文件等不保留
- 确保压缩包和临时目录完全清理，不留残余
- 版本号提取失败时，用日期 `YYYY-MM-DD` 兜底，并告知用户
