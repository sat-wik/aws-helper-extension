from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tqdm import tqdm
import json
import time

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
)
service = Service("/opt/homebrew/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)


def fetch_left_menu_links(url):
    """
    Fetch all links from the left-hand side menu of an AWS user guide webpage.
    Specifically, look within the 'doc-page-toc' div.
    """
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='doc-page-toc']"))
        )

        # Find the 'doc-page-toc' container
        toc_div = driver.find_element(By.CSS_SELECTOR, "div[data-testid='doc-page-toc']")

        # Extract all links within the list
        link_elements = toc_div.find_elements(By.TAG_NAME, "a")
        links = [
            link.get_attribute("href")
            for link in link_elements
            if link.get_attribute("href")  # Ensure the href attribute is not None
        ]

        return links
    except TimeoutException:
        print(f"Timeout while loading {url}")
        return []
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")
        return []


def scrape_main_col_body(url, retries=3):
    """
    Scrape the content inside the 'main-col-body' div of a page.
    Includes retry logic with timeout adjustment and debugging.
    """
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempting to scrape: {url} (Attempt {attempt}/{retries})")
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "main-col-body"))
            )
            main_col_body = driver.find_element(By.ID, "main-col-body").text
            print(f"Successfully scraped content from {url}.")
            return {"url": url, "content": main_col_body.strip()}
        except TimeoutException:
            print(f"Timeout while loading {url} (Attempt {attempt}/{retries})")
            if attempt < retries:
                driver.refresh()
        except NoSuchElementException:
            print(f"'main-col-body' not found on {url}")
            return {"url": url, "content": ""}
        except Exception as e:
            print(f"Error scraping {url} (Attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                driver.refresh()
        time.sleep(2)

    print(f"Failed to load content from {url} after {retries} attempts.")
    return {"url": url, "content": ""}


def scrape_aws_user_guide(base_url):
    """
    Fetch links from the left-hand side menu of the AWS user guide and scrape
    the content of each link from the 'main-col-body' div.
    """
    # Step 1: Get all links from the left-hand side menu
    print(f"Fetching links from left-hand side menu at {base_url}...")
    links = fetch_left_menu_links(base_url)
    print(f"Found {len(links)} links in the left menu.")

    scraped_data = []

    # Step 2: Scrape the content of each link
    for link in tqdm(links, desc="Scraping progress"):
        page_data = scrape_main_col_body(link)
        if page_data["content"]:
            scraped_data.append(page_data)

    return scraped_data


# Main execution
if __name__ == "__main__":
    BASE_URL = "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/what-is-ec2.html"
    try:
        scraped_data = scrape_aws_user_guide(BASE_URL)
        with open("scraped_data.json", "w") as f:
            json.dump(scraped_data, f, indent=4)
        print(f"Scraping completed! Data saved to 'scraped_data.json'.")
    finally:
        driver.quit()
