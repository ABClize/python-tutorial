# Maple Mono Web 字体

教程站点使用本地托管的 Maple Mono CN 网页字体，避免依赖访客设备是否安装字体，也不依赖外部
CDN。

## 字体来源

- 上游项目：<https://github.com/subframe7536/maple-font>
- 上游版本：`v7.9`
- 原始压缩包：`MapleMono-CN.zip`
- 原始压缩包 SHA-256：
  `cb1e79b2c23dff772ae351784ef2b84454a61b3920e9b20bd5db4bf207e4472d`
- 选用源文件：`MapleMono-CN-Regular.ttf`
- 网页字体族名：`Maple Mono Web`

使用 `cn-font-split 7.4.3` 将 Regular 字重拆分为 WOFF2，并保留 OpenType
特性。分片目标大小为 256 KiB，浏览器根据 `unicode-range` 只下载当前页面需要的字符片段。

教程代码不使用 Nerd Font 图标，因此没有打包完整 NF-CN 字形集。英文、中文、日文和常见代码
符号由 Maple Mono CN 提供；未覆盖字符继续使用主题配置中的回退字体。

## 授权

Maple Mono 使用 SIL Open Font License 1.1。完整版权声明和授权条款见同目录的
`LICENSE.txt`。
