import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from models.database import get_db
from models import Skill, User
from app.security import get_current_user
from app.config import settings
from tasks.evaluation_tasks import evaluate_skill

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.post("/upload")
async def upload_skill(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传 Skill 压缩包"""
    
    # 验证文件扩展名
    filename = file.filename
    if not any(filename.endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # 保存文件
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 创建数据库记录
    new_skill = Skill(
        name=name,
        description=description,
        file_path=file_path,
        owner_id=current_user.id,
        status="pending"
    )
    
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    
    # 触发异步评估任务
    task = evaluate_skill.delay(new_skill.id)
    
    return {
        "id": new_skill.id,
        "name": new_skill.name,
        "status": new_skill.status,
        "task_id": task.id,
        "message": "Skill uploaded successfully. Evaluation started."
    }


@router.get("/")
async def list_skills(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的 Skill 列表"""
    query = db.query(Skill).filter(Skill.owner_id == current_user.id)
    
    total = query.count()
    skills = query.order_by(Skill.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "status": skill.status,
                "total_score": skill.total_score,
                "created_at": skill.created_at.isoformat() if skill.created_at else None
            }
            for skill in skills
        ]
    }


@router.get("/{skill_id}")
async def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 Skill 详情"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.owner_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "status": skill.status,
        "created_at": skill.created_at.isoformat() if skill.created_at else None,
        "updated_at": skill.updated_at.isoformat() if skill.updated_at else None,
        "scores": {
            "technical": {
                "tool_capability": skill.tool_capability_score,
                "code_quality": skill.code_quality_score,
                "logic": skill.logic_score,
                "rag": skill.rag_score,
                "total": skill.technical_total
            },
            "ai": {
                "task_completion": skill.task_completion_score,
                "instruction_following": skill.instruction_following_score,
                "robustness": skill.robustness_score,
                "token_efficiency": skill.token_efficiency_score,
                "total": skill.ai_total
            },
            "total": skill.total_score
        }
    }


@router.get("/{skill_id}/report/json")
async def get_report_json(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 JSON 格式报告"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.owner_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if not skill.report_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report not ready"
        )
    
    import json
    return json.loads(skill.report_json)


@router.get("/{skill_id}/report/html")
async def get_report_html(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 HTML 格式报告"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.owner_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if not skill.report_html:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report not ready"
        )
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=skill.report_html)


@router.get("/{skill_id}/report/markdown")
async def get_report_markdown(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 Markdown 格式报告"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.owner_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if not skill.report_markdown:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report not ready"
        )
    
    return {"markdown": skill.report_markdown}


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除 Skill"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.owner_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # 删除文件
    if os.path.exists(skill.file_path):
        os.remove(skill.file_path)
    
    # 删除数据库记录
    db.delete(skill)
    db.commit()
    
    return {"message": "Skill deleted successfully"}
