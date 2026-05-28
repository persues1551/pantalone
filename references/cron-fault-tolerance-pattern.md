# Cron 容错与备份机制 (2026-05-28更新)

**教训**: 渠道级限流导致6个任务全部失败；docx发送需要显式步骤

## 当前备份架构

主job → 备份job(local保存) → 主job失败时手动补发

## 渠道级限流（核心问题）

微信iLink限流是**渠道级**的：一旦触发，后续所有消息都被挡，恢复时间1-2小时。

**2026-05-27实测**：14:01-16:21期间6个任务全部被限流，根因是15:35两个任务撞车+15:40紧跟+16:15两个任务撞车。

**解决方案**：
1. 多渠道备份（Discord已接入，Telegram待接入）
2. 合并推送（6个报告→1-2个大报告）
3. 本地缓存+手动拉取

详见 `references/cron-schedule-optimized.md` 的"渠道级限流解决方案"章节。

## 正确的备份策略

1. **备份job改为local保存**: deliver='local'，不发微信，由Amadeus手动补发
2. **或用不同渠道**: 主job发Discord，备份job发微信
3. **或取消备份job**: 改为"主job delivery失败时自动补发"机制

## 限流规则

- 同一渠道连续推送间隔≥10分钟（5分钟是iLink临界值，2026-05-27实测不够）
- 同一小时内最多3个推送任务（超过3个即使间隔够也可能触发渠道级限流）
- 限流恢复时间不确定，可能需要1-2小时

## Docx发送必须有显式步骤（2026-05-27教训）

**问题**：prompt只写"完整版转.docx通过MEDIA:发送"，cron agent不知道怎么执行。

**修复**：cron prompt必须包含显式的第四步：
```
## 第四步：生成docx并发送（必须执行）
1. 将完整报告保存为markdown文件
2. 运行 `cat <报告文件> | python3 ~/.hermes/scripts/amadeus/to_docx.py "报告标题" ~/.hermes/cache/amadeus/report_$(date +%Y%m%d).docx`
3. 在最终回复中包含 `MEDIA:/home/ubuntu/.hermes/cache/amadeus/report_$(date +%Y%m%d).docx`
```

**铁律**：cron prompt中提到的每个动作必须有可执行的命令，不能只写意图。

## Gateway重启cron修复（2026-05-28）

详见 `references/gateway-restart-cron-fix.md`。

**核心结论**：Gateway有systemd `Restart=on-failure`，不需要主动重启。原6次/天的cron已禁用。

## 脚本级时间门控模式

当无法修改crontab时，在被cron调用的脚本内部添加时间判断：

```bash
#!/bin/bash
HOUR=$(date '+%H')
if [ "$HOUR" != "03" ]; then
    exit 0
fi
# 实际执行逻辑
```

**应用场景**：
- Gateway定时重启改为凌晨
- 限制某个cron job只在特定时段执行
- 临时禁用某个cron job（直接`exit 0`）

## delivery失败诊断

```
cronjob list → 看last_delivery_error字段
"iLink sendmessage rate limited" → 微信限流
job可能显示status:ok但delivery_error非空 → 执行成功但发送失败
```

## 补发流程

1. 找报告文件: `~/.hermes/cron/output/<job_id>/最新文件`
2. 提取REPORT_START到REPORT_END之间的内容
3. 生成docx: `cat file.md | python3 ~/.hermes/scripts/amadeus/to_docx.py "标题" output.docx`
4. 手动send_message发送，包含MEDIA:标签
