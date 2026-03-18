import json
import os
import re
from typing import Dict, List

import anthropic


class NewsClassifier:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def select_top_ai_news(self, articles: List[Dict]) -> List[Dict]:
        """Use Claude to rank AI news and always fall back safely on failure."""
        if not articles:
            return []

        candidates = articles[:80]
        articles_text = "\n\n".join(
            [
                (
                    f"[{i + 1}] Title: {a['title']}\n"
                    f"URL: {a['url']}\n"
                    f"Source: {a['source']}\n"
                    f"Published: {a.get('published_at', '')}\n"
                    f"Summary: {a.get('summary', '')[:200]}"
                )
                for i, a in enumerate(candidates)
            ]
        )

        print("Selecting top AI news with Claude...")

        prompt = f"""
From the article list below, pick the top 20 AI news items and return JSON only.

Rules:
- Return exactly 20 items when possible.
- Assign category "latest" to ranks 1-10.
- Assign category "japan" to ranks 11-15.
- Assign category "overseas" to ranks 16-20.
- Favor recency, importance, and direct relevance to AI.
- Prefer Japanese articles in the "japan" section and overseas articles in the "overseas" section.
- Rewrite title and summary in natural Japanese.
- Keep summary_ja around 120-180 Japanese characters.
- point should be a short Japanese bullet-like takeaway.

Return this JSON shape only:
{{
  "selected": [
    {{
      "rank": 1,
      "category": "latest",
      "index": 1,
      "title_ja": "Japanese title",
      "source": "Source name",
      "url": "https://example.com",
      "summary_ja": "Japanese summary",
      "point": "Short Japanese takeaway"
    }}
  ]
}}

Articles:
{articles_text}
"""

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=6000,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            print(f"Claude API error: {e}")
            return _fallback_selection(candidates)

        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text = block.text
                break

        try:
            json_match = re.search(r"\{[\s\S]*\}", response_text)
            if not json_match:
                print("Failed to find JSON in Claude response:", response_text[:300])
                return _fallback_selection(candidates)

            data = json.loads(json_match.group())
            selected = data.get("selected", [])

            result = []
            for item in selected:
                idx = item.get("index", 0) - 1
                if 0 <= idx < len(candidates):
                    original = candidates[idx].copy()
                    original["rank"] = item.get("rank", len(result) + 1)
                    original["category"] = item.get("category", "latest")
                    original["title"] = item.get("title_ja", original["title"])
                    original["summary"] = item.get("summary_ja", original.get("summary", ""))
                    original["point"] = item.get("point", "")
                    result.append(original)

            print(f"Selected {len(result)} articles")
            return result or _fallback_selection(candidates)

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print("Response:", response_text[:500])
            return _fallback_selection(candidates)
        except Exception as e:
            print(f"Unexpected classifier error: {e}")
            return _fallback_selection(candidates)


def _fallback_selection(articles: List[Dict]) -> List[Dict]:
    """Fallback selection when Claude is unavailable."""
    result = []
    for i, article in enumerate(articles[:20]):
        article = article.copy()
        article["rank"] = i + 1
        if i < 10:
            article["category"] = "latest"
        elif i < 15:
            article["category"] = "japan"
        else:
            article["category"] = "overseas"
        article["point"] = ""
        result.append(article)
    return result
