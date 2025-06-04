'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useRouter } from 'next/navigation';

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
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const handleDeleteEpisode = async (episodeId:number) => {
    const confirmDelete = confirm("정말로 이 에피소드를 삭제 하시겠습니까?");
    if (!confirmDelete) return;

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
    const deleted= await res.json();
    console.log('삭제 완료:', deleted);

    alert("에피소드가 성공적으로 삭제되었습니다.");
    router.push(`/works/${work_id}`);
  }catch(error){
    console.error("삭제 오류:", error);
    alert("에피소드 삭제에 실패했습니다.");
  }

  }

  useEffect(() => {
    const fetchEpisode = async () => {
      try {
        const res = await fetch(`http://localhost:8000/episodes/${work_id}/${episode_id}`);
        const data = await res.json();
        setEpisode(data);
      } catch (err) {
        console.error('에피소드 불러오기 실패:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEpisode();
  }, [work_id, episode_id]);

  if (loading) return <div className="p-6">로딩 중...</div>;
  if (!episode) return <div className="p-6 text-red-500">에피소드를 찾을 수 없습니다.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">EP. {episode.episode_id}</h1>
      <div className="bg-white p-4 rounded shadow">
        <p className="text-gray-800 whitespace-pre-line">{episode.episode_content}</p>
      </div>

      {/* 떠다니는 버튼 */}
        <button className="px-4 py-2 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition"
        onClick={() => handleDeleteEpisode(episode.episode_id)}>

          - 에피소드 삭제
        </button>
    </div>
    
  );
}
