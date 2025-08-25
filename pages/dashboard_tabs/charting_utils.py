import streamlit as st
import pandas as pd
import altair as alt

def render_filter_bar(df, key_prefix, agg_options, chart_type_options, default_agg_index=0):
    """Renders the common filter widgets and returns their values."""
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        start_date = st.date_input("Start date", df.index.min(), key=f"{key_prefix}_start")
    with c2:
        end_date = st.date_input("End date", df.index.max(), key=f"{key_prefix}_end")
    with c3:
        aggregation_period = st.selectbox(
            "Aggregation Period:",
            options=agg_options,
            index=default_agg_index,
            key=f"{key_prefix}_agg_period"
        )
    with c4:
        chart_type = st.radio("Chart Type:", chart_type_options, key=f"{key_prefix}_chart_type", horizontal=True)
    with c5:
        chart_view = st.radio("Chart View:", ["Combined", "Individual"], key=f"{key_prefix}_view_type", horizontal=True)
    
    return start_date, end_date, aggregation_period, chart_type, chart_view

def render_altair_chart(df, aggregation_period, chart_type, chart_view, x_col, y_col, color_col, chart_title):
    """Renders a customized Altair chart from a melted dataframe, with combined/individual views."""
    
    # --- X-Axis Formatting ---
    if aggregation_period == 'Yearly':
        df['Label'] = df[x_col].dt.strftime('%Y')
        x_title = 'Year'
    elif aggregation_period == 'Quarterly':
        df['Label'] = df[x_col].dt.to_period('Q').astype(str)
        x_title = 'Quarter'
    else: # Monthly
        df['Label'] = df[x_col].dt.strftime('%b %Y')
        x_title = 'Month'
    
    x_axis = alt.X('Label:O', title=x_title, sort=None)

    # --- Chart Rendering ---
    if chart_view == 'Individual':
        unique_metrics = df[color_col].unique()
        for metric in unique_metrics:
            metric_df = df[df[color_col] == metric]
            base = alt.Chart(metric_df).encode(
                x=x_axis,
                y=alt.Y(f'{y_col}:Q', title=metric),
                tooltip=['Label', y_col]
            ).properties(
                title=f"{metric} ({aggregation_period})"
            )
            if chart_type == "Line":
                chart = base.mark_line().interactive()
            else: # Bar
                chart = base.mark_bar().interactive()
            st.altair_chart(chart, use_container_width=True)
    else: # Combined View
        base = alt.Chart(df).encode(
            x=x_axis,
            y=alt.Y(f'{y_col}:Q', title='Value', scale=alt.Scale(zero=False)),
            color=alt.Color(f'{color_col}:N', title='Metric'),
            tooltip=['Label', color_col, y_col]
        ).properties(
            title=chart_title
        )

        if chart_type == "Line":
            chart = base.mark_line().interactive()
        else: # Bar
            chart = base.mark_bar().interactive()
        
        st.altair_chart(chart, use_container_width=True)