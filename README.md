# Rufus Agent

## Summary
Rufus is an agent that is able to crawl webpages and provide relevant information given a prompt and a website. For example, if the instructions are to "Find information about product features and customer FAQs." and the website is "https://www.nike.com/". Rufus will crawl through the website and provide information about the products and customer FAQs in a structured manner. This is an early implementation (PoC) and has many improvements that can be made in terms of accuracy and efficiency.

---

## Approach

### Steps Taken
1. **Initial Research**: I first had to take some time to think about how I would approach this and what would make most sense. I had to research agents and web crawlers that would work as an initial implementation.
2. **Frameworks**: I decided that LangChain, BeautifulSoup, and HTTPX would be the main frameworks that I would use for this task.
3. **Implementation**: There are many heuristics/approaches I could've taken. Given the time constrain, I prioritized finishing the task over the efficiency and accuracy of Rufus. To crawl the web, I used BeautifulSoup that would look for links and would pull their title and content. To make those requests, I used httpx. In order to use only relevant links, I used an LLM to rank the scraped links with respect to relevance to the instructions on a 1-10 scale. I then took the filtered links and used an LLM to output a JSON object that contained 3 keys: section, content, and URL. This JSON object can be used in downstream RAG applications to query on the JSON object.

---

## Challenges Faced
There were 2 main challenges I faced:

### Challenge 1: Webpage Relevance
- **Description**: When crawling the provided webpage, it is important to know which links are useful and when to stop.
- **Solution**: I tried a couple approaches for finding relevant links. I would collect the link itself and the title of the webpage. I used an LLM to generate a number of keywords that were relevant to the original instructions and link that the user provided. I compared the title of the webpage with the keywords and scored the link. If the score was above a certain threshold, I would keep it, or else I would discard it. The issue with this was that the LLM was generating generic keywords that were irrelevant. My current approach uses an LLM to rank the scraped link, title, and content with respect to relevant to the original instructions on a 1-10 scale. If the score is above a certain threshold, I keep the link, or else I discard it. This is also a very basic heuristic and works okay. In regards to when to stop, I used a BFS/DFS method to crawl the websites with a depth factor that is a parameter. I think this works well.

### Challenge 2: Efficiency Issues
- **Description**: Crawling the webpage takes quite a while, depending on the depth parameter and the website that we are crawling.
- **Solution**: I currently don't have a solution in place, however in my time playing around with scrapy, it is at least an order of magnitude faster than httpx.

---


## Future Improvements
I have a lot of improvements in mind. Most of the improvements would be in regards to prompt engineering the LLM to give better outputs. In order to scrape relevant links, I think a better approach would be to embed the title of the webpage and prompt, and do a similarity comparison between them, incorporating the instructions somehow.

---

## Usage

An example of the usage is given in the `main.py` file, but I will replicate it here.
```python
from rufus import RufusClient

model = "llama3.2"
logging = False

client = RufusClient(model, logging)
instructions = "We're making a chatbot for the HR in San Francisco."
website = "https://www.sf.gov/"
output = client.scrape(instructions, website)
print(output)
```

As you can see, the `RufusClient` object takes in the model and logging flag as parameters. The `scrape` function takes in `instructions, website, depth, crawl_strategy, max_concurrent_requests` as parameters. 