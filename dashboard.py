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
    page_icon="",
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

.badge-tambah {
    background-color: #e0f2fe;
    color: #0284c7;
    font-size: 11px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 12px;
}
.badge-pertahankan {
    background-color: #dcfce7;
    color: #166534;
    font-size: 11px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 12px;
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
    year_options = ["Pilih Semua Tahun"] + list(years)
    sel_years = st.multiselect("Years", year_options)

    quarters = sorted(df['purchase_quarter'].dropna().unique().astype(int))
    quarter_options = ["Pilih Semua Quarter"] + list(quarters)
    sel_quarters = st.multiselect("Quarter", quarter_options)

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
if sel_years and "Pilih Semua Tahun" not in sel_years:
    mask &= df['purchase_year'].isin(sel_years)
if sel_quarters and "Pilih Semua Quarter" not in sel_quarters:
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
# Convert to datetime if not already
if not pd.api.types.is_datetime64_any_dtype(df['order_purchase_timestamp']):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
if not fdf.empty and not pd.api.types.is_datetime64_any_dtype(fdf['order_purchase_timestamp']):
    fdf['order_purchase_timestamp'] = pd.to_datetime(fdf['order_purchase_timestamp'])

# Calculate previous period data for dynamic trend
if not fdf.empty:
    min_date = fdf['order_purchase_timestamp'].min()
    max_date = fdf['order_purchase_timestamp'].max()
    delta = max_date - min_date
    if delta.total_seconds() == 0:
        delta = pd.Timedelta(days=30)
        
    prev_max = min_date - pd.Timedelta(seconds=1)
    prev_min = prev_max - delta
    
    prev_mask = (df['order_purchase_timestamp'] >= prev_min) & (df['order_purchase_timestamp'] <= prev_max)
    if sel_states:
        prev_mask &= df['customer_state'].isin(sel_states)
    prev_fdf = df[prev_mask]
else:
    prev_fdf = pd.DataFrame()

total_orders = fdf['order_id'].nunique()
late_delivery_rate = fdf['is_late_delivery'].mean() * 100 if not fdf.empty else 0
avg_review_score = fdf['avg_review_score'].mean() if not fdf.empty else 0
avg_delay = fdf['carrier_handling_days'].mean() if not fdf.empty else 0

prev_orders = prev_fdf['order_id'].nunique() if not prev_fdf.empty else 0
prev_late_rate = prev_fdf['is_late_delivery'].mean() * 100 if not prev_fdf.empty else 0
prev_review = prev_fdf['avg_review_score'].mean() if not prev_fdf.empty else 0
prev_delay = prev_fdf['carrier_handling_days'].mean() if not prev_fdf.empty else 0

def get_trend_html(curr_val, prev_val):
    if prev_val == 0 or pd.isna(prev_val) or pd.isna(curr_val):
        pct_change = 0
    else:
        pct_change = ((curr_val - prev_val) / prev_val) * 100
        
    is_positive = pct_change >= 0
    arrow = "↑" if is_positive else "↓"
    
    # User strictly requested UP = Green (trend-up), DOWN = Red (trend-down) for all cards
    css_class = "trend-up" if is_positive else "trend-down"
        
    if pct_change == 0:
        return f'<div style="display: flex; align-items: center;"><span class="kpi-trend" style="background-color:#f1f5f9;color:#64748b;">- 0.00%</span><span class="trend-text">Compared to last period</span></div>'
        
    return f'<div style="display: flex; align-items: center;"><span class="kpi-trend {css_class}">{arrow} {abs(pct_change):.2f}%</span><span class="trend-text">Compared to last period</span></div>'

c1, c2, c3, c4 = st.columns(4, gap="small")
with c1:
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Late delivery rate</div>
<div class="kpi-value">{late_delivery_rate:.1f}%</div>
{get_trend_html(late_delivery_rate, prev_late_rate)}
</div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Avg review score</div>
<div class="kpi-value">{avg_review_score:.2f}</div>
{get_trend_html(avg_review_score, prev_review)}
</div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Avg delay (days)</div>
<div class="kpi-value">{avg_delay:.1f}</div>
{get_trend_html(avg_delay, prev_delay)}
</div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Total orders</div>
<div class="kpi-value">{total_orders:,}</div>
{get_trend_html(total_orders, prev_orders)}
</div>""", unsafe_allow_html=True)


# ============================================
# ROW 2: Main Chart + Side List
# ============================================
r2c1, r2c2 = st.columns([2, 1], gap="small")

with r2c1:
    mr = fdf.groupby(fdf['purchase_date'].dt.to_period('M'))[['approval_days', 'carrier_handling_days', 'delivery_days']].mean().reset_index()
    mr['purchase_date'] = mr['purchase_date'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mr['purchase_date'], y=mr['delivery_days'], mode='lines',
        name='Delivery (Bottleneck)', line=dict(color=C_GREEN, width=2, shape='spline')
    ))
    fig.add_trace(go.Scatter(
        x=mr['purchase_date'], y=mr['carrier_handling_days'], mode='lines',
        name='Carrier Handling', line=dict(color=C_ORANGE, width=2, shape='spline')
    ))
    fig.add_trace(go.Scatter(
        x=mr['purchase_date'], y=mr['approval_days'], mode='lines',
        name='Approval', line=dict(color='#4facfe', width=2, shape='spline')
    ))
    
    fig.update_layout(**base_layout(height=260, title_text="Avg Time per Delivery Stage", margin=dict(l=10, r=10, t=50, b=10)),
                      title_x=0.02, title_y=0.93,
                      legend=dict(orientation="h", yanchor="top", y=1.3, xanchor="left", x=0.35, font=dict(color=C_DARK, size=11)),
                      showlegend=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r2c2:
    conditions = [
        (fdf['is_late_delivery'] == 0) | (fdf['delay_days'].isna()) | (fdf['delay_days'] <= 0),
        (fdf['delay_days'] <= 3),
        (fdf['delay_days'] <= 7),
        (fdf['delay_days'] > 7)
    ]
    choices = ['On-Time', 'Telat 1-3 hr', 'Telat 4-7 hr', 'Telat >7 hr']
    fdf['delay_group'] = np.select(conditions, choices, default='On-Time')
    
    group_scores = fdf.groupby('delay_group')['avg_review_score'].mean().reset_index()
    order = ['Telat >7 hr', 'Telat 4-7 hr', 'Telat 1-3 hr', 'On-Time']
    group_scores['delay_group'] = pd.Categorical(group_scores['delay_group'], categories=order, ordered=True)
    group_scores = group_scores.sort_values('delay_group')
    group_scores['avg_review_score'] = group_scores['avg_review_score'].fillna(0)
    
    color_map = {
        'On-Time': C_GREEN,
        'Telat 1-3 hr': C_ORANGE,
        'Telat 4-7 hr': '#d35436',
        'Telat >7 hr': '#832616'
    }
    colors = [color_map.get(g, C_GRAY) for g in group_scores['delay_group']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=group_scores['delay_group'],
        y=group_scores['avg_review_score'],
        marker_color=colors,
        text=group_scores['avg_review_score'].apply(lambda x: f"{x:.2f} ★" if x > 0 else ""),
        textposition='outside',
        textfont=dict(size=10, color=C_DARK)
    ))
    
    fig.update_layout(**base_layout(height=260, title_text="Review Score vs Delivery", margin=dict(l=10, r=10, t=50, b=20),
                                    xaxis=dict(showgrid=False, tickfont=dict(size=11, color=C_GRAY)),
                                    yaxis=dict(showgrid=False, showticklabels=False),
                                    plot_bgcolor='white', paper_bgcolor='white'))
    
    fig.update_yaxes(range=[0, 5.5])
        
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# ============================================
# ROW 3: 3 Charts
# ============================================
r3c1, r3c2, r3c3 = st.columns(3, gap="small")

with r3c1:
    cat_stats = fdf.groupby('product_category_name_english').agg(
        item_count=('order_id', 'count'),
        late_rate=('is_late_delivery', lambda x: x.mean() * 100)
    ).reset_index()
    
    valid_cats = cat_stats[cat_stats['item_count'] > 50]
    if valid_cats.empty:
        valid_cats = cat_stats
        
    top_cats = valid_cats.nlargest(4, 'late_rate')
    colors = [C_DARK, C_GREEN, C_ORANGE, '#4facfe']
    
    fig = go.Figure(go.Pie(
        labels=top_cats['product_category_name_english'], 
        values=top_cats['late_rate'], 
        hole=0.75, domain=dict(x=[0, 0.45], y=[0, 1]),
        marker=dict(colors=colors),
        textinfo='none', hoverinfo='label+value',
        title=dict(text="Top 4<br><b>Delay</b>", font=dict(size=14, color=C_DARK))
    ))
    
    y_start = 0.85
    y_step = 0.23
    
    cat_map_short = {
        'christmas_supplies': 'Christmas',
        'fashion_underwear_beach': 'Fashion Beach',
        'construction_tools_lights': 'Tools Lights',
        'office_furniture': 'Office Furn.',
        'books_technical': 'Tech Books'
    }
    
    for i, row in enumerate(top_cats.itertuples()):
        color = colors[i % len(colors)]
        raw_label = row.product_category_name_english
        label = cat_map_short.get(raw_label, str(raw_label).replace('_', ' ').title()[:12])
        rate = row.late_rate
        y_pos = y_start - (i * y_step)
        
        fig.add_annotation(x=0.50, y=y_pos, text="■", showarrow=False, xanchor="left", font=dict(size=15, color=color), xref="paper", yref="paper")
        fig.add_annotation(x=0.55, y=y_pos, text=label, showarrow=False, xanchor="left", font=dict(size=11, color=C_DARK), xref="paper", yref="paper")
        fig.add_annotation(x=1.0, y=y_pos, text=f"<b>{rate:.1f}%</b>", showarrow=False, xanchor="right", font=dict(size=11, color=C_DARK), xref="paper", yref="paper")
        
        if i < len(top_cats) - 1:
            fig.add_shape(type="line", x0=0.50, y0=y_pos - (y_step/2), x1=1.0, y1=y_pos - (y_step/2), line=dict(color="#e2e8f0", width=1, dash="dot"), xref="paper", yref="paper")
            
    fig.update_layout(**base_layout(height=230, title_text="Late Delivery Rate by Category", margin=dict(l=10, r=10, t=50, b=20)), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r3c2:
    ht = fdf.groupby(['purchase_year', 'purchase_month'])['is_late_delivery'].mean().reset_index()
    ht['late_rate'] = ht['is_late_delivery'] * 100
    pvt = ht.pivot(index='purchase_year', columns='purchase_month', values='late_rate')
    
    month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    pvt = pvt.reindex(columns=range(1, 13))
    pvt.columns = [month_names[m] for m in pvt.columns]
    pvt = pvt.sort_index()
    
    fig = go.Figure()
    
    colors = {2016: '#fbc2eb', 2017: '#a18cd1', 2018: '#4facfe'}
    fill_colors = {2016: 'rgba(251, 194, 235, 0.3)', 2017: 'rgba(161, 140, 209, 0.3)', 2018: 'rgba(79, 172, 254, 0.3)'}
    
    for year in pvt.index:
        y_data = pvt.loc[year].values
        fig.add_trace(go.Scatter(
            x=pvt.columns, y=y_data, mode='lines+markers', name=str(year),
            line=dict(color=colors.get(year, C_GREEN), width=2, shape='spline'),
            marker=dict(size=6, color='white', line=dict(color=colors.get(year, C_GREEN), width=2)),
            fill='tozeroy', fillcolor=fill_colors.get(year, 'rgba(32, 139, 115, 0.2)'),
            connectgaps=False, hovertemplate="<b>%{x}</b><br>Late Rate: %{y:.1f}%<extra></extra>"
        ))
    
    fig.update_layout(**base_layout(height=230, title_text="Trend Late Delivery per Bulan", margin=dict(l=10, r=10, t=50, b=10)),
                      legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=10, color=C_DARK)),
                      showlegend=True, hovermode="x unified")
    
    fig.update_xaxes(showgrid=True, gridcolor='#e2e8f0', griddash='dash', tickfont=dict(size=10, color=C_GRAY))
    fig.update_yaxes(showgrid=False, tickfont=dict(size=10, color=C_GRAY), ticksuffix="%")
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with r3c3:
    state_stats = fdf.groupby('customer_state').agg(
        item_count=('order_id', 'count'),
        late_rate=('is_late_delivery', lambda x: x.mean() * 100)
    ).reset_index()
    
    valid_states = state_stats[state_stats['item_count'] > 50]
    if valid_states.empty:
        valid_states = state_stats
        
    tcs = valid_states.nlargest(4, 'late_rate')
    max_rate = tcs['late_rate'].max() if not tcs.empty else 0
    
    # Format HTML string WITHOUT indentation to prevent Streamlit parsing it as a Markdown code block
    html_str = f"""<div class='kpi-card' style='height: 230px; overflow: hidden;'>
<div class='kpi-title' style='color: {C_DARK}; font-size: 14px; font-weight: 700; margin-bottom: 16px;'>Late Delivery by State</div>
<div style='display: flex; flex-direction: column; gap: 12px;'>"""
    
    state_names = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
        'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
        'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    
    for _, row in tcs.iterrows():
        rate = row['late_rate']
        pct = int((rate / max_rate) * 100) if max_rate else 0
        state = row['customer_state']
        full_state_name = state_names.get(state, state)
        flag_url = f"https://raw.githubusercontent.com/vasfvitor/bandeiras/master/public/states/{state}-bandeira.svg"
        html_str += f"""
<div style='display: flex; align-items: center; margin-bottom: 6px;'>
    <img src="{flag_url}" style="width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1px solid #e2e8f0; margin-right: 12px; flex-shrink: 0;">
    <div style='flex-grow: 1; display: flex; flex-direction: column; gap: 5px;'>
        <div style='display: flex; justify-content: space-between; align-items: center; line-height: 1;'>
            <div style='color: #94a3b8; font-size: 13px; font-weight: 500;'>{full_state_name}</div>
            <div style='font-weight: 600; color: {C_DARK}; font-size: 12px;'>{rate:.1f}%</div>
        </div>
        <div style='width: 100%; background: #f0f2f5; height: 7px; border-radius: 4px;'>
            <div style='background: {C_GREEN}; height: 100%; border-radius: 4px; width: {pct}%;'></div>
        </div>
    </div>
</div>"""
    
    html_str += "</div></div>"
    st.markdown(html_str, unsafe_allow_html=True)
