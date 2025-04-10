import time
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    service = Service(executable_path='C:\\Users\\ksman\\Music\\edgedriver_win64\\msedgedriver.exe')
    options = webdriver.EdgeOptions()
    # options.add_argument('--headless')  # Disable for debugging
    driver = webdriver.Edge(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    return driver, wait

def create_database():
    conn = sqlite3.connect('ai_articles.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT UNIQUE,
                  url TEXT UNIQUE,
                  summary TEXT,
                  publication_date TEXT)''')
    conn.commit()
    return conn, c

def extract_publication_date(driver):
    """Extract publication date from specific element structure"""
    try:
        date_element = driver.find_element(
            By.CSS_SELECTOR,
            'div.elementor-element-3544cb26 p.elementor-heading-title.elementor-size-default'
        )
        date_text = date_element.text.strip()
        
        try:
            parsed_date = datetime.strptime(date_text, "%B %d, %Y")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            return date_text
            
    except Exception as e:
        print(f"⚠️ Date extraction error: {str(e)[:50]}")
        return None

def get_article_summary(driver, url):
    """Extract both summary and publication date from article page"""
    original_window = driver.current_window_handle
    summary = None  # Initialize as None to identify skipped articles
    pub_date = "Date not found"
    
    try:
        driver.switch_to.new_window('tab')
        print(f"   🌐 Visiting: {url[:60]}...")
        driver.get(url)
        time.sleep(2)

        # Get publication date
        article_page_date = extract_publication_date(driver)
        if article_page_date:
            pub_date = article_page_date
            print(f"   📅 Article page date: {pub_date}")

        # Extract summary
        try:
            summary_container = driver.find_element(
                By.CSS_SELECTOR, 
                '.elementor-element-1bbcd091'
            )
            paragraphs = summary_container.find_elements(By.TAG_NAME, 'p')
            
            if paragraphs:
                clean_paragraphs = [
                    p.text.strip() for p in paragraphs 
                    if p.text.strip() 
                    and len(p.text.strip().split()) > 3
                    and not p.text.strip().startswith(('ADVERTISEMENT', 'Sponsored', 'Sign up'))
                ]
                if clean_paragraphs:  # Only proceed if we have valid paragraphs
                    summary = '\n\n'.join(clean_paragraphs[:8])
                    print(f"   📝 Extracted {len(clean_paragraphs)} summary paragraphs")
                else:
                    print("   ⚠️ No valid content in summary container")
            else:
                print("   ⚠️ No paragraphs found in summary container")
                
        except Exception as e:
            print(f"   🔄 Using fallback summary extraction ({str(e)[:50]})")
            for selector in ['.entry-content', 'article', 'div[itemprop="articleBody"]']:
                try:
                    content = driver.find_element(By.CSS_SELECTOR, selector)
                    paragraphs = content.find_elements(By.TAG_NAME, 'p')
                    if paragraphs:
                        summary = '\n\n'.join([p.text.strip() for p in paragraphs[:5] if p.text.strip()])
                        break
                except:
                    continue
        
    except Exception as e:
        print(f"   🚨 Article page error: {str(e)[:50]}")
    finally:
        driver.close()
        driver.switch_to.window(original_window)
        return summary, pub_date

def get_article_data(driver, wait, max_articles):
    """Main scraping function with full pagination support"""
    articles_data = []
    articles_fetched = 0
    page_num = 1
    consecutive_empty_pages = 0
    max_consecutive_empty = 3  # Stop after this many empty pages
    
    while (articles_fetched < max_articles and 
           consecutive_empty_pages < max_consecutive_empty):
        try:
            # Construct URL for current page
            if page_num == 1:
                url = "https://www.artificialintelligence-news.com/artificial-intelligence-news/"
            else:
                url = f"https://www.artificialintelligence-news.com/artificial-intelligence-news/?e-page-144a33e6={page_num}"
            
            print(f"\n📰 Fetching Page {page_num}: {url}")
            driver.get(url)
            time.sleep(3)  # Allow page to load
            
            # Check if page has articles
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.elementor-widget-theme-post-title')))
                articles = driver.find_elements(By.CSS_SELECTOR, '.elementor-widget-theme-post-title')
                
                if not articles:
                    print("⚠️ No articles found on this page")
                    consecutive_empty_pages += 1
                    page_num += 1
                    continue
                    
                consecutive_empty_pages = 0  # Reset counter if we found articles
                print(f"Found {len(articles)} articles on this page")
                
                # Process articles
                for article in articles:
                    if articles_fetched >= max_articles:
                        break
                        
                    try:
                        title_element = article.find_element(By.CSS_SELECTOR, 'h1.elementor-heading-title a')
                        title = title_element.text.strip()
                        url = title_element.get_attribute('href').strip()
                        
                        # Get listing page publication date (fallback)
                        date_container = article.find_element(
                            By.XPATH, 
                            './preceding::div[contains(@class, "elementor-widget-heading")][1]'
                        )
                        listing_pub_date = date_container.find_element(
                            By.CSS_SELECTOR, 
                            'p.elementor-heading-title'
                        ).text.strip()
                        
                        # Get summary and article page date
                        summary, article_pub_date = get_article_summary(driver, url)
                        
                        # Skip if no summary was extracted
                        if summary is None:
                            print(f"⏩ Skipping article (no summary): {title[:50]}...")
                            continue
                        
                        pub_date = article_pub_date if article_pub_date != "Date not found" else listing_pub_date
                        
                        print(f"\n✅ Final Article Data:")
                        print(f"   Title: {title[:50]}...")
                        print(f"   URL: {url[:50]}...")
                        print(f"   Date: {pub_date}")
                        print(f"   Summary Preview: {summary[:100]}...")
                        
                        articles_data.append((title, url, summary, pub_date))
                        articles_fetched += 1
                        
                    except Exception as e:
                        print(f"⚠️ Article processing error: {str(e)[:50]}")
                        continue
                        
            except Exception as e:
                print(f"⚠️ No articles container found on page {page_num}")
                consecutive_empty_pages += 1
                page_num += 1
                continue
                
            # Move to next page if we still need more articles
            if articles_fetched < max_articles:
                page_num += 1
                
        except Exception as e:
            print(f"🚨 Page loading error: {str(e)[:50]}")
            break
    
    # Final report
    if consecutive_empty_pages >= max_consecutive_empty:
        print(f"\n⚠️ Stopped after {max_consecutive_empty} consecutive empty pages")
    print(f"Total articles scraped: {len(articles_data)} (requested: {max_articles})")
    return articles_data


def print_articles_before_save(articles):
    """Print all articles before saving to database"""
    print("\n" + "="*80)
    print("📋 FINAL ARTICLES TO BE SAVED")
    print("="*80)
    for idx, (title, url, summary, pub_date) in enumerate(articles, 1):
        print(f"\nARTICLE {idx}:")
        print("-"*60)
        print(f"Title: {title}")
        print(f"Date: {pub_date}")
        print(f"URL: {url}")
        print(f"\nSummary Preview:\n{summary[:200]}...")
        print("-"*60)
    print("\n" + "="*80)
    print(f"Total articles ready to save: {len(articles)}")
    print("="*80 + "\n")

def save_to_db(data, cursor, conn):
    """Save articles to database with conflict handling"""
    try:
        print_articles_before_save(data)
        
        if not data:
            print("No articles to save")
            return
        
        save = input("Save these articles to database? (y/n): ").lower()
        if save == 'y':
            cursor.executemany('''INSERT OR IGNORE INTO articles 
                                (title, url, summary, publication_date)
                                VALUES (?, ?, ?, ?)''', data)
            conn.commit()
            print(f"✅ Saved {cursor.rowcount} articles to database")
        else:
            print("🚫 Save cancelled by user")
    except Exception as e:
        print(f"🚨 Database error: {e}")

def scrape_and_save():
    """Main execution function"""
    driver, wait = setup_driver()
    conn, cursor = create_database()
    
    try:
        while True:
            try:
                max_articles = int(input("How many articles would you like to fetch? "))
                if max_articles > 0:
                    break
                print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
        print(f"\n🚀 Starting to fetch {max_articles} articles...")
        article_data = get_article_data(driver, wait, max_articles)
        
        if article_data:
            save_to_db(article_data, cursor, conn)
        else:
            print("❌ No articles were fetched")
            
    except Exception as e:
        print(f"🚨 Critical error: {e}")
    finally:
        conn.close()
        driver.quit()
        print("\n🏁 Scraping completed")

if __name__ == "__main__":
    scrape_and_save()