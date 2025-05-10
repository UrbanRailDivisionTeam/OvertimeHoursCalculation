# 使用官方的基础镜像
FROM ghcr.io/astral-sh/uv:python3.13-alpine

# 添加项目代码
ADD . /OvertimeHoursCalculation
WORKDIR /OvertimeHoursCalculation

# 安装依赖
RUN uv sync --locked

# 运行应用
CMD ["uv", "run", "app.py"]