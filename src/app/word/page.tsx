"use client";

import WordCard from "@/components/WordCard";
import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";

interface Example {
  word_example_content: string;
  example_sequence: number;
}

interface Word {
  words_id: number;
  word_name: string;
  word_content: string;
  user_id: string;
  word_created_time: string;
  word_count: number;
  examples: Example[];
}

export default function WordsMain() {
  const { data: session } = useSession();
  const userId = session?.user?.email ?? "guest";

  const [words, setWords] = useState<Word[]>([]);
  const [wordName, setWordName] = useState("");
  const [example1, setExample1] = useState("");
  const [example2, setExample2] = useState("");

  // ✅ 단어 목록 불러오기
  const fetchWords = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/words/created_time/${userId}/sort`
      );
      if (!res.ok) {
        throw new Error(`서버 응답 오류: ${res.status}`);
      }
      const data = await res.json();
      setWords(data);
    } catch (error) {
      console.error("단어 불러오기 실패:", error);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchWords();
    }
  }, [userId]);

  // ✅ 단어 등록
  const handlePost = async () => {
    if (!userId) {
      alert("로그인이 필요합니다.");
      return;
    }

    if (!wordName.trim()) {
      alert("단어를 입력해주세요");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/words/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          word_name: wordName,
          word_content: "",
          user_id: userId,
          examples: [
            { word_example_content: example1 },
            { word_example_content: example2 },
          ],
        }),
      });

      const data = await response.json();
      console.log("응답 결과:", data);
      alert("단어가 등록되었습니다!");

      // 등록 후 다시 단어 목록 불러오기
      await fetchWords();

      setWordName("");
      setExample1("");
      setExample2("");
    } catch (error) {
      console.error("단어 등록 실패:", error);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">단어 등록</h2>

      <input
        type="text"
        placeholder="단어 입력"
        value={wordName}
        onChange={(e) => setWordName(e.target.value)}
        className="w-full px-3 py-2 rounded mb-2"
      />
      <input
        type="text"
        placeholder="예시 1"
        value={example1}
        onChange={(e) => setExample1(e.target.value)}
        className="w-full px-3 py-2 rounded mb-2"
      />
      <input
        type="text"
        placeholder="예시 2"
        value={example2}
        onChange={(e) => setExample2(e.target.value)}
        className="w-full px-3 py-2 rounded mb-4"
      />

      <button
        onClick={handlePost}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        단어 등록하기
      </button>

      <div className="mt-8 space-y-4">
        <h1 className="text-2xl font-bold mb-4">📘 단어 목록</h1>
        {words.length === 0 ? (
          <p>단어가 없습니다.</p>
        ) : (
          words.map((word) => (
            <WordCard
              key={word.words_id}
              words_id={word.words_id}
              word_name={word.word_name}
              word_content={word.word_content}
              user_id={word.user_id}
            />
          ))
        )}
      </div>
    </div>
  );
}
