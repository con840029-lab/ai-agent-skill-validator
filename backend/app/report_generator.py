import json
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """评估报告生成器"""
    
    def __init__(self, tech_results: Dict, ai_results: Dict, total_score: float, skill_name: str):
        self.tech_results = tech_results
        self.ai_results = ai_results
        self.total_score = total_score
        self.skill_name = skill_name
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_json(self) -> Dict[str, Any]:
        """生成 JSON 格式报告"""
        return {
            "skill_name": self.skill_name,
            "evaluated_at": self.timestamp,
            "total_score": round(self.total_score, 2),
            "technical_evaluation": {
                "total": round(self.tech_results['technical_total'], 2),
                "weight": 0.5,
                "details": {
                    "tool_capability": self.tech_results['tool_capability'],
                    "code_quality": self.tech_results['code_quality'],
                    "logic_design": self.tech_results['logic_design'],
                    "rag_capability": self.tech_results['rag_capability']
                }
            },
            "ai_evaluation": {
                "total": round(self.ai_results['ai_total'], 2),
                "weight": 0.5,
                "details": {
                    "task_completion": self.ai_results['task_completion'],
                    "instruction_following": self.ai_results['instruction_following'],
                    "robustness": self.ai_results['robustness'],
                    "token_efficiency": self.ai_results['token_efficiency']
                }
            }
        }
    
    def generate_markdown(self) -> str:
        """生成 Markdown 格式报告"""
        md = f"""# {self.skill_name} - Skill 评估报告

**评估时间**: {self.timestamp}

---

## 总分: {self.total_score:.2f} / 100

---

## 第一部分: 技术评分 (50%)

### 总分: {self.tech_results['technical_total']:.2f} / 50

#### 1. 工具能力 ({self.tech_results['tool_capability']['score']:.1f}/25)
"""
        for detail in self.tech_results['tool_capability'].get('details', []):
            md += f"- {detail}\n"
        
        md += f"""
#### 2. 代码质量 ({self.tech_results['code_quality']['score']:.1f}/25)
"""
        for detail in self.tech_results['code_quality'].get('details', []):
            md += f"- {detail}\n"
        
        md += f"""
#### 3. 逻辑设计 ({self.tech_results['logic_design']['score']:.1f}/25)
"""
        for detail in self.tech_results['logic_design'].get('details', []):
            md += f"- {detail}\n"
        
        md += f"""
#### 4. RAG 检索能力 ({self.tech_results['rag_capability']['score']:.1f}/25)
"""
        for detail in self.tech_results['rag_capability'].get('details', []):
            md += f"- {detail}\n"
        
        md += f"""
---

## 第二部分: AI 表现评分 (50%)

### 总分: {self.ai_results['ai_total']:.2f} / 50

#### 1. 任务达成率 ({self.ai_results['task_completion']['score']:.1f}/25)
"""
        for detail in self.ai_results['task_completion'].get('details', []):
            md += f"- {detail}\n"
        
        md += f"""
#### 2. 指令遵循度 ({self.ai_results['instruction_following']['score']:.1f}/25)
"""
        for detail in self.ai_results['instruction_following'].get('details', []):
            md += f"- {detail}\n"
        
        md += f"""
#### 3. 抗干扰能力 ({self.ai_results['robustness']['score']:.1f}/25)
"""
        for detail in self.ai_results['robustness'].get('details', []):
            md += f"- {detail}\n"
        
        md += f"""
#### 4. Token 消耗效率 ({self.ai_results['token_efficiency']['score']:.1f}/25)
"""
        for detail in self.ai_results['token_efficiency'].get('details', []):
            md += f"- {detail}\n"
        
        md += "\n---\n\n*此报告由 AI Agent Skill Validator 自动生成*"
        
        return md
    
    def generate_html(self) -> str:
        """生成 HTML 格式报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.skill_name} - Skill 评估报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        h3 {{ color: #666; margin-top: 20px; }}
        .score {{ font-size: 48px; font-weight: bold; color: #4CAF50; text-align: center; margin: 30px 0; }}
        .section {{ margin: 20px 0; padding: 20px; border-radius: 8px; background: #f9f9f9; }}
        .detail {{ margin: 10px 0; padding-left: 20px; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; margin-right: 8px; }}
        .badge-pass {{ background: #e8f5e9; color: #2e7d32; }}
        .badge-warn {{ background: #fff3e0; color: #f57c00; }}
        .badge-fail {{ background: #ffebee; color: #c62828; }}
        .progress {{ height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }}
        .progress-bar {{ height: 100%; background: #4CAF50; }}
        .footer {{ text-align: center; margin-top: 40px; color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.skill_name} - Skill 评估报告</h1>
        <p style="color: #666;">评估时间: {self.timestamp}</p>
        
        <div class="score">
            总分: {self.total_score:.2f} / 100
        </div>
        
        <h2>📊 第一部分: 技术评分 (50%)</h2>
        <div class="progress"><div class="progress-bar" style="width: {self.tech_results['technical_total']}%"></div></div>
        <p>技术总分: <strong>{self.tech_results['technical_total']:.2f}</strong> / 50</p>
        
        <div class="section">
            <h3>🔧 1. 工具能力 ({self.tech_results['tool_capability']['score']:.1f}/25)</h3>
"""
        for detail in self.tech_results['tool_capability'].get('details', []):
            badge_class = 'badge-pass' if '✓' in detail else 'badge-warn' if '⚠' in detail else 'badge-fail'
            html += f'            <div class="detail"><span class="badge {badge_class}">{detail}</span></div>\n'
        
        html += f"""        </div>
        
        <div class="section">
            <h3>💻 2. 代码质量 ({self.tech_results['code_quality']['score']:.1f}/25)</h3>
"""
        for detail in self.tech_results['code_quality'].get('details', []):
            badge_class = 'badge-pass' if '✓' in detail else 'badge-warn' if '⚠' in detail else 'badge-fail'
            html += f'            <div class="detail"><span class="badge {badge_class}">{detail}</span></div>\n'
        
        html += f"""        </div>
        
        <div class="section">
            <h3>🧠 3. 逻辑设计 ({self.tech_results['logic_design']['score']:.1f}/25)</h3>
"""
        for detail in self.tech_results['logic_design'].get('details', []):
            badge_class = 'badge-pass' if '✓' in detail else 'badge-warn' if '⚠' in detail else 'badge-fail'
            html += f'            <div class="detail"><span class="badge {badge_class}">{detail}</span></div>\n'
        
        html += f"""        </div>
        
        <div class="section">
            <h3>📚 4. RAG 检索能力 ({self.tech_results['rag_capability']['score']:.1f}/25)</h3>
"""
        for detail in self.tech_results['rag_capability'].get('details', []):
            badge_class = 'badge-pass' if '✓' in detail else 'badge-warn' if '⚠' in detail else 'badge-fail'
            html += f'            <div class="detail"><span class="badge {badge_class}">{detail}</span></div>\n'
        
        html += f"""        </div>
        
        <h2>🤖 第二部分: AI 表现评分 (50%)</h2>
        <div class="progress"><div class="progress-bar" style="width: {self.ai_results['ai_total']}%"></div></div>
        <p>AI 表现总分: <strong>{self.ai_results['ai_total']:.2f}</strong> / 50</p>
        
        <div class="section">
            <h3>✅ 1. 任务达成率 ({self.ai_results['task_completion']['score']:.1f}/25)</h3>
"""
        for detail in self.ai_results['task_completion'].get('details', []):
            html += f'            <div class="detail">• {detail}</div>\n'
        
        html += f"""        </div>
        
        <div class="section">
            <h3>📋 2. 指令遵循度 ({self.ai_results['instruction_following']['score']:.1f}/25)</h3>
"""
        for detail in self.ai_results['instruction_following'].get('details', []):
            html += f'            <div class="detail">• {detail}</div>\n'
        
        html += f"""        </div>
        
        <div class="section">
            <h3>🛡️ 3. 抗干扰能力 ({self.ai_results['robustness']['score']:.1f}/25)</h3>
"""
        for detail in self.ai_results['robustness'].get('details', []):
            html += f'            <div class="detail">• {detail}</div>\n'
        
        html += f"""        </div>
        
        <div class="section">
            <h3>⚡ 4. Token 消耗效率 ({self.ai_results['token_efficiency']['score']:.1f}/25)</h3>
"""
        for detail in self.ai_results['token_efficiency'].get('details', []):
            badge_class = 'badge-pass' if '✓' in detail else 'badge-warn' if '⚠' in detail else 'badge-fail'
            html += f'            <div class="detail"><span class="badge {badge_class}">{detail}</span></div>\n'
        
        html += f"""        </div>
        
        <div class="footer">
            此报告由 AI Agent Skill Validator 自动生成
        </div>
    </div>
</body>
</html>"""
        
        return html
