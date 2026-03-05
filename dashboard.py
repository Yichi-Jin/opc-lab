import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import altair as alt
    import pandas as pd
    import random
    import datetime

    return alt, datetime, mo, pd, random


@app.cell
def state_init(mo, pd):
    # 1. 初始化系统状态：返回 (get方法, set方法)
    get_is_running, set_is_running = mo.state(False)

    # 2. 初始化数据状态：存储图表历史数据
    get_chart_data, set_chart_data = mo.state(pd.DataFrame(columns=["time", "pv", "sv"]))
    
    return get_chart_data, get_is_running, set_chart_data, set_is_running


@app.cell
def ui_elements(mo):
    # 独立定义具有自身内部状态的 UI 组件，防止被意外重置
    sv_slider = mo.ui.slider(start=0, stop=45, step=1, value=20, label="设定液位 (SV) [cm]:")
    refresh_timer = mo.ui.refresh(options=["1s"], default_interval="1s")
    
    return refresh_timer, sv_slider


@app.cell
def control_panel_ui(
    get_is_running,
    mo,
    refresh_timer,
    set_is_running,
    sv_slider,
):
    # 启停按钮回调逻辑
    def start_sys(_):
        set_is_running(True)

    def stop_sys(_):
        set_is_running(False)

    # 注意这里的 disabled 判断使用的是 get_is_running()
    start_btn = mo.ui.button(label="▶ 启动系统", on_click=start_sys, disabled=get_is_running())
    stop_btn = mo.ui.button(label="⏹ 停止系统", on_click=stop_sys, disabled=not get_is_running())

    # 渲染控制面板
    control_panel = mo.md(f"""
    # 🎛️ OPC-LAB 控制中心

    **系统状态**: {"🟢 运行中" if get_is_running() else "🔴 已停止"}

    {start_btn} {stop_btn}

    ---
    ### 参数设定
    {sv_slider}

    *(图表刷新引擎: {refresh_timer})*
    """)
    
    # 💡 核心修复：必须返回 control_panel 才能在浏览器中渲染！
    return control_panel, 


@app.cell
def data_simulation(
    datetime,
    get_chart_data,
    get_is_running,
    pd,
    random,
    refresh_timer,
    set_chart_data,
    sv_slider,
):
    # 这一行是 Marimo 的魔法：读取 refresh_timer.value 会让这个单元格每秒自动执行一次！
    _ = refresh_timer.value 

    # 如果系统处于运行状态，则生成一帧新数据
    if get_is_running():
        current_time = datetime.datetime.now()
        current_sv = sv_slider.value

        # 模拟真实的 PV 波动
        simulated_pv = current_sv + random.uniform(-2, 2)

        new_row = pd.DataFrame({
            "time": [current_time],
            "pv": [simulated_pv],
            "sv": [current_sv]
        })

        # 获取旧数据，拼接新数据，保留最新的50条，再存回去
        updated_df = pd.concat([get_chart_data(), new_row]).tail(50)
        set_chart_data(updated_df)
        
    return


@app.cell
def chart_render(alt, get_chart_data, mo):
    df = get_chart_data()

    if df.empty:
        chart_ui = mo.md("⏳ *暂无数据，请点击「启动系统」...*")
    else:
        # 将宽表转换为长表，方便 Altair 在同一张图里画多条线
        df_melted = df.melt(id_vars=['time'], value_vars=['pv', 'sv'], var_name='Variable', value_name='Value')

        base_chart = alt.Chart(df_melted).mark_line(point=True).encode(
            x=alt.X("time:T", title="时间", axis=alt.Axis(format="%H:%M:%S")),
            y=alt.Y("Value:Q", title="液位高度 (cm)", scale=alt.Scale(domain=[0, 50])),
            color=alt.Color("Variable:N", scale=alt.Scale(domain=['pv', 'sv'], range=['#1f77b4', '#d62728'])),
            tooltip=["time:T", "Variable:N", "Value:Q"]
        ).properties(
            width=800,
            height=350,
            title="水箱液位实时曲线"
        )
        chart_ui = base_chart
        
    # 💡 核心修复：必须返回 chart_ui 才能显示图表！
    return chart_ui,


if __name__ == "__main__":
    app.run()