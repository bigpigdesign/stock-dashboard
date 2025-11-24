import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# -------------------------
# FTSE 100 Reference List
# -------------------------
ftse100 = [
    ("III.L", "3i Group plc"),
    ("ADM.L", "Admiral Group plc"),
    ("AAF.L", "Airtel Africa plc"),
    ("AAL.L", "Anglo American plc"),
    ("ANTO.L", "Antofagasta plc"),
    ("AST.L", "Ashtead Group plc"),
    ("ABF.L", "Associated British Foods plc"),
    ("AZN.L", "AstraZeneca plc"),
    ("AUTO.L", "Auto Trader Group plc"),
    ("AV.L", "Aviva plc"),
    ("BAB.L", "Babcock International Group plc"),
    ("BA.L", "BAE Systems plc"),
    ("BARC.L", "Barclays plc"),
    ("BTRW.L", "Barratt Redrow plc"),
    ("BEZ.L", "Beasy plc"),
    ("BKG.L", "Berkley Group Holdings plc"),
    ("BP.L", "BP plc"),
    ("BATS.L", "British American Tobacco plc"),
    ("BT-A.L", "BT Group plc"),
    ("BNZL.L", "Bunzl plc"),
    ("BRBY.L", "Burberry Group plc"),
    ("CNA.L", "Centrica plc"),
    ("CCEP.L", "Coca-Cola Europacific Partners plc"),
    ("CPG.L", "Compass Group plc"),
    ("CRDA.L", "Croda International plc"),
    ("DCC.L", "DCC plc"),
    ("DGE.L", "Diageo plc"),
    ("EZJ.L", "EasyJet plc"),
    ("EXPN.L", "Experian plc"),
    ("FRES.L", "Fresnillo plc"),
    ("GLEN.L", "Glencore plc"),
    ("GSK.L", "GlaxoSmithKline plc"),
    ("HLN.L", "Haleon plc"),
    ("HLMA.L", "Halma plc"),
    ("HIK.L", "Hikma Pharmaceuticals plc"),
    ("HSBA.L", "HSBC Holdings plc"),
    ("IMI.L", "IMI plc"),
    ("IMB.L", "Imperial Brands plc"),
    ("INF.L", "Informa plc"),
    ("IAG.L", "International Airlines Group plc"),
    ("ITRK.L", "Intertek Group plc"),
    ("JD.L", "JD Sports Fashion plc"),
    ("KGF.L", "Kingfisher plc"),
    ("LAND.L", "Land Securities Group plc"),
    ("LGEN.L", "Legal & General Group plc"),
    ("LLOY.L", "Lloyds Banking Group plc"),
    ("LMP.L", "LondonMetric Property plc"),
    ("LSEG.L", "London Stock Exchange Group plc"),
    ("MNG.L", "M&G plc"),
    ("MKS.L", "Marks & Spencer Group plc"),
    ("MRO.L", "Melrose Industries plc"),
    ("MNDI.L", "Mondi plc"),
    ("NG.L", "National Grid plc"),
    ("NXT.L", "Next plc"),
    ("PSON.L", "Pearson plc"),
    ("PHNX.L", "Phoenix Group plc"),
    ("PRU.L", "Prudential plc"),
    ("RKT.L", "Reckitt plc"),
    ("REL.L", "RELX plc"),
    ("RTO.L", "Rentokill Initial plc"),
    ("RMV.L", "Rightmove plc"),
    ("RIO.L", "Rio Tinto plc"),
    ("RR.L", "Rolls-Royce Holdings plc"),
    ("RDSA.L", "Shell plc"),
    ("TSCO.L", "Tesco plc"),
    ("VOD.L", "Vodafone Group plc")
]

# -------------------------
# Dashboard Title & Refresh
# -------------------------
st.title("UK Stock Prices Dashboard")

if st.button("Refresh Now 🔄"):
    st.rerun()

# -------------------------
# Persistent 5 dropdowns (single row)
# -------------------------
if "tickers" not in st.session_state:
    st.session_state.tickers = ["AV.L", "VOD.L", "BP.L", "LLOY.L", ""]

st.write("### Select up to 5 UK stock tickers")

cols = st.columns(5)
new_tickers = []

# Create a mapping of code -> name for lookup
ftse_dict = dict(ftse100)

for i in range(5):
    with cols[i]:
        # Display code without '.L'
        options = [f"{code.replace('.L','')} - {name}" for code, name in ftse100]
        default = st.session_state.tickers[i].replace(".L","") if st.session_state.tickers[i] else None
        # Determine default index
        default_index = 0
        if default:
            for idx, option in enumerate(options):
                if option.startswith(default):
                    default_index = idx
                    break
        selection = st.selectbox(
            f"Stock {i+1}",
            options=options,
            index=default_index,
            key=f"ticker_select_{i}"
        )
        # Re-add '.L' for internal yfinance use
        ticker_code = selection.split(" - ")[0] + ".L"
        new_tickers.append(ticker_code)

st.session_state.tickers = new_tickers
tickers = [t for t in new_tickers if t]

if not tickers:
    st.warning("Please select at least one stock.")
    st.stop()

# -------------------------
# Fetch stock data
# -------------------------
@st.cache_data(ttl=30)
def get_stock_data(tickers):
    data = []
    for t in tickers:
        stock = yf.Ticker(t)
        info = stock.fast_info
        last_price = info.get("lastPrice", None)
        change_pct = info.get("regularMarketChangePercent", None)
        if change_pct is None and last_price is not None:
            prev_close = info.get("previousClose", last_price)
            change_pct = ((last_price - prev_close) / prev_close) * 100
        data.append({
            "Ticker": t,
            "Price": last_price,
            "Change %": change_pct
        })
    return pd.DataFrame(data)

df = get_stock_data(tickers)

# -------------------------
# Display metrics
# -------------------------
cols = st.columns(len(tickers))
for i, ticker in enumerate(tickers):
    price = df.loc[df['Ticker'] == ticker, 'Price'].values[0]
    change = df.loc[df['Ticker'] == ticker, 'Change %'].values[0]

 #   delta_color = "normal" if change <= 0 else "inverse"
    cols[i].metric(
        label=ticker.replace(".L",""),
        value=f"{price:.2f}p" if price is not None else "N/A",
        delta=round(change, 2) if change is not None else 0,
        delta_color= "normal"
    )

st.write(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# -------------------------
# FTSE 100 Reference Table
# -------------------------
st.write("### FTSE 100 Stock Reference")
df_ftse = pd.DataFrame(ftse100, columns=["Stock", "Company"])
st.dataframe(df_ftse, height=300, use_container_width=True)
