"""
评估指标定义
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RetrievalMetrics(BaseModel):
    """检索质量指标"""
    precision: float = Field(description="精确率")
    recall: float = Field(description="召回率")
    f1_score: float = Field(description="F1 分数")
    mrr: float = Field(description="平均倒数排名 (MRR)")
    ndcg: float = Field(description="归一化折损累积增益 (NDCG)")
    relevance_score: float = Field(description="相关性得分")
    
    def to_dict(self) -> Dict[str, float]:
        return self.model_dump()


class GenerationMetrics(BaseModel):
    """生成质量指标"""
    fluency: float = Field(description="流畅度 (1-10)")
    coherence: float = Field(description="连贯性 (1-10)")
    relevance: float = Field(description="相关性 (1-10)")
    factuality: float = Field(description="事实准确性 (1-10)")
    completeness: float = Field(description="完整性 (1-10)")
    overall_score: float = Field(description="综合得分 (1-10)")
    
    def to_dict(self) -> Dict[str, float]:
        return self.model_dump()


class WorkflowMetrics(BaseModel):
    """工作流执行指标"""
    total_time: float = Field(description="总执行时间（秒）")
    node_times: Dict[str, float] = Field(description="各节点执行时间")
    iterations: int = Field(description="迭代次数")
    success: bool = Field(description="是否成功完成")
    error_count: int = Field(default=0, description="错误次数")
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class EvaluationReport(BaseModel):
    """完整评估报告"""
    task_type: str = Field(description="任务类型")
    task_description: str = Field(description="任务描述")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # 各类指标
    retrieval_metrics: Optional[RetrievalMetrics] = None
    generation_metrics: Optional[GenerationMetrics] = None
    workflow_metrics: Optional[WorkflowMetrics] = None
    
    # 额外信息
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    comments: str = Field(default="", description="评估备注")
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
    
    def summary(self) -> str:
        """生成评估摘要"""
        lines = [
            f"评估报告 - {self.task_type}",
            f"时间: {self.timestamp}",
            f"任务: {self.task_description}",
            ""
        ]
        
        if self.retrieval_metrics:
            lines.append("检索指标:")
            lines.append(f"  - F1 Score: {self.retrieval_metrics.f1_score:.3f}")
            lines.append(f"  - 相关性: {self.retrieval_metrics.relevance_score:.3f}")
            lines.append("")
        
        if self.generation_metrics:
            lines.append("生成指标:")
            lines.append(f"  - 综合得分: {self.generation_metrics.overall_score:.1f}/10")
            lines.append(f"  - 流畅度: {self.generation_metrics.fluency:.1f}/10")
            lines.append(f"  - 相关性: {self.generation_metrics.relevance:.1f}/10")
            lines.append("")
        
        if self.workflow_metrics:
            lines.append("工作流指标:")
            lines.append(f"  - 总时间: {self.workflow_metrics.total_time:.2f}秒")
            lines.append(f"  - 迭代次数: {self.workflow_metrics.iterations}")
            lines.append(f"  - 成功: {'是' if self.workflow_metrics.success else '否'}")
            lines.append("")
        
        if self.comments:
            lines.append(f"备注: {self.comments}")
        
        return "\n".join(lines)
