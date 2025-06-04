'use client';

import React from 'react';
import Link from 'next/link';
export default function WorldListPage() {
  const worlds = [
    '트란사가 제국',
    '2왕국 르브바드',
    '1왕국 잉케리움',
    '4왕국 그레이엄',
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6 relative">
      

      {/* 제목 */}
      <h1 className="text-2xl font-bold mb-6">세계관 설정</h1>

      {/* 세계관 리스트 */}
      <div className="bg-white rounded-2xl shadow-md p-6 space-y-4 max-w-3xl">
        {worlds.map((world, index) => (
          <div
            key={index}
            className="flex justify-center items-center bg-black text-white font-semibold rounded px-6 py-3"
          >
            {world}
          </div>
        ))
        }
      <div className="absolute bottom-6 right-6">
        <button className="px-4 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">
            <Link href="/works/worlds/create">
          세계관 추가
            </Link>
        </button>
      </div>
      </div>

    </div>
  );
}
