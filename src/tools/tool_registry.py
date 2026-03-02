"""
工具注册表：管理所有可用的工具
"""


class ToolRegistry:
    """工具注册表，用于注册、获取和列出工具"""
    
    def __init__(self):
        """初始化工具注册表"""
        self.tools = {}  # 存储工具的字典，key 为工具名称

    def register(self, tool):
        """
        注册一个工具
        
        Args:
            tool: 工具实例（必须继承 BaseTool）
        """
        self.tools[tool.name] = tool

    def get(self, name):
        """
        根据名称获取工具
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例，如果不存在则返回 None
        """
        return self.tools.get(name)

    def list_tools(self):
        """
        列出所有已注册的工具
        
        Returns:
            工具实例列表
        """
        return list(self.tools.values())
