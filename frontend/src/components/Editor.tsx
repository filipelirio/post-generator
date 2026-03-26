"use client";

import dynamic from 'next/dynamic';
import 'react-quill/dist/quill.snow.css'; // Importa estilos do Quill

// Carregamento dinâmico para evitar erro de SSR (Server-Side Rendering)
const ReactQuill = dynamic(() => import('react-quill'), { 
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-slate-100 rounded-lg flex items-center justify-center">Carregando editor...</div>
});

interface EditorProps {
  value: string;
  onChange: (content: string) => void;
  className?: string;
}

export default function Editor({ value, onChange, className }: EditorProps) {
  const modules = {
    toolbar: [
      [{ 'header': [2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike', 'blockquote'],
      [{'list': 'ordered'}, {'list': 'bullet'}, {'indent': '-1'}, {'indent': '+1'}],
      ['link', 'image'],
      ['clean']
    ],
  };

  const formats = [
    'header',
    'bold', 'italic', 'underline', 'strike', 'blockquote',
    'list', 'bullet', 'indent',
    'link', 'image'
  ];

  return (
    <div className={className}>
      <ReactQuill 
        theme="snow"
        value={value}
        onChange={onChange}
        modules={modules}
        formats={formats}
        className="bg-white rounded-b-lg"
      />
    </div>
  );
}
