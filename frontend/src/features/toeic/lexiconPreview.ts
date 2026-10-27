import type {LexiconPage} from "./api";
let worker:Worker | undefined;
let sequence=0;
const pending=new Map<number,{resolve:(page:LexiconPage)=>void;reject:(error:Error)=>void}>();

/** Offload the large public dictionary to a worker, keeping typing/scrolling
 * responsive. The signed-in application receives only 30 entries from the API. */
export async function previewLexicon(params:URLSearchParams):Promise<LexiconPage> {
  if(typeof Worker==="undefined") {
    const {previewDictionary}=await import("./previewDictionary");
    return previewDictionary(params);
  }
  if(!worker) {
    worker=new Worker(new URL("./lexicon.worker.ts",import.meta.url),{type:"module"});
    worker.onmessage=(event:MessageEvent<{id:number;data?:LexiconPage;error?:string}>)=>{
      const task=pending.get(event.data.id);if(!task)return;
      pending.delete(event.data.id);
      if(event.data.error) task.reject(new Error(event.data.error));else task.resolve(event.data.data!);
    };
    worker.onerror=()=>{for(const task of pending.values())task.reject(new Error("Không tải được từ điển xem thử. Vui lòng thử lại."));pending.clear();worker?.terminate();worker=undefined;};
  }
  const id=++sequence;
  return new Promise((resolve,reject)=>{pending.set(id,{resolve,reject});worker!.postMessage({id,params:params.toString()});});
}
