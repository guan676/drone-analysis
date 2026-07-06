import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===== 页面配置 =====
st.set_page_config(
    page_title="无人机飞行分析",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 自定义 CSS 样式 =====
st.markdown("""
<style>
    /* 主标题 */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: #00b4d8;
        text-align: center;
        padding: 20px 0 10px 0;
        background: linear-gradient(90deg, #0077b6, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-title {
        text-align: center;
        color: #90e0ef;
        font-size: 18px;
        margin-bottom: 30px;
    }
    /* 统计卡片 */
    .metric-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 18px 12px;
        text-align: center;
        border: 1px solid #2a2a4e;
        box-shadow: 0 4px 12px rgba(0, 180, 216, 0.1);
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #00b4d8;
    }
    .metric-label {
        font-size: 14px;
        color: #90e0ef;
        margin-top: 4px;
    }
    /* 警告框 */
    .warning-box {
        background: #2a1a1a;
        border-left: 4px solid #ff6b6b;
        padding: 12px 18px;
        border-radius: 6px;
        color: #ff6b6b;
    }
    /* 成功框 */
    .success-box {
        background: #1a2a1a;
        border-left: 4px solid #51cf66;
        padding: 12px 18px;
        border-radius: 6px;
        color: #51cf66;
    }
    /* 上传区域 */
    .upload-area {
        border: 2px dashed #00b4d8;
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        background: #0d1b2a;
        transition: all 0.3s;
    }
    .upload-area:hover {
        border-color: #90e0ef;
        background: #1a2a3a;
    }
</style>
""", unsafe_allow_html=True)

# ===== 标题 =====
st.markdown('<div class="main-title">🚁 无人机飞行数据分析</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">上传飞行日志 · 自动生成报告 · 检测异常</div>', unsafe_allow_html=True)

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("### ⚙️ 分析参数")

    # 阈值设置
    阈值 = st.slider(
        "急剧下降阈值 (m/s)",
        min_value=-5.0,
        max_value=-0.5,
        value=-2.0,
        step=0.5,
        help="爬升率低于此值时标记为急剧下降"
    )

    st.markdown("---")
    st.markdown("### 📊 图表设置")

    chart_style = st.selectbox(
        "图表风格",
        ["专业蓝", "暗夜紫", "森林绿", "暖阳橙"]
    )

    show_grid = st.checkbox("显示网格", value=True)
    show_markers = st.checkbox("显示数据点", value=True)

    st.markdown("---")
    st.markdown("### 📁 数据来源")
    uploaded = st.file_uploader("上传 CSV", type=['csv'], label_visibility="collapsed")

# ===== 颜色主题 =====
color_map = {
    "专业蓝": ['#0077b6', '#00b4d8', '#90e0ef', '#023e8a'],
    "暗夜紫": ['#7b2cbf', '#9d4edd', '#c77dff', '#3c096c'],
    "森林绿": ['#2d6a4f', '#40916c', '#52b788', '#1b4332'],
    "暖阳橙": ['#e85d04', '#f48c06', '#faa307', '#dc2f02']
}
colors = color_map.get(chart_style, color_map["专业蓝"])

# ===== 数据加载 =====
if uploaded:
    df = pd.read_csv(uploaded)
    st.success(f"✅ 已加载：{len(df)} 行，{len(df.columns)} 列")
else:
    df = pd.DataFrame({
        '时间': range(10),
        '高度': [10, 12, 15, 18, 20, 22, 19, 17, 14, 11],
        '速度': [0, 1, 2, 3, 4, 5, 4, 3, 2, 1],
        '温度': [25, 26, 27, 28, 29, 30, 29, 28, 27, 26]
    })
    st.info("📊 使用默认模拟数据")

# ===== 数据预览 =====
with st.expander("📋 查看原始数据"):
    st.dataframe(df.style.background_gradient(cmap='Blues', subset=df.select_dtypes(include=['float64', 'int64']).columns))

# ===== 列选择 =====
cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
selected = st.multiselect(
    "选择要分析的列",
    cols,
    default=['高度', '速度'] if '高度' in cols and '速度' in cols else cols[:2]
)

# ===== 分析按钮 =====
if st.button("🚀 开始分析", type="primary", use_container_width=True) and selected:

    # 计算爬升率
    if '时间' in df.columns and '高度' in df.columns:
        df['爬升率'] = df['高度'].diff() / df['时间'].diff()
        df['急剧下降'] = df['爬升率'] < 阈值

    # ===== 统计卡片 =====
    st.markdown("### 📊 统计摘要")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">📏 数据行数</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        max_alt = df['高度'].max() if '高度' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{max_alt:.1f}</div>
            <div class="metric-label">📈 最大高度 (m)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        max_spd = df['速度'].max() if '速度' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{max_spd:.1f}</div>
            <div class="metric-label">💨 最大速度 (m/s)</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        if '急剧下降' in df.columns:
            count = df['急剧下降'].sum()
            color = "#ff6b6b" if count > 0 else "#51cf66"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color}">{count}</div>
                <div class="metric-label">🚨 急剧下降次数</div>
            </div>
            """, unsafe_allow_html=True)

    # ===== 异常警告 =====
    if '急剧下降' in df.columns:
        down = df[df['急剧下降']]
        if len(down) > 0:
            st.markdown(f"""
            <div class="warning-box">
                ⚠️ 检测到 <b>{len(down)}</b> 次急剧下降，发生在 <b>{down['时间'].tolist()}</b> 秒
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box">
                ✅ 未检测到急剧下降，飞行平稳
            </div>
            """, unsafe_allow_html=True)

    # ===== 图表 =====
    st.markdown("### 📈 飞行数据趋势")

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('#0d1b2a')
    ax.set_facecolor('#0d1b2a')

    for i, col in enumerate(selected):
        marker = 'o' if show_markers else ''
        ax.plot(
            df.index, df[col],
            marker=marker,
            linewidth=2.5,
            label=col,
            color=colors[i % len(colors)],
            markersize=8,
            markeredgecolor='white',
            markeredgewidth=1.5
        )

    ax.set_xlabel('采样点', color='#90e0ef', fontsize=12)
    ax.set_ylabel('数值', color='#90e0ef', fontsize=12)
    ax.set_title('飞行数据变化趋势', color='#00b4d8', fontsize=16, fontweight='bold')
    ax.legend(loc='upper left', frameon=True, facecolor='#1a1a2e', labelcolor='#90e0ef')
    if show_grid:
        ax.grid(True, linestyle='--', alpha=0.3, color='#2a2a4e')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#2a2a4e')
    ax.spines['left'].set_color('#2a2a4e')
    ax.tick_params(colors='#90e0ef')

    st.pyplot(fig)

    # ===== 爬升率图 =====
    if '爬升率' in df.columns:
        st.markdown("### 📈 爬升率分析")

        fig2, ax2 = plt.subplots(figsize=(12, 4))
        fig2.patch.set_facecolor('#0d1b2a')
        ax2.set_facecolor('#0d1b2a')

        ax2.plot(
            df['时间'], df['爬升率'],
            color='#51cf66',
            marker='o' if show_markers else '',
            linewidth=2.5,
            label='爬升率',
            markersize=8,
            markeredgecolor='white',
            markeredgewidth=1.5
        )

        ax2.axhline(y=阈值, color='#ff6b6b', linestyle='--', linewidth=2, label=f'阈值 {阈值} m/s')

        if '急剧下降' in df.columns:
            down = df[df['急剧下降']]
            if len(down) > 0:
                ax2.scatter(
                    down['时间'], down['爬升率'],
                    color='#ff6b6b',
                    s=120,
                    zorder=5,
                    label='急剧下降',
                    edgecolors='white',
                    linewidths=1.5
                )

        ax2.set_xlabel('时间 (秒)', color='#90e0ef', fontsize=12)
        ax2.set_ylabel('爬升率 (m/s)', color='#90e0ef', fontsize=12)
        ax2.set_title('爬升率与异常检测', color='#00b4d8', fontsize=16, fontweight='bold')
        ax2.legend(loc='upper left', frameon=True, facecolor='#1a1a2e', labelcolor='#90e0ef')
        if show_grid:
            ax2.grid(True, linestyle='--', alpha=0.3, color='#2a2a4e')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color('#2a2a4e')
        ax2.spines['left'].set_color('#2a2a4e')
        ax2.tick_params(colors='#90e0ef')

        st.pyplot(fig2)

    # ===== 下载 =====
    plt.savefig("report.png", dpi=300, bbox_inches='tight', facecolor='#0d1b2a')
    with open("report.png", "rb") as f:
        st.download_button(
            label="📥 下载报告图片",
            data=f,
            file_name="飞行分析报告.png",
            mime="image/png",
            use_container_width=True
        )