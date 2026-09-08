"use client";

export default function ErrorBoundary({
  reset,
}: Readonly<{
  error: Error & { digest?: string };
  reset: () => void;
}>) {
  return (
    <main role="alert">
      <h1>Something went wrong</h1>
      <p>CineWatch TV could not complete this request.</p>
      <button type="button" onClick={() => reset()}>
        Try again
      </button>
    </main>
  );
}
