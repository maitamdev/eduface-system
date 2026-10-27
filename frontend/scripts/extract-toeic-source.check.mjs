import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, unlinkSync, rmdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const parser = fileURLToPath(new URL("./extract-toeic-source.mjs", import.meta.url));
function extract(source) {
  const directory = mkdtempSync(join(tmpdir(), "eduface-ast-test-"));
  const fixture = join(directory, "source.js");
  try {
    writeFileSync(fixture, source);
    return spawnSync(process.execPath, [parser, fixture], {encoding:"utf8"});
  } finally {unlinkSync(fixture); rmdirSync(directory);}
}
test("extracts literals and spreads without running top-level source code", () => {
  const run = extract(`throw Error('This must never execute'); const choices=['A','B','C']; window.BUILTIN_BANK=[{id:'q1',choices,answer:0}]; window.BUILTIN_BANK.push(...[{id:'q2',choices:[...choices,'D'],answer:3}]);`);
  assert.equal(run.status, 0, run.stderr);
  const data = JSON.parse(run.stdout);
  assert.deepEqual(data.appends[1][0].choices, ["A","B","C","D"]);
});
test("extracts the input of map without executing callbacks", () => {
  const run = extract(`const items=[{id:'q1'}].map(() => {throw Error('Do not execute');});`);
  assert.equal(run.status, 0, run.stderr);
  const data = JSON.parse(run.stdout);
  assert.deepEqual(data.mappedLiterals, ["items"]);
  assert.equal(data.literals.items[0].id, "q1");
});
test("rejects calls and getters in scored question data", () => {
  for (const source of ["window.BUILTIN_BANK=[{answer:process.exit(77)}];", "window.BUILTIN_BANK=[{get prompt(){throw Error('no');}}];"]) {
    const run = extract(source);
    assert.notEqual(run.status, 0);
    assert.notEqual(run.status, 77);
    assert.match(run.stderr, /Non-literal/);
  }
});
test("rejects malformed syntax and non-array spreads", () => {
  for (const source of ["const items = [{id: ;", "window.BUILTIN_BANK=[...{id:'q'}];"]) assert.notEqual(extract(source).status, 0);
});
test("preserves special property names as inert data", () => {
  const run = extract(`window.BUILTIN_BANK=[{id:'q',__proto__:{flag:true}}];`);
  assert.equal(run.status, 0, run.stderr);
  const row = JSON.parse(run.stdout).appends[0][0];
  assert.equal(Object.hasOwn(row, "__proto__"), true);
  assert.equal(row.flag, undefined);
});
