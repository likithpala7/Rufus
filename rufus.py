from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from crawler import WebCrawler
import ast
import asyncio
import json

class RufusClient:
    def __init__(self, model, logging):
        self.model = model
        self.logging = logging
        self.llm = ChatOllama(model=model, device="cuda")

    def scrape(self, instructions, website, depth=2, crawl_strategy="BFS", max_concurrent_requests=10):
        self.instructions = instructions
        self.website = website
        crawler = WebCrawler(base_url=self.website, depth_limit=depth, crawl_strategy=crawl_strategy, max_concurrent_requests=max_concurrent_requests, logging=self.logging)

        print("Crawling website...")
        webpage_dict = asyncio.run(crawler.crawl())

        print("Filtering relevant links...")
        filtered_links = self._filter_relevant_links(webpage_dict)
        while len(filtered_links) > 20:
            filtered_links = self._filter_relevant_links(filtered_links)

        print("Generating structured output...")
        json_output = []
        for link, (title, content) in filtered_links.items():
            output = self._info_to_output(link, title, content)
            json_output.append(output)
        return json_output
        

    def _get_relevance_score(self, title, content):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a helpful assistant that will take in a URL, title, content, instructions, and keywords and provide a relevance score 
                    based on the relevance of the URL, title, and content to the instructions provided. If you do not think that the webpage would contain 
                    information that the instructions are looking for, be sure to give the link a low score. Make sure to provide a score from 0-10 where 0 is not 
                    relevant at all and 10 is extremely relevant. The relevance score should be based on the relevance of the URL, title, and content, 
                    to the instructions provided. Be as accurate as possible. If there is no title or no content for the URL, give a score of 0.
                    You must only return a number that is the score and no other text. Be very critical in your judgement.
                    """
                ),
                (
                    "human",
                    """
                    Instructions: {instructions}
                    
                    URL: {url}
                    Title: {title}
                    Content: {content}  # Limit content length for prompt efficiency
                    """
                ),
            ]
        )
        chain = prompt | self.llm
        response = chain.invoke(
            {
                "instructions": self.instructions,
                "url": self.website,
                "title": title,
                "content": content,
            }
        )
        return float(response.content)
    
    def _filter_relevant_links(self, links_dict, threshold=8):
        relevant_links = {}
        for link, (title, content) in links_dict.items():
            score = self._get_relevance_scoreget_relevance_score(title, content[:500])
            print(score)
            if score >= threshold:
                relevant_links[link] = (title, content)
        return relevant_links
    
    def _info_to_output(self, url, title, content):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a helpful assistant that will take in an instruction, URL, title, and content and provide a structured output in the format of a JSON object. The JSON object 
                    should contain 3 keys: "section", "content", and "url". The "section" key should contain a one word string that describes the section of the website 
                    that the content is from. You should describe the content accurately and descriptively as it pertains to the instruction. The "url" key should contain the URL 
                    of the website. If the content of the website does not have information that the instructions are looking for, you should provide an empty string for the "section" and "content" keys. You should 
                    attempt to do this job in the most accurate way possible. You must only return the JSON object and no other text.
                    """
                ),
                (
                    "human",
                    """
                    Instructions: {instructions}
                    
                    URL: {url}
                    Title: {title}
                    Content: {content}
                    """
                ),
            ]
        )
        chain = prompt | self.llm
        response = chain.invoke(
            {
                "instructions": self.instructions,
                "url": url,
                "title": title,
                "content": content,
            }
        )
        return json.loads(response.content)