# 视频截图工具 - 构建指南

支持 macOS (.app) 和 Windows (.exe)，通过 GitHub Actions 自动构建。

## 构建方式（推荐）

### 1. 创建 GitHub 仓库

在 GitHub 上新建一个空仓库（如 `videoscreenshottool`），不要勾选 README/gitignore。

### 2. 本地初始化 Git 并推送

```bash
cd VideoScreenshotTool
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/videoscreenshottool.git
git push -u origin main
```

### 3. 触发构建

推送后进入 GitHub 仓库页面 → **Actions** → 选择 **Build Installers** → 点击 **Run workflow**

等待 3~5 分钟后：

- **Windows**: 下载 `VideoScreenshotTool-win` → 解压 → 运行 `VideoFrameExtractor.exe`
- **macOS**: 下载 `VideoScreenshotTool-mac` → 双击 `.app` 即可

## 手动构建（仅限 macOS）

```bash
# 安装依赖
brew install tesseract-lang
pip3 install pyinstaller opencv-python pytesseract pillow tkinterdnd2

# 打包
python3 -m PyInstaller VideoFrameExtractor_mac.spec
```

## 依赖说明

| 组件 | 用途 |
|------|------|
| tesseract | OCR 引擎（英文+中文识别） |
| opencv-python | 视频帧读取 |
| pytesseract | Python 调用 tesseract |
| pillow | 图像处理 |
| tkinterdnd2 | macOS 拖拽上传支持 |

## Windows 系统依赖

构建前需安装 tesseract（workflow 中已自动处理）：

```powershell
choco install tesseract -y
```

## 功能

- 🎬 字幕出现时自动截图（pytesseract OCR 识别中文/英文）
- ⏱️ 固定时间间隔截图
- 📂 支持拖拽上传视频
- 📁 截图完成自动打开保存文件夹
- 🌗 亮/暗主题支持
