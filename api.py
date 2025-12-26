"""
Shift Manager API - FastAPI Backend
シフト管理システムのAPIサーバー
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import calendar

from backend import StaffData, ShiftRequest, ShiftResponse, ShiftSolver

# FastAPI アプリケーション
app = FastAPI(
    title="Shift Manager API",
    version="2.0.0",
    description="シフト表自動生成システムのバックエンドAPI"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Utility Functions
# ==========================================

def parse_days(input_str: Optional[str]) -> list:
    """日付文字列をパースして整数リストに変換"""
    if not input_str or not input_str.strip():
        return []
    try:
        fixed_str = input_str.replace('，', ',').translate(
            str.maketrans('０１２３４５６７８９', '0123456789')
        )
        return sorted(list(set([
            int(x.strip()) for x in fixed_str.split(',') 
            if x.strip().isdigit()
        ])))
    except:
        return []


# ==========================================
# API Endpoints
# ==========================================

@app.post("/api/shift/solve", response_model=ShiftResponse)
async def create_shift(request: ShiftRequest):
    """
    シフトを作成する
    
    - **year**: 年 (2025-2030)
    - **month**: 月 (1-12)
    - **target_off_days**: 常勤スタッフの目標公休日数 (1-15)
    - **staff_data**: スタッフ設定のリスト
    - **max_attempts**: 最大試行回数 (デフォルト: 2500)
    """
    if not request.staff_data:
        raise HTTPException(status_code=400, detail="スタッフが登録されていません")
    
    try:
        solver = ShiftSolver(
            staff_data=request.staff_data,
            year=request.year,
            month=request.month,
            target_off_days=request.target_off_days,
            max_attempts=request.max_attempts
        )
        
        schedule, errors = solver.solve()
        
        if schedule is None:
            raise HTTPException(status_code=500, detail="シフトの作成に失敗しました")
        
        _, days = calendar.monthrange(request.year, request.month)
        
        return ShiftResponse(
            schedule=schedule,
            errors=errors,
            year=request.year,
            month=request.month,
            days=days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラーが発生しました: {str(e)}")


@app.post("/api/shift/parse-days")
async def parse_days_endpoint(input_str: Optional[str] = None):
    """
    日付文字列をパースして整数リストに変換する
    
    - **input_str**: カンマ区切りの日付文字列 (例: "1,2,3" または "1，2，3")
    """
    result = parse_days(input_str)
    return {"days": result}


@app.get("/")
async def root():
    """APIのルートエンドポイント"""
    return {
        "message": "Shift Manager API",
        "version": "2.0.0",
        "endpoints": {
            "POST /api/shift/solve": "シフトを作成",
            "POST /api/shift/parse-days": "日付文字列をパース",
            "GET /docs": "APIドキュメント (Swagger UI)",
            "GET /redoc": "APIドキュメント (ReDoc)"
        }
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
