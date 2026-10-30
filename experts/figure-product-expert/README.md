# Figure Product Expert

把角色创意做成能量产的手办：三段翻译模型、24 任务 4 闸门、拆件分模与壁厚的量化红线。

## 类型

Agent 型（单个 AI 专家）

## 功能

- 三段翻译模型：2D→3D→零件集→货架，定位问题出在哪一次翻译
- 24 任务 / 4 闸门工作流，交付 5 份可填模板（Brief、仕様書、拆件工程表、打样验收单、QC 抽检表）
- 量化红线：壁厚 2.5–4mm、拔模角 1–3°、配合间隙 0.25–0.3mm、色块 ≤4
- `gate_check.py` 过闸脚本、`new_project.py` 项目脚手架
- 缺陷回滚诊断：脸崩 / 站不住 / 接缝穿脸 / 装不上 / 色差

## 使用示例

- 帮我把这个角色设计成一款能量产的手办，先判断现在卡在哪个闸门
- 评审一下这份拆件与分模方案，看有没有不能出模或壁厚超标的地方
- 诊断一下：样品脸崩、站不住、接缝穿脸，该回滚到哪一步

## 头像

头像已自动生成在 `avatars/` 目录下。替换要求：PNG 或 JPG，512×512，≤500KB。

## 安装

```
~/.workbuddy/plugins/marketplaces/my-experts/plugins/figure-product-expert/
```

## 打包分享

```bash
python3 <expert-manager>/scripts/package_expert.py <expert-dir>
```
