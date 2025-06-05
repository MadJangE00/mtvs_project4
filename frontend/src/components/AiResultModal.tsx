'use client';

import React from 'react';

interface AiResultModalProps {
  content: string;
  onClose: () => void;
}

export default function AiResultModal({ content, onClose }: AiResultModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-xl w-full">
        <h2 className="text-xl font-bold mb-4">🤖 AI 생성 콘텐츠</h2>
        <p className="text-gray-800 whitespace-pre-wrap max-h-[400px] overflow-y-auto">
          {content}
        </p>
        <div className="mt-4 text-right">
          <button
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            onClick={onClose}
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}
