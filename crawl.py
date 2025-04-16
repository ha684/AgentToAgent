#!/usr/bin/env python3
# NCC.asia Web Crawler in Python
# This script crawls the ncc.asia website and extracts data from its pages

import os
import json
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import re
from collections import deque
import concurrent.futures
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ncc_crawler.log'),
        logging.StreamHandler()
    ]
)

class NCCCrawler:
    def __init__(self):
        # Configuration
        self.start_url = 'https://ncc.asia/'
        self.base_url = 'https://ncc.asia'
        self.output_dir = './ncc_data'
        self.max_pages = 500  # Limit number of pages
        self.delay = 1  # Delay between requests in seconds
        self.pages_per_folder = 100
        self.timeout = 30
        self.max_workers = 5  # Number of concurrent workers for requests
        
        # User agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Create a session for persistent connections
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Store visited URLs to avoid duplicates
        self.visited = set()
        # Queue for URLs to visit
        self.queue = deque([self.start_url])
        # Store extracted data
        self.all_data = []
        # Counter for pages
        self.page_counter = 0
        
        # Check robots.txt
        self.robots_parser = RobotFileParser()
        self.robots_parser.set_url(urljoin(self.base_url, '/robots.txt'))
        try:
            self.robots_parser.read()
            logging.info("Successfully parsed robots.txt")
        except Exception as e:
            logging.error(f"Error parsing robots.txt: {e}")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def normalize_url(self, url):
        """Normalize URL by removing fragments, query params, and trailing slashes"""
        parsed = urlparse(url)
        # Remove query parameters and fragments
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        # Remove trailing slash
        if clean_url.endswith('/'):
            clean_url = clean_url[:-1]
        return clean_url
    
    def should_crawl(self, url):
        """Check if URL should be crawled"""
        parsed_url = urlparse(url)
        
        # Check if URL belongs to the same domain
        if not parsed_url.netloc.endswith('ncc.asia'):
            return False
        
        # Check robots.txt
        if not self.robots_parser.can_fetch(self.headers['User-Agent'], url):
            logging.info(f"Skipping {url} as per robots.txt")
            return False
        
        # Skip certain file types
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', 
                           '.xls', '.xlsx', '.zip', '.rar', '.mp4', '.mp3', '.mov']
        if any(parsed_url.path.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip certain paths
        skip_paths = ['/login', '/logout', '/signup', '/search', '/cart', '/checkout']
        if any(path in parsed_url.path.lower() for path in skip_paths):
            return False
        
        return True
    
    def extract_links(self, soup, base_url):
        """Extract links from a page"""
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            # Skip empty links and javascript
            if not href or href.startswith('javascript:') or href == '#':
                continue
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Check if URL should be crawled
            if self.should_crawl(absolute_url):
                links.add(self.normalize_url(absolute_url))
        
        return list(links)
    
    def extract_page_data(self, soup, url):
        """Extract data from a page"""
        # Basic data extraction
        page_data = {
            'url': url,
            'title': soup.title.text.strip() if soup.title else '',
            'description': '',
            'h1_headings': [h1.text.strip() for h1 in soup.find_all('h1')],
            'h2_headings': [h2.text.strip() for h2 in soup.find_all('h2')],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            page_data['description'] = meta_desc['content'].strip()
        
        # Main content extraction
        main_content = soup.find('main') or soup.find(id='content') or soup.find(class_='content') or soup.find('article')
        if main_content:
            page_data['content'] = main_content.get_text(separator=' ', strip=True)
        else:
            # Fallback to body content
            body_content = soup.find('body')
            if body_content:
                page_data['content'] = body_content.get_text(separator=' ', strip=True)[:10000]  # Limit size
            else:
                page_data['content'] = ''
        
        # Extract links with text
        page_data['links'] = []
        for a_tag in soup.find_all('a', href=True):
            link_data = {
                'text': a_tag.get_text(strip=True),
                'href': a_tag['href']
            }
            page_data['links'].append(link_data)
        
        # Extract article specific data
        if soup.find('article') or '/blog/' in url or '/news/' in url:
            page_data['article_data'] = {
                'author': '',
                'date': '',
                'categories': []
            }
            
            # Try to find author
            author_elem = soup.find(class_=['author', 'byline']) or soup.find('meta', attrs={'name': 'author'})
            if author_elem:
                if author_elem.name == 'meta':
                    page_data['article_data']['author'] = author_elem.get('content', '')
                else:
                    page_data['article_data']['author'] = author_elem.text.strip()
            
            # Try to find date
            date_elem = soup.find(class_=['date', 'published']) or soup.find('time')
            if date_elem:
                if date_elem.has_attr('datetime'):
                    page_data['article_data']['date'] = date_elem['datetime']
                else:
                    page_data['article_data']['date'] = date_elem.text.strip()
            
            # Try to find categories/tags
            categories = soup.find(class_=['categories', 'tags', 'category', 'tag'])
            if categories:
                page_data['article_data']['categories'] = [tag.text.strip() for tag in categories.find_all('a')]
        
        # Extract service page data
        if '/services/' in url or '/solutions/' in url:
            service_features = []
            feature_lists = soup.select('.features li, .feature-list li, .services li')
            for item in feature_lists:
                service_features.append(item.text.strip())
            
            page_data['service_data'] = {
                'features': service_features,
                'service_name': soup.h1.text.strip() if soup.h1 else ''
            }
        
        # Extract team/about data
        if '/team/' in url or '/about/' in url:
            team_members = []
            member_elements = soup.select('.team-member, .staff-member, .employee, .member')
            
            for member in member_elements:
                member_data = {
                    'name': '',
                    'position': '',
                    'bio': ''
                }
                
                name_elem = member.find(['h3', 'h4', '.name'])
                if name_elem:
                    member_data['name'] = name_elem.text.strip()
                
                position_elem = member.find(['.position', '.role', '.job-title'])
                if position_elem:
                    member_data['position'] = position_elem.text.strip()
                
                bio_elem = member.find(['.bio', '.description', '.about'])
                if bio_elem:
                    member_data['bio'] = bio_elem.text.strip()
                
                team_members.append(member_data)
            
            if team_members:
                page_data['team_data'] = team_members
        
        return page_data
    
    def save_data(self, data):
        """Save data to a file"""
        # Calculate folder name based on counter
        folder_index = self.page_counter // self.pages_per_folder
        output_folder = os.path.join(self.output_dir, f'batch_{folder_index}')
        
        # Ensure folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        # Create a safe filename based on URL
        parsed_url = urlparse(data['url'])
        path = parsed_url.path.replace('/', '_')
        if not path or path == '_':
            path = 'index'
        filename = f"{path}.json"
        
        # Save data to JSON file
        with open(os.path.join(output_folder, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Also append to all_data list
        self.all_data.append(data)
        
        # Periodically save all data to a single file
        if self.page_counter % 20 == 0 or self.page_counter >= self.max_pages:
            with open(os.path.join(self.output_dir, 'all_data.json'), 'w', encoding='utf-8') as f:
                json.dump(self.all_data, f, ensure_ascii=False, indent=2)
    
    def crawl_url(self, url):
        """Crawl a single URL"""
        try:
            logging.info(f"Crawling: {url}")
            
            # Send request
            response = self.session.get(url, timeout=self.timeout)
            
            # Check if request was successful
            if response.status_code != 200:
                logging.warning(f"Failed to fetch {url}: Status code {response.status_code}")
                return None
            
            # Check content type to make sure it's HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logging.info(f"Skipping non-HTML content: {url}")
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data
            page_data = self.extract_page_data(soup, url)
            
            # Save data
            self.save_data(page_data)
            
            # Extract links for further crawling
            links = self.extract_links(soup, url)
            
            # Return new links
            return links
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {url}: {e}")
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")
        
        return None
    
    def run(self):
        """Run the crawler"""
        logging.info(f"Starting crawl from {self.start_url}")
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                while self.queue and self.page_counter < self.max_pages:
                    # Get next batch of URLs to process
                    batch_size = min(self.max_workers, len(self.queue))
                    current_batch = []
                    
                    for _ in range(batch_size):
                        if self.queue:
                            url = self.queue.popleft()
                            # Skip if already visited
                            if url in self.visited:
                                continue
                            self.visited.add(url)
                            current_batch.append(url)
                    
                    if not current_batch:
                        continue
                    
                    # Process batch
                    future_to_url = {executor.submit(self.crawl_url, url): url for url in current_batch}
                    
                    for future in concurrent.futures.as_completed(future_to_url):
                        url = future_to_url[future]
                        self.page_counter += 1
                        
                        try:
                            new_links = future.result()
                            if new_links:
                                # Add new links to queue
                                for link in new_links:
                                    if link not in self.visited:
                                        self.queue.append(link)
                        except Exception as e:
                            logging.error(f"Error processing {url}: {e}")
                        
                        logging.info(f"Progress: {self.page_counter}/{self.max_pages}")
                    
                    # Be nice to the server
                    time.sleep(self.delay)
            
            logging.info(f"Crawl complete. Processed {self.page_counter} pages.")
            
            # Save final data
            with open(os.path.join(self.output_dir, 'all_data.json'), 'w', encoding='utf-8') as f:
                json.dump(self.all_data, f, ensure_ascii=False, indent=2)
                
        except KeyboardInterrupt:
            logging.info("Crawl interrupted by user.")
            # Save data before exiting
            with open(os.path.join(self.output_dir, 'all_data.json'), 'w', encoding='utf-8') as f:
                json.dump(self.all_data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logging.error(f"Fatal error: {e}")

def main():
    if os.path.exists("./ncc_data/ncc_data.txt"):
        logging.info("File already exists.")
        return
    crawler = NCCCrawler()
    crawler.run()
    with open("./ncc_data/all_data.json", "r",encoding="utf8") as f:
        data = json.load(f)
    
    txt = data[0]["content"]
    
    with open("./ncc_data/ncc_data.txt","w",encoding="utf8") as f:
        f.write(txt)

if __name__ == "__main__":
    main()