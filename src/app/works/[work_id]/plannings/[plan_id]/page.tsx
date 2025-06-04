'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Planning {
  plan_id: number;
  plan_title: string;
  plan_content: string;
  works_id: number;
}

export default function PlanningDetailPage() {
  const { work_id, plan_id } = useParams() as {
    work_id: string;
    plan_id: string;
  };

  const [plan, setPlan] = useState<Planning | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchPlan = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/plannings/${plan_id}`
      );
      if (!res.ok) throw new Error('기획 정보를 찾을 수 없습니다.');
      const data = await res.json();
      setPlan(data);
    } catch (error) {
      console.error('에러:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, [work_id, plan_id]);

  if (loading) return <div className="p-6">로딩 중...</div>;
  if (!plan) return <div className="p-6 text-red-500">기획을 찾을 수 없습니다.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">📝 {plan.plan_title}</h1>

      <div className="bg-white p-6 rounded shadow text-gray-800 whitespace-pre-wrap">
        {plan.plan_content}
      </div>
    </div>
  );
}
