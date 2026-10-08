/** Exercise real TS manifest validation and server denial; no playback fixture committed. */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const ts = require("typescript");
const root = path.resolve(import.meta.dirname, "..");
function load(file) {
  const filename = path.join(root, file);
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  const module = { exports: {} };
  // The test runs the server module in Node; production Next enforces this poison-pill import.
  const imports = name => { if (name === "server-only") return {}; throw new Error(`Unexpected runtime dependency: ${name}`); };
  new Function("require", "module", "exports", output)(imports, module, module.exports);
  return module.exports;
}
const { assertPlayableManifest } = load("apps/web/src/lib/playable/validate.ts");
const { resolveAuthorizedPlayback } = load("apps/web/src/lib/playable/authority.ts");
const manifest = { playableId: "synthetic", title: "Synthetic", kind: "movie", sources: [{ id: "source", src: "/protected/synthetic.webm", mimeType: "video/webm", label: "Source" }], subtitles: [], capabilities: { pictureInPicture: true, playbackSpeed: true, subtitles: false } };
let count = 0;
assert.equal(assertPlayableManifest(manifest), manifest); count++;
assert.equal(assertPlayableManifest({ ...manifest, kind: "episode", episodeLabel: "S01E01" }).kind, "episode"); count++;
for (const change of [null, {}, { ...manifest, playableId: " " }, { ...manifest, kind: "tv" }, { ...manifest, sources: [] }, { ...manifest, sources: [null] }, { ...manifest, subtitles: null }, { ...manifest, capabilities: { pictureInPicture: "true" } }]) {
  assert.throws(() => assertPlayableManifest(change)); count++;
}
for (const src of ["javascript:alert(1)", "data:video/mp4;base64,test", "file:///private/movie.mp4", "http://example.com/movie.mp4", "//example.com/movie.mp4", "https://user:password@example.com/movie.mp4"]) {
  assert.throws(() => assertPlayableManifest({ ...manifest, sources: [{ ...manifest.sources[0], src }] })); count++;
}
assert.throws(() => assertPlayableManifest({ ...manifest, sources: [manifest.sources[0], manifest.sources[0]] })); count++;
assert.throws(() => assertPlayableManifest({ ...manifest, subtitles: [{ id: "cc", language: "en", label: "CC", src: "/cc.vtt", format: "srt" }] })); count++;
for (const identity of [null, { kind: "movie", id: "synthetic" }, { kind: "movie", id: "tmdb:123" }, { kind: "episode", id: "S01E01" }, { kind: "movie", id: "../../private/movie" }]) {
  assert.equal(await resolveAuthorizedPlayback(identity), null); count++;
}
console.log(`PASS ${count} real manifest/server-denial checks`);
