# ML训练踩坑记录

## v5特征扩展训练（2026-05-25）

### 训练配置
- 脚本：`train_v5_features.py`
- 目标：113特征（38技术+26高阶+14基本面+31行业+4市值）
- 数据源：yfinance（日线）+ **Tushare（基本面主力）** + AKShare（行业分类备用）
- 子集：300只股票快速测试

### ⚠️ 核心教训：数据源优先级（2026-05-25用户纠正）

**用户原话**："怎么还在纠结akshare，有其他数据源啊，之前不是用的tushare和yfinance吗"

**铁律**：
1. **A股数据源优先级**：yfinance > Tushare Pro > AKShare（严重限流）
2. **基本面数据**：Tushare `daily_basic`（PE/PB/市值）+ `fina_indicator`（ROE/EPS/毛利率）
3. **日线数据**：yfinance（质量最好，已缓存733只）
4. **行业分类**：AKShare `stock_board_industry_name_ths()`（此接口相对稳定）
5. **绝不能用AKShare获取基本面**：`stock_individual_info_em`/`stock_yjkb_em`/`stock_zh_a_spot_em`全部限流严重

**修复**：`fetch_fundamental_data()`已重写为三级降级：Tushare → yfinance → 缓存

### 踩坑1：AKShare空数据被缓存（已修复）

**时间线**：
1. 15:36 启动训练，Phase 2（技术特征）正常完成
2. 15:40 进入Phase 3（基本面数据），调用AKShare
3. AKShare限流返回空，`fetch_fundamental_data()`返回`{}`
4. 空结果被缓存到`fundamental_data/{symbol}.json`（2字节）
5. 后续300只股票全部命中缓存，全部是空JSON

**根因**：缓存逻辑没有验证数据非空

**影响**：v5新增的基本面特征（PE/PB/ROE/EPS/毛利率等）全部为0，训练效果可能不如预期

**修复**：修改`fetch_fundamental_data()`函数，只缓存非空结果

### 踩坑2：并发训练进程竞争

**时间线**：
1. 15:36 启动subset 300训练（PID 4132487）
2. 16:06 启动full训练（PID 4141696）
3. 两个进程同时运行，竞争资源
4. 16:17 手动杀掉full训练进程

**影响**：
- 内存：两个进程各占600MB+，总计1.2GB+
- 网络：两个进程同时调AKShare，加剧限流
- 磁盘：两个进程写同一个fundamental_data目录

**修复**：训练脚本应检查是否有同名进程在跑，或prompt中明确只运行一个实例

### 踩坑3：stdout缓冲无输出

**现象**：训练进程运行40+分钟，process log显示0行输出

**根因**：Python stdout缓冲，print输出没有刷新到日志

**修复**：
- 脚本中添加`sys.stdout.flush()`或设置`PYTHONUNBUFFERED=1`
- 或用`python3 -u train_v5_features.py`强制无缓冲

### 训练进度（截至16:17）
- Phase 2（技术特征）：完成
- Phase 3（基本面数据）：120/300只（40%）
- Phase 4-6：未开始
- 预计总耗时：1-2小时

### 后续TODO
- [x] 修复`fetch_fundamental_data()`缓存逻辑 → 已清理空缓存
- [x] 用Tushare替代AKShare获取基本面数据 → 已重写函数
- [ ] 等subset 50训练完成，验证Tushare数据正常返回
- [ ] 如果Tushare正常，运行subset 300完整训练
- [ ] 评估v5模型AUC是否达到预期0.68-0.70

### 数据源修复详情（2026-05-25）

**改动**：
1. 添加Tushare初始化（token: `3ef8313afcf53496a71f4ae4253e8af6ac1ca8104fb088a35301bc3a`）
2. `fetch_fundamental_data()`重写：
   - 方法1: Tushare `daily_basic`（PE/PB/市值/换手率）
   - 方法2: Tushare `fina_indicator`（ROE/EPS/毛利率/营收增长）
   - 方法3: yfinance `info`（备用）
3. 缓存逻辑：只缓存非空结果（`len(data) > 2`）
4. 清理所有空缓存文件（2字节的`{}`）

**Tushare接口说明**：
- `daily_basic`: 需要2000积分以上才能用，120积分可能受限
- `fina_indicator`: 财务指标，120积分可用
- `stock_basic`: 股票列表，120积分可用
- 备用方案：yfinance的`info`属性可以获取PE/PB/ROE等
