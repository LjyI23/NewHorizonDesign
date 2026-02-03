import json
import requests

class OllamaBackend:
    """Ollama 本地模型后端 - 完全免费"""
    
    def __init__(self, model="qwen2.5:7b", base_url="http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/chat"
        self.base_url = base_url
        self.is_available = self.check_connection()
    
    def check_connection(self):
        """检测Ollama服务是否可用"""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except:
            return False
    
    def get_system_prompt(self, persona):
        """为不同角色生成专属system prompt"""
        prompts = {
            "nova": """You are Nova, a versatile and friendly AI assistant.
- Personality: Warm, patient, logically clear
- Expertise: General knowledge, problem solving, learning guidance
- Tone: Professional yet approachable, like a trusted friend
- Always respond in the same language as the user's query.""",
            
            "byte": """You are Byte, a senior full-stack development expert.
- Personality: Rigorous, geek spirit, loves sharing best practices
- Expertise: Python, system design, algorithm optimization, debugging
- Tone: Technical with a touch of humor, avoids over-engineering
- Always provide runnable code examples with comments when applicable.
- Respond in the same language as the user's query.""",
            
            "muse": """You are Muse, a creative content generator with rich imagination.
- Personality: Sensitive, imaginative, aesthetically perceptive
- Expertise: Story writing, copywriting, poetry, character design
- Tone: Poetic and elegant, good at creating vivid imagery
- Always respond in the same language as the user's query.""",
            
            "oracle": """You are Oracle, a strategic business advisor.
- Personality: Insightful, data-driven, forward-thinking
- Expertise: Market analysis, product strategy, decision support
- Tone: Concise, structured, actionable
- Always respond in the same language as the user's query."""
        }
        return prompts.get(persona, prompts["nova"])
    
    def chat_stream(self, messages, persona, callback):
        """流式对话（逐块返回）"""
        system_prompt = self.get_system_prompt(persona)
        
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": True,
            "options": {"temperature": 0.7}
        }
        
        try:
            with requests.post(self.api_url, json=payload, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                full_response = ""
                for line in resp.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            token = chunk["message"]["content"]
                            full_response += token
                            callback(token, False)  # 流式更新
                callback("", True)  # 完成标记
                return full_response
        except requests.exceptions.ConnectionError:
            error = "❌ Ollama not running\nPlease start Ollama first:\n  macOS/Linux: ollama serve\n  Windows: Launch Ollama app"
            callback(error, True)
            return error
        except requests.exceptions.Timeout:
            error = "❌ Request timeout\nModel may be loading. Try again in 30 seconds."
            callback(error, True)
            return error
        except Exception as e:
            error = f"❌ AI error: {str(e)}"
            callback(error, True)
            return error