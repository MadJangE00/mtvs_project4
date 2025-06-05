'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import AiPromptModal from '@/components/AiPromptModal'; 
import LoadingSpinner from '@/components/LoadingSpinner';// ✅ 새로 추가된 컴포넌트

interface Episode {
  episode_id: number;
  works_id: number;
  episode_content: string;
}

export default function EpisodeDetailPage() {
  const { work_id, episode_id } = useParams() as {
    work_id: string;
    episode_id: string;
  };

  const [episode, setEpisode] = useState<Episode | null>(null);
  const [episodeIndex, setEpisodeIndex] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showPromptModal, setShowPromptModal] = useState(false); // ✅ 프롬프트 입력용

  const router = useRouter();

  useEffect(() => {
    const fetchEpisode = async () => {
      try {
        const res = await fetch(`http://localhost:8000/works/${work_id}/work`);
        const data = await res.json();

        const episodes: Episode[] = data.episodes;
        const index = episodes.findIndex(ep => ep.episode_id === parseInt(episode_id));
        const foundEpisode = episodes[index];

        if (foundEpisode) {
          setEpisode(foundEpisode);
          setEpisodeIndex(index + 1);
        }
      } catch (err) {
        console.error('에피소드 불러오기 실패:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEpisode();
  }, [work_id, episode_id]);

  const handleDeleteEpisode = async () => {
    const confirmDelete = confirm("정말로 이 에피소드를 삭제 하시겠습니까?");
    if (!confirmDelete || !episode) return;

    try {
      const res = await fetch(`http://localhost:8000/episodes/${work_id}/${episode_id}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error("삭제 실패:", errorText);
        alert("에피소드 삭제에 실패 했습니다.");
        return;
      }

      alert("에피소드가 성공적으로 삭제되었습니다.");
      router.push(`/works/${work_id}`);
    } catch (error) {
      console.error("삭제 오류:", error);
      alert("에피소드 삭제에 실패했습니다.");
    }
  };

  const handleGenerateAIContent = async (prompt: string) => {
    if (!episode) return;
    setGenerating(true);
    try {
      const res = await fetch(
        `http://localhost:8000/episodes/${work_id}/${episode_id}/ai_episode_content`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ additional_prompt: prompt }),
        }
      );

      const data = await res.json();
      setEpisode((prev) =>
        prev ? { ...prev, episode_content: data.episode_content } : prev
      );
    } catch (err) {
      console.error('AI 생성 실패:', err);
      alert('AI 콘텐츠 생성 중 오류가 발생했습니다.');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="p-6">로딩 중...</div>;
  if (!episode) return <div className="p-6 text-red-500">에피소드를 찾을 수 없습니다.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">EP. {episodeIndex ?? episode.episode_id}</h1>

      <div className="bg-white p-4 rounded shadow">
        <p className="text-gray-800 whitespace-pre-line">{episode.episode_content}</p>
      </div>

      <div className="flex gap-4 mt-4">
        <button
          className="px-4 py-2 bg-green-600 text-white rounded-full shadow-lg hover:bg-green-700 transition"
          onClick={() => router.push(`/works/${work_id}/episodes/${episode_id}/edit`)}
        >
          ✏️ 에피소드 수정
        </button>
        <button
          className="px-4 py-2 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition"
          onClick={handleDeleteEpisode}
        >
          ❌ 에피소드 삭제
        </button>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition"
          onClick={() => setShowPromptModal(true)}
          disabled={generating}
        >
          🤖 AI로 콘텐츠 생성
        </button>
      </div>

{showPromptModal && (
  <AiPromptModal
    onSubmit={handleGenerateAIContent}
    onClose={() => setShowPromptModal(false)}
  />
)}

{generating && <LoadingSpinner />}

    </div>
  );
}
