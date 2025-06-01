# CFP Hierarchical Search Test System
import json
import logging
from typing import Dict, Any
import time

# Import your main classes
from test3 import (
    ElasticsearchConnection, 
    JSONCFPProcessor, 
    JSONCFPHierarchicalSearch,
    debug_elasticsearch
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CFPTestSuite:
    """Complete test suite for CFP Hierarchical Search System"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.processor = None
        self.search_system = None
        self.test_results = {}
        
    def run_all_tests(self):
        """Run complete test suite"""
        
        logger.info("="*60)
        logger.info("Starting CFP Hierarchical Search Test Suite")
        logger.info("="*60)
        
        tests = [
            ("Test 1: Elasticsearch Connection", self.test_elasticsearch_connection),
            ("Test 2: JSON Data Loading", self.test_json_loading),
            ("Test 3: Data Processing", self.test_data_processing),
            ("Test 4: Hierarchy Creation", self.test_hierarchy_creation),
            ("Test 5: Index Setup", self.test_index_setup),
            ("Test 6: Document Indexing", self.test_document_indexing),
            ("Test 7: Basic Search", self.test_basic_search),
            ("Test 8: Level Navigation", self.test_level_navigation),
            ("Test 9: Text Search", self.test_text_search),
            ("Test 10: Data Verification", self.test_data_verification)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n{test_name}")
            logger.info("-" * len(test_name))
            
            try:
                result = test_func()
                if result:
                    logger.info(f"PASS: {test_name}")
                    self.test_results[test_name] = "PASS"
                    passed_tests += 1
                else:
                    logger.error(f"FAIL: {test_name}")
                    self.test_results[test_name] = "FAIL"
            except Exception as e:
                logger.error(f"ERROR: {test_name} - {e}")
                self.test_results[test_name] = f"ERROR: {e}"
            
            time.sleep(1)  # Brief pause between tests
        
        # Final summary
        self.print_test_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def test_elasticsearch_connection(self) -> bool:
        """Test 1: Elasticsearch Connection"""
        
        try:
            # Test basic connection
            es = ElasticsearchConnection.get_instance()
            
            if not es.ping():
                logger.error("Elasticsearch ping failed")
                return False
            
            # Get cluster info
            cluster_info = es.info()
            logger.info(f"Connected to Elasticsearch {cluster_info['version']['number']}")
            
            # List existing indices
            indices = es.indices.get_alias(name="*")
            logger.info(f"Found {len(indices)} existing indices")
            
            return True
            
        except Exception as e:
            logger.error(f"Elasticsearch connection test failed: {e}")
            return False
    
    def test_json_loading(self) -> bool:
        """Test 2: JSON Data Loading"""
        
        try:
            self.processor = JSONCFPProcessor(self.json_file_path)
            
            # Load JSON data
            raw_data = self.processor.load_json_data()
            
            if not raw_data:
                logger.error("No data loaded from JSON file")
                return False
            
            logger.info(f"Successfully loaded {len(raw_data)} records")
            
            # Check sample record structure
            sample_record = raw_data[0]
            required_fields = ['Name', 'Industrials', 'Company_name', 'EF']
            
            for field in required_fields:
                if field not in sample_record:
                    logger.warning(f"Field '{field}' not found in sample record")
            
            logger.info(f"Sample record has {len(sample_record)} fields")
            return True
            
        except Exception as e:
            logger.error(f"JSON loading test failed: {e}")
            return False
    
    def test_data_processing(self) -> bool:
        """Test 3: Data Processing"""
        
        try:
            if not self.processor:
                logger.error("Processor not initialized")
                return False
            
            # Convert to DataFrame
            df = self.processor.json_to_dataframe()
            logger.info(f"Created DataFrame with {len(df)} rows, {len(df.columns)} columns")
            
            # Clean and validate
            df_clean = self.processor.clean_and_validate_data()
            logger.info(f"Cleaned DataFrame has {len(df_clean)} rows")
            
            # Check data quality
            ef_count = df_clean['ef_value'].notna().sum()
            logger.info(f"Records with EF values: {ef_count}")
            
            industries_count = df_clean['industrials'].nunique()
            logger.info(f"Unique industries: {industries_count}")
            
            companies_count = df_clean['company'].nunique()
            logger.info(f"Unique companies: {companies_count}")
            
            self.df_clean = df_clean
            return True
            
        except Exception as e:
            logger.error(f"Data processing test failed: {e}")
            return False
    
    def test_hierarchy_creation(self) -> bool:
        """Test 4: Hierarchy Creation"""
        
        try:
            if not hasattr(self, 'df_clean'):
                logger.error("Clean data not available")
                return False
            
            self.search_system = JSONCFPHierarchicalSearch()
            
            # Create hierarchy
            df_with_hierarchy = self.search_system.create_hierarchy(self.df_clean)
            
            # Check hierarchy levels
            level1_count = df_with_hierarchy['level1_industry'].nunique()
            level2_count = df_with_hierarchy['level2_product_type'].nunique()
            level3_count = df_with_hierarchy['level3_company'].nunique()
            
            logger.info(f"Level 1 (Industries): {level1_count} categories")
            logger.info(f"Level 2 (Products): {level2_count} categories")
            logger.info(f"Level 3 (Companies): {level3_count} categories")
            
            # Show sample hierarchy paths
            sample_paths = df_with_hierarchy['full_path'].value_counts().head(3)
            logger.info("Sample hierarchy paths:")
            for path, count in sample_paths.items():
                logger.info(f"  {path}: {count} items")
            
            self.df_with_hierarchy = df_with_hierarchy
            return True
            
        except Exception as e:
            logger.error(f"Hierarchy creation test failed: {e}")
            return False
    
    def test_index_setup(self) -> bool:
        """Test 5: Index Setup"""
        
        try:
            if not self.search_system:
                logger.error("Search system not initialized")
                return False
            
            # Setup index
            self.search_system.setup_index()
            
            # Verify index exists
            es = self.search_system.es
            if es.indices.exists(index=self.search_system.index_name):
                logger.info(f"Index '{self.search_system.index_name}' created successfully")
                
                # Get index info
                index_info = es.indices.get(index=self.search_system.index_name)
                mappings = index_info[self.search_system.index_name]['mappings']
                
                # Check key fields exist in mapping
                properties = mappings.get('properties', {})
                required_fields = ['name', 'industrials', 'hierarchy', 'ef_value']
                
                for field in required_fields:
                    if field in properties:
                        logger.info(f"Field '{field}' found in mapping")
                    else:
                        logger.warning(f"Field '{field}' missing in mapping")
                
                return True
            else:
                logger.error("Index not found after creation")
                return False
                
        except Exception as e:
            logger.error(f"Index setup test failed: {e}")
            return False
    
    def test_document_indexing(self) -> bool:
        """Test 6: Document Indexing"""
        
        try:
            if not hasattr(self, 'df_with_hierarchy'):
                logger.error("Hierarchy data not available")
                return False
            
            # Index documents
            success_count, error_count = self.search_system.index_documents(self.df_with_hierarchy)
            
            logger.info(f"Indexing results:")
            logger.info(f"  Success: {success_count} documents")
            logger.info(f"  Errors: {error_count} documents")
            
            # Verify document count
            es = self.search_system.es
            time.sleep(2)  # Wait for indexing to complete
            
            count_response = es.count(index=self.search_system.index_name)
            doc_count = count_response['count']
            
            logger.info(f"Total documents in index: {doc_count}")
            
            if doc_count > 0:
                logger.info("Documents successfully indexed")
                return True
            else:
                logger.error("No documents found in index")
                return False
                
        except Exception as e:
            logger.error(f"Document indexing test failed: {e}")
            return False
    
    def test_basic_search(self) -> bool:
        """Test 7: Basic Search"""
        
        try:
            if not self.search_system:
                logger.error("Search system not available")
                return False
            
            # Test basic search (should return level 1 aggregation)
            results = self.search_system.search()
            
            if 'categories' in results:
                logger.info(f"Level 1 aggregation returned {len(results['categories'])} categories")
                
                # Show sample categories
                for category in results['categories'][:3]:
                    name = category['name']
                    count = category['count']
                    avg_ef = category.get('avg_ef')
                    logger.info(f"  {name}: {count} items, avg EF: {avg_ef}")
                
                return True
            else:
                logger.error("No categories returned from basic search")
                return False
                
        except Exception as e:
            logger.error(f"Basic search test failed: {e}")
            return False
    
    def test_level_navigation(self) -> bool:
        """Test 8: Level Navigation"""
        
        try:
            # Test level-specific aggregations
            levels_to_test = [1, 2, 3]
            
            for level in levels_to_test:
                results = self.search_system._get_level_aggregation(level)
                
                if 'categories' in results:
                    count = len(results['categories'])
                    logger.info(f"Level {level}: {count} categories")
                else:
                    logger.warning(f"Level {level}: No categories returned")
            
            return True
            
        except Exception as e:
            logger.error(f"Level navigation test failed: {e}")
            return False
    
    def test_text_search(self) -> bool:
        """Test 9: Text Search"""
        
        try:
            # Test text searches
            test_queries = [
                "น้ำส้มสายชู",
                "เคมี",
                "บริษัท",
                "อาหาร"
            ]
            
            for query in test_queries:
                results = self.search_system.search(query=query)
                
                if 'total' in results:
                    total = results['total']
                    logger.info(f"Query '{query}': {total} results")
                    
                    # Show sample results
                    if 'items' in results and results['items']:
                        sample_item = results['items'][0]
                        logger.info(f"  Sample: {sample_item.get('name', 'N/A')}")
                else:
                    logger.warning(f"Query '{query}': No results structure")
            
            return True
            
        except Exception as e:
            logger.error(f"Text search test failed: {e}")
            return False
    
    def test_data_verification(self) -> bool:
        """Test 10: Data Verification"""
        
        try:
            es = self.search_system.es
            
            # Get random documents to verify data integrity
            search_body = {
                "size": 5,
                "query": {"match_all": {}}
            }
            
            response = es.search(index=self.search_system.index_name, **search_body)
            
            if response['hits']['total']['value'] > 0:
                logger.info("Sample documents verification:")
                
                for hit in response['hits']['hits']:
                    source = hit['_source']
                    name = source.get('name', 'N/A')
                    industry = source.get('hierarchy', {}).get('level1_industry', 'N/A')
                    ef_value = source.get('ef_value', 'N/A')
                    
                    logger.info(f"  {name[:50]}... | {industry} | EF: {ef_value}")
                
                return True
            else:
                logger.error("No documents found for verification")
                return False
                
        except Exception as e:
            logger.error(f"Data verification test failed: {e}")
            return False
    
    def print_test_summary(self, passed: int, total: int):
        """Print test summary"""
        
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        for test_name, result in self.test_results.items():
            status_symbol = "✓" if result == "PASS" else "✗"
            logger.info(f"{status_symbol} {test_name}: {result}")
        
        logger.info("-"*60)
        logger.info(f"PASSED: {passed}/{total} tests")
        logger.info(f"SUCCESS RATE: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("ALL TESTS PASSED! System is ready for use.")
        else:
            logger.info("Some tests failed. Please check the issues above.")
        
        logger.info("="*60)

def quick_test(json_file_path: str):
    """Quick test function"""
    
    print("Starting Quick CFP System Test...")
    print("-" * 40)
    
    try:
        # Test Elasticsearch connection
        print("1. Testing Elasticsearch connection...")
        if debug_elasticsearch():
            print("   ✓ Elasticsearch connection OK")
        else:
            print("   ✗ Elasticsearch connection FAILED")
            return False
        
        # Test JSON file
        print("2. Testing JSON file loading...")
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   ✓ JSON file loaded: {len(data)} records")
        except Exception as e:
            print(f"   ✗ JSON file loading FAILED: {e}")
            return False
        
        print("\n✓ Quick test passed! You can run the full system.")
        return True
        
    except Exception as e:
        print(f"Quick test failed: {e}")
        return False

def run_performance_test(json_file_path: str):
    """Run performance test"""
    
    logger.info("Starting Performance Test...")
    
    start_time = time.time()
    
    try:
        # Run full processing
        from new_json_cfp_processor import process_json_cfp_complete
        results = process_json_cfp_complete(json_file_path)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if results:
            logger.info(f"Performance Test Results:")
            logger.info(f"  Total processing time: {total_time:.2f} seconds")
            logger.info(f"  Documents processed: {results['indexed_docs']}")
            logger.info(f"  Processing rate: {results['indexed_docs']/total_time:.1f} docs/second")
            logger.info(f"  Errors: {results['errors']}")
            
            return True
        else:
            logger.error("Performance test failed - no results returned")
            return False
            
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        return False

if __name__ == "__main__":
    # Configuration
    json_file_path = "cfp_label_20250525.json"  # Replace with your file path
    
    print("CFP Hierarchical Search System - Test Suite")
    print("=" * 50)
    print("Choose test type:")
    print("1. Quick Test (Fast)")
    print("2. Full Test Suite (Comprehensive)")
    print("3. Performance Test")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        quick_test(json_file_path)
    elif choice == "2":
        test_suite = CFPTestSuite(json_file_path)
        test_suite.run_all_tests()
    elif choice == "3":
        run_performance_test(json_file_path)
    else:
        print("Invalid choice. Running quick test...")
        quick_test(json_file_path)