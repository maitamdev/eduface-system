// @vitest-environment jsdom
import {afterEach, expect, it, vi} from "vitest";
import {cleanup, render, screen} from "@testing-library/react";
import {MemoryRouter,Route,Routes} from "react-router-dom";
import {RequireAuth} from "./RouteGuards";
vi.mock("@/context/AuthContext",()=>({useAuth:()=>({isAuthenticated:true,isLoading:false,role:"student"})}));
vi.mock("@/context/LanguageContext",()=>({useLanguage:()=>({t:(vi:string)=>vi})}));
afterEach(cleanup);
it.each(["/toeic","/toeic/"])("allows the student learning route %s",path=>{
 render(<MemoryRouter initialEntries={[path]}><Routes><Route path="/toeic" element={<RequireAuth><h1>Learning allowed</h1></RequireAuth>}/><Route path="/student" element={<h1>Student portal</h1>}/></Routes></MemoryRouter>);
 expect(screen.getByText("Learning allowed")).toBeTruthy();
});
it.each(["/system","/toeic-admin","/toeic/other"])("continues to block unrelated student routes %s",path=>{
 render(<MemoryRouter initialEntries={[path]}><Routes><Route path={path} element={<RequireAuth><h1>Restricted</h1></RequireAuth>}/><Route path="/student" element={<h1>Student portal</h1>}/></Routes></MemoryRouter>);
 expect(screen.getByText("Student portal")).toBeTruthy();
});
