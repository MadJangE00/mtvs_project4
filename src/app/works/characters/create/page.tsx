'use client';

import React, { useState } from 'react';

export default function CharacterCreatePage() {
  const [form, setForm] = useState({
    이름: '',
    성별: '',
    나이: '',
    외형: '',
    인물유형: '',
    소개: '',
    표정: '',
    직업: '',
    성격: '',
    역할: '',
    즉각적욕망: '',
    대자적욕망: '',
    동기부여: '',
    가족관계: '',
  });

  const handleChange = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('캐릭터 제출:', form);
    // TODO: Supabase 저장 or API 연동
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-6">👤 캐릭터 생성</h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-2xl shadow-md p-6 space-y-4 max-w-3xl"
      >
        {Object.entries(form).map(([key, value]) => (
          <div key={key}>
            <label className="block font-semibold mb-1">{key}</label>
            <textarea
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
              className="w-full px-4 py-2 border rounded resize-none"
              placeholder={`${key} 입력`}
              rows={key === '소개' || key.includes('욕망') ? 3 : 1}
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
