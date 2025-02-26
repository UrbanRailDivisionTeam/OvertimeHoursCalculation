from flask import Flask, request, render_template, send_file
import pandas as pd
from io import BytesIO
import openpyxl
import chinese_calendar as calendar  # 导入chinese-calendar库
from datetime import datetime
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

app = Flask(__name__)

def calculate_overtime(row, non_working_days, working_days):
    # 检查刷卡数据是否为NaN
    if pd.isna(row['刷卡数据']):
        return 0, ''  # 如果刷卡数据为空，返回0小时加班和空的加班时间段
    
    # 解析刷卡数据
    card_times = row['刷卡数据'].split(',')
    card_times = [pd.to_datetime(time.strip(), format='%H:%M', errors='coerce') for time in card_times if time.strip()]
    card_times = [time for time in card_times if pd.notnull(time)]
    
    # 获取日期
    date = pd.to_datetime(row['日期'])
    
    # 判断是否为工作日
    if date in non_working_days:
        is_workday = False
    elif date in working_days:
        is_workday = True
    else:
        is_workday = calendar.is_workday(date)
    
    overtime = pd.Timedelta(0)
    overtime_period = ''
    
    if is_workday:
        # 工作日加班时间计算
        start_overtime = pd.to_datetime('18:30', format='%H:%M')
        end_overtime = pd.to_datetime('23:55', format='%H:%M')
        for time in card_times:
            if start_overtime <= time <= end_overtime:
                overtime += min(end_overtime, time) - start_overtime
                overtime_period = f"{start_overtime.strftime('%H:%M')} - {time.strftime('%H:%M')}"
    else:
        # 非工作日加班时间计算
        if len(card_times) > 1:
            overtime = card_times[-1] - card_times[0]
            overtime_period = f"{card_times[0].strftime('%H:%M')} - {card_times[-1].strftime('%H:%M')}"
    
    return overtime.total_seconds() / 3600, overtime_period  # 转换为小时并返回加班时间段

def format_worksheet(ws):
    # 设置列宽
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # 获取列字母
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 设置标题行的字体和对齐方式
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        
        # 解析用户输入的日期段
        non_working_days_input = request.form.get('non_working_days', '')
        working_days_input = request.form.get('working_days', '')
        
        non_working_days = set(pd.to_datetime(date.strip()) for date in non_working_days_input.split(',') if date.strip())
        
        # 解析多个工作日日期段
        working_days = set()
        for period in working_days_input.split(';'):
            dates = period.split(',')
            if len(dates) == 2:
                start_date, end_date = pd.to_datetime(dates[0].strip()), pd.to_datetime(dates[1].strip())
                working_days.update(pd.date_range(start=start_date, end=end_date))
        
        # 读取考勤记录和人员单位信息
        df_attendance = pd.read_excel(file, sheet_name='考勤记录')
        df_units = pd.read_excel(file, sheet_name='人员单位')
        
        # 合并考勤记录和人员单位信息
        df = pd.merge(df_attendance, df_units, on=['工号', '姓名'])
        
        # 过滤部门包含"组"的记录
        df = df[df['部门'].str.contains('组')]
        
        # 计算加班时长和加班时间段
        df[['加班时长', '加班时间段']] = df.apply(calculate_overtime, axis=1, result_type='expand', args=(non_working_days, working_days))
        
        # 过滤掉加班时长为0的记录
        df = df[df['加班时长'] > 0]
        
        # 删除不需要的字段
        df = df.drop(columns=['班次', '上班时长', '出勤类型', '时段', '时长'])
        
        # 修改"部门"字段为"单位部门"
        df['单位部门'] = df['单位'] + df['部门']
        
        # 按单位部门和工号排序
        df_sorted = df.sort_values(by=['单位部门', '工号'])
        
        # 计算每个单位部门的总加班时长
        department_overtime = df_sorted.groupby(['单位', '部门', '单位部门'])['加班时长'].sum().reset_index()
        department_overtime = department_overtime.sort_values(by='加班时长', ascending=False)
        
        # 计算每个单位部门的人数
        department_counts = df_sorted.groupby(['单位', '部门', '单位部门'])['工号'].nunique().reset_index(name='人数')
        
        # 计算每个单位部门的人均加班时长
        department_avg_overtime = pd.merge(department_overtime, department_counts, on=['单位', '部门', '单位部门'])
        department_avg_overtime['人均加班时长'] = department_avg_overtime['加班时长'] / department_avg_overtime['人数']
        department_avg_overtime = department_avg_overtime.sort_values(by='人均加班时长', ascending=False)
        
        # 计算每个单位的总加班时长和人数
        unit_overtime = df_sorted.groupby('单位')['加班时长'].sum().reset_index()
        unit_counts = df_sorted.groupby('单位')['工号'].nunique().reset_index(name='人数')
        
        # 计算每个单位的人均加班时长
        unit_avg_overtime = pd.merge(unit_overtime, unit_counts, on='单位')
        unit_avg_overtime['人均加班时长'] = unit_avg_overtime['加班时长'] / unit_avg_overtime['人数']
        unit_avg_overtime = unit_avg_overtime.sort_values(by='人均加班时长', ascending=False)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 输出包含"单位部门"、"部门"和"单位"的个人加班时长
            df_sorted.to_excel(writer, sheet_name='个人加班时长', index=False, columns=['工号', '姓名', '日期', '刷卡数据', '单位', '部门', '单位部门', '加班时长', '加班时间段'])
            # 输出包含"单位"、"部门"和"单位部门"的单位部门总加班时长
            department_overtime.to_excel(writer, sheet_name='单位部门总加班时长', index=False, columns=['单位', '部门', '单位部门', '加班时长'])
            # 输出包含"单位"、"部门"、"单位部门"、"人数"和"人均加班时长"的单位部门人均加班时长
            department_avg_overtime.to_excel(writer, sheet_name='单位部门人均加班时长', index=False, columns=['单位', '部门', '单位部门', '人数', '人均加班时长'])
            # 输出包含"单位"、"人数"和"人均加班时长"的单位人均加班时长
            unit_avg_overtime.to_excel(writer, sheet_name='单位人均加班时长', index=False, columns=['单位', '人数', '人均加班时长'])
        
        # 获取Excel文件对象
        workbook = writer.book
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            format_worksheet(worksheet)
        
        output.seek(0)
        return send_file(output, download_name='overtime_report.xlsx', as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
