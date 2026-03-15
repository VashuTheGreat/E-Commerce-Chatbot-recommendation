CHAT_LLM_PROMPT = """
You are an expert product-query generator.
Given a user request and a summary of an image, generate a structured search query.

User Query: {user_query}
Image Summary: {image_summary}

Return the query as a structured output.
"""