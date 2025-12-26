/**
 * Shift Solve API Route
 * POST /api/shift/solve
 */

import { NextRequest, NextResponse } from 'next/server';
import { ShiftSolver, ShiftRequest, getDaysInMonth } from '@/app/lib/solver';

export async function POST(request: NextRequest) {
  try {
    const body: ShiftRequest = await request.json();

    // バリデーション
    if (!body.staff_data || body.staff_data.length === 0) {
      return NextResponse.json(
        { error: 'スタッフが登録されていません' },
        { status: 400 }
      );
    }

    if (!body.year || !body.month || !body.target_off_days) {
      return NextResponse.json(
        { error: '必須パラメータが不足しています' },
        { status: 400 }
      );
    }

    // ソルバー実行
    const solver = new ShiftSolver(
      body.staff_data,
      body.year,
      body.month,
      body.target_off_days,
      body.max_attempts || 2500
    );

    const { schedule, errors } = solver.solve();

    if (!schedule || Object.keys(schedule).length === 0) {
      return NextResponse.json(
        { error: 'シフトの作成に失敗しました' },
        { status: 500 }
      );
    }

    const days = getDaysInMonth(body.year, body.month);

    return NextResponse.json({
      schedule,
      errors,
      year: body.year,
      month: body.month,
      days,
    });
  } catch (error) {
    console.error('Shift solve error:', error);
    return NextResponse.json(
      { error: `エラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    );
  }
}

// ヘルスチェック用
export async function GET() {
  return NextResponse.json({
    message: 'Shift Solver API',
    version: '2.1.0',
    status: 'healthy',
  });
}

