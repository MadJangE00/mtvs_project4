'use client';

import React from 'react';

export default function CharacterListPage() {
  const characters = ['시아나', '아시엘', '린지', '클로드'];

  return (
    <div className="min-h-screen bg-gray-50 p-6 relative">

      {/* 제목 */}
      <h1 className="text-2xl font-bold mb-6">캐릭터 설정</h1>

      {/* 캐릭터 리스트 */}
      <div className="bg-white rounded-2xl shadow-md p-6 space-y-4 max-w-3xl">
        {characters.map((name, index) => (
          <div
            key={index}
            className="flex justify-center items-center bg-black text-white font-semibold rounded px-6 py-3"
          >
            {name}
          </div>
        ))}
      </div>

      {/* 하단 우측 버튼 */}
      <div className="absolute bottom-6 right-6">
        <button className="px-4 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">
          캐릭터 추가
        </button>
      </div>
    </div>
  );
}
