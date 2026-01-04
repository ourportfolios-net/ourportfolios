function render_price_chart(chart_options, chart_data) {
  container = document.getElementById("price_chart");
  container.innerHTML = "";

  // Chart layout settings
  chart_layout = chart_options.chart_layout; // dict[str, Any]
  series_configs = chart_options.series_configs; // dict[str, Any]
  rsi_configs = chart_options.rsi_configs ?? null; // dict[str, Any]
  ma_line_configs = chart_options.ma_line_configs ?? null; // dict[dict[str, Any]]

  // Chart data
  chart_type = chart_data.type;
  price_data = chart_data.price_data;
  ma_line_data = chart_data.ma_line_data;
  rsi_line_data = chart_data.rsi_line_data;

  let chart = LightweightCharts.createChart(container, chart_layout);
  let series;

  // Default price value
  if (chart_type === "Candlestick") {
    series = chart.addSeries(
      LightweightCharts.CandlestickSeries,
      series_configs,
      0
    );
  } else {
    series = chart.addSeries(LightweightCharts.LineSeries, series_configs, 0);
  }

  series.setData(price_data);

  // MA lines
  let selected_ma_series = {}; // Assign each MA period with its specific data
  Object.keys(ma_line_data).forEach((period) => {
    ma_series = chart.addSeries(
      LightweightCharts.LineSeries,
      ma_line_configs[period]
    );
    ma_series.setData(ma_line_data[period]);
    selected_ma_series[period] = ma_series;
  });

  // RSI line
  if (rsi_line_data.length > 0) {
    const rsiSeries = chart.addSeries(
      LightweightCharts.LineSeries,
      rsi_configs,
      1
    );
    // Configure the RSI price scale: fixed 0–100
    rsiSeries.priceScale().applyOptions({
      autoScale: false,
      minValue: 0,
      maxValue: 100,
      borderVisible: false,
    });
    // Draw threshold lines at 70 & 30
    rsiSeries.createPriceLine({
      price: 70,
      color: "#FFAB00 ",
      lineWidth: 0.5,
      lineStyle: LightweightCharts.LineStyle.Dashed,
      axisLabelVisible: true,
    });
    rsiSeries.createPriceLine({
      price: 30,
      color: "#FF1744",
      lineWidth: 0.5,
      lineStyle: LightweightCharts.LineStyle.Dashed,
      axisLabelVisible: true,
    });

    // Split charts
    const totalHeight = container.clientHeight;
    chart.applyOptions({
      panes: [
        { height: totalHeight * 0.7 }, // 70%
        { height: totalHeight * 0.3 }, // 30%
      ],
    });
    rsiSeries.setData(rsi_line_data);
  }
}
