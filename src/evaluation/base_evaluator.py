"""
评估器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class BaseEvaluator(ABC):
    """评估器抽象基类"""
    
    def __init__(self, llm=None):
        """
        初始化评估器
        
        Args:
            llm: 大语言模型实例（用于基于 LLM 的评估）
        """
        self.llm = llm
        self.evaluation_history = []
    
    @abstractmethod
    def evaluate(self, **kwargs) -> Dict[str, Any]:
        """
        执行评估
        
        Returns:
            评估结果字典
        """
        pass
    
    def save_evaluation(self, result: Dict[str, Any]):
        """保存评估结果到历史记录"""
        result['timestamp'] = datetime.now().isoformat()
        self.evaluation_history.append(result)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取评估历史"""
        return self.evaluation_history
    
    def clear_history(self):
        """清空评估历史"""
        self.evaluation_history = []
