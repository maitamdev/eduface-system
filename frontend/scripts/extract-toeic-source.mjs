// Offline authoring only: inspect literal data; never evaluate upstream scripts.
import fs from "node:fs";
import ts from "typescript";

const source = ts.createSourceFile("upstream.js", fs.readFileSync(process.argv[2], "utf8"), ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
if (source.parseDiagnostics.length) throw new SyntaxError("Malformed source data script");
const bindings = new Map();
const result = { literals: Object.create(null), appends: [], sets: [], groupArrays: [], mappedLiterals: [], dynamicCalls: [], unsupported: [] };
function literal(node) {
  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) return node.text;
  if (ts.isNumericLiteral(node)) return Number(node.text);
  if (node.kind === ts.SyntaxKind.TrueKeyword) return true;
  if (node.kind === ts.SyntaxKind.FalseKeyword) return false;
  if (node.kind === ts.SyntaxKind.NullKeyword) return null;
  if (ts.isIdentifier(node) && bindings.has(node.text)) return structuredClone(bindings.get(node.text));
  if (ts.isPrefixUnaryExpression(node) && node.operator === ts.SyntaxKind.MinusToken && ts.isNumericLiteral(node.operand)) return -Number(node.operand.text);
  if (ts.isArrayLiteralExpression(node)) return node.elements.flatMap(item => {
    if (!ts.isSpreadElement(item)) return [literal(item)];
    const values = literal(item.expression);
    if (!Array.isArray(values)) throw Error("Non-array spread in source data");
    return values;
  });
  if (ts.isObjectLiteralExpression(node)) {
    const value = Object.create(null);
    for (const property of node.properties) {
      if (ts.isSpreadAssignment(property)) Object.assign(value, literal(property.expression));
      else if (ts.isShorthandPropertyAssignment(property)) value[property.name.text] = literal(property.name);
      else if (ts.isPropertyAssignment(property) && !ts.isComputedPropertyName(property.name)) value[property.name.text] = literal(property.initializer);
      else throw Error("Non-literal object property");
    }
    return value;
  }
  throw Error(`Non-literal data: ${ts.SyntaxKind[node.kind]}`);
}
function walk(node) {
  if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) && node.initializer) {
    try {
      let initializer = node.initializer;
      // Only extract the source array of .map; transformations are explicitly
      // implemented and audited in the Python importer, never executed here.
      if (ts.isCallExpression(initializer) && ts.isPropertyAccessExpression(initializer.expression) && initializer.expression.name.text === "map" && ts.isArrayLiteralExpression(initializer.expression.expression)) {
        initializer = initializer.expression.expression;
        result.mappedLiterals.push(node.name.text);
      }
      const value = literal(initializer);
      bindings.set(node.name.text, value);
      result.literals[node.name.text] = value;
    } catch {
      if (["items", "groups", "part6Groups", "readingGroups", "correctedGroups", "corrections", "p5Items", "grammarItems"].includes(node.name.text)) result.unsupported.push(node.name.text);
    }
  }
  if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.EqualsToken && node.left.getText(source) === "window.BUILTIN_BANK") result.appends.push(literal(node.right));
  if (ts.isCallExpression(node)) {
    const name = node.expression.getText(source);
    if (name === "window.BUILTIN_BANK.push") {
      for (const argument of node.arguments) {
        const value = ts.isSpreadElement(argument) ? argument.expression : argument;
        if (ts.isArrayLiteralExpression(value)) result.appends.push(literal(value));
      }
    }
    if (["pushSet", "pushReadingSet"].includes(name)) {
      try { result.sets.push({ name, args: node.arguments.map(literal) }); }
      catch { result.dynamicCalls.push(name); }
    }
  }
  if (ts.isArrayLiteralExpression(node) && node.elements.length && ts.isObjectLiteralExpression(node.elements[0])) {
    const names = node.elements[0].properties.map(p => p.name?.text);
    if (names.includes("groupId") && names.includes("items")) result.groupArrays.push(literal(node));
  }
  ts.forEachChild(node, walk);
}
walk(source);
process.stdout.write(JSON.stringify(result));
