/** Shared by the preview worker and tests. Runtime student lookup uses SQLite.
 * Token boundaries, punctuation and accent handling match dictionary_text.py.
 */
export const normalizeLookup = (value: string) => value.normalize("NFKC").toLowerCase().replace(/đ/g,"d").replace(/ß/g,"ss").normalize("NFKD").replace(/\p{M}/gu,"").match(/[\p{L}\p{N}]+/gu)?.join(" ") || "";
export const compactLookup = (value: string) => normalizeLookup(value).replace(/ /g,"");
export const containsPhrase = (haystack: string, needle: string) => haystack.startsWith(needle) || haystack.includes(` ${needle}`);

export function editDistance(a: string, b: string, limit: number): number {
  if (Math.abs(a.length-b.length)>limit) return limit+1;
  let previous=Array.from({length:b.length+1},(_,i)=>i),before=previous;
  for(let i=1;i<=a.length;i++) {
    const current=[i,...Array<number>(b.length).fill(limit+1)];
    for(let j=Math.max(1,i-limit);j<=Math.min(b.length,i+limit);j++) {
      current[j]=Math.min(current[j-1]+1,previous[j]+1,previous[j-1]+Number(a[i-1]!==b[j-1]));
      if(i>1 && j>1 && a[i-1]===b[j-2] && a[i-2]===b[j-1]) current[j]=Math.min(current[j],before[j-2]+1);
    }
    if(Math.min(...current)>limit) return limit+1;
    before=previous;previous=current;
  }
  return previous[b.length];
}
