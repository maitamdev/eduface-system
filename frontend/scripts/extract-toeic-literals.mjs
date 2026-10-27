// Authoring utility: parse literal data, never execute downloaded JavaScript.
import fs from "node:fs";
import ts from "typescript";

const source = ts.createSourceFile("upstream.js", fs.readFileSync(process.argv[2], "utf8"), ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
function literal(node) {
  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) return node.text;
  if (ts.isNumericLiteral(node)) return Number(node.text);
  if (node.kind === ts.SyntaxKind.TrueKeyword) return true;
  if (node.kind === ts.SyntaxKind.FalseKeyword) return false;
  if (node.kind === ts.SyntaxKind.NullKeyword) return null;
  if (ts.isArrayLiteralExpression(node)) return node.elements.map(literal);
  if (ts.isObjectLiteralExpression(node)) return Object.fromEntries(node.properties.map(p => {
    if (!ts.isPropertyAssignment(p) || ts.isComputedPropertyName(p.name)) throw Error("Only literal properties are allowed");
    return [p.name.text, literal(p.initializer)];
  }));
  throw Error(`Non-literal source rejected: ${ts.SyntaxKind[node.kind]}`);
}
const result = {};
function walk(node) {
  if (ts.isVariableDeclaration(node) && ["part6Groups", "readingGroups", "items"].includes(node.name.text)) result[node.name.text] = literal(node.initializer);
  ts.forEachChild(node, walk);
}
walk(source);
process.stdout.write(JSON.stringify(result));
