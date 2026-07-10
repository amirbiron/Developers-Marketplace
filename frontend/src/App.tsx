import { Route, Routes } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { HomePage } from "@/pages/HomePage";
import { JoinPage } from "@/pages/JoinPage";
import { MatchPage } from "@/pages/MatchPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/match" element={<MatchPage />} />
        <Route path="/join" element={<JoinPage />} />
      </Routes>
    </Layout>
  );
}
