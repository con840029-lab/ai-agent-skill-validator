import os
import zipfile
import tarfile
import re
from pathlib import Path
from typing import Dict, List, Any
import yaml


class TechnicalEvaluator:
    """技术评分引擎 - 静态分析 Skill 包"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.extracted_path = None
        self.skill_md = None
        self.python_files = []
        self.javascript_files = []
        
    def extract_archive(self) -> str:
        """解压技能包"""
        if self.skill_path.endswith('.zip'):
            with zipfile.ZipFile(self.skill_path, 'r') as zip_ref:
                extract_to = self.skill_path.replace('.zip', '_extracted')
                zip_ref.extractall(extract_to)
                self.extracted_path = extract_to
                return extract_to
        elif self.skill_path.endswith('.tar.gz'):
            with tarfile.open(self.skill_path, 'r:gz') as tar_ref:
                extract_to = Path(self.skill_path).parent / Path(self.skill_path).stem.replace('.tar', '_extracted')
                tar_ref.extractall(extract_to)
                self.extracted_path = str(extract_to)
                return str(extract_to)
        else:
            raise ValueError("Unsupported archive format")
    
    def discover_files(self):
        """发现所有源代码文件"""
        if not self.extracted_path:
            self.extract_archive()
        
        for root, _, files in os.walk(self.extracted_path):
            for file in files:
                if file.endswith('.py'):
                    self.python_files.append(os.path.join(root, file))
                elif file.endswith('.js') or file.endswith('.ts'):
                    self.javascript_files.append(os.path.join(root, file))
                elif file == 'SKILL.md':
                    self.skill_md = os.path.join(root, file)
    
    def evaluate_tool_capability(self) -> Dict[str, Any]:
        """评估工具能力"""
        score = 0.0
        max_score = 100.0
        details = []
        
        if not self.skill_md:
            details.append("❌ 未找到 SKILL.md 文件")
            return
        
        with open(self.skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查工具定义
        tool_pattern = r'-\s+([a-z_]+):\s*(.+)'
        tools = re.findall(tool_pattern, content)
        
        if len(tools) >= 5:
            score += 40
            details.append(f"✓ 定义了 {len(tools)} 个工具")
        else:
            details.append(f"⚠ 工具数量不足 ({len(tools)} 个)")
        
        # 检查工具描述质量
        described_tools = sum(1 for _, desc in tools if desc.strip())
        if described_tools > 0:
            score += 20
            details.append(f"✓ {described_tools} 个工具有描述")
        
        # 检查是否使用了常用工具
        common_tools = ['read', 'write', 'exec', 'web_search', 'web_fetch', 'browser']
        used_common = sum(1 for tool, _ in tools if tool in common_tools)
        if used_common >= 2:
            score += 20
            details.append(f"✓ 使用了 {used_common} 个常用工具")
        
        # 检查工具调用示例
        if '```' in content or 'example' in content.lower():
            score += 20
            details.append("✓ 包含代码示例或使用说明")
        
        return {
            "score": min(score, max_score),
            "max_score": max_score,
            "details": details
        }
    
    def evaluate_code_quality(self) -> Dict[str, Any]:
        """评估代码质量"""
        score = 0.0
        max_score = 100.0
        details = []
        
        total_lines = 0
        functions = 0
        classes = 0
        comments = 0
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    
                    for line in lines:
                        if line.strip().startswith('def '):
                            functions += 1
                        elif line.strip().startswith('class '):
                            classes += 1
                        elif line.strip().startswith('#'):
                            comments += 1
            except:
                continue
        
        for file_path in self.javascript_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    
                    for line in lines:
                        if 'function ' in line or '=>' in line:
                            functions += 1
                        elif 'class ' in line:
                            classes += 1
                        elif line.strip().startswith('//') or line.strip().startswith('*'):
                            comments += 1
            except:
                continue
        
        if total_lines > 0:
            # 代码行数评分 (合理范围 50-500 行)
            if 50 <= total_lines <= 500:
                score += 20
                details.append(f"✓ 代码量合理: {total_lines} 行")
            elif total_lines > 0:
                score += 10
                details.append(f"⚠ 代码量: {total_lines} 行")
            
            # 函数和类组织
            if functions >= 3:
                score += 20
                details.append(f"✓ 定义了 {functions} 个函数")
            
            if classes >= 1:
                score += 10
                details.append(f"✓ 使用了面向对象设计")
            
            # 注释率
            comment_ratio = comments / max(total_lines, 1)
            if comment_ratio >= 0.15:
                score += 20
                details.append(f"✓ 注释充分 ({comment_ratio*100:.1f}%)")
            elif comment_ratio >= 0.05:
                score += 10
                details.append(f"⚠ 注释率偏低 ({comment_ratio*100:.1f}%)")
            
            # 有代码文件
            if total_lines > 0:
                score += 20
                details.append(f"✓ 包含源代码文件")
        
        return {
            "score": min(score, max_score),
            "max_score": max_score,
            "details": details,
            "stats": {
                "total_lines": total_lines,
                "functions": functions,
                "classes": classes,
                "comments": comments
            }
        }
    
    def evaluate_logic(self) -> Dict[str, Any]:
        """评估逻辑设计"""
        score = 0.0
        max_score = 100.0
        details = []
        
        if not self.skill_md:
            details.append("❌ SKILL.md 不存在")
        
        with open(self.skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查描述质量
        if len(content) > 500:
            score += 20
            details.append("✓ SKILL.md 内容详实")
        else:
            score += 10
            details.append("⚠ SKILL.md 内容偏简")
        
        # 检查是否定义了触发条件
        if 'when' in content.lower() or 'trigger' in content.lower() or 'activate' in content.lower():
            score += 20
            details.append("✓ 定义了触发条件")
        
        # 检查是否有步骤说明
        steps = re.findall(r'\d+\.', content) or re.findall(r'step', content.lower())
        if len(steps) >= 3:
            score += 20
            details.append(f"✓ 包含 {len(steps)} 个步骤说明")
        
        # 检查是否有错误处理说明
        if 'error' in content.lower() or 'exception' in content.lower() or 'fail' in content.lower():
            score += 20
            details.append("✓ 包含错误处理说明")
        
        # 检查是否有示例
        if '```' in content or 'example' in content.lower():
            score += 20
            details.append("✓ 包含使用示例")
        
        return {
            "score": min(score, max_score),
            "max_score": max_score,
            "details": details
        }
    
    def evaluate_rag(self) -> Dict[str, Any]:
        """评估 RAG 检索能力"""
        score = 0.0
        max_score = 100.0
        details = []
        
        if not self.skill_md:
            details.append("❌ SKILL.md 不存在")
        
        with open(self.skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否使用了检索相关工具
        rag_keywords = ['memory_search', 'memory_get', 'feishu', 'read', 'list', 'search']
        rag_used = sum(1 for kw in rag_keywords if kw in content.lower())
        
        if rag_used >= 2:
            score += 40
            details.append(f"✓ 使用了 {rag_used} 个检索相关工具")
        
        # 检查是否有记忆/上下文管理
        if 'memory' in content.lower() or 'context' in content.lower() or 'session' in content.lower():
            score += 30
            details.append("✓ 考虑了记忆/上下文管理")
        
        # 检查是否有知识库相关操作
        if 'wiki' in content.lower() or 'knowledge' in content.lower() or 'doc' in content.lower():
            score += 30
            details.append("✓ 涉及知识库操作")
        
        return {
            "score": min(score, max_score),
            "max_score": max_score,
            "details": details
        }
    
    def evaluate_all(self) -> Dict[str, Any]:
        """执行完整技术评估"""
        self.discover_files()
        
        tool_score = self.evaluate_tool_capability()
        code_score = self.evaluate_code_quality()
        logic_score = self.evaluate_logic()
        rag_score = self.evaluate_rag()
        
        # 技术总分 (各 25%)
        technical_total = (
            tool_score['score'] * 0.25 +
            code_score['score'] * 0.25 +
            logic_score['score'] * 0.25 +
            rag_score['score'] * 0.25
        )
        
        return {
            "tool_capability": tool_score,
            "code_quality": code_score,
            "logic_design": logic_score,
            "rag_capability": rag_score,
            "technical_total": technical_total
        }
