'use client';

import React, { useEffect, useState } from 'react';
import WorkCard from '@/components/WorkCard';
import Link from 'next/link';
import { useSession } from 'next-auth/react';

interface Work {
  works_id: number;
  works_title: string;
  user_id: string;
}

export default function WorksPage() {
  const { data: session, status } = useSession();
  const [works, setWorks] = useState<Work[]>([]);

  useEffect(() => {
    if (status === "authenticated" && session?.user?.email) {
      const fetchWorks = async () => {
        try {
          const res = await fetch(`http://localhost:8000/works/${session?.user?.email}/user_works`);
          if (!res.ok) throw new Error("API 호출 실패");
          const data = await res.json();
          setWorks(data);
        } catch (error) {
          console.error('작품 목록 가져오기 실패:', error);
        }
      };
      fetchWorks();
    }
  }, [status, session]);

  if (status === "loading") {
    return <p className="text-center text-gray-500">로딩중...정보 확인 중...</p>;
  }

  return (
    <div className="relative flex flex-col min-h-screen bg-gray-50 p-6">
      {/* 콘텐츠 영역 */}
      <div className="flex-grow">
        <h1 className="text-2xl font-bold mb-6">작품 목록</h1>

        <div className="space-y-4">
          {works.map((work) => (
            <WorkCard
              key={work.works_id}
              id={work.works_id}
              title={work.works_title}
              tag=""
            />
          ))}
        </div>
      </div>

      {/* 떠다니는 버튼 */}
      <Link
        href="/works/new"
        className="fixed bottom-6 right-6 z-50"
      >
        <button className="px-4 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition">
          + 작품 추가
        </button>
      </Link>
    </div>
  );
}
