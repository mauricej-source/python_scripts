-- -----------------------------------------------------------
-- FINVIZ API Token:    5c4e80ff-b219-4a31-8fb8-10725a640658
-- -----------------------------------------------------------


-- ------------------------------------------------------
Buy and Hold Screener

URL:  "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=cap_microover,fa_curratio_o1.5,fa_eps5years_o10,fa_roe_o15,ta_beta_o1.5,ta_change_u,ta_sma20_pa&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
-- ------------------------------------------------------
Market Cap > 50 Million
Price above 20day Moving Average
Beta > 1.5
EPS growth over next 5 years > 10%
Return on Equity > 15%
Current ratio > 1.5

-- ------------------------------------------------------
Bounce Play Screener - Oversold Situations

URL:  "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_price_o3%2Csh_relvol_1to3%2Cta_change_1to100%2Cta_rsi_os30&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"
-- ------------------------------------------------------
Stock Price > 5
RSI = Oversold
Change = Up
Relative Volume > 2

-- ------------------------------------------------------
Bounce Play Screener - Off Moving Averages

URL:  https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=sh_avgvol_o400%2Csh_curvol_o2000%2Csh_relvol_o1%2Cta_change_u2%2Cta_sma20_pa%2Cta_sma50_pb&ft=4&o=-change&auth=5c4e80ff-b219-4a31-8fb8-10725a640658

-- ------------------------------------------------------
Price above 20day Moving Average
Price below 50day Moving Average
Average Volume > "Over 400K"
Relative Volume > 1
Current Volume > "2M"

-- ------------------------------------------------------
Breakout

URL:  https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=fa_debteq_0to1,fa_roe_o15,sh_avgvol_o100,sh_price_1to150,ta_change_u1,ta_highlow50d_nh,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=-price&auth=5c4e80ff-b219-4a31-8fb8-10725a640658

-- ------------------------------------------------------
price above, 20,50,200
Day High/Low => New High past 50 days
Return on Equity > 20%
Debt to Equity <= 1
Average Volume > "Over 100K"

-- ------------------------------------------------------
Short Screener

URL:  https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63 &auth=5c4e80ff-b219-4a31-8fb8-10725a640658
-- ------------------------------------------------------
Market Cap > 300 Million
Short Float High > 20%
Average Volume > "Over 500K"
Relative Volume > 1
Current Volume > "Over 500K"

-- ------------------------------------------------------
Short Screener - Bounce - Short Squeeze
-- ------------------------------------------------------

URL:  "https://elite.finviz.com/export.ashx?v=151&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63&f=an_recom_buybetter|holdbetter,sh_float_x40to100,sh_instown_10to100,sh_price_0.75to8.25,sh_short_o20,ta_change_u,ta_perf_1wup&ft=4&o=-price&auth=5c4e80ff-b219-4a31-8fb8-10725a640658"


Required Historical Data for EVWMA Analysis
{'open'(86), 'high'(87), 'low'(88), 'close'(81), 'volume'(67)}


Columns
&c=1,2,3,4,5,6,7,28,30,31,44,46,62,63
1	Ticker
2	Company
3	Sector
4	Industry
5	Country
6	Market Cap > "Small (sub $2B)" - can also help. Smaller companies often have lower trading volumes and smaller floats, which can make them more susceptible to a short squeeze.
7	P/E = N/A
28	Institutional Ownership > 30%
30	Short Float > 20%
31	Short Ratio >= 10
44	Performance (Quarter) - Down
46	Performance (Year) - Down -20%
62	Analyst Recom - Sell or Strong Sell
63	Average Volume > "Over 100K" or "Over 200K" <= Filter for stocks where it would take longer for short sellers to cover their positions









-- ------------------------------------------------------
FINVIZ Columns
-- ------------------------------------------------------
1	Ticker
2	Company
3	Sector
4	Industry
5	Country
6	Market Cap
7	P/E
8	Forward P/E
9	PEG
10	P/S
11	P/B
12	P/Cash
13	P/Free Cash Flow
14	Dividend Yield
15	Payout Ratio
16	EPS (ttm)
17	EPS Growth This Year
18	EPS Growth Next Year
19	EPS Growth Past 5 Years
20	EPS Growth Next 5 Years
21	Sales Growth Past 5 Years
22	EPS Growth Quarter Over Quarter
23	Sales Growth Quarter Over Quarter
24	Shares Outstanding
25	Shares Float
26	Insider Ownership
27	Insider Transactions
28	Institutional Ownership
29	Institutional Transactions


32	Return on Assets
33	Return on Equity
34	Return on Invested Capital
35	Current Ratio
36	Quick Ratio
37	LT Debt/Equity
38	Total Debt/Equity
39	Gross Margin
40	Operating Margin
41	Profit Margin
42	Performance (Week)
43	Performance (Month)
44	Performance (Quarter)
45	Performance (Half Year)
46	Performance (Year)
47	Performance (YTD)
48	Beta
49	Average True Range
50	Volatility (Week)
51	Volatility (Month)
52	20-Day Simple Moving Average
53	50-Day Simple Moving Average
54	200-Day Simple Moving Average
55	50-Day High
56	50-Day Low
57	52-Week High
58	52-Week Low
59	Relative Strength Index (14)
60	Change from Open
61	Gap
62	Analyst Recom

64	Relative Volume
65	Price
66	Change
67	Volume
68	Earnings Date
69	Target Price
70	IPO Date
71	After-Hours Close
72	After-Hours Change
73	Book/sh
74	Cash/sh
75	Dividend
76	Employees
77	EPS Next Q
78	Income
79	Index
80	Optionable
81	Prev Close
82	Sales
83	Shortable
84	Short Interest
85	Float %
86	Open
87	High
88	Low
89	Trades
90	Performance (1 Minute)
91	Performance (2 Minutes)
92	Performance (3 Minutes)
93	Performance (5 Minutes)
94	Performance (10 Minutes)
95	Performance (15 Minutes)
96	Performance (30 Minutes)
97	Performance (1 Hour)
98	Performance (2 Hours)
99	Performance (4 Hours)
100	Asset Type
101	ETF Type
102	Region
103	Single Category
104	Sector/Theme
105	Tags
106	Active/Passive
107	Net Expense Ratio
108	Total Holdings
109	Assets Under Management
110	Net Asset Value
111	Net Asset Value %
112	Net Flows (1 Month)
113	Net Flows % (1 Month)
114	Net Flows (3 Month)
115	Net Flows % (3 Month)
116	Net Flows (YTD)
117	Net Flows % (YTD)
118	Net Flows (1 Year)
119	Net Flows % (1 Year)
120	Return 1 Year
121	Return 3 Year
122	Return 5 Year
123	Return 10 Year
124	Return Since Inception
125	All-Time High
126	All-Time Low
127	EPS Surprise
128	Revenue Surprise
129	Exchange
130	Dividend TTM
131	Dividend Ex Date
132	EPS Year Over Year TTM
133	Sales Year Over Year TTM
134	52-Week Range
135	News Time
136	News URL
137	News Title
138	Performance (3 Years)
139	Performance (5 Years)
140	Performance (10 Years)
141	After-Hours Volume
142	EPS Growth Past 3 Years
143	Sales Growth Past 3 Years
144	Enterprise Value
145	EV/EBITDA
146	EV/Sales
147	Dividend Growth 1 Year
148	Dividend Growth 3 Years
149	Dividend Growth 5 Years