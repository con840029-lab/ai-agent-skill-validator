import json
import os
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import SessionLocal, engine, Base
from models import Skill
from app.evaluator import TechnicalEvaluator, AIEvaluator
from app.report_generator import ReportGenerator
from tasks.celery_app import celery_app


@celery_app.task
def evaluate_skill(skill_id: int):
    """异步评估 Skill"""
    db = SessionLocal()
    
    try:
        # 获取 Skill 记录
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return {"error": "Skill not found"}
        
        skill.status = "analyzing"
        db.commit()
        
        # 技术评估
        tech_evaluator = TechnicalEvaluator(skill.file_path)
        tech_results = tech_evaluator.evaluate_all()
        
        # 读取 SKILL.md 内容用于 AI 评估
        skill_md_path = os.path.join(tech_evaluator.extracted_path, "SKILL.md")
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            skill_content = f.read()
        
        # AI 评估 (需要异步运行)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        ai_evaluator = AIEvaluator()
        ai_results = loop.run_until_complete(ai_evaluator.evaluate_all(skill_content))
        
        loop.close()
        
        # 计算总分
        technical_total = tech_results['technical_total']
        ai_total = ai_results['ai_total']
        total_score = (technical_total * 0.5) + (ai_total * 0.5)
        
        # 更新数据库
        skill.tool_capability_score = tech_results['tool_capability']['score']
        skill.code_quality_score = tech_results['code_quality']['score']
        skill.logic_score = tech_results['logic_design']['score']
        skill.rag_score = tech_results['rag_capability']['score']
        skill.technical_total = technical_total
        
        skill.task_completion_score = ai_results['task_completion']['score']
        skill.instruction_following_score = ai_results['instruction_following']['score']
        skill.robustness_score = ai_results['robustness']['score']
        skill.token_efficiency_score = ai_results['token_efficiency']['score']
        skill.ai_total = ai_total
        
        skill.total_score = total_score
        
        # 生成报告
        report_gen = ReportGenerator(tech_results, ai_results, total_score, skill.name)
        skill.report_json = json.dumps(report_gen.generate_json(), ensure_ascii=False)
        skill.report_html = report_gen.generate_html()
        skill.report_markdown = report_gen.generate_markdown()
        
        skill.status = "completed"
        db.commit()
        
        return {
            "skill_id": skill_id,
            "status": "completed",
            "total_score": total_score
        }
        
    except Exception as e:
        skill.status = "failed"
        db.commit()
        return {"error": str(e)}
        
    finally:
        db.close()
