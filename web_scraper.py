import requests
from bs4 import BeautifulSoup

def search_web(query):
    # Use a search engine to get search results, for example, using Bing or Google search
    query = query.replace(" ", "+")  # Format the query for a URL
    url = f"https://www.bing.com/search?q={query}"

    try:
        # Perform the web request and parse the HTML
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract top links from the search results
        links = []
        for link in soup.find_all("a", href=True):
            href = link['href']
            if href.startswith('http'):
                links.append(href)

        # Prepare a summary of the search results
        summary = f"Top links for '{query}':\n" + "\n".join(links[:5])  # Limit to top 5 results
        return summary
    except Exception as e:
        print(f"Error during web search: {e}")
        return "Sorry, I couldn't fetch search results. Please try again later."
