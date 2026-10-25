# 生成层评估报告（az08fix-fun-fix）

- 来源: `az08fix-fun-20261015-172423.json`，题目数 **20**
- judge 模型: qwen-plus

## 汇总

| 指标 | 值 |
|---|---|
| questions | 20 |
| judgeModel | qwen-plus |
| avgFactRecall | 1.0 |
| avgGroundingRate | 1.0 |
| questionsWithUngroundedNumbers | 0 |
| questionsWithInvalidCitations | 5 |
| questionsWithCitationsOutsideRecorded | 8 |
| avgCorrectness | 2.5 |
| avgFaithfulness | 2.35 |
| avgRelevance | 2.9 |
| questionsWithUnsupportedClaims | 6 |

## 逐题

| 题 | 类别 | 事实召回 | 数字接地率 | 无据数字 | 幻觉引用 | 引用超记录 | judge 正确/忠实/相关 |
|---|---|---|---|---|---|---|---|
| E01 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E02 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E03 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E04 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E05 | single_hop | 1.00 | 1.00 | - | 信息安全操作细则（执行版） | - | 1/1/3 |
| E06 | single_hop | 1.00 | 1.00 | - | 专项假期管理规定（婚假、产假、陪产假、丧假） | - | 3/3/3 |
| E07 | single_hop | 1.00 | 1.00 | - | 紧急费用说明单 | - | 3/3/3 |
| E08 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| E09 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| MA01 | multi_aspect | 1.00 | 1.00 | - | - | 员工试用期管理办法, 考勤管理制度, 试用期管理办法 | 2/2/3 |
| MA02 | multi_aspect | 1.00 | 1.00 | - | - | 员工奖惩条例 | 3/3/3 |
| MA03 | multi_aspect | 1.00 | 1.00 | - | - | 出差住宿酒店协议价目录 | 3/3/3 |
| AG01 | aggregation | 1.00 | 1.00 | - | - | - | 1/0/3 |
| AG02 | aggregation | 1.00 | 1.00 | - | 紧急费用说明单 | IT 服务工单处理时限, 加班与调休管理制度, 离职交接管理办法, 驻场人员差旅规定 | 1/1/2 |
| E10 | single_hop | 1.00 | 1.00 | - | - | - | 3/3/3 |
| AZ01 | agent_zone | 1.00 | 1.00 | - | - | - | 3/3/3 |
| AZ02 | agent_zone | 1.00 | 1.00 | - | - | 年假管理制度 | 3/3/3 |
| AZ06 | agent_zone2 | 1.00 | 1.00 | - | - | 远程办公管理办法 | 3/3/3 |
| AZ07 | agent_zone2 | 1.00 | 1.00 | - | 专项假期管理规定（婚假、产假、陪产假、丧假） | 年假管理规定 | 2/1/3 |
| AZ08 | agent_zone2 | 1.00 | 1.00 | - | - | 员工试用期管理办法 | 1/0/2 |