import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

# ✅ Predefined Google Dork categories with all relevant queries
DORKS = {
    "Free Stuff (Giveaways, NFTs, Testnet, Free $)": [
        '"free airdrop" OR "crypto airdrop" OR "testnet faucet" site:x.com OR site:medium.com OR site:coinmarketcap.com',
        '"free nft" OR "free mint" OR "nft giveaway" OR "free whitelist" site:twitter.com OR site:opensea.io OR site:discord.com',
        '"free dollars" OR "free crypto" OR "USDT giveaway" OR "claim free BTC" OR "claim free USDT" site:reddit.com OR site:bitcointalk.org',
        '"free testnet tokens" OR "claim testnet" OR "testnet rewards" site:github.com OR site:cointelegraph.com OR site:cryptobriefing.com',
        '"free subscription" OR "free premium account" OR "free trial" OR "promo code" site:github.com OR site:debrid.cc OR site:stackexchange.com'
    ],
    "Invite-Only Events (Launch, Mumbai, Global)": [
        '"invite only event" OR "exclusive launch" OR "private beta" OR "early access" site:eventbrite.com OR site:meetup.com OR site:ticketmaster.com',
        '"private event Mumbai" OR "Mumbai exclusive event" OR "launch party Mumbai" site:insider.in OR site:bookmyshow.com OR site:allevents.in',
        '"invite only crypto event" OR "VIP crypto conference" OR "exclusive blockchain summit" site:coindesk.com OR site:cointelegraph.com',
        '"exclusive global summit" OR "invite-only global event" OR "worldwide blockchain conference" site:forbes.com OR site:bloomberg.com OR site:fortune.com'
    ],
    "Crypto & X.com Related": [
        '"crypto project" OR "new blockchain launch" OR "airdrops" site:x.com OR site:twitter.com OR site:coingecko.com',
        '"crypto giveaways" OR "free Bitcoin" OR "free USDT" OR "token claim" site:x.com OR site:bitcointalk.org OR site:reddit.com/r/cryptocurrency',
        '"new DeFi project" OR "IDO launch" OR "crypto presale" OR "prelaunch token" site:medium.com OR site:coinmarketcap.com OR site:crypto.com',
        '"crypto regulations" OR "Web3 policies" OR "blockchain law" site:sec.gov OR site:europa.eu OR site:gov.in OR site:financialexpress.com'
    ],
    "AI & ML Events & Resources": [
        '"AI summit" OR "machine learning conference" OR "deep learning workshop" site:eventbrite.com OR site:meetup.com OR site:ai.googleblog.com',
        '"AI research papers" OR "latest ML papers" OR "open source AI models" site:arxiv.org OR site:paperswithcode.com OR site:github.com',
        '"AI startup funding" OR "AI startup accelerator" OR "AI investment round" site:techcrunch.com OR site:forbes.com OR site:venturebeat.com',
        '"free AI courses" OR "AI certification free" OR "learn ML online free" site:coursera.org OR site:udacity.com OR site:edx.org'
    ]
}

# ✅ Function to perform Google search
def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    for g in soup.find_all('div', class_='yuRUbf'):
        a = g.find('a', href=True)
        if a:
            links.append(a['href'])
    
    return links

# ✅ Streamlit UI
st.title("🔍 Smart Search: Free Stuff, Invites, Crypto & AI/ML Events")
st.write("Find relevant links automatically using Google Dorking!")

# ✅ Select category or search all
search_all = st.checkbox("Search all categories at once")
if not search_all:
    selected_category = st.selectbox("Choose a category:", list(DORKS.keys()))

# ✅ Search button
if st.button("Search Now"):
    all_links = []
    
    if search_all:
        st.write("🔍 Searching across **all categories**...")
        for category, queries in DORKS.items():
            st.write(f"🔎 Searching: **{category}**...")
            for query in queries:
                try:
                    links = google_search(query)
                    all_links.extend(links)
                except Exception as e:
                    st.warning(f"Error with query: {query}. Error: {e}")
    else:
        st.write(f"🔍 Searching for **{selected_category}**...")
        for query in DORKS[selected_category]:
            try:
                links = google_search(query)
                all_links.extend(links)
            except Exception as e:
                st.warning(f"Error with query: {query}. Error: {e}")

    # ✅ Remove duplicate links
    unique_links = list(set(all_links))
    
    if unique_links:
        st.success(f"✅ Found {len(unique_links)} relevant links!")
        link_text = "\n".join(unique_links)
        st.text_area("Results", link_text, height=300)

        # ✅ Download as text file
        st.download_button("📄 Download as .txt", data=link_text, file_name="search_results.txt", mime="text/plain")

        # ✅ Download as PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for link in unique_links:
            pdf.cell(200, 10, txt=link, ln=True)
        pdf_output = pdf.output(dest='S').encode('latin1')
        st.download_button("📜 Download as .pdf", data=pdf_output, file_name="search_results.pdf", mime="application/pdf")
    else:
        st.warning("⚠ No relevant links found.")

st.write("Created with ❤️ using Streamlit")
