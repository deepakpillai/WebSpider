# WebSpider

Welcome to WebSpider! This project is a comprehensive web crawler designed to index large portions of the internet efficiently and effectively. You can retrieve the data based on semantic similarity. Below, you'll find an overview of what WebSpider does, how it works, and how you can get started.

<img align="left" src="https://github.com/deepakpillai/WebSpider/blob/main/spider_banner.jpg?raw=true" width="100%"/>
<br />
<br />
## Features

- **Efficient Crawling:** WebSpider uses advanced techniques to crawl websites quickly while respecting the robots.txt rules.
- **Sitemap Integration:** Automatically fetches and parses sitemap.xml files to gather URLs and metadata.
- **Dynamic User-Agent Rotation:** Uses a pool of user-agents to avoid detection and prevent server overload.
- **Unicode Handling:** Properly handles and converts Unicode escape sequences to ensure accurate data extraction.
- **Intelligent Queuing:** Prioritizes URLs within the same domain and efficiently manages the crawling queue.
- **Metadata Extraction:** Extracts essential metadata such as titles, descriptions, last modified dates, and change frequency.
- **Database Integration:** Saves crawled data in a structured format, ready for database insertion. 

## Installation

To get started with WebSpider, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/webspider.git
cd webspider
pip install -r requirements.txt
```

## Usage
To run the WebSpider, simply execute the main script:

```bash

python app.py
```
The crawler will start indexing the internet from a predefined list of seed URLs. You can customize the seed URLs in the script as per your requirements.

## Code Overview
<br />
Here is a brief overview of the main components of the WebSpider:

- **Crawling Logic:** The crawl function handles the core crawling process, fetching pages, extracting metadata, and managing the crawling queue.
- **Sitemap Handling:** Functions like get_sitemap_data and parse_sitemap_data are responsible for fetching and parsing sitemap.xml files.
- **User-Agent Management:** The get_useragent function randomly selects a user-agent from a list to avoid detection.
- **Unicode Handling:** The convert_unicode_escape function ensures that Unicode escape sequences are properly converted.
- **Database Integration:** The do_db function (imported from the db module) saves crawled data in a structured format.

## Contributing
We welcome contributions! If you have ideas for new features, optimizations, or bug fixes, feel free to open an issue or submit a pull request.

## License
This project is licensed under the Apache 2.0 License.

Acknowledgments
Special thanks to all the open-source projects and contributors who made this project possible.

Happy crawling with WebSpider!
