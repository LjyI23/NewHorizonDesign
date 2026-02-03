# core/agent.py
from .ollama_backend import OllamaBackend

class AgentCore:
    """Agent核心 - 角色管理与对话逻辑"""
    
    def __init__(self):
        self.backend = OllamaBackend()
        self.current_persona = "nova"
        self.conversation_history = []
    
    def switch_persona(self, persona_id):
        """切换角色"""
        valid_personas = ["nova", "byte", "muse", "oracle"]
        if persona_id in valid_personas:
            self.current_persona = persona_id
            self.conversation_history = []
            return True
        return False
    
    # ✅ 修复1：增加 persona_id 参数（默认使用当前角色）
    def get_persona_name(self, lang="zh", persona_id=None):
        """获取角色显示名称"""
        if persona_id is None:
            persona_id = self.current_persona
            
        names = {
            "zh": {
                "nova": "Nova • 全能助手",
                "byte": "Byte • 代码专家", 
                "muse": "Muse • 创意写手",
                "oracle": "Oracle • 战略顾问"
            },
            "en": {
                "nova": "Nova • General Assistant",
                "byte": "Byte • Code Expert",
                "muse": "Muse • Creative Writer",
                "oracle": "Oracle • Strategy Advisor"
            }
        }
        return names.get(lang, names["zh"]).get(persona_id, persona_id)
    
    def chat(self, message, callback):
        """发起对话（流式）"""
        self.conversation_history.append({"role": "user", "content": message})
        return self.backend.chat_stream(self.conversation_history, self.current_persona, callback)
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []