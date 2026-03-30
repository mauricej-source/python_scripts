The Python script consBatchP2EVWMA.py is a financial analysis tool designed to evaluate trading signals for multiple stock tickers using various indicators, with a primary focus on the Elastic Volume Weighted Moving Average (EVWMA). It automates the process of downloading stock data, calculating indicators, and generating a summary report.

The script's core function is to:

1.  Download Historical Stock Data: It uses the yfinance library to download historical stock data (Open, High, Low, Close, and Volume) for a list of tickers provided in a CSV input file.

2.  Calculate Technical Indicators: After downloading the data, it computes several technical indicators, including:

		Volume Weighted Average Price (VWAP): The average price weighted by trading volume.

		Moving Average Convergence Divergence (MACD): A trend-following momentum indicator.

		Elastic Volume Weighted Moving Average (EVWMA): This is the main indicator. It calculates both a short-term and a long-term EVWMA. Unlike a standard moving average, the EVWMA's smoothing factor adapts based on the stock's trading volume, making it more responsive during high-volume periods and less so during low-volume periods.

		EVWMA-based Oscillator: The difference between the short-term and long-term EVWMAs.

3.  Evaluate Trading Signals: It analyzes three different trading strategies based on crossovers to generate buy or sell signals:

		Single EVWMA: A crossover between the stock's closing price and the short-term EVWMA.

		EVWMA Oscillator: A crossover between the EVWMA oscillator line and its signal line.

		Double EVWMA Crossover: A crossover between the short-term and long-term EVWMAs.

4.  Generate a Consolidated HTML Report: It processes the signals for all tickers and compiles a comprehensive HTML report. This report categorizes tickers into "Leaning Buy," "Leaning Sell," and "Undetermined" based on the analysis of the indicator crossovers. The final report is saved as an HTML file in a specified directory.