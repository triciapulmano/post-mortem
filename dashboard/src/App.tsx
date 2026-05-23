import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import AnalysisPage from "./pages/Analysis";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/analysis/:id" element={<AnalysisPage />} />
      </Routes>
    </BrowserRouter>
  );
}