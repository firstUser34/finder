import streamlit as st
import requests
from time import sleep
import random
from fpdf import FPDF
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

# ✅ Google Dorks Categories
DORKS = {
    "Free Stuff (Giveaways, NFTs, Testnet, Free $)": [
        '"free airdrop" OR "crypto airdrop" OR "testnet faucet"',
        '"free nft" OR "free mint" OR "nft giveaway" OR "free whitelist"',
        '"free dollars" OR "free crypto" OR "USDT giveaway" OR "claim free BTC" OR "claim free USDT"',
        '"free testnet tokens" OR "claim testnet" OR "testnet rewards"',
        '"free subscription" OR "free premium account" OR "free trial" OR "promo code"',
    ],
    "Invite-Only Events (Launch, Mumbai, Global)": [
        '"invite only event" OR "exclusive launch" OR "private beta" OR "early access"',
        '"private event Mumbai" OR "Mumbai exclusive event" OR "launch party Mumbai"',
        '"invite only crypto event" OR "VIP crypto conference" OR "exclusive blockchain summit"',
        '"exclusive global summit" OR "invite-only global event" OR "worldwide blockchain conference"',
    ],
    "Crypto & X.com Related": [
        '"crypto project" OR "new blockchain launch" OR "airdrops"',
        '"crypto giveaways" OR "free Bitcoin" OR "free USDT" OR "token claim"',
        '"new DeFi project" OR "IDO launch" OR "crypto presale" OR "prelaunch token"',
        '"crypto regulations" OR "Web3 policies" OR "blockchain law"',
    ],
    "AI & ML Events & Resources": [
        '"AI summit" OR "machine learning conference" OR "deep learning workshop"',
        '"AI research papers" OR "latest ML papers" OR "open source AI models"',
        '"AI startup funding" OR "AI startup accelerator" OR "AI investment round"',
        '"free AI courses" OR "AI certification free" OR "learn ML online free"',
    ]
}

# ✅ Relevant websites for specific categories
CATEGORY_SITES = {
    "Free Stuff (Giveaways, NFTs, Testnet, Free $)": ["google.com"],
    "Invite-Only Events (Launch, Mumbai, Global)": ["google.com", "eventbrite.com", "meetup.com"],
    "Crypto & X.com Related": ["google.com", "coindesk.com", "cointelegraph.com", "crypto.com", "x.com"],
    "AI & ML Events & Resources": ["google.com", "forbes.com", "bloomberg.com", "fortune.com"]
}

# ✅ Function to perform Google search using Playwright (headless browser)
def google_search_playwright(query, site=None):
    if site:
        query = f"{query} site:{site}"
    search_query = quote_plus(query)
    url = f"https://www.google.com/search?q={search_query}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) #Headless browser
            page = browser.new_page()
            page.goto(url, timeout=60000) #Increased timeout.
            page.wait_for_selector('div.yuRUbf', timeout=60000) #Increased timeout.
            results = page.eval_on_selector_all('div.yuRUbf', lambda elements: [
                {'url': el.querySelector('a').href, 'title': el.querySelector('h3').textContent}
                for el in elements if el.querySelector('a') and el.querySelector('h3')
            ])
            browser.close()
            return results

    except Exception as e:
        st.warning(f"❌ Playwright Search Failed: {query}. Error: {e}")
        return []

# ✅ Streamlit UI
st.title("🔍 Smart Search: Free Stuff, Invites, Crypto & AI/ML Events")
st.write("Find relevant links automatically using Google Dorking!")

# ✅ Select category
selected_category = st.selectbox("Choose a category:", list(DORKS.keys()))

# ✅ Search button
if st.button("Search Now"):
    st.write(f"🔍 Searching for **{selected_category}**...")
    all_links = []

    # ✅ Get relevant sites for the category
    relevant_sites = CATEGORY_SITES[selected_category]

    for query in DORKS[selected_category]:
        # ✅ Search Google globally first
        st.write(f"🔍 Searching Google: {query}")
        links = google_search_playwright(query)
        all_links.extend(links)
        sleep(random.randint(3, 7))

        # ✅ Search only relevant sites, not all
        for site in relevant_sites:
            if site != "google.com":
                st.write(f"🔍 Searching {site}: {query}")
                links = google_search_playwright(query, site)
                all_links.extend(links)
                sleep(random.randint(3, 7))

    # ✅ Remove duplicate links
    unique_links = []
    seen_urls = set()
    for link_data in all_links:
        if link_data['url'] not in seen_urls:
            unique_links.append(link_data)
            seen_urls.add(link_data['url'])

    if unique_links:
        st.success(f"✅ Found {len(unique_links)} relevant links!")
        link_text = "\n".join([f"{link['title']}: {link['url']}" for link in unique_links])
        st.text_area("Results", link_text, height=300)

        # ✅ Download as text file
        st.download_button("📄 Download as .txt", data=link_text, file_name="search_results.txt", mime="text/plain")

        # ✅ Download as PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for link in unique_links:
            pdf.cell(200, 10, txt=f"{link['title']}: {link['url']}", ln=True)
        pdf_output = pdf.output(dest='S').encode('latin1')
        st.download_button("📜 Download as .pdf", data=pdf_output, file_name="search_results.pdf", mime="application/pdf")
    else:
        st.warning("⚠ No relevant links found.")

st.write("Created with ❤️ using Streamlit")
