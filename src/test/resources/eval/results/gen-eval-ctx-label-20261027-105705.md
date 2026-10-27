# 生成层评估报告（ctx-label）

- 来源: `ctx-label-20261027-105426.json`，题目数 **20**
- judge 模型: qwen-plus

## 汇总

| 指标 | 值 |
|---|---|
| questions | 20 |
| judgeModel | qwen-plus |
| avgFactRecall | 1.0 |
| avgGroundingRate | 0.716 |
| questionsWithUngroundedNumbers | 18 |
| questionsWithInvalidCitations | 1 |
| questionsWithCitationsOutsideRecorded | 8 |
| questionsWithFormNameCitations | 2 |
| avgCorrectness | 2.5 |
| avgFaithfulness | 2.65 |
| avgRelevance | 2.75 |
| questionsWithUnsupportedClaims | 6 |

## 逐题

| 题 | 类别 | 事实召回 | 数字接地率 | 无据数字 | 幻觉引用 | 引用超记录 | judge 正确/忠实/相关 |
|---|---|---|---|---|---|---|---|
| E01 | single_hop | 1.00 | 0.80 | 01 | - | - | 3/3/3 |
| E02 | single_hop | 1.00 | 0.67 | 01, 05 | - | 05-考勤管理制度 | 3/3/3 |
| E03 | single_hop | 1.00 | 0.80 | 07 | - | - | 3/3/3 |
| E04 | single_hop | 1.00 | 0.67 | 08 | - | - | 3/3/3 |
| E05 | single_hop | 1.00 | 1.00 | - | - | - | 0/2/1 |
| E06 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E07 | single_hop | 1.00 | 0.50 | 04 | - | - | 3/3/3 |
| E08 | single_hop | 1.00 | 0.67 | 08 | - | - | 3/3/3 |
| E09 | single_hop | 1.00 | 0.50 | 05, 06 | - | - | 3/3/3 |
| MA01 | multi_aspect | 1.00 | 0.73 | 01, 03, 04, 05, 06, 07 | C05-试用期管理办法 | 06-员工试用期管理办法, 06-试用期管理办法 | 2/2/3 |
| MA02 | multi_aspect | 1.00 | 0.93 | 05 | - | - | 3/3/3 |
| MA03 | multi_aspect | 1.00 | 0.73 | 03, 13, 47 | - | E47-出差住宿酒店协议价目录 | 3/3/3 |
| AG01 | aggregation | 1.00 | 0.50 | 07, 11 | - | 07-加班与调休管理制度 | 2/3/3 |
| AG02 | aggregation | 1.00 | 0.72 | 03, 04, 08, 13, 14 | - | C13-驻场人员差旅规定, E08-离职交接管理办法, E24-客户投诉处理管理办法 | 1/0/1 |
| E10 | single_hop | 1.00 | 0.57 | 04, 07, 08 | - | - | 2/3/2 |
| AZ01 | agent_zone | 1.00 | 0.77 | 07, 08, 09 | - | F02-信息安全操作细则 | 3/3/3 |
| AZ02 | agent_zone | 1.00 | 0.67 | 01, 04, 05, 06 | - | 01-年假管理制度 | 3/3/3 |
| AZ06 | agent_zone2 | 1.00 | 0.71 | 03, 05, 07, 08 | - | - | 3/3/3 |
| AZ07 | agent_zone2 | 1.00 | 0.73 | 01, 03, 06, 07 | - | 10-专项假期管理规定, C01-上海子公司年假管理规定 | 3/3/3 |
| AZ08 | agent_zone2 | 1.00 | 0.67 | 01, 03, 05, 06, 11, 13 | - | - | 1/1/3 |