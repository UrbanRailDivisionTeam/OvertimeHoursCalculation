import pandas as pd
from datetime import datetime

def calculate_overtime_simple(card_data_str):
    """
    简化的加班时长计算函数，假设是工作日
    card_data_str: 刷卡数据字符串，如 "09:30,12:11,13:41,17:40,21:43,23:18,23:29"
    """
    # 检查刷卡数据是否为空
    if not card_data_str:
        return 0, ''  # 如果刷卡数据为空，返回0小时加班和空的加班时间段
    
    # 解析刷卡数据
    card_times = card_data_str.split(',')
    card_times = [pd.to_datetime(time.strip(), format='%H:%M', errors='coerce') for time in card_times if time.strip()]
    card_times = [time for time in card_times if pd.notnull(time)]
    
    overtime = pd.Timedelta(0)
    overtime_period = ''
    
    # 工作日加班时间计算（修复后的逻辑）
    start_overtime = pd.to_datetime('18:30', format='%H:%M')  # 修改为18:30
    end_overtime = pd.to_datetime('23:55', format='%H:%M')
    
    # 找到所有在加班时间段内的刷卡记录
    overtime_times = [time for time in card_times if start_overtime <= time <= end_overtime]
    
    if overtime_times:
        # 取最晚的加班刷卡时间
        latest_overtime = max(overtime_times)
        # 计算从18:30到最晚刷卡时间的时长
        overtime = latest_overtime - start_overtime
        overtime_period = f"{start_overtime.strftime('%H:%M')} - {latest_overtime.strftime('%H:%M')}"
    
    return overtime.total_seconds() / 3600, overtime_period  # 转换为小时并返回加班时间段

def calculate_overtime_old(card_data_str):
    """
    原来有bug的加班时长计算函数，用于对比
    """
    # 检查刷卡数据是否为空
    if not card_data_str:
        return 0, ''  # 如果刷卡数据为空，返回0小时加班和空的加班时间段
    
    # 解析刷卡数据
    card_times = card_data_str.split(',')
    card_times = [pd.to_datetime(time.strip(), format='%H:%M', errors='coerce') for time in card_times if time.strip()]
    card_times = [time for time in card_times if pd.notnull(time)]
    
    overtime = pd.Timedelta(0)
    overtime_period = ''
    
    # 工作日加班时间计算（原来有bug的逻辑）
    start_overtime = pd.to_datetime('18:30', format='%H:%M')  # 修改为18:30
    end_overtime = pd.to_datetime('23:55', format='%H:%M')
    for time in card_times:
        if start_overtime <= time <= end_overtime:
            overtime += time - start_overtime  # 这里会重复累加
            overtime_period = f"{start_overtime.strftime('%H:%M')} - {time.strftime('%H:%M')}"
    
    return overtime.total_seconds() / 3600, overtime_period  # 转换为小时并返回加班时间段

# 测试用户报告的bug案例
if __name__ == "__main__":
    # 用户输入的测试数据
    card_data = "09:30,12:11,13:41,17:40,21:43,23:18,23:29"
    
    print("=== 加班时长计算测试 ===")
    print(f"输入刷卡数据: {card_data}")
    
    # 使用修复后的逻辑计算
    overtime_hours_new, overtime_period_new = calculate_overtime_simple(card_data)
    
    # 使用原来有bug的逻辑计算
    overtime_hours_old, overtime_period_old = calculate_overtime_old(card_data)
    
    print(f"\n修复后的计算结果:")
    print(f"加班时长: {overtime_hours_new:.2f} 小时")
    print(f"加班时间段: {overtime_period_new}")
    
    print(f"\n原来有bug的计算结果:")
    print(f"加班时长: {overtime_hours_old:.2f} 小时")
    print(f"加班时间段: {overtime_period_old}")
    
    # 验证计算逻辑
    print(f"\n逻辑验证:")
    print(f"- 工作日加班时间从18:30开始")
    print(f"- 刷卡记录中在18:30之后的时间: 21:43, 23:18, 23:29")
    print(f"- 最晚的加班刷卡时间: 23:29")
    expected_hours = (pd.to_datetime('23:29', format='%H:%M') - pd.to_datetime('18:30', format='%H:%M')).total_seconds() / 3600
    print(f"- 从18:30到23:29的正确时长: {expected_hours:.2f} 小时")
    
    # 检查是否修复了bug
    if abs(overtime_hours_new - expected_hours) < 0.01:
        print(f"\n✅ Bug已修复！新逻辑计算结果正确。")
    else:
        print(f"\n❌ Bug仍然存在，期望值: {expected_hours:.2f} 小时，新逻辑实际值: {overtime_hours_new:.2f} 小时")
    
    print(f"\n问题分析:")
    print(f"- 原来的bug: 对每个18:30后的刷卡时间都计算一次完整时长并累加")
    print(f"- 21:43时计算: 21:43 - 18:30 = {(pd.to_datetime('21:43', format='%H:%M') - pd.to_datetime('18:30', format='%H:%M')).total_seconds() / 3600:.2f} 小时")
    print(f"- 23:18时计算: 23:18 - 18:30 = {(pd.to_datetime('23:18', format='%H:%M') - pd.to_datetime('18:30', format='%H:%M')).total_seconds() / 3600:.2f} 小时")
    print(f"- 23:29时计算: 23:29 - 18:30 = {(pd.to_datetime('23:29', format='%H:%M') - pd.to_datetime('18:30', format='%H:%M')).total_seconds() / 3600:.2f} 小时")
    print(f"- 累加结果: {(pd.to_datetime('21:43', format='%H:%M') - pd.to_datetime('18:30', format='%H:%M')).total_seconds() / 3600 + (pd.to_datetime('23:18', format='%H:%M') - pd.to_datetime('18:30', format='%H:%M')).total_seconds() / 3600 + (pd.to_datetime('23:29', format='%H:%M') - pd.to_datetime('18:30', format='%H:%M')).total_seconds() / 3600:.2f} 小时（错误）")
    print(f"- 修复后: 只计算18:30到最晚刷卡时间23:29的时长 = {expected_hours:.2f} 小时（正确）")