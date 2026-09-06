# 微信派风格推文工坊

根据运营材料生成借鉴微信派表达方法的原创公众号内容，保留自己的品牌身份和真实事实。

## 包含什么

- 6 个候选标题、推荐标题和摘要。
- 两套封面方向；运行环境有图像能力时，生成推荐方向的原创封面。
- 完整正文、HTML 排版初稿、事实核对与待补项。
- 基于真实阅读数据的分组排序和逐篇复盘流程。

## 文件导航

| 文件 | 用途 |
| --- | --- |
| [weixinpai-editor/SKILL.md](weixinpai-editor/SKILL.md) | Skill 入口与完整工作流程 |
| [编辑规则](weixinpai-editor/references/editorial.md) | 选题、标题、正文与不同内容类型 |
| [封面与排版](weixinpai-editor/references/visual.md) | 视觉方案、排版规则及 HTML 输入格式 |
| [样本证据](weixinpai-editor/references/evidence.md) | 研究来源、逐篇分析和适用边界 |
| [数据复盘规则](weixinpai-editor/references/analytics.md) | 阅读数据格式、比较口径和分析方法 |
| [研究报告](weixinpai-research.md) | 研究结论、运营调用模板与验证记录 |

## 使用方式

在支持 Skill 的助手中加载完整的 `weixinpai-editor` 文件夹，保留其子目录。具体安装方式取决于所用工具。

调用 `weixinpai-editor`，附上原始材料、品牌、目标读者和希望读者完成的动作。已有品牌色、图片和必须保留的数字、时间、资格限制也可一并提供。完整调用模板见研究报告。

这是一套初稿生成的工作流程，只负责数据整理和排版

## 两个辅助脚本

使用 Python 3，无需额外第三方依赖。

```bash
python3 weixinpai-editor/scripts/render_article.py article.json article.html
python3 weixinpai-editor/scripts/rank_articles.py records.json ranked.json
```

输入结构分别见「封面与排版」和「数据复盘规则」。排序脚本也接受 CSV；精确值、10万+下界和缺失值分开处理，重复观测会被隔离。

## 研究覆盖与限制

原始材料使用了腾讯新闻认证“微信派”公开同步目录的 628 条记录
