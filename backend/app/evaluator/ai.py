import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings


class AIEvaluator:
    """AI 评分引擎 - 模拟测试 Skill 行为"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    async def evaluate_task_completion(self, skill_content: str) -> Dict[str, Any]:
        """评估任务达成率"""
        score = 0.0
        details = []
        
        prompt = f"""
你是一个 AI Agent Skill 评估专家。请分析以下 Skill 定义，评估其任务达成能力：

{skill_content}

请从以下维度评分 (0-100分):
1. 目标明确性: Skill 的任务目标是否清晰明确
2. 能力完整性: 是否具备完成任务所需的能力
3. 输出质量: 预期输出是否明确且有价值

以 JSON 格式返回，只返回分数和简要说明:
{{
    "score": 数字 (0-100),
    "analysis": "分析说明"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            score = float(result.get("score", 50))
            details.append(result.get("analysis", ""))
            
        except Exception as e:
            score = 50.0
            details.append(f"⚠ AI 评估失败: {str(e)}")
        
        return {
            "score": max(0, min(100, score)),
            "max_score": 100.0,
            "details": details
        }
    
    async def evaluate_instruction_following(self, skill_content: str) -> Dict[str, Any]:
        """评估指令遵循度"""
        score = 0.0
        details = []
        
        prompt = f"""
你是一个 AI Agent Skill 评估专家。请分析以下 Skill 定义，评估其对复杂指令的遵循能力：

{skill_content}

请从以下维度评分 (0-100分):
1. 参数处理: 是否有明确的参数定义和验证
2. 边界情况: 是否考虑了异常和边界情况
3. 指令解析: 是否能正确解析和理解复杂指令
4. 约束遵循: 是否遵循了约束条件（SOUL.md 中的规则）

以 JSON 格式返回，只返回分数和简要说明:
{{
    "score": 数字 (0-100),
    "analysis": "分析说明"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            score = float(result.get("score", 50))
            details.append(result.get("analysis", ""))
            
        except Exception as e:
            score = 50.0
            details.append(f"⚠ AI 评估失败: {str(e)}")
        
        return {
            "score": max(0, min(100, score)),
            "max_score": 100.0,
            "details": details
        }
    
    async def evaluate_robustness(self, skill_content: str) -> Dict[str, Any]:
        """评估抗干扰能力"""
        score = 0.0
        details = []
        
        prompt = f"""
你是一个 AI Agent Skill 评估专家。请分析以下 Skill 定义，评估其在异常情况下的鲁棒性：

{skill_content}

请从以下维度评分 (0-100分):
1. 错误处理: 是否有明确的错误处理机制
2. 重试机制: 面临失败时是否有重试或降级策略
3. 输入验证: 是否对用户输入进行验证
4. 资源清理: 是否有适当的资源清理（文件、连接等）

以 JSON 格式返回，只返回分数和简要说明:
{{
    "score": 数字 (0-100),
    "analysis": "分析说明"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            score = float(result.get("score", 50))
            details.append(result.get("analysis", ""))
            
        except Exception as e:
            score = 50.0
            details.append(f"⚠ AI 评估失败: {str(e)}")
        
        return {
            "score": max(0, min(100, score)),
            "max_score": 100.0,
            "details": details
        }
    
    async def evaluate_token_efficiency(self, skill_content: str) -> Dict[str, Any]:
        """评估 Token 消耗效率"""
        score = 0.0
        details = []
        
        # 基础分：内容简洁性
        char_count = len(skill_content)
        word_count = len(skill_content.split())
        
        if 200 <= char_count <= 3000:
            score += 40
            details.append(f"✓ Skill 描述长度合理: {char_count} 字符")
        elif char_count > 3000:
            details.append(f"⚠ Skill 描述过长: {char_count} 字符")
        else:
            details.append(f"⚠ Skill 描述过短: {char_count} 字符")
        
        # 检查是否有高效的工具调用模式
        if 'batch' in skill_content.lower() or 'parallel' in skill_content.lower():
            score += 30
            details.append("✓ 考虑了并行处理")
        
        # 检查是否有记忆/缓存策略
        if 'memory' in skill_content.lower() or 'cache' in skill_content.lower():
            score += 30
            details.append("✓ 使用了记忆/缓存机制")
        
        return {
            "score": max(0, min(100, score)),
            "max_score": 100.0,
            "details": details
        }
    
    async def evaluate_all(self, skill_content: str) -> Dict[str, Any]:
        """执行完整 AI 评估"""
        task_score = await self.evaluate_task_completion(skill_content)
        instruction_score = await self.evaluate_instruction_following(skill_content)
        robustness_score = await self.evaluate_robustness(skill_content)
        efficiency_score = await self.evaluate_token_efficiency(skill_content)
        
        # AI 表现总分 (各 25%)
        ai_total = (
            task_score['score'] * 0.25 +
            instruction_score['score'] * 0.25 +
            robustness_score['score'] * 0.25 +
            efficiency_score['score'] * 0.25
        )
        
        return {
            "task_completion": task_score,
            "instruction_following": instruction_score,
            "robustness": robustness_score,
            "token_efficiency": efficiency_score,
            "ai_total": ai_total
        }
