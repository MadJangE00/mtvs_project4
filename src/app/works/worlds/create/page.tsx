'use client';

import React, { useState } from 'react';

export default function WorldFormPage() {
  const [form, setForm] = useState({
    국호: '',
    이명: '',
    기간: '',
    성립이전: '',
    멸망이유: '',
    국기: '',
    위치: '',
    대륙: '',
    환경: '',
    수도: '',
    통치자: '',
    통치체제: '',
    종교: '',
    통화: '',
    유통상태: '',
    기술수준: '',
    군사력: '',
    빈부격차: '',
    생활형태: '',
  });

  const handleChange = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('제출된 데이터:', form);
    // TODO: API 호출 or Supabase 연동
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">

      <h1 className="text-2xl font-bold mb-6">🌍 세계관 생성</h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-2xl shadow-md p-6 space-y-4 max-w-3xl"
      >
        {Object.entries(form).map(([key, value]) => (
          <div key={key}>
            <label className="block font-semibold mb-1">{key}</label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:ring focus:ring-blue-200"
              placeholder={`${key} 입력`}
            />
          </div>
        ))}

        <div className="text-right">
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            저장하기
          </button>
        </div>
      </form>
    </div>
  );
}
