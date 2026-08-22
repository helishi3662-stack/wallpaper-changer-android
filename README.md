# 壁纸切换器 - 安卓版（GitHub Actions 自动打包）

## 为什么会出现 "Build, test, and deploy..."？

因为你还没有上传 `.github/workflows/build.yml` 文件，或者文件位置不对。
GitHub 只有在仓库根目录检测到 `.github/workflows/` 里的 `.yml` 文件后，才会显示工作流。

---

## 正确上传步骤（图文版）

### 第1步：创建 GitHub 仓库

1. 打开 [github.com](https://github.com) 登录
2. 点击右上角 **"+" → New repository**
3. 仓库名填 `wallpaper-changer-android`
4. 选择 **Public**（公开仓库 Actions 完全免费）
5. 点击 **Create repository**

### 第2步：上传文件（关键！必须包含 .github 文件夹）

**方法：网页拖拽上传**

1. 在仓库页面点击 **"uploading an existing file"**
2. 把解压后的**所有文件和文件夹**拖进去，包括：

```
main.py
buildozer.spec
.github/
  └── workflows/
      └── build.yml
```

> ⚠️ **注意**：`.github` 是隐藏文件夹，确保你上传了它！

3. 在 "Commit changes" 框里写 `first commit`
4. 点击 **Commit changes**

### 第3步：验证工作流是否识别

上传成功后：
1. 刷新页面
2. 点击顶部 **Actions** 标签
3. 你应该看到左侧有 **"Build Android APK"**
4. 右侧显示正在运行 🟡（黄色）

如果还是看到 "Build, test, and deploy..."，说明 `.github/workflows/build.yml` 没上传成功，请检查文件路径。

---

## 打包进度

| 阶段 | 时间 | 说明 |
|------|------|------|
| 首次打包 | 15-25分钟 | 下载 Android SDK/NDK（约3GB） |
| 后续打包 | 5-10分钟 | 使用缓存，速度快 |

---

## 下载 APK

打包完成后：

**方式1：Artifacts（推荐）**
1. 点击完成的 Actions 记录
2. 页面最底部 **Artifacts**
3. 点击 **wallpaper-changer-apk** 下载 ZIP
4. 解压 ZIP 得到 `.apk`

**方式2：Releases**
1. 仓库右侧点击 **Releases**
2. 找到最新版本
3. 下载 APK

---

## 手机安装

1. 把 APK 传到手机
2. 文件管理器中点击安装
3. 安卓 10+ 需要额外授权：
   - 设置 → 应用 → 壁纸切换器 → 权限 → 允许"所有文件访问"

---

## 如果 Actions 运行失败

1. 点击失败的记录
2. 查看红色报错日志
3. 点击右上角 **"Re-run jobs"** 重试
4. 如果还是失败，把报错截图发给我
