"""
Agent 系统评估器
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
import json
import re
import time

from .base_evaluator import BaseEvaluator
from .metrics import GenerationMetrics, EvaluationReport
from ..config import Config


class AgentEvaluator(BaseEvaluator):
    """
    Agent 系统评估器
    
    评估维度：
    1. 工具选择准确性
    2. 推理过程合理性
    3. 最终答案质量
    4. 执行效率
    """
    
    def __init__(self, llm=None):
        super().__init__(llm)
        if self.llm is None:
            self.llm = ChatOpenAI(
                model=Config.DEEPSEEK_MODEL,
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL
            )
    
    def evaluate_tool_selection(
        self,
        task: str,
        selected_tools: List[str],
        expected_tools: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        评估工具选择的准确性
        
        Args:
            task: 任务描述
            selected_tools: Agent 选择的工具列表
            expected_tools: 期望的工具列表（可选）
            
        Returns:
            工具选择评估结果
        """
        if expected_tools:
            # 有标注数据，计算准确率
            correct = len(set(selected_tools) & set(expected_tools))
            precision = correct / len(selected_tools) if selected_tools else 0
            recall = correct / len(expected_tools) if expected_tools else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            return {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "selected_tools": selected_tools,
                "expected_tools": expected_tools
            }
        else:
            # 使用 LLM 评估
            prompt = f"""
评估 Agent 的工具选择是否合理。

任务：{task}

Agent 选择的工具：{', '.join(selected_tools)}

评估：
1. 工具选择是否合理？（1-10分）
2. 是否有遗漏的必要工具？
3. 是否有不必要的工具？

返回 JSON：
{{
    "score": <1-10>,
    "is_reasonable": <true/false>,
    "missing_tools": [<遗漏的工具>],
    "unnecessary_tools": [<不必要的工具>],
    "comment": "<评价>"
}}
"""
            
            response = self.llm.invoke(prompt)
            
            try:
                json_match = re.search(r'\{[\s\S]*\}', response.content)
                result = json.loads(json_match.group() if json_match else response.content)
                return result
            except:
                return {
                    "score": 7.0,
                    "is_reasonable": True,
                    "missing_tools": [],
                    "unnecessary_tools": [],
                    "comment": "评估失败"
                }
    
    def evaluate_reasoning(
        self,
        task: str,
        reasoning_steps: List[str],
        final_answer: str
    ) -> Dict[str, Any]:
        """
        评估推理过程的合理性
        
        Args:
            task: 任务描述
            reasoning_steps: 推理步骤列表
            final_answer: 最终答案
            
        Returns:
            推理过程评估结果
        """
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(reasoning_steps)])
        
        prompt = f"""
评估 Agent 的推理过程。

任务：{task}

推理步骤：
{steps_text}

最终答案：{final_answer}

评估维度（每项 1-10 分）：
1. logic_score：推理逻辑是否清晰
2. completeness_score：推理是否完整
3. efficiency_score：推理是否高效（无冗余步骤）
4. correctness_score：推理是否正确

返回 JSON：
{{
    "logic_score": <1-10>,
    "completeness_score": <1-10>,
    "efficiency_score": <1-10>,
    "correctness_score": <1-10>,
    "comment": "<评价>"
}}
"""
        
        response = self.llm.invoke(prompt)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            result = json.loads(json_match.group() if json_match else response.content)
            
            # 计算综合得分
            result['overall_score'] = (
                result.get('logic_score', 7) * 0.3 +
                result.get('completeness_score', 7) * 0.25 +
                result.get('efficiency_score', 7) * 0.2 +
                result.get('correctness_score', 7) * 0.25
            )
            
            return result
        except:
            return {
                "logic_score": 7.0,
                "completeness_score": 7.0,
                "efficiency_score": 7.0,
                "correctness_score": 7.0,
                "overall_score": 7.0,
                "comment": "评估失败"
            }
    
    def evaluate_answer_quality(
        self,
        task: str,
        answer: str,
        reference_answer: Optional[str] = None
    ) -> GenerationMetrics:
        """
        评估最终答案质量
        
        Args:
            task: 任务描述
            answer: Agent 的答案
            reference_answer: 参考答案（可选）
            
        Returns:
            答案质量指标
        """
        prompt = f"""
评估 Agent 答案的质量（每项 1-10 分）。

任务：{task}

Agent 答案：
{answer}

{f"参考答案：{reference_answer}" if reference_answer else ""}

评估维度：
1. fluency：语言流畅度
2. coherence：逻辑连贯性
3. relevance：与任务的相关性
4. factuality：事实准确性
5. completeness：答案完整性

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
        selected_tools: List[str],
        reasoning_steps: List[str],
        final_answer: str,
        execution_time: float,
        expected_tools: Optional[List[str]] = None,
        reference_answer: Optional[str] = None
    ) -> EvaluationReport:
        """
        完整评估 Agent 系统
        
        Args:
            task: 任务描述
            selected_tools: 选择的工具列表
            reasoning_steps: 推理步骤
            final_answer: 最终答案
            execution_time: 执行时间
            expected_tools: 期望的工具（可选）
            reference_answer: 参考答案（可选）
            
        Returns:
            完整评估报告
        """
        print("[AgentEvaluator] 开始评估...")
        
        # 1. 评估工具选择
        print("[AgentEvaluator] 评估工具选择...")
        tool_eval = self.evaluate_tool_selection(task, selected_tools, expected_tools)
        
        # 2. 评估推理过程
        print("[AgentEvaluator] 评估推理过程...")
        reasoning_eval = self.evaluate_reasoning(task, reasoning_steps, final_answer)
        
        # 3. 评估答案质量
        print("[AgentEvaluator] 评估答案质量...")
        answer_metrics = self.evaluate_answer_quality(task, final_answer, reference_answer)
        
        # 生成报告
        report = EvaluationReport(
            task_type="Agent",
            task_description=task,
            generation_metrics=answer_metrics,
            input_data={
                "task": task,
                "selected_tools": selected_tools,
                "reasoning_steps_count": len(reasoning_steps),
                "execution_time": execution_time
            },
            output_data={
                "final_answer": final_answer[:200] + "...",
                "tool_selection_eval": tool_eval,
                "reasoning_eval": reasoning_eval
            },
            comments=f"工具选择得分: {tool_eval.get('score', 'N/A')}, 推理得分: {reasoning_eval.get('overall_score', 'N/A'):.1f}"
        )
        
        self.save_evaluation(report.to_dict())
        
        print("[AgentEvaluator] 评估完成！")
        return report
