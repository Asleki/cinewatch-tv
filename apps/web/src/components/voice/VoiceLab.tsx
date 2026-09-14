"use client";

import { useRef, useState } from "react";

import styles from "./VoiceLab.module.css";

type CaptureState = "idle" | "recording" | "paused" | "ready" | "staging" | "stored" | "error";

type RecordedSample = {
  blob: Blob;
  url: string;
  sampleRate: number;
  durationSeconds: number;
};

const consentVersion = "CWTV-NEXVOX-CONSENT-R3-001" as const;
const testers = ["tester-01", "tester-02", "tester-03", "tester-04"] as const;
const defaultPrompt = "CineWatch brings stories, people and discovery together in one experience.";

function encodeWav(chunks: Float32Array[], sampleRate: number): Blob {
  const frameCount = chunks.reduce((total, chunk) => total + chunk.length, 0);
  const buffer = new ArrayBuffer(44 + frameCount * 2);
  const view = new DataView(buffer);
  const write = (offset: number, text: string) => {
    for (let index = 0; index < text.length; index += 1) view.setUint8(offset + index, text.charCodeAt(index));
  };
  write(0, "RIFF");
  view.setUint32(4, 36 + frameCount * 2, true);
  write(8, "WAVE");
  write(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  write(36, "data");
  view.setUint32(40, frameCount * 2, true);

  let offset = 44;
  for (const chunk of chunks) {
    for (let index = 0; index < chunk.length; index += 1) {
      const sample = Math.max(-1, Math.min(1, chunk[index] ?? 0));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      offset += 2;
    }
  }
  return new Blob([buffer], { type: "audio/wav" });
}

async function blobToBase64(blob: Blob): Promise<string> {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  let binary = "";
  const slice = 0x8000;
  for (let index = 0; index < bytes.length; index += slice) {
    binary += String.fromCharCode(...bytes.subarray(index, index + slice));
  }
  return btoa(binary);
}

export default function VoiceLab() {
  const [testerId, setTesterId] = useState<(typeof testers)[number]>("tester-01");
  const [language, setLanguage] = useState("English");
  const [prompt, setPrompt] = useState(defaultPrompt);
  const [consented, setConsented] = useState(false);
  const [state, setState] = useState<CaptureState>("idle");
  const [sample, setSample] = useState<RecordedSample | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const contextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const chunksRef = useRef<Float32Array[]>([]);
  const startedAtRef = useRef<number | null>(null);
  const activeDurationRef = useRef(0);
  const resumedAtRef = useRef<number | null>(null);
  const capturingRef = useRef(false);

  function revokeSample() {
    if (sample) URL.revokeObjectURL(sample.url);
    setSample(null);
  }

  async function startRecording() {
    if (!consented) {
      setMessage("Consent must be accepted before CineWatch requests microphone access.");
      return;
    }
    setMessage(null);
    revokeSample();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true } });
      const AudioContextCtor = window.AudioContext;
      const context = new AudioContextCtor();
      const source = context.createMediaStreamSource(stream);
      const processor = context.createScriptProcessor(4096, 1, 1);
      const silentGain = context.createGain();
      silentGain.gain.value = 0;
      chunksRef.current = [];
      capturingRef.current = true;
      processor.onaudioprocess = (event) => {
        if (!capturingRef.current) return;
        const input = event.inputBuffer.getChannelData(0);
        chunksRef.current.push(new Float32Array(input));
      };
      source.connect(processor);
      processor.connect(silentGain);
      silentGain.connect(context.destination);
      streamRef.current = stream;
      contextRef.current = context;
      sourceRef.current = source;
      processorRef.current = processor;
      startedAtRef.current = performance.now();
      activeDurationRef.current = 0;
      resumedAtRef.current = performance.now();
      setState("recording");
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? `Microphone capture failed: ${error.message}` : "Microphone capture failed.");
    }
  }

  function pauseRecording() {
    if (state !== "recording") return;
    capturingRef.current = false;
    if (resumedAtRef.current != null) activeDurationRef.current += (performance.now() - resumedAtRef.current) / 1000;
    resumedAtRef.current = null;
    setState("paused");
  }

  function resumeRecording() {
    if (state !== "paused") return;
    capturingRef.current = true;
    resumedAtRef.current = performance.now();
    setState("recording");
  }

  async function stopRecording() {
    if (state !== "recording" && state !== "paused") return;
    if (state === "recording" && resumedAtRef.current != null) activeDurationRef.current += (performance.now() - resumedAtRef.current) / 1000;
    capturingRef.current = false;
    resumedAtRef.current = null;
    const context = contextRef.current;
    const processor = processorRef.current;
    const source = sourceRef.current;
    processor?.disconnect();
    source?.disconnect();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    processorRef.current = null;
    sourceRef.current = null;
    if (context) await context.close();
    contextRef.current = null;

    if (!context || !chunksRef.current.length) {
      setState("error");
      setMessage("No audio frames were captured. Nothing was staged.");
      return;
    }
    const wav = encodeWav(chunksRef.current, context.sampleRate);
    const next = {
      blob: wav,
      url: URL.createObjectURL(wav),
      sampleRate: context.sampleRate,
      durationSeconds: Math.max(activeDurationRef.current, (performance.now() - (startedAtRef.current ?? performance.now())) / 1000),
    };
    setSample(next);
    setState("ready");
    setMessage("Recording complete. Listen to your sample, then accept it or record again.");
  }

  function discard() {
    revokeSample();
    chunksRef.current = [];
    setState("idle");
    setMessage("Recording discarded. You can record another sample.");
  }

  async function acceptAndStage() {
    if (!sample || !consented) return;
    setState("staging");
    setMessage("Submitting the accepted recording...");
    const sessionId = crypto.randomUUID();
    try {
      const response = await fetch("/api/cinewatch/voice-lab/samples", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          metadata: {
            tester_id: testerId,
            session_id: sessionId,
            recorded_at: new Date().toISOString(),
            language,
            prompt,
            sample_rate: sample.sampleRate,
            duration_seconds: Number(sample.durationSeconds.toFixed(3)),
            consent_version: consentVersion,
          },
          wav_base64: await blobToBase64(sample.blob),
        }),
      });
      const payload = await response.json().catch(() => null) as { sample_id?: string; message?: string } | null;
      if (!response.ok) throw new Error(payload?.message || `staging ${response.status}`);
      setState("stored");
      setMessage(`Recording submitted as ${payload?.sample_id ?? "a governed NexVox sample"}.`);
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? `Recording could not be submitted: ${error.message}` : "Recording could not be submitted.");
    }
  }

  return (
    <section className={styles.lab}>
      <div className={styles.intro}>
        <p className={styles.eyebrow}>NexVox Voice Lab</p>
        <h1>Consent first. Capture second.</h1>
        <p>This controlled Voice Lab records training speech only from an authorized tester. Nothing is captured before consent, and nothing is submitted until you listen locally and accept the sample.</p>
      </div>

      <div className={styles.panel}>
        <div className={styles.fields}>
          <label>Authorized tester<select value={testerId} onChange={(event) => setTesterId(event.target.value as (typeof testers)[number])}>{testers.map((tester) => <option key={tester} value={tester}>{tester}</option>)}</select></label>
          <label>Language<input value={language} onChange={(event) => setLanguage(event.target.value)} maxLength={40} /></label>
          <label className={styles.prompt}>Prompt<textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} maxLength={500} rows={3} /></label>
        </div>
        <label className={styles.consent}>
          <input type="checkbox" checked={consented} disabled={state === "recording" || state === "paused" || state === "staging"} onChange={(event) => setConsented(event.target.checked)} />
          <span>I consent to this recording being used only for the approved NexVox training workflow described here. I understand I can discard it before acceptance.</span>
        </label>
        <small className={styles.version}>Consent version: {consentVersion}</small>

        <div className={styles.controls}>
          {state === "idle" || state === "error" || state === "stored" ? <button type="button" className={styles.primary} onClick={startRecording} disabled={!consented}>Start recording</button> : null}
          {state === "recording" ? <><button type="button" onClick={pauseRecording}>Pause</button><button type="button" onClick={stopRecording}>Stop</button></> : null}
          {state === "paused" ? <><button type="button" onClick={resumeRecording}>Resume</button><button type="button" onClick={stopRecording}>Stop</button></> : null}
          {sample && (state === "ready" || state === "error") ? <><button type="button" className={styles.primary} onClick={acceptAndStage}>Accept recording</button><button type="button" onClick={discard}>Record again</button></> : null}
        </div>

        {sample ? <div className={styles.preview}><strong>Playback</strong><audio controls src={sample.url} /><span>{sample.sampleRate.toLocaleString()} Hz · {sample.durationSeconds.toFixed(1)} seconds · PCM 16-bit mono WAV</span></div> : null}
        <div className={`${styles.status} ${state === "error" ? styles.statusError : ""}`} role="status" aria-live="polite">
          <strong>{state === "recording" ? "Recording" : state === "paused" ? "Paused" : state === "staging" ? "Submitting" : state === "stored" ? "Submitted" : state === "ready" ? "Recorded" : "Voice Lab ready"}</strong>
          <span>{message ?? "Choose an authorized tester and explicitly consent before microphone access can begin."}</span>
        </div>
      </div>
    </section>
  );
}
