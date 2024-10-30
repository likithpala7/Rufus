from rufus import RufusClient

model = "llama3.2"
logging = False

client = RufusClient(model, logging)
instructions = "We're making a chatbot for the HR in San Francisco."
website = "https://www.sf.gov/"
output = client.scrape(instructions, website)
print(output)