'use client';

import React from 'react';

export default function CreatePage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">

      {/* 제목 */}
      <h1 className="text-2xl font-bold mb-6">✍️ 기획 생성</h1>

      {/* Form */}
      <form className="bg-white rounded-2xl shadow-md p-6 space-y-4 max-w-3xl">
        {/* 각 입력 필드 */}
        <div>
          <label className="block text-sm font-semibold mb-1">제목</label>
          <input
            type="text"
            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring focus:ring-blue-200"
            placeholder="작품 제목 입력"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1">장르</label>
          <input
            type="text"
            className="w-full px-4 py-2 border rounded"
            placeholder="예: 로맨스 판타지"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1">타겟층</label>
          <select className="w-full px-4 py-2 border rounded">
            <option>10대</option>
            <option>20대</option>
            <option>30대</option>
            <option>기타</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1">작품 소개</label>
          <textarea
            rows={4}
            className="w-full px-4 py-2 border rounded"
            placeholder="작품 설명을 입력하세요"
          ></textarea>
        </div>

        {/* 등록 버튼 */}
        <div className="text-right">
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            등록
          </button>
        </div>
      </form>
    </div>
  );
}
