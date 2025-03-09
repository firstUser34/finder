import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import re

def google_dork_search(query, max_results=10):
    """Search for events using Google Dorking."""
    results = []
    try:
        url = f"https://www.google.com/search?q={query}&num={max_results}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.text, "html.parser")
        for g in soup.find_all("div", class_="tF2Cxc"):
            title = g.find("h3").text if g.find("h3") else "No Title"
            link = g.find("a")["href"] if g.find("a") else "No Link"
            if re.search(r"(lu\.ma|luma|lu\.ma/[a-zA-Z0-9]+)", link):
                results.append({"title": title, "link": link})
        return results
    except Exception as e:
        st.error(f"Google search failed: {e}")
        return results

def scrape_events(url, filter_word):
    """Generic function to scrape events from a website with error handling."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True) if filter_word in a['href']]
    except Exception as e:
        st.warning(f"Failed to fetch events from {url}: {e}")
        return []

def aggregate_results():
    """Fetch events from multiple platforms with fault tolerance."""
    sources = {
        "BookMyShow": ("https://in.bookmyshow.com/explore/events-mumbai", "/events/"),
        "Eventbrite": ("https://www.eventbrite.com/d/india--mumbai/events/", "/e/"),
        "Luma": ("https://lu.ma/mumbai", "lu.ma"),
        "Insider": ("https://insider.in/mumbai", "/event/"),
        "Tripoto": ("https://www.tripoto.com/mumbai", "/mumbai/events/"),
        "Explara": ("https://explara.com/events/mumbai", "/events/"),
        "MeraEvents": ("https://www.meraevents.com/events/mumbai", "/events/")
    }
    all_links = []
    for name, (url, keyword) in sources.items():
        links = scrape_events(url, keyword)
        if links:
            all_links.extend(links)
        else:
            st.warning(f"No events found on {name}, trying other sources...")
    return all_links

def create_pdf(links, filename="event_links.pdf"):
    """Create a PDF with event links."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Event Links", ln=True, align="C")
    pdf.ln(10)
    for idx, link in enumerate(links, start=1):
        pdf.multi_cell(0, 10, txt=f"{idx}. {link}", border=0)
        pdf.ln(2)
    return pdf.output(dest="S").encode("latin1")

st.title("Smart Event Finder")
st.sidebar.header("Search Filters")
search_keywords = st.sidebar.text_input("Enter keywords:", "Mumbai events")
max_results = st.sidebar.slider("Number of Google Results", 5, 50, 10)
selected_date = st.date_input("Pick a date:", datetime.today())
formatted_date = selected_date.strftime("%Y-%m-%d")
free_only = st.sidebar.checkbox("Show only free events")

if st.sidebar.button("Search Events"):
    st.write(f"Searching events using Google Dork and aggregating from various sources...")
    google_query = f'site:lu.ma OR inurl:lu.ma "{search_keywords}" after:{formatted_date}'
    links = google_dork_search(google_query, max_results)
    event_links = aggregate_results()
    links.extend(event_links)
    links = list(set(links))  # Remove duplicates
    
    if free_only:
        links = [link for link in links if "free" in link.lower()]  # Basic filtering for free events
    
    if links:
        st.success(f"Found {len(links)} events!")
        for idx, link in enumerate(links, start=1):
            st.markdown(f"{idx}. [{link}]({link})", unsafe_allow_html=True)
        pdf_data = create_pdf(links)
        st.download_button("Download PDF", data=pdf_data, file_name="events.pdf", mime="application/pdf")
        st.download_button("Download .txt", data="\n".join(links), file_name="events.txt", mime="text/plain")
    else:
        st.warning("No events found. Try different keywords.")
st.write("Created with ❤️ using Streamlit")
