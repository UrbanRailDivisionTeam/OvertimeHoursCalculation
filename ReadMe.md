# 加班时长计算器项目

## 项目简介

加班时长计算器是一个基于Flask的Web应用程序，旨在帮助用户上传考勤记录并计算加班时长。用户可以手动设置非工作日和工作日的日期段，以便更准确地计算加班时长。

## 技术栈

- Python
- Flask
- Pandas
- Openpyxl
- Chinese Calendar
- Bootstrap

## 功能

- 上传考勤记录（Excel格式）
- 手动设置非工作日和工作日的日期段
- 计算加班时长和加班时间段
- 生成包含个人加班时长和单位部门加班时长的Excel报告

## 安装与使用

### 先决条件

确保你的环境中已安装以下软件：

- Python 3.x
- pip

### 安装步骤

1. 克隆项目到本地：

   ```bash
   git clone <项目的Git仓库地址>
   cd <项目目录>
   ```

2. 安装所需的Python库：

   ```bash
   pip install -r requirements.txt
   ```

3. 运行Flask应用：

   ```bash
   python app.py
   ```

4. 打开浏览器，访问 `http://127.0.0.1:5000/`。

### 使用说明

1. 在网页上，点击"上传考勤记录"按钮，选择包含考勤数据的Excel文件。
2. 根据需要手动设置非工作日和工作日的日期段。
3. 点击"计算加班时长"按钮，系统将处理数据并生成加班时长报告。
4. 下载生成的Excel报告。

## 文件结构

├── app.py # Flask应用主文件
├── templates
│ └── index.html # 主页面HTML模板
├── static
│ └── bootstrap.min.css # Bootstrap样式文件
├── requirements.txt # Python依赖库列表
└── LICENSE # 项目许可证

## 许可证

本项目采用GNU通用公共许可证（GPL）第3版，详细信息请参见 `LICENSE` 文件。

## 贡献

欢迎任何形式的贡献！请提交问题或拉取请求。

## 联系信息

如有任何问题或建议，请联系项目维护者。