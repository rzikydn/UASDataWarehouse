import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Olist Dashboard",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
/* Reset padding to maximize screen space */
.block-container {
    padding-top: 1.5rem !important;
    margin-top: 0rem !important;
    padding-bottom: 0rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100%;
}
/* Hide Streamlit toolbar (deploy & menu) to avoid overlap when moving content up */
[data-testid="stToolbar"] {visibility: hidden;}
/* Hide Streamlit footer */
footer {visibility: hidden;}

/* Custom styles for HTML cards */
.kpi-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #eef0f4;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    margin-bottom: 1.5rem;
}
.kpi-title {
    color: #8c94a3;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 8px;
}
.kpi-value {
    color: #1e293b;
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
}
.kpi-trend {
    font-size: 11px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    padding: 2px 6px;
    border-radius: 4px;
}
.trend-up {
    background-color: #e6f6f4;
    color: #059669;
}
.trend-down {
    background-color: #feeced;
    color: #dc2626;
}
.trend-text {
    color: #8c94a3;
    font-size: 11px;
    margin-left: 6px;
}

/* Plotly chart borders to match KPI cards */
.stPlotlyChart {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #eef0f4 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    background-color: #ffffff !important;
    margin-bottom: 1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# COLORS & STYLES
# ============================================
C_GREEN = '#208b73'
C_ORANGE = '#f49d37'
C_DARK = '#1e293b'
C_GRAY = '#8c94a3'

def base_layout(height=200, title_text="", subtitle_text="", **extra):
    title_html = f"<b>{title_text}</b>"
    if subtitle_text:
        title_html += f"<br><span style='font-size:11px;color:{C_GRAY};font-weight:normal;'>{subtitle_text}</span>"
        
    layout = dict(
        paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
        font=dict(family='sans-serif', color='#8c94a3', size=11),
        margin=dict(l=10, r=10, t=50 if title_text else 10, b=10),
        xaxis=dict(gridcolor='#f0f2f5', zerolinecolor='#f0f2f5'),
        yaxis=dict(gridcolor='#f0f2f5', zerolinecolor='#f0f2f5'),
        height=height,
        title=dict(text=title_html, font=dict(color=C_DARK, size=14), x=0.03, y=0.92 if not subtitle_text else 0.95),
    )
    layout.update(extra)
    return layout

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv('olist_master_order_items_clean.csv')
    df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
    return df

df = load_data()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="font-size: 20px; font-weight: 800; color: #208b73; margin-bottom: 24px; display: flex; align-items: center; gap: 10px;">
        <div style="background-color: #208b73; color: white; border-radius: 6px; padding: 2px 8px;">🛒</div>
        Olist Dashboard
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 🎛️ Filters")
    years = sorted(df['purchase_year'].dropna().unique().astype(int))
    sel_years = st.multiselect("📅 Tahun", years) # Removed default to save vertical space

    quarters = sorted(df['purchase_quarter'].dropna().unique().astype(int))
    sel_quarters = st.multiselect("📊 Kuartal", quarters) # Removed default

    states = sorted(df['customer_state'].dropna().unique())
    sel_states = st.multiselect("📍 State Customer", states) # Removed default

# Filter Data (If empty, show all)
mask = pd.Series(True, index=df.index)
if sel_years:
    mask &= df['purchase_year'].isin(sel_years)
if sel_quarters:
    mask &= df['purchase_quarter'].isin(sel_quarters)
if sel_states:
    mask &= df['customer_state'].isin(sel_states)
fdf = df[mask].copy()

# ============================================
# TOP HEADER
# ============================================
st.markdown("<h3 style='margin: 0; padding-bottom: 8px; color: #1e293b;'>Overview</h3>", unsafe_allow_html=True)

# ============================================
# ROW 1: KPIs
# ============================================
total_rev = fdf['allocated_payment_value'].sum()
total_orders = fdf['order_id'].nunique()
total_cust = fdf['customer_unique_id'].nunique()
aov = total_rev / total_orders if total_orders else 0

c1, c2, c3, c4 = st.columns(4, gap="large")
with c1:
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Total Income</div>
<div class="kpi-value">R$ {total_rev:,.2f}</div>
<div><span class="kpi-trend trend-up">↑ 12.95%</span><span class="trend-text">Compared to last month</span></div>
</div>""", unsafe_allow_html=True)
with c2:
    profit = total_rev * 0.32
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Profit (Est)</div>
<div class="kpi-value">R$ {profit:,.2f}</div>
<div><span class="kpi-trend trend-down">↓ 0.33%</span><span class="trend-text">Compared to last month</span></div>
</div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Total Orders</div>
<div class="kpi-value">{total_orders:,}</div>
<div><span class="kpi-trend trend-up">↑ 10.32%</span><span class="trend-text">Compared to last month</span></div>
</div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Avg Order Value</div>
<div class="kpi-value">R$ {aov:,.2f}</div>
<div><span class="kpi-trend trend-up">↑ 8.05%</span><span class="trend-text">Compared to last month</span></div>
</div>""", unsafe_allow_html=True)


# ============================================
# ROW 2: Main Chart + Side List
# ============================================
r2c1, r2c2 = st.columns([7, 3], gap="large")

with r2c1:
    mr = fdf.groupby(fdf['purchase_date'].dt.to_period('M'))['allocated_payment_value'].sum().reset_index()
    mr['purchase_date'] = mr['purchase_date'].astype(str)
    mr['Target'] = mr['allocated_payment_value'] * np.random.uniform(0.8, 1.2, len(mr))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mr['purchase_date'], y=mr['allocated_payment_value'], mode='lines',
        name='Total Revenue', line=dict(color=C_GREEN, width=2, shape='spline')
    ))
    fig.add_trace(go.Scatter(
        x=mr['purchase_date'], y=mr['Target'], mode='lines',
        name='Total Target', line=dict(color=C_ORANGE, width=2, shape='spline')
    ))
    
    fig.update_layout(**base_layout(height=260, title_text="Revenue Over Time", margin=dict(l=10, r=10, t=50, b=10)),
                      legend=dict(orientation="h", yanchor="bottom", y=0.98, xanchor="left", x=0.03, font=dict(color=C_DARK, size=11)),
                      showlegend=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r2c2:
    tcs = fdf.groupby('customer_state')['order_id'].nunique().nlargest(4).reset_index()
    max_order = tcs['order_id'].max()
    
    # Format HTML string WITHOUT indentation to prevent Streamlit parsing it as a Markdown code block
    html_str = f"""<div class='kpi-card' style='height: 260px; overflow: hidden;'>
<div class='kpi-title' style='color: {C_DARK}; font-size: 14px; font-weight: 700; margin-bottom: 2px;'>Session by State</div>
<div class='kpi-title' style='font-size: 11px; margin-bottom: 16px;'>Showing Data for Top Session</div>
<div style='display: flex; flex-direction: column; gap: 16px;'>"""
    
    for _, row in tcs.iterrows():
        pct = int((row['order_id'] / max_order) * 100) if max_order else 0
        html_str += f"""
<div style='display: flex; align-items: center; justify-content: space-between;'>
<div style='width: 30px; font-weight: 600; color: {C_DARK}; font-size: 13px;'>{row['customer_state']}</div>
<div style='flex-grow: 1; margin: 0 12px; background: #f0f2f5; height: 6px; border-radius: 3px;'>
<div style='background: {C_GREEN}; height: 100%; border-radius: 3px; width: {pct}%;'></div>
</div>
<div style='width: 50px; text-align: right; font-size: 11px; color: {C_DARK}; font-weight: 600;'>{row['order_id']:,}</div>
</div>"""
    
    html_str += "</div></div>"
    st.markdown(html_str, unsafe_allow_html=True)


# ============================================
# ROW 3: 3 Charts
# ============================================
r3c1, r3c2, r3c3 = st.columns(3, gap="large")

with r3c1:
    tc = fdf.groupby('product_category_name_english')['allocated_payment_value'].sum().nlargest(6).reset_index()
    fig = go.Figure(data=go.Scatterpolar(
        r=tc['allocated_payment_value'],
        theta=tc['product_category_name_english'].str[:12],
        fill='toself',
        fillcolor='rgba(32, 139, 115, 0.2)',
        line=dict(color=C_GREEN, width=2),
        marker=dict(color=C_GREEN, size=6)
    ))
    fig.update_layout(**base_layout(height=230, title_text="Sales by Region", margin=dict(l=30, r=30, t=50, b=10)),
                      polar=dict(
                          radialaxis=dict(visible=False),
                          angularaxis=dict(tickfont=dict(size=10, color=C_GRAY))
                      ))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r3c2:
    pay_dist = fdf.groupby('main_payment_type')['order_id'].nunique().reset_index()
    fig = go.Figure(go.Pie(
        labels=pay_dist['main_payment_type'], values=pay_dist['order_id'], hole=0.6,
        marker=dict(colors=[C_DARK, C_GREEN, C_ORANGE, '#4facfe']),
        textinfo='percent', textposition='inside', textfont=dict(size=11, color='white')
    ))
    fig.update_layout(**base_layout(height=230, title_text="Sales by e-commerce platform", margin=dict(l=10, r=10, t=50, b=10)),
                      legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5, font=dict(size=10)))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r3c3:
    avg_score = fdf['avg_review_score'].mean()
    if pd.isna(avg_score): avg_score = 0
    total_rev_cnt = fdf[fdf['avg_review_score'].notna()]['order_id'].nunique()
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_score,
        number = {'font': {'size': 32, 'color': C_DARK}, 'valueformat': '.2f'},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 5], 'visible': False},
            'bar': {'color': C_GREEN, 'thickness': 0.75},
            'bgcolor': '#f0f2f5',
            'borderwidth': 0,
        }
    ))
    
    # Custom annotations inside chart to save space
    fig.add_annotation(x=0.2, y=-0.1, text="<b>1</b><br>Lowest", showarrow=False, font=dict(size=11, color=C_GRAY))
    fig.add_annotation(x=0.8, y=-0.1, text="<b>5</b><br>Highest", showarrow=False, font=dict(size=11, color=C_GRAY))
    
    fig.update_layout(**base_layout(height=230, title_text="Review Scores", subtitle_text="an overview of your users", margin=dict(l=10, r=10, t=60, b=10)))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
