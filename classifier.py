import anthropic
import json
import re
import os
from typing import List, Dict


class NewsClassifier:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def select_top_ai_news(self, articles: List[Dict]) -> List[Dict]:
        """Claude を使ってAI関連ニュース上位10件を選択・要約"""
        if not articles:
            return []

        # Claudeに渡す記事リスト（最大60件）
        candidates = articles[:60]
        articles_text = "\n\n".join([
            f"[{i+1}] タイトル: {a['title']}\nURL: {a['url']}\nソース: {a['source']}\n概要: {a.get('summary', '')[:200]}"
            for i, a in enumerate(candidates)
        ])

        print("Claude でAI関連ニュースを選択中...")

        response = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4000,
            thinking={"type": "adaptive"},
            messages=[{
                "role": "user",
                "content": f"""以下の記事リストから、AI（人工知能）に関連する最も重要・注目すべき10件を選んでください。

【選択基準】
- AI技術の重要な進歩・新モデル発表（OpenAI、Anthropic、Google、Meta等）
- AI政策・規制・投資の動向
- 日本のAIビジネス・産業への影響（日経新聞の記事を優先）
- 社会に大きな影響を与えるAIニュース
- AIスタートアップの重要発表・資金調達

【記事リスト】
{articles_text}

【出力形式】
以下のJSONのみを出力してください（他のテキスト不要）：
{{
  "selected": [
    {{
      "rank": 1,
      "index": 記事番号（1始まり）,
      "title_ja": "日本語タイトル（英語の場合は翻訳）",
      "source": "ソース名",
      "url": "URL",
      "summary_ja": "120〜180文字の日本語要約。技術的内容・背景・重要性を含める",
      "point": "この記事が重要な理由（40文字以内）"
    }}
  ]
}}"""
            }],
        )

        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text = block.text
                break

        try:
            # JSONを抽出
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                print("JSON抽出失敗。レスポンス:", response_text[:300])
                return _fallback_selection(candidates)

            data = json.loads(json_match.group())
            selected = data.get("selected", [])

            result = []
            for item in selected:
                idx = item.get("index", 0) - 1
                if 0 <= idx < len(candidates):
                    original = candidates[idx].copy()
                    original["rank"] = item.get("rank", len(result) + 1)
                    original["title"] = item.get("title_ja", original["title"])
                    original["summary"] = item.get("summary_ja", original.get("summary", ""))
                    original["point"] = item.get("point", "")
                    result.append(original)

            print(f"選択完了: {len(result)} 件")
            return result

        except json.JSONDecodeError as e:
            print(f"JSONパースエラー: {e}")
            print("レスポンス:", response_text[:500])
            return _fallback_selection(candidates)
        except Exception as e:
            print(f"分類エラー: {e}")
            return _fallback_selection(candidates)


def _fallback_selection(articles: List[Dict]) -> List[Dict]:
    """Claudeが失敗した場合のフォールバック（上位10件をそのまま返す）"""
    result = []
    for i, article in enumerate(articles[:10]):
        article = article.copy()
        article["rank"] = i + 1
        article["point"] = ""
        result.append(article)
    return result
