'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Character {
  character_id: number;
  character_name: string;
  character_settings: string;
  works_id: number;
}

export default function CharacterDetailPage() {
  const { work_id, character_id } = useParams() as {
    work_id: string;
    character_id: string;
  };

  const router = useRouter();
  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCharacter = async () => {
    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/characters/${character_id}`);
      if (!res.ok) throw new Error('캐릭터 정보를 찾을 수 없습니다.');
      const data = await res.json();
      setCharacter(data);
    } catch (err) {
      console.error('에러:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCharacter = async () => {
    const confirmDelete = confirm('정말로 이 캐릭터를 삭제하시겠습니까?');
    if (!confirmDelete) return;

    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/characters/${character_id}`,
        {
          method: 'DELETE',
        }
      );

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText);
      }

      alert('✅ 캐릭터가 삭제되었습니다.');
      router.push(`/works/${work_id}`);
    } catch (err) {
      console.error('삭제 실패:', err);
      alert('삭제 중 오류 발생');
    }
  };

  useEffect(() => {
    fetchCharacter();
  }, [work_id, character_id]);

  if (loading) return <div className="p-6">로딩 중...</div>;
  if (!character) return <div className="p-6 text-red-500">캐릭터를 찾을 수 없습니다.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">👤 캐릭터 상세</h1>
      <div className="bg-white rounded-lg p-6 shadow space-y-4">
        <p><strong>이름:</strong> {character.character_name}</p>
        <p><strong>설정:</strong></p>
        <p className="whitespace-pre-wrap">{character.character_settings}</p>
      </div>

      <div className="flex gap-4 mt-6">
        <button
          className="px-4 py-2 bg-green-600 text-white rounded-full shadow-lg hover:bg-green-700 transition"
          onClick={() => router.push(`/works/${work_id}/characters/${character_id}/edit`)}
        >
          ✏️ 캐릭터 수정
        </button>

        <button
          className="px-4 py-2 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition"
          onClick={handleDeleteCharacter}
        >
          ❌ 캐릭터 삭제
        </button>
      </div>
    </div>
  );
}
