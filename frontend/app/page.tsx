# frontend/app/page.tsx
'use client';

import { FormEvent, useState } from 'react';

export default function HomePage() {
  const [prompt, setPrompt] = useState('A cinematic close-up of a confident presenter speaking naturally in a studio');
  const [negativePrompt, setNegativePrompt] = useState('blurry, low quality, distorted face');
  const [duration, setDuration] = useState(8);
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [jobId, setJobId] = useState('');
  const [status, setStatus] = useState('');
  const [referenceImage, setReferenceImage] = useState<File | null>(null);
  const [voiceover, setVoiceover] = useState<File | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setStatus('Submitting...');

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('negative_prompt', negativePrompt);
    formData.append('duration', String(duration));
    formData.append('aspect_ratio', aspectRatio);

    if (referenceImage) {
      formData.append('reference_image', referenceImage);
    }

    if (voiceover) {
      formData.append('voiceover', voiceover);
    }

    const res = await fetch(`${apiUrl}/generate`, {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    setJobId(data.job_id || '');
    setStatus(data.status || 'queued');
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="text-4xl font-bold mb-8">Realistic Video Generator</h1>

        <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
          <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="space-y-5">
              <div>
                <label className="mb-2 block text-sm">Prompt</label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={5}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm">Negative Prompt</label>
                <textarea
                  value={negativePrompt}
                  onChange={(e) => setNegativePrompt(e.target.value)}
                  rows={3}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-2 block text-sm">Duration</label>
                  <input
                    type="number"
                    min={4}
                    max={60}
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm">Aspect Ratio</label>
                  <select
                    value={aspectRatio}
                    onChange={(e) => setAspectRatio(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3"
                  >
                    <option value="16:9">16:9</option>
                    <option value="9:16">9:16</option>
                    <option value="1:1">1:1</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-2 block text-sm">Reference Image</label>
                  <input type="file" accept="image/*" onChange={(e) => setReferenceImage(e.target.files?.[0] || null)} className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3" />
                </div>

                <div>
                  <label className="mb-2 block text-sm">Voiceover</label>
                  <input type="file" accept="audio/*" onChange={(e) => setVoiceover(e.target.files?.[0] || null)} className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3" />
                </div>
              </div>

              <button type="submit" className="w-full rounded-xl bg-violet-600 px-4 py-3 font-semibold hover:bg-violet-500">
                Generate Video
              </button>
            </div>
          </form>

          <aside className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold mb-4">Status</h2>
            <div className="rounded-xl border border-slate-700 bg-slate-950 p-4">
              <p className="text-sm text-slate-400">Current status</p>
              <p className="mt-2 text-lg font-medium text-violet-300">{status || 'Idle'}</p>
              {jobId ? <p className="mt-4 break-all text-sm">Job ID: {jobId}</p> : null}
            </div>

            <div className="mt-6 space-y-2 text-sm text-slate-300">
              <p>• text-to-video</p>
              <p>• image + prompt conditioning</p>
              <p>• character profiles</p>
              <p>• lip-sync ready</p>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
