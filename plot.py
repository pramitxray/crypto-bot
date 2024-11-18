import plotly.graph_objects as go

def line_chart(df, ticker):
    fig = go.Figure()

    # Add OHLC data as line plots
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Open'],
        mode='lines',
        name='Open',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['High'],
        mode='lines',
        name='High',
        line=dict(color='green')
    ))
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Low'],
        mode='lines',
        name='Low',
        line=dict(color='red')
    ))
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close',
        line=dict(color='orange')
    ))

    # Customize layout
    fig.update_layout(
        title=f"{ticker} OHLC Line Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,  # Disable range slider
        template="plotly_dark",  # Optional: Choose a dark theme
        height=600,  # Adjust chart height
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)  # Position legend
    )

    return fig