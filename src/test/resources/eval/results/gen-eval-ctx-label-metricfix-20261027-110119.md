# 生成层评估报告（ctx-label-metricfix）

- 来源: `ctx-label-20261027-105426.json`，题目数 **20**
- judge 模型: （未启用，仅确定性指标）

## 汇总

| 指标 | 值 |
|---|---|
| questions | 20 |
| judgeModel | None |
| avgFactRecall | 1.0 |
| avgGroundingRate | 0.992 |
| questionsWithUngroundedNumbers | 1 |
| questionsWithInvalidCitations | 1 |
| questionsWithCitationsOutsideRecorded | 8 |
| questionsWithFormNameCitations | 2 |
| avgCorrectness | None |
| avgFaithfulness | None |
| avgRelevance | None |
| questionsWithUnsupportedClaims | 0 |

## 逐题

| 题 | 类别 | 事实召回 | 数字接地率 | 无据数字 | 幻觉引用 | 引用超记录 | judge 正确/忠实/相关 |
|---|---|---|---|---|---|---|---|
| E01 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| E02 | single_hop | 1.00 | 1.00 | - | - | 05-考勤管理制度 | -/-/- |
| E03 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| E04 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| E05 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| E06 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| E07 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| E08 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| E09 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| MA01 | multi_aspect | 1.00 | 1.00 | - | C05-试用期管理办法 | 06-员工试用期管理办法, 06-试用期管理办法 | -/-/- |
| MA02 | multi_aspect | 1.00 | 1.00 | - | - | - | -/-/- |
| MA03 | multi_aspect | 1.00 | 1.00 | - | - | E47-出差住宿酒店协议价目录 | -/-/- |
| AG01 | aggregation | 1.00 | 1.00 | - | - | 07-加班与调休管理制度 | -/-/- |
| AG02 | aggregation | 1.00 | 1.00 | - | - | C13-驻场人员差旅规定, E08-离职交接管理办法, E24-客户投诉处理管理办法 | -/-/- |
| E10 | single_hop | 1.00 | 1.00 | - | - | - | -/-/- |
| AZ01 | agent_zone | 1.00 | 1.00 | - | - | F02-信息安全操作细则 | -/-/- |
| AZ02 | agent_zone | 1.00 | 1.00 | - | - | 01-年假管理制度 | -/-/- |
| AZ06 | agent_zone2 | 1.00 | 1.00 | - | - | - | -/-/- |
| AZ07 | agent_zone2 | 1.00 | 1.00 | - | - | 10-专项假期管理规定, C01-上海子公司年假管理规定 | -/-/- |
| AZ08 | agent_zone2 | 1.00 | 0.85 | 11, 13 | - | - | -/-/- |