'use client';

import { useState } from 'react';

interface AiPromptModalProps {
  onSubmit: (prompt: string) => void;
  onClose: () => void;
}

export default function AiPromptModal({ onSubmit, onClose }: AiPromptModalProps) {
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    if (!input.trim()) {
      alert("프롬프트를 입력해주세요.");
      return;
    }
    onSubmit(input.trim());
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 className="text-lg font-bold mb-4">AI 프롬프트 입력</h2>
        <textarea
          className="w-full h-32 p-2 border rounded resize-none"
          placeholder="예: 더 감동적인 결말을 추가해줘"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <div className="mt-4 flex justify-end gap-2">
          <button className="px-4 py-2 bg-gray-400 text-white rounded" onClick={onClose}>
            취소
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={handleSubmit}>
            생성
          </button>
        </div>
      </div>
    </div>
  );
}
