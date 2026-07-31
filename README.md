# 吃什么 / What to Eat

一个帮助 Codex 快速决定早餐、午餐或晚餐吃什么的 Skill。

它会结合你的口味、忌口、当前饭点、近期真实饮食和反馈，给出三个具体菜品。它会记住你实际吃了什么，避免连续推荐同一道菜、同一菜系或同一种主食形态。

## 能做什么

- 首次使用时轻量收集口味和饮食限制
- 每次给出有明确排序的 Top 3 菜品
- 将过敏、忌口和饮食限制作为硬约束
- 记录真实饮食、选择和满意度
- 控制菜品、菜系、口味和形态重复
- 理解“换一批”“最近别推荐面”“我最后吃了黄焖鸡”等自然表达
- 可按你的三餐时间，在每餐前约 10 分钟主动发送当天建议

它只推荐菜品，不推荐餐厅、外卖商家、实时价格或下单链接，也不提供医疗级饮食建议。

## 安装

把 `skills/what-to-eat` 目录复制到你的 Codex Skills 目录：

```bash
cp -R skills/what-to-eat ~/.codex/skills/what-to-eat
```

重新打开 Codex 后，可以直接说“中午吃什么？”，也可以显式调用 `$what-to-eat`。

安装后可运行 `python3 skills/what-to-eat/scripts/doctor.py --json` 检查脚本和状态路径。定时建议依赖 Agent 宿主的自动化能力；没有该能力时仍可手动调用，不能声称提醒已创建。

### Agent 使用说明

每次推荐前先读取本地状态快照。状态默认保存在 `~/.codex/state/what-to-eat/`，测试时使用临时 `--state-dir`。脚本写入成功后才能报告画像、饮食记录或反馈已保存。定时任务需要宿主自动化能力，并且必须保存和复用任务 ID，避免重复创建。详见 [`skills/what-to-eat/references/runtime.md`](skills/what-to-eat/references/runtime.md)。

饮食画像和记录默认只保存在本机的 `~/.codex/state/what-to-eat/`，不会提交到这个仓库。

## English

What to Eat gives personalized Top 3 dish recommendations for breakfast, lunch, and dinner. It learns from actual meals and feedback, respects allergies and dietary restrictions, reduces repetition, and can proactively send suggestions about 10 minutes before each usual meal.

Copy `skills/what-to-eat` into `~/.codex/skills/what-to-eat`, reopen Codex, and ask “What should I eat for lunch?” Local food history stays under `~/.codex/state/what-to-eat/`.
