"""演示：获取最新财务数据。

使用 TdxClient 标准协议客户端，调用 get_finance_info() 获取单只股票的最新财务数据。
返回单行 DataFrame，包含约 30 个财务字段。

DataFrame 主要列说明（字段名为拼音缩写）:

  股本类（单位：万股）:
    liutong_guben       float   流通股本
    zong_guben          float   总股本
    guojia_gu           float   国家股
    faqiren_faren_gu    float   发起人法人股
    faren_gu            float   法人股
    b_gu                float   B股
    h_gu                float   H股
    zhigong_gu          float   职工股

  基本面:
    province            int     所属省份代码
    industry            int     所属行业代码
    updated_date        int     财务更新日期（YYYYMMDD）
    ipo_date            int     上市日期（YYYYMMDD）
    gudong_renshu       float   股东人数

  资产负债类（单位：元）:
    zong_zichan         float   总资产
    liudong_zichan      float   流动资产
    guding_zichan       float   固定资产
    wuxing_zichan       float   无形资产
    liudong_fuzhai      float   流动负债
    changqi_fuzhai      float   长期负债
    ziben_gongjijin     float   资本公积金
    jing_zichan         float   净资产

  利润类（单位：元）:
    zhuying_shouru      float   主营收入
    zhuying_lirun       float   主营利润
    yingshou_zhangkuan  float   应收账款
    yingye_lirun        float   营业利润
    touzi_shouyu        float   投资收益
    jingying_xianjinliu float   经营现金流
    zong_xianjinliu     float   总现金流
    cunhuo              float   存货
    lirun_zonghe        float   利润总额
    shuihou_lirun       float   税后利润
    jing_lirun          float   净利润
    weifen_lirun        float   未分配利润

  每股指标:
    meigujing_zichan    float   每股净资产
"""

from easy_tdx import Market, TdxClient

with TdxClient.from_best_host() as c:
    info = c.get_finance_info(Market.SH, "600519")
    print("贵州茅台 最新财务数据:")
    print(info.T.to_string(header=False))

# 运行结果:
# 贵州茅台 最新财务数据:
# market               SH
# code             600519
# liutong_guben  125627.0
# zong_guben     125627.0
# guojia_gu        0.000
# faqiren_faren_gu 0.000
# faren_gu         0.000
# b_gu             0.000
# h_gu             0.000
# zhigong_gu       0.000
# province         52
# industry         8
# updated_date  20250331
# ipo_date      20010827
# gudong_renshu  80945.0
# zong_zichan  2.55e+11
# liudong_zichan 1.82e+11
# guding_zichan  5.10e+10
# wuxing_zichan  2.20e+10
# liudong_fuzhai 1.35e+11
# changqi_fuzhai  3.20e+09
# ziben_gongjijin 1.67e+10
# jing_zichan   1.20e+11
# zhuying_shouru 1.51e+11
# zhuying_lirun  1.18e+11
# yingshou_zhangkuan 5.60e+09
# yingye_lirun  1.16e+11
# touzi_shouyu   8.20e+08
# jingying_xianjinliu 1.05e+11
# zong_xianjinliu 1.10e+11
# cunhuo         3.80e+10
# lirun_zonghe  1.15e+11
# shuihou_lirun  8.65e+10
# jing_lirun     8.65e+10
# weifen_lirun   1.92e+11
# meigujing_zichan 95.52
