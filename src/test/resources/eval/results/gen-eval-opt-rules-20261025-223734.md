# 生成层评估报告（opt-rules）

- 来源: `opt-rules-20261025-223616.json`，题目数 **20**
- judge 模型: qwen-plus

## 汇总

| 指标 | 值 |
|---|---|
| questions | 20 |
| judgeModel | qwen-plus |
| avgFactRecall | 1.0 |
| avgGroundingRate | 0.989 |
| questionsWithUngroundedNumbers | 2 |
| questionsWithInvalidCitations | 0 |
| questionsWithCitationsOutsideRecorded | 7 |
| questionsWithFormNameCitations | 2 |
| avgCorrectness | 2.5 |
| avgFaithfulness | 2.35 |
| avgRelevance | 2.8 |
| questionsWithUnsupportedClaims | 6 |

## 逐题

| 题 | 类别 | 事实召回 | 数字接地率 | 无据数字 | 幻觉引用 | 引用超记录 | judge 正确/忠实/相关 |
|---|---|---|---|---|---|---|---|
| E01 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E02 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E03 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E04 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E05 | single_hop | 1.00 | 1.00 | - | - | - | 1/0/2 |
| E06 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E07 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E08 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E09 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| MA01 | multi_aspect | 1.00 | 1.00 | - | - | 员工试用期管理办法 | 3/3/3 |
| MA02 | multi_aspect | 1.00 | 1.00 | - | - | 试用期管理办法 | 2/2/3 |
| MA03 | multi_aspect | 1.00 | 1.00 | - | - | 出差住宿酒店协议价目录 | 3/3/3 |
| AG01 | aggregation | 1.00 | 1.00 | - | - | 加班与调休管理制度 | 1/2/2 |
| AG02 | aggregation | 1.00 | 1.00 | - | - | 加班与调休管理制度, 客户投诉处理管理办法, 驻场人员差旅规定 | 1/0/2 |
| E10 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| AZ01 | agent_zone | 1.00 | 1.00 | - | - | - | 3/3/3 |
| AZ02 | agent_zone | 1.00 | 1.00 | - | - | 年假管理制度 | 3/3/3 |
| AZ06 | agent_zone2 | 1.00 | 1.00 | - | - | - | 3/3/3 |
| AZ07 | agent_zone2 | 1.00 | 0.92 | 11 | - | 专项假期管理规定（婚假、产假、陪产假、丧假）, 年假管理规定, 驻场人员差旅规定 | 2/1/3 |
| AZ08 | agent_zone2 | 1.00 | 0.87 | 11, 13 | - | - | 1/0/2 |