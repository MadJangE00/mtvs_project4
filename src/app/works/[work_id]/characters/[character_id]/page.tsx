'use client';

import { useParams } from 'next/navigation';
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
    </div>
  );
}
