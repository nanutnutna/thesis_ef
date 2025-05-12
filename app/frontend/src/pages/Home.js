import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { homeAPI } from '../api/api';

function Home() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await homeAPI();
        setMessage(response.data.message || 'API connected successfully!');
      } catch (error) {
        console.error('Error fetching data:', error);
        setMessage('Failed to connect to API');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const menuItems = [
    { name: 'Carbon Footprint for Organization', path: '/cfo', icon: '🏭' },
    { name: 'Carbon Footprint for Product', path: '/cfp', icon: '♻️' },
    { name: 'Carbon Footprint for Thailand Product', path: '/cfplabel', icon: '🛍️' },
    // { name: 'Keyword-Search', path: '/search', icon: '🔍' },
    // { name: 'Semantic-Search', path: '/combine', icon: '🔍' },
    // { name: 'Hybrid-Search', path: '/hybrid-search', icon: '🔄' },
    // { name: 'CLP', path: '/clp', icon: '📋' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-400 to-emerald-500 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header - Made larger */}
        <header className="bg-white rounded-xl shadow-lg p-8 mb-10">
          <div className="flex items-center justify-between">
            <h1 className="text-4xl font-bold text-emerald-700 flex items-center">
              <span className="mr-3 text-5xl">🌎</span> 
              Emission Factor Home Page
            </h1>
            <div className="bg-gray-100 px-6 py-3 rounded-lg">
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin h-6 w-6 mr-3 border-t-2 border-teal-700 border-r-2 rounded-full"></div>
                  <span className="text-green-700 text-lg">Connecting...</span>
                </div>
              ) : (
                <div className={`text-lg font-medium ${message.includes('Failed') ? 'text-red-500' : 'text-teal-700'}`}>
                  {message.includes('Failed') ? '❌ ' : '✅ '}
                  {message}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Main Content - Larger cards with more spacing */}
        <main>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {menuItems.map((item, index) => (
              <Link 
                key={index}
                to={item.path}
                className="group"
              >
                <div className="bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 transform hover:scale-105 hover:shadow-xl group-hover:bg-green-50 h-full">
                  <div className="p-8">
                    <div className="flex items-center justify-between mb-6">
                      <span className="text-5xl">{item.icon}</span>
                      <div className="bg-emerald-600 group-hover:bg-emerald-700 text-white rounded-full w-10 h-10 flex items-center justify-center transition-all duration-300">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                    <h2 className="text-2xl font-semibold text-gray-800 mb-2">{item.name}</h2>
                    <p className="text-gray-500 text-base">
                      {getDescription(item.name)}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </main>

        {/* Footer
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} Your Company Name. All rights reserved.</p>
        </footer> */}
      </div>
    </div>
  );
}

// Helper function to generate descriptions for menu items
function getDescription(name) {
  const descriptions = {
    'Carbon Footprint for Organization': "Total greenhouse gas emissions produced directly and indirectly by an organization's activities, operations",
    'Carbon Footprint for Product': "Total amount of greenhouse gases emitted throughout a product's entire life cycle",
    'Carbon Footprint for Thailand Product': 'Total greenhouse gas emissions throughout the entire life cycle of products manufactured in Thailand, certified under Thailand'
    // 'Keyword-Search': "Find exactly what you're looking for with precise word matching.",
    // 'Semantic-Search': 'Discover relevant content based on meaning, not just exact words.',
    // 'Hybrid-Search': 'Get the best of both worlds—precise matching plus meaning-based results for optimal relevance.'
    // 'CLP': 'Custom labeling platform',
  };
  
  return descriptions[name] || 'Access module functionalities';
}

export default Home;