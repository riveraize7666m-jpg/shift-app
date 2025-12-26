// API client for Shift Manager

import { ShiftRequest, ShiftResponse } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function createShift(request: ShiftRequest): Promise<ShiftResponse> {
  const response = await fetch(`${API_BASE_URL}/api/shift/solve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorMessage = 'シフトの作成に失敗しました';
    try {
      const error = await response.json();
      errorMessage = error.detail || errorMessage;
    } catch {
      errorMessage = `HTTP Error: ${response.status} ${response.statusText}`;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export function parseDays(inputStr: string): number[] {
  if (!inputStr || !inputStr.trim()) return [];
  
  const fixedStr = inputStr.replace(/，/g, ',').replace(/[０１２３４５６７８９]/g, (char) => {
    return String.fromCharCode(char.charCodeAt(0) - 0xFEE0);
  });
  
  const parts = fixedStr.split(',');
  const days = new Set<number>();
  
  for (const part of parts) {
    const trimmed = part.trim();
    if (trimmed && /^\d+$/.test(trimmed)) {
      days.add(parseInt(trimmed, 10));
    }
  }
  
  return Array.from(days).sort((a, b) => a - b);
}

