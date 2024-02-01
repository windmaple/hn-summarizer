import json
import httpx
from phi.assistant import Assistant
from tinydb import TinyDB, Query


def get_top_hackernews_stories(num_stories: int = 10) -> str:
    """Use this function to get top stories from Hacker News.

    Args:
        num_stories (int): Number of stories to return. Defaults to 10.

    Returns:
        str: JSON string of top stories.
    """

    # Override num_stories since I don't know where '5' comes from
    num_stories = 50

    # Fetch top story IDs
    response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
    story_ids = response.json()

    db = TinyDB("cache.json")
    # Fetch story details
    stories = []
    Story = Query()
    for story_id in story_ids[:num_stories]:
        query_result = db.search(Story.id == story_id)

        if query_result == []:
            print("hitting HN db")
            story_response = httpx.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            )
            story = story_response.json()
            if "text" in story:
                story.pop("text", None)
            db.insert(story)
        else:
            print("skipping hitting HN db")
            story = query_result
        stories.append(story)
    db.close()

    return json.dumps(stories)


assistant = Assistant(tools=[get_top_hackernews_stories], show_tool_calls=True)
assistant.print_response(
    "Summarize the top stories on hackernews in Chinese, but only include the ones related to articifical intelligence."
)
