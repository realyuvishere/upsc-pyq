import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Store the input URL in a separate variable
INPUT_URLS = ["https://www.upsc.gov.in/examinations/previous-question-papers"]

# Folder to store the PDFs
OUTPUT_FOLDER = "PYQs"

def fetch_and_save_pdfs(url):
    # Create the output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Fetch the HTML content of the page
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Handle both normal and archives page structures
    # Archives page uses view-grouping-header for year, then a table for that year
    view_groupings = soup.find_all("div", class_="view-grouping")
    if view_groupings:
        for grouping in view_groupings:
            year_header = grouping.find("div", class_="view-grouping-header")
            if not year_header:
                continue
            import re
            year_match = re.search(r"(20\d{2}|19\d{2})", year_header.text)
            year = year_match.group(1) if year_match else "UnknownYear"
            tables = grouping.find_all("table")
            for table in tables:
                caption = table.find("caption")
                if not caption or "Civil Services" not in caption.text:
                    continue
                phase = "Mains" if "Main" in caption.text else "Prelims" if "Prelim" in caption.text else "UnknownPhase"
                rows = table.find_all("tr")
                for row in rows:
                    tds = row.find_all("td")
                    if len(tds) < 2:
                        continue
                    category = tds[0].get_text(strip=True)
                    # The <ul> may be in td[2] or td[1] depending on structure
                    ul = None
                    for td in tds[1:]:
                        ul = td.find("ul")
                        if ul:
                            break
                    if not ul:
                        continue
                    for li in ul.find_all("li"):
                        time.sleep(1)
                        a = li.find("a", href=True)
                        if a and a["href"].endswith(".pdf"):
                            title = a.previous_sibling.strip() if a.previous_sibling else a.get_text(strip=True)
                            # Clean up title, category, and year for folder and filename
                            clean_title = title.replace("/", "-").replace(" ", "_").replace("__", "_")
                            clean_category = category.replace("/", "-").replace(" ", "_").replace("__", "_")
                            clean_year = year.replace("/", "-").replace(" ", "_").replace("__", "_")
                            subfolder = os.path.join(OUTPUT_FOLDER, clean_year, clean_category)
                            if not os.path.exists(subfolder):
                                os.makedirs(subfolder)
                            filename = f"{clean_title}_{phase}_{year}_{clean_category}.pdf"
                            filepath = os.path.join(subfolder, filename)
                            pdf_url = urljoin(url, a["href"])
                            download_pdf(pdf_url, filepath)
        return

    # Fallback to original structure for non-archives pages
    tables = soup.find_all("table")
    for table in tables:
        caption = table.find("caption")
        if caption and "Civil Services" in caption.text:
            phase = "Mains" if "Main" in caption.text else "Prelims" if "Prelim" in caption.text else "UnknownPhase"
            rows = table.find_all("tr")
            for row in rows:
                tds = row.find_all("td")
                if len(tds) < 2:
                    continue
                category = tds[0].get_text(strip=True)
                ul = tds[1].find("ul")
                if not ul:
                    continue
                for li in ul.find_all("li"):
                    time.sleep(1)
                    a = li.find("a", href=True)
                    if a and a["href"].endswith(".pdf"):
                        title = a.previous_sibling.strip() if a.previous_sibling else a.get_text(strip=True)
                        # Try to extract year from caption or title
                        year = None
                        import re
                        year_match = re.search(r"\b(20\d{2}|19\d{2})\b", caption.text)
                        if year_match:
                            year = year_match.group(1)
                        else:
                            year_match = re.search(r"\b(20\d{2}|19\d{2})\b", title)
                            if year_match:
                                year = year_match.group(1)
                        if not year:
                            year = "UnknownYear"
                        clean_title = title.replace("/", "-").replace(" ", "_").replace("__", "_")
                        clean_category = category.replace("/", "-").replace(" ", "_").replace("__", "_")
                        clean_year = year.replace("/", "-").replace(" ", "_").replace("__", "_")
                        subfolder = os.path.join(OUTPUT_FOLDER, clean_year, clean_category)
                        if not os.path.exists(subfolder):
                            os.makedirs(subfolder)
                        filename = f"{clean_title}_{phase}_{year}_{clean_category}.pdf"
                        filepath = os.path.join(subfolder, filename)
                        pdf_url = urljoin(url, a["href"])
                        download_pdf(pdf_url, filepath)

def download_pdf(pdf_url, filepath):
    response = requests.get(pdf_url, stream=True)
    if response.status_code == 200:
        with open(filepath, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)
        print(f"Downloaded: {filepath}")
    else:
        print(f"Failed to download {pdf_url}. Status code: {response.status_code}")

if __name__ == "__main__":
    for url in INPUT_URLS:
        fetch_and_save_pdfs(url)