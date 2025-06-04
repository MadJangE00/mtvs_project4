'use client';

import { useEffect, useState } from 'react';

export default function EpisodeDetailPage() {
  // 샘플 상태들
  const [selectedWorld, setSelectedWorld] = useState('트란시카 제국');
  const [selectedCharacters, setSelectedCharacters] = useState(['시아나', '린지']);
  const [description, setDescription] = useState('트란시카 성을 급습해 빠져나오며 시아나와 린지는 이후의 일을 도모한다.');
  const [dialogue, setDialogue] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateDialogue = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/episode/generate-dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          world: selectedWorld,
          characters: selectedCharacters,
          description,
        }),
      });
      const data = await res.json();
      setDialogue(data.dialogue || '(응답 없음)');
    } catch (error) {
      console.error('대사 생성 실패:', error);
      setDialogue('(에러 발생)');
    } finally {
      setLoading(false);
    }
  };

  const isReady = selectedWorld && selectedCharacters.length > 0 && description;

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">EP. 1-1</h1>

      <div className="bg-white rounded shadow p-4 space-y-2">
        <div>
          <p className="font-semibold mb-1">세계관 선택</p>
          <div className="flex flex-wrap gap-2">
            <span className="bg-blue-500 text-white rounded px-2 py-1 text-sm">{selectedWorld}</span>
          </div>
        </div>

        <div>
          <p className="font-semibold mb-1">캐릭터 선택</p>
          <div className="flex flex-wrap gap-2">
            {selectedCharacters.map((c) => (
              <span
                key={c}
                className="bg-blue-400 text-white rounded px-2 py-1 text-sm"
              >
                {c}
              </span>
            ))}
          </div>
        </div>

        <div>
          <p className="font-semibold">에피소드 설명</p>
          <p className="text-gray-700">{description}</p>
        </div>

        <button
          disabled={!isReady || loading}
          onClick={handleGenerateDialogue}
          className={`mt-2 px-4 py-2 rounded ${
            loading || !isReady
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {loading ? '생성 중...' : '대사 생성'}
        </button>
      </div>

      <div className="mt-6">
        <p className="font-semibold text-lg mb-2">대사가 이곳에 생성된다.</p>
        <pre className="whitespace-pre-wrap text-sm text-gray-800 border border-gray-200 rounded p-4 bg-gray-50">
          {dialogue || '~~~~~~\n~~~~\n~~~~~~'}
        </pre>
      </div>
    </div>
  );
}
