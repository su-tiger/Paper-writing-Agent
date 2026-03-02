"""
工作流评估器
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
import json
import re
import time

from .base_evaluator import BaseEvaluator
from .metrics import WorkflowMetrics, GenerationMetrics, EvaluationReport
from ..config import Config


class WorkflowEvaluator(BaseEvaluator):
    """
    工作流评估器
    
    评估维度：
    1. 执行效率：时间、迭代次数
    2. 节点质量：各节点输出质量
    3. 流程合理性：节点流转是否合理
    4. 最终结果质量
    """
    
    def __init__(self, llm=None):
        super().__init__(llm)
        if self.llm is None:
            self.llm = ChatOpenAI(
                model=Config.DEEPSEEK_MODEL,
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL
            )
    
    def evaluate_workflow_execution(
        self,
        total_time: float,
        node_times: Dict[str, float],
        iterations: int,
        max_iterations: int,
        success: bool,
        error_count: int = 0
    ) -> WorkflowMetrics:
        """
        评估工作流执行效率
        
        Args:
            total_time: 总执行时间
            node_times: 各节点执行时间
            iterations: 实际迭代次数
            max_iterations: 最大迭代次数
            success: 是否成功完成
            error_count: 错误次数
            
        Returns:
            工作流执行指标
        """
        return WorkflowMetrics(
            total_time=total_time,
            node_times=node_times,
            iterations=iterations,
            success=success,
            error_count=error_count
        )
    
    def evaluate_node_quality(
        self,
        node_name: str,
        node_input: str,
        node_output: str,
        expected_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        评估单个节点的输出质量
        
        Args:
            node_name: 节点名称
            node_input: 节点输入
            node_output: 节点输出
            expected_output: 期望输出（可选）
            
        Returns:
            节点质量评估结果
        """
        prompt = f"""
评估工作流节点的输出质量。

节点名称：{node_name}

节点输入：
{node_input[:500]}...

节点输出：
{node_output[:500]}...

{f"期望输出：{expected_output[:500]}..." if expected_output else ""}

评估维度（每项 1-10 分）：
1. correctness：输出是否正确
2. completeness：输出是否完整
3. quality：输出质量如何

返回 JSON：
{{
    "correctness": <1-10>,
    "completeness": <1-10>,
    "quality": <1-10>,
    "comment": "<评价>"
}}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            result = json.loads(json_match.group() if json_match else response.content)
            
            result['overall_score'] = (
                result.get('correctness', 7) * 0.4 +
                result.get('completeness', 7) * 0.3 +
                result.get('quality', 7) * 0.3
            )
            
            return result
        except:
            return {
                "correctness": 7.0,
                "completeness": 7.0,
                "quality": 7.0,
                "overall_score": 7.0,
                "comment": "评估失败"
            }
    
    def evaluate_workflow_design(
        self,
        workflow_description: str,
        node_sequence: List[str],
        node_transitions: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        评估工作流设计的合理性
        
        Args:
            workflow_description: 工作流描述
            node_sequence: 节点执行序列
            node_transitions: 节点转移关系
            
        Returns:
            工作流设计评估结果
        """
        prompt = f"""
评估工作流设计的合理性。

工作流描述：{workflow_description}

节点执行序列：{' → '.join(node_sequence)}

节点转移关系：
{json.dumps(node_transitions, indent=2, ensure_ascii=False)}

评估维度（每项 1-10 分）：
1. logic_score：流程逻辑是否清晰
2. efficiency_score：流程是否高效
3. robustness_score：流程是否健壮（错误处理）
4. flexibility_score：流程是否灵活

返回 JSON：
{{
    "logic_score": <1-10>,
    "efficiency_score": <1-10>,
    "robustness_score": <1-10>,
    "flexibility_score": <1-10>,
    "comment": "<评价>"
}}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            result = json.loads(json_match.group() if json_match else response.content)
            
            result['overall_score'] = (
                result.get('logic_score', 7) * 0.3 +
                result.get('efficiency_score', 7) * 0.25 +
                result.get('robustness_score', 7) * 0.25 +
                result.get('flexibility_score', 7) * 0.2
            )
            
            return result
        except:
            return {
                "logic_score": 7.0,
                "efficiency_score": 7.0,
                "robustness_score": 7.0,
                "flexibility_score": 7.0,
                "overall_score": 7.0,
                "comment": "评估失败"
            }
    
    def evaluate_final_output(
        self,
        task: str,
        final_output: str,
        reference_output: Optional[str] = None
    ) -> GenerationMetrics:
        """
        评估工作流最终输出质量
        
        Args:
            task: 任务描述
            final_output: 最终输出
            reference_output: 参考输出（可选）
            
        Returns:
            输出质量指标
        """
        prompt = f"""
评估工作流最终输出的质量（每项 1-10 分）。

任务：{task}

最终输出：
{final_output}

{f"参考输出：{reference_output}" if reference_output else ""}

评估维度：
1. fluency：语言流畅度
2. coherence：逻辑连贯性
3. relevance：与任务的相关性
4. factuality：事实准确性
5. completeness：输出完整性

返回 JSON：
{{
    "fluency": <1-10>,
    "coherence": <1-10>,
    "relevance": <1-10>,
    "factuality": <1-10>,
    "completeness": <1-10>
}}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            scores = json.loads(json_match.group() if json_match else response.content)
            
            fluency = float(scores.get('fluency', 7))
            coherence = float(scores.get('coherence', 7))
            relevance = float(scores.get('relevance', 7))
            factuality = float(scores.get('factuality', 7))
            completeness = float(scores.get('completeness', 7))
            
        except:
            fluency = coherence = relevance = factuality = completeness = 7.0
        
        overall_score = (
            fluency * 0.15 +
            coherence * 0.20 +
            relevance * 0.25 +
            factuality * 0.25 +
            completeness * 0.15
        )
        
        return GenerationMetrics(
            fluency=fluency,
            coherence=coherence,
            relevance=relevance,
            factuality=factuality,
            completeness=completeness,
            overall_score=overall_score
        )
    
    def evaluate(
        self,
        task: str,
        workflow_description: str,
        node_sequence: List[str],
        node_outputs: Dict[str, str],
        final_output: str,
        total_time: float,
        node_times: Dict[str, float],
        iterations: int,
        max_iterations: int,
        success: bool,
        error_count: int = 0,
        reference_output: Optional[str] = None
    ) -> EvaluationReport:
        """
        完整评估工作流
        
        Args:
            task: 任务描述
            workflow_description: 工作流描述
            node_sequence: 节点执行序列
            node_outputs: 各节点输出
            final_output: 最终输出
            total_time: 总执行时间
            node_times: 各节点执行时间
            iterations: 迭代次数
            max_iterations: 最大迭代次数
            success: 是否成功
            error_count: 错误次数
            reference_output: 参考输出（可选）
            
        Returns:
            完整评估报告
        """
        print("[WorkflowEvaluator] 开始评估...")
        
        # 1. 评估执行效率
        print("[WorkflowEvaluator] 评估执行效率...")
        workflow_metrics = self.evaluate_workflow_execution(
            total_time=total_time,
            node_times=node_times,
            iterations=iterations,
            max_iterations=max_iterations,
            success=success,
            error_count=error_count
        )
        
        # 2. 评估最终输出质量
        print("[WorkflowEvaluator] 评估最终输出质量...")
        generation_metrics = self.evaluate_final_output(
            task=task,
            final_output=final_output,
            reference_output=reference_output
        )
        
        # 3. 评估工作流设计（可选）
        print("[WorkflowEvaluator] 评估工作流设计...")
        node_transitions = self._infer_transitions(node_sequence)
        design_eval = self.evaluate_workflow_design(
            workflow_description=workflow_description,
            node_sequence=node_sequence,
            node_transitions=node_transitions
        )
        
        # 生成报告
        report = EvaluationReport(
            task_type="Workflow",
            task_description=task,
            workflow_metrics=workflow_metrics,
            generation_metrics=generation_metrics,
            input_data={
                "task": task,
                "workflow_description": workflow_description,
                "node_count": len(node_sequence),
                "max_iterations": max_iterations
            },
            output_data={
                "final_output": final_output[:200] + "...",
                "design_eval": design_eval,
                "node_sequence": node_sequence
            },
            comments=f"设计得分: {design_eval.get('overall_score', 'N/A'):.1f}, 迭代: {iterations}/{max_iterations}"
        )
        
        self.save_evaluation(report.to_dict())
        
        print("[WorkflowEvaluator] 评估完成！")
        return report
    
    def _infer_transitions(self, node_sequence: List[str]) -> Dict[str, List[str]]:
        """从节点序列推断转移关系"""
        transitions = {}
        for i in range(len(node_sequence) - 1):
            current = node_sequence[i]
            next_node = node_sequence[i + 1]
            if current not in transitions:
                transitions[current] = []
            if next_node not in transitions[current]:
                transitions[current].append(next_node)
        return transitions
