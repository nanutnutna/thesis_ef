import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import SearchPageCFP from './pages/SearchPageCFP';
import SearchPageCFO from './pages/SearchPageCFO';
import SearchPageCFPLabel from './pages/SearchPageCFPLabel';
import Dictionary from './pages/Dictionary';
import SearchPageCombine from './pages/SearchPageCombine';
// import Search from './pages/#Search';
// import RealTimeSearch from './pages/RealTimeSearch';
// import Upload from './pages/Upload';
// import SearchPageCLP from './pages/SearchPageCLP';
// import SearchPageCombine from './pages/SearchPageCombine';
// import SearchPageEmbedding from "./pages/SearchPageEmbedding";
// import SearchPageHybrid from "./pages/SearchPageHybrid";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        {/* <Route path="/search" element={<Search />} /> */}
        <Route path="/cfp" element={<SearchPageCFP />} />
        <Route path="/cfo" element={<SearchPageCFO />} />
        <Route path="/cfplabel" element={<SearchPageCFPLabel />} />
        <Route path="/dictionary" element={<Dictionary />} />
        <Route path="/all" element={<SearchPageCombine />} />
        {/* <Route path="/realtime" element={<RealTimeSearch />} /> */}
        {/* <Route path="/clp" element={<SearchPageCLP />} /> */}
        {/* <Route path="/combine" element={<SearchPageCombine />} /> */}
        {/* <Route path="/upload" element={<Upload />} /> */}
        {/* <Route path="/search-embedding" element={<SearchPageEmbedding />} /> */}
        {/* <Route path="/hybrid-search" element={<SearchPageHybrid  />} /> */}
      </Routes>
    </Router>
  );
}

export default App;
