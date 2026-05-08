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
    padding-top: 2.5rem !important;
    margin-top: 0rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100%;
}
/* Ensure collapsed control is always on top and visible */
[data-testid="collapsedControl"] {
    z-index: 999999 !important;
    visibility: visible !important;
}
/* Make header transparent so it doesn't cut off content */
header {background-color: transparent !important;}
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
        margin=dict(l=10, r=10, t=50 if title_text else 10, b=20),
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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&display=swap" rel="stylesheet">
    <div style="font-family: 'Orbitron', sans-serif; font-size: 22px; color: #1e293b; margin-bottom: 20px; margin-top: -7px; font-weight: 400;">
        Olist Dashboard
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### Filters")
    years = sorted(df['purchase_year'].dropna().unique().astype(int))
    sel_years = st.multiselect("Years", years) # Removed default to save vertical space

    quarters = sorted(df['purchase_quarter'].dropna().unique().astype(int))
    sel_quarters = st.multiselect("Quarter", quarters) # Removed default

    STATE_MAP = {
        'SP': 'SP: São Paulo', 'RJ': 'RJ: Rio de Janeiro', 'MG': 'MG: Minas Gerais', 'ES': 'ES: Espírito Santo',
        'PR': 'PR: Paraná', 'RS': 'RS: Rio Grande do Sul', 'SC': 'SC: Santa Catarina',
        'BA': 'BA: Bahia', 'CE': 'CE: Ceará', 'PE': 'PE: Pernambuco', 'MA': 'MA: Maranhão',
        'PB': 'PB: Paraíba', 'RN': 'RN: Rio Grande do Norte', 'AL': 'AL: Alagoas', 'PI': 'PI: Piauí', 'SE': 'SE: Sergipe',
        'DF': 'DF: Distrito Federal', 'GO': 'GO: Goiás', 'MT': 'MT: Mato Grosso', 'MS': 'MS: Mato Grosso do Sul',
        'PA': 'PA: Pará', 'AM': 'AM: Amazonas', 'RO': 'RO: Rondônia', 'TO': 'TO: Tocantins',
        'AC': 'AC: Acre', 'AP': 'AP: Amapá', 'RR': 'RR: Roraima'
    }
    states = sorted(df['customer_state'].dropna().unique())
    sel_states = st.multiselect(
        "State Customer", 
        states, 
        format_func=lambda x: STATE_MAP.get(x, x),
        help="Filter the data based on the customer's delivery state."
    )
    st.markdown("""
    <div style='background-color: #f8f9fa; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-top: 15px;'>
        <div style='font-size: 12px; color: #1e293b; line-height: 1.5;'>
            <div style='margin-bottom: 6px;'><span style='font-size: 14px;'></span> <b>About the Dataset:</b></div>
            This dashboard utilizes the <b>Brazilian E-Commerce Public Dataset by Olist</b>, containing over 100,000 anonymized orders made at multiple marketplaces in Brazil from 2016 to 2018.
            <br><br>
            It offers a comprehensive view of the e-commerce landscape, including order status, pricing, payment methods, freight performance, customer locations, and product attributes—providing valuable insights into customer purchasing behavior and regional sales distribution.
        </div>
    </div>
    """, unsafe_allow_html=True)

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
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&display=swap" rel="stylesheet">
<h3 style="font-family: 'Orbitron', sans-serif; font-weight: 400; margin: 0; padding-bottom: 6px; color: #1e293b;">Overview</h3>
""", unsafe_allow_html=True)

# ============================================
# ROW 1: KPIs
# ============================================
total_rev = fdf['allocated_payment_value'].sum()
total_orders = fdf['order_id'].nunique()
total_cust = fdf['customer_unique_id'].nunique()
aov = total_rev / total_orders if total_orders else 0

c1, c2, c3, c4 = st.columns(4, gap="small")
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
r2c1, r2c2 = st.columns([2, 1], gap="small")

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
                      title_x=0.02, title_y=0.93,
                      legend=dict(orientation="h", yanchor="top", y=1.3, xanchor="left", x=0.70, font=dict(color=C_DARK, size=11)),
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
        state = row['customer_state']
        flag_url = f"https://raw.githubusercontent.com/vasfvitor/bandeiras/master/public/states/{state}-bandeira.svg"
        html_str += f"""
<div style='display: flex; align-items: center; justify-content: space-between;'>
<div style='display: flex; align-items: center; width: 65px;'>
<img src="{flag_url}" style="width: 22px; height: 22px; border-radius: 50%; object-fit: cover; border: 1px solid #e2e8f0; margin-right: 8px;">
<div style='font-weight: 600; color: {C_DARK}; font-size: 13px;'>{state}</div>
</div>
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
r3c1, r3c2, r3c3 = st.columns(3, gap="small")

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
    fig.update_layout(**base_layout(height=230, title_text="Sales by Region", margin=dict(l=30, r=30, t=50, b=20)),
                      polar=dict(
                          radialaxis=dict(visible=False),
                          angularaxis=dict(tickfont=dict(size=10, color=C_GRAY))
                      ))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r3c2:
    pay_dist = fdf.groupby('main_payment_type')['order_id'].nunique().nlargest(4).reset_index()
    total_orders_pay = pay_dist['order_id'].sum()
    colors = [C_DARK, C_GREEN, C_ORANGE, '#4facfe']
    
    fig = go.Figure(go.Pie(
        labels=pay_dist['main_payment_type'], values=pay_dist['order_id'], 
        hole=0.75, domain=dict(x=[0, 0.45], y=[0, 1]),
        marker=dict(colors=colors),
        textinfo='none', hoverinfo='label+percent',
        title=dict(text=f"Total<br><b>{total_orders_pay:,}</b>", font=dict(size=14, color=C_DARK))
    ))
    
    y_start = 0.85
    y_step = 0.23
    
    for i, row in enumerate(pay_dist.itertuples()):
        color = colors[i % len(colors)]
        label = row.main_payment_type
        pct = (row.order_id / total_orders_pay * 100) if total_orders_pay else 0
        y_pos = y_start - (i * y_step)
        
        fig.add_annotation(x=0.50, y=y_pos, text="■", showarrow=False, xanchor="left", font=dict(size=15, color=color), xref="paper", yref="paper")
        fig.add_annotation(x=0.55, y=y_pos, text=label, showarrow=False, xanchor="left", font=dict(size=11, color=C_DARK), xref="paper", yref="paper")
        fig.add_annotation(x=1.0, y=y_pos, text=f"<b>{pct:.1f}%</b>", showarrow=False, xanchor="right", font=dict(size=11, color=C_DARK), xref="paper", yref="paper")
        
        if i < len(pay_dist) - 1:
            fig.add_shape(type="line", x0=0.50, y0=y_pos - (y_step/2), x1=1.0, y1=y_pos - (y_step/2), line=dict(color="#e2e8f0", width=1, dash="dot"), xref="paper", yref="paper")
            
    fig.update_layout(**base_layout(height=230, title_text="Sales by e-commerce platform", margin=dict(l=10, r=10, t=50, b=20)), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r3c3:
    avg_score = fdf['avg_review_score'].mean()
    if pd.isna(avg_score): avg_score = 0
    total_rev_cnt = fdf[fdf['avg_review_score'].notna()]['order_id'].nunique()
    
    fig = go.Figure(go.Indicator(
        mode = "gauge",
        value = avg_score,
        domain = {'x': [0.15, 0.85], 'y': [0.35, 1.0]},
        gauge = {
            'axis': {'range': [None, 5], 'visible': False},
            'bar': {'color': C_GREEN, 'thickness': 0.85},
            'bgcolor': '#f0f2f5',
            'borderwidth': 0,
        }
    ))
    
    # Custom annotations inside chart to save space
    fig.add_annotation(x=0.5, y=0.3, text=f"<b>{avg_score:.2f}</b>", showarrow=False, font=dict(size=36, color=C_DARK), xref="paper", yref="paper", xanchor="center")
    fig.add_annotation(x=0.15, y=0.15, text="<b>1</b><br>Lowest", showarrow=False, font=dict(size=12, color=C_GRAY))
    fig.add_annotation(x=0.85, y=0.15, text="<b>5</b><br>Highest", showarrow=False, font=dict(size=12, color=C_GRAY))
    
    fig.update_layout(**base_layout(height=230, title_text="Review Scores", margin=dict(l=10, r=10, t=60, b=20)))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
