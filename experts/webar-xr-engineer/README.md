# WebAR XR Engineer

把手机扫图出 3D 和卡牌识别做成能上线的产品。

## 类型

Agent 型（单个 AI 专家）

## 功能

- 路线选型：MindAR 图像识别 / OpenXR 标记追踪 / WebXR 空间锚定的边界划分
- 绕开 `node-canvas` 编译 `.mind`，删掉整个原生工具链
- 编译期打印特征点数，把「这图能不能用」变成 <100 / 100–300 / ≥300 三档
- 参数调优：`maxTrack`、`missTolerance`、`autoStart` 的默认值与实测值差异
- 合成 Y4M 假摄像头 + 状态回报端点，做无头端到端验证
- Godot 侧：初始化时序、`OpenXRMarkerTracker`、AruCo 字典按名字对齐、headless 编译校验

## 使用示例

- 我要做一个手机扫一扫出模型的活动页，帮我选技术路线并给出可落地的方案
- 这张目标图能扫得出来吗？帮我量特征点数并给出改图建议
- Godot 里 OpenXR 标记追踪起不来，报 Cannot call non-static function，怎么查

## 头像

头像已自动生成在 `avatars/` 目录下。替换要求：PNG 或 JPG，512×512，≤500KB。
