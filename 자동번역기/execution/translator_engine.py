import os
import json
import difflib
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TranslatorEngine:
    def __init__(self, kb_path=".tmp/kb_data.json"):
        self.kb_path = kb_path
        self.kb_data = self._load_kb()
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            # Use gemini-flash-latest which was confirmed to work
            try:
                self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
                print("Using Gemini Flash Latest.")
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.gemini_model = genai.GenerativeModel('gemini-pro-latest')
        elif self.openai_key:
            self.client = OpenAI(api_key=self.openai_key)
            print("Using OpenAI API.")
        else:
            print("Warning: No API key found in .env")

    def _load_kb(self):
        if os.path.exists(self.kb_path):
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def find_cache(self, text, threshold=0.95):
        best_match = None
        max_ratio = 0
        
        for entry in self.kb_data:
            ratio = difflib.SequenceMatcher(None, text, entry['ko']).ratio()
            if ratio > max_ratio:
                max_ratio = ratio
                best_match = entry
        
        if max_ratio >= threshold:
            return best_match, max_ratio
        return None, max_ratio

    def translate(self, text):
        cache_hit, ratio = self.find_cache(text)
        if cache_hit:
            return {
                "source": "cache",
                "similarity": ratio,
                "translations": {
                    "en": cache_hit['en'],
                    "ja": cache_hit['ja'],
                    "zh": cache_hit['zh']
                }
            }

        context_hint = ""
        if ratio > 0.5:
            closest, _ = self.find_cache(text, threshold=0)
            if closest:
                context_hint = f"\n참고 스타일: {closest['ko']} -> {closest['en']} / {closest['ja']} / {closest['zh']}"

        prompt = f"""당신은 전문 번역가입니다. 다음 한국어 문장을 영어, 일본어, 중국어로 번역하세요.
결과는 반드시 다음 JSON 형식으로만 출력하세요:
{{
  "en": "영어 번역",
  "ja": "일본어 번역",
  "zh": "중국어 번역"
}}

입력 문장: {text}
{context_hint}"""

        try:
            if self.gemini_key:
                # Some models might not support JSON mode properly in all tiers, 
                # so we add a manual fallback just in case
                try:
                    response = self.gemini_model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            response_mime_type="application/json",
                        )
                    )
                    result = json.loads(response.text)
                except:
                    response = self.gemini_model.generate_content(prompt + " (JSON 출력)")
                    text_resp = response.text
                    start = text_resp.find('{')
                    end = text_resp.rfind('}') + 1
                    result = json.loads(text_resp[start:end])
            else:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                
            return {
                "source": "llm",
                "similarity": ratio,
                "translations": result
            }
        except Exception as e:
            return {"error": f"Gemini Error: {str(e)}"}

if __name__ == "__main__":
    engine = TranslatorEngine()
    print(engine.translate("테스트"))
