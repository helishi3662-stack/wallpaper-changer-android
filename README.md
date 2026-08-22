# 壁纸切换器 - 安卓版（GitHub Actions 自动打包）

## 使用步骤（超简单，不用装任何环境）

### 第1步：创建 GitHub 仓库

1. 打开 [github.com](https://github.com)，登录你的账号
2. 点击右上角 **"+" → New repository**
3. 仓库名填 `wallpaper-changer-android`
4. 选择 **Public**（公开仓库免费使用 Actions）
5. 点击 **Create repository**

### 第2步：上传代码

**方法A：网页上传（最简单）**
1. 解压 `wallpaper_changer_android.zip`
2. 在 GitHub 仓库页面点击 **"uploading an existing file"**
3. 把解压后的所有文件拖进去：
   - `main.py`
   - `buildozer.spec`
   - `.github/workflows/build.yml`
4. 点击 **Commit changes**

**方法B：命令行上传**
```bash
# 解压 wallpaper_changer_android.zip
cd wallpaper_changer_android

git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/你的用户名/wallpaper-changer-android.git
git push -u origin main
```

### 第3步：等待自动打包

1. 进入仓库 → 点击顶部 **Actions** 标签
2. 你会看到 **"Build Android APK"** 正在运行（黄色圆圈）
3. 首次打包约 **15-25 分钟**（自动下载 Android SDK/NDK）
4. 打包完成后变成绿色 ✅

### 第4步：下载 APK

**方式1：Artifacts（每次提交都有）**
1. 点击完成的 Actions 记录
2. 页面底部 **Artifacts** 区域
3. 点击 **wallpaper-changer-apk** 下载 ZIP
4. 解压 ZIP 得到 `.apk` 文件

**方式2：Releases（更稳定）**
1. 仓库右侧点击 **Releases**
2. 找到最新版本（如 `v1`）
3. 下载 Assets 中的 APK 文件

---

## 后续更新代码

如果你修改了 `main.py` 或配置：

```bash
git add .
git commit -m "更新功能"
git push
```

推送后 Actions 会自动重新打包，新的 APK 会出现在 Releases 中。

---

## 常见问题

**Q: Actions 运行失败？**
A: 点击失败的记录 → 查看日志。通常是网络问题，点击 **Re-run jobs** 重试即可。

**Q: 打包时间太长？**
A: 首次打包需要下载 SDK/NDK（约3GB），后续会快很多（约5-10分钟），因为 GitHub 会缓存。

**Q: 如何手动触发打包？**
A: 进入 Actions → Build Android APK → 点击右侧 **Run workflow** 按钮。

**Q: 私有仓库能用吗？**
A: 可以，但 GitHub 对私有仓库的 Actions 有免费额度限制（每月2000分钟）。公开仓库完全免费。

---

## 功能说明

| 功能 | 说明 |
|------|------|
| 播放模式 | 随机播放 / 顺序播放 / 乱序播放 |
| 缩放模式 | 适应 / 拉伸 / 填充 / 居中 |
| 切换间隔 | 5秒 / 10秒 / 15秒 |
| 预缓存 | 5张图片 |
| 自动扫描 | 每2小时检测新图片 |
| 后台运行 | ⚠️ 安卓限制，建议保持前台或加入电池白名单 |
