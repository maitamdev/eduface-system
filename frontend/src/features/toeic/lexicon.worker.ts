import {previewDictionary} from "./previewDictionary";

self.onmessage = async (event:MessageEvent<{id:number;params:string}>) => {
  const {id,params}=event.data;
  try {self.postMessage({id,data:await previewDictionary(new URLSearchParams(params))});}
  catch(error) {self.postMessage({id,error:error instanceof Error?error.message:"Chưa tải được từ điển."});}
};
