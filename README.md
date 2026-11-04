# VilaxVPN 直连规则

当前网段：`172.18.5.0/24`，覆盖 `172.18.5.0` 至 `172.18.5.255`。

## 下载地址

- 首选 GitHub Pages：https://kkxiaoa.github.io/vilaxvpn-rules/direct-ip.srs
- CDN 备用：https://cdn.jsdelivr.net/gh/kkxiaoa/vilaxvpn-rules@rule-set/direct-ip.srs
- JSON 源文件：[direct-ip.json](direct-ip.json)

在 VilaxVPN 的自定义规则中添加 `.srs` 地址，动作选择 **直连**，关闭 **反选**，然后刷新规则并重新连接 VPN。

## 修改网段

1. [在 GitHub 网页编辑 direct-ip.json](https://github.com/kkxiaoa/vilaxvpn-rules/edit/main/direct-ip.json)。
2. 修改 `ip_cidr` 数组并提交到 `main`，例如添加 `192.168.10.0/24`。使用标准 CIDR 网络地址。
3. 等待 [Publish VPN rules](https://github.com/kkxiaoa/vilaxvpn-rules/actions/workflows/publish.yml) 显示成功。
4. 在客户端刷新规则。下载 URL 保持不变。

工作流会验证 CIDR、编译 SRS v1、反编译核对网段，再把结果发布到 GitHub Pages 和 `rule-set` 分支。编译失败时保留之前已发布的版本。请只修改 `main` 上的 JSON；`rule-set` 分支由工作流维护。

CDN 和客户端可能缓存旧版本。jsDelivr 官方说明分支 URL 缓存为 12 小时；频繁修改时优先使用 Pages，并在客户端刷新。能否直连仍以客户端所在网络的实际测试为准。

## 本地编译

安装 sing-box 后执行：

```sh
python3 scripts/build.py
```

也可通过 `SING_BOX=/path/to/sing-box` 指定编译器。输出位于 `dist/`。自动发布使用固定版本 sing-box 1.14.4，并校验官方发布文件的 SHA-256。

参考：[sing-box 规则集格式](https://sing-box.sagernet.org/configuration/rule-set/source-format/)、[GitHub Pages 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)、[jsDelivr 缓存说明](https://github.com/jsdelivr/jsdelivr#caching)。
