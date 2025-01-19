import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Search from './pages/Search';
import RealTimeSearch from './pages/RealTimeSearch';
import Upload from './pages/Upload';
import SearchPageCFP from './pages/SearchPageCFP';
import SearchPageCFO from './pages/SearchPageCFO';
import SearchPageCLP from './pages/SearchPageCLP';
import SearchPageCombine from './pages/SearchPageCombine';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/realtime" element={<RealTimeSearch />} />
        <Route path="/cfp" element={<SearchPageCFP />} />
        <Route path="/cfo" element={<SearchPageCFO />} />
        <Route path="/clp" element={<SearchPageCLP />} />
        <Route path="/combine" element={<SearchPageCombine />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Router>
  );
}

export default App;
