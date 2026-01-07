# Skill: Web Search

This skill provides Miyori with the ability to access real-time information from the internet.

## Web Search Tool (`web_search`)
Used to supplement the agent's knowledge with up-to-date facts, news, and technical documentation not available in its training data or local memory.

### Implementation:
- **Backend**: Uses the `DDGS` (DuckDuckGo Search) library for anonymous, privacy-respecting search results.
- **Location**: `src/miyori/tools/web_search.py`.

### Parameters:
- `query`: The search string.
- `num_results`: Number of results to return (Default: 3, Max: 10).

### Output Format:
Returns a formatted string containing:
1. Title of the page.
2. Snippet/Summary of the content.
3. URL for attribution.

### Best Practices:
- **Contextual Search**: Use specific queries to get targeted technical information.
- **Verification**: If information from the web seems contradictory to local memory, document the discrepancy in a new episodic memory.
- **Latency**: Be mindful that web searches add a few seconds to the response time.
