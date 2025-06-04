'use client';

import { useRouter, useParams } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { useState } from 'react';

export default function NewEpisodePage() {
  const router = useRouter();
  const { work_id } = useParams() as { work_id: string };
  const [content, setContent] = useState('');

  const handleCreate = async () => {
    if (!content.trim()) {
      alert('내용을 입력해주세요.');
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/episodes/${work_id}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          episode_content: content,
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error('에피소드 생성 실패:', errorText);
        alert('에피소드 생성 실패');
        return;
      }

      const result = await res.json();
      console.log('에피소드 생성 완료:', result);

      // 작품 상세 페이지로 이동
      router.push(`/works/${work_id}`);
    } catch (error) {
      console.error('에러:', error);
      alert('에피소드 생성 중 오류 발생');
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-4">✍️ 에피소드 추가</h1>

      <textarea
        placeholder="에피소드 내용을 입력하세요"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="w-full h-40 border rounded p-3 mb-4"
      />

      <button
        onClick={handleCreate}
        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
      >
        에피소드 생성
      </button>
    </div>
  );
}
