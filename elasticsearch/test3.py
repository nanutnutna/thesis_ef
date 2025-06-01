# Complete JSON CFP Hierarchical Search System
import json
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional

from elasticsearch import Elasticsearch
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from elastic_connection import ElasticsearchConnection

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONCFPProcessor:
    """Process JSON CFP data"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.raw_data = None
        self.df = None
        
    def load_json_data(self) -> List[Dict]:
        """Load JSON data from file"""
        logger.info(f"Loading JSON data from: {self.json_file_path}")
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.raw_data = json.load(file)
            
            logger.info(f"Loaded {len(self.raw_data)} records from JSON")
            return self.raw_data
            
        except FileNotFoundError:
            logger.error(f"File not found: {self.json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            raise
    
    def json_to_dataframe(self) -> pd.DataFrame:
        """Convert JSON data to pandas DataFrame"""
        if not self.raw_data:
            self.load_json_data()
        
        logger.info("Converting JSON to DataFrame...")
        
        # Convert to DataFrame
        df_raw = pd.DataFrame(self.raw_data)
        
        # Map JSON fields to expected column names
        column_mapping = {
            'Seq': 'seq',
            'License': 'license', 
            'Name': 'name',
            'Detail': 'detail',
            'Industrials': 'industrials',
            'ApproveDate': 'approve_date',
            'EF': 'ef_value',
            'Unit': 'unit',
            'Scope': 'scope',
            'Contract': 'contract',
            'Phone': 'phone',
            'Mail': 'mail',
            'Company_name': 'company'
        }
        
        # Rename columns
        df_mapped = df_raw.rename(columns=column_mapping)
        
        # Create DataFrame with required columns
        required_columns = ['license', 'name', 'industrials', 'company', 'approve_date', 'ef_value', 'unit']
        self.df = pd.DataFrame()
        
        for col in required_columns:
            if col in df_mapped.columns:
                self.df[col] = df_mapped[col]
            else:
                logger.warning(f"Column '{col}' not found, creating empty column")
                self.df[col] = ''
        
        # Add optional columns
        optional_columns = ['seq', 'detail', 'scope', 'contract', 'phone', 'mail']
        for col in optional_columns:
            if col in df_mapped.columns:
                self.df[col] = df_mapped[col]
        
        logger.info(f"Created DataFrame with {len(self.df)} rows and {len(self.df.columns)} columns")
        return self.df
    
    def clean_and_validate_data(self) -> pd.DataFrame:
        """Clean and validate the DataFrame"""
        if self.df is None:
            self.json_to_dataframe()
        
        logger.info("Cleaning and validating data...")
        
        # Clean text fields
        text_columns = ['license', 'name', 'industrials', 'company']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
                self.df[col] = self.df[col].replace('NULL', '')
                self.df[col] = self.df[col].replace('nan', '')
        
        # Clean EF values
        if 'ef_value' in self.df.columns:
            self.df['ef_value_clean'] = self.df['ef_value'].astype(str).str.extract(r'([0-9.]+)')[0]
            self.df['ef_value_clean'] = pd.to_numeric(self.df['ef_value_clean'], errors='coerce')
            self.df['ef_value_original'] = self.df['ef_value']
            self.df['ef_value'] = self.df['ef_value_clean']
        
        # Clean unit field
        if 'unit' in self.df.columns:
            self.df['unit'] = self.df['unit'].astype(str).str.strip()
        
        # Clean dates
        if 'approve_date' in self.df.columns:
            self.df['approve_date'] = self.df['approve_date'].astype(str)
        
        # Remove empty rows
        self.df = self.df.dropna(how='all')
        
        # Log statistics
        logger.info("Data Quality Summary:")
        logger.info(f"  Total records: {len(self.df)}")
        logger.info(f"  Records with EF values: {self.df['ef_value'].notna().sum()}")
        logger.info(f"  Unique industries: {self.df['industrials'].nunique()}")
        logger.info(f"  Unique companies: {self.df['company'].nunique()}")
        
        # Show industries
        logger.info("Top industries:")
        industry_counts = self.df['industrials'].value_counts()
        for industry, count in industry_counts.head(5).items():
            logger.info(f"  {industry}: {count} records")
        
        return self.df

class JSONCFPHierarchicalSearch:
    """CFP Hierarchical Search for JSON data"""
    
    def __init__(self, es_host=ElasticsearchConnection.get_instance()):
        self.es = es_host
        self.index_name = "json_cfp_hierarchy"
        
        # Test connection
        try:
            if self.es.ping():
                logger.info("Connected to Elasticsearch successfully")
            else:
                logger.error("Cannot connect to Elasticsearch")
                raise ConnectionError("Elasticsearch connection failed")
        except Exception as e:
            logger.error(f"Elasticsearch connection error: {e}")
            raise
    
    def setup_index(self):
        """Setup Elasticsearch index"""
        logger.info(f"Setting up index: {self.index_name}")
        
        mapping = {
            "mappings": {
                "properties": {
                    # Original fields
                    "seq": {"type": "keyword"},
                    "license": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "completion"}
                        }
                    },
                    "detail": {"type": "text"},
                    "industrials": {"type": "keyword"},
                    "company": {"type": "keyword"}, 
                    "approve_date": {"type": "keyword"},
                    "ef_value": {"type": "float"},
                    "ef_value_original": {"type": "keyword"},
                    "unit": {"type": "keyword"},
                    "scope": {"type": "keyword"},
                    "contract": {"type": "text"},
                    "phone": {"type": "keyword"},
                    "mail": {"type": "keyword"},
                    
                    # Hierarchy structure
                    "hierarchy": {
                        "properties": {
                            "level1_industry": {"type": "keyword"},
                            "level2_product_type": {"type": "keyword"},
                            "level3_company": {"type": "keyword"},
                            "full_path": {"type": "keyword"}
                        }
                    },
                    
                    # Time filter
                    "time_filter": {
                        "properties": {
                            "year": {"type": "keyword"},
                            "buddhist_year": {"type": "keyword"}
                        }
                    },
                    
                    # Search optimization
                    "all_hierarchy_text": {"type": "text"},
                    "search_keywords": {"type": "keyword"},
                    "ef_range": {"type": "keyword"},
                    "has_ef_data": {"type": "boolean"}
                }
            }
        }
        
        try:
            # Delete existing index
            if self.es.indices.exists(index=self.index_name):
                logger.info(f"Deleting existing index: {self.index_name}")
                self.es.indices.delete(index=self.index_name)
            
            # Create new index
            logger.info(f"Creating new index: {self.index_name}")
            response = self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Index created successfully")
            
            # Verify creation
            if self.es.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} confirmed to exist")
            else:
                logger.error(f"Index {self.index_name} not found after creation")
                
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    def create_hierarchy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create 3-level hierarchy from JSON CFP data"""
        logger.info("Creating hierarchy from JSON data...")
        
        # Level 1: Industries (use actual data from JSON)
        df['level1_industry'] = df['industrials'].apply(self._categorize_industry)
        
        # Level 2: Product Types (categorize by product names)
        df['level2_product_type'] = df['name'].apply(self._categorize_product)
        
        # Level 3: Companies (simplify company names)
        df['level3_company'] = df['company'].apply(self._categorize_company)
        
        # Create full path
        df['full_path'] = (
            df['level1_industry'] + '/' +
            df['level2_product_type'] + '/' +
            df['level3_company']
        )
        
        # Time processing
        df['year'] = df['approve_date'].apply(self._extract_year)
        df['buddhist_year'] = df['approve_date'].apply(self._extract_buddhist_year)
        
        # Search optimization
        df['all_hierarchy_text'] = (
            df['level1_industry'] + ' ' +
            df['level2_product_type'] + ' ' +
            df['level3_company'] + ' ' +
            df['name'].fillna('') + ' ' +
            df.get('detail', pd.Series([''] * len(df))).fillna('')
        )
        
        df['search_keywords'] = df['name'].apply(self._extract_keywords)
        df['ef_range'] = df['ef_value'].apply(self._categorize_ef_range)
        df['has_ef_data'] = df['ef_value'].notna()
        
        logger.info(f"Hierarchy created with:")
        logger.info(f"  Level 1 categories: {df['level1_industry'].nunique()}")
        logger.info(f"  Level 2 categories: {df['level2_product_type'].nunique()}")
        logger.info(f"  Level 3 categories: {df['level3_company'].nunique()}")
        
        return df
    
    def _categorize_industry(self, industry: str) -> str:
        """Categorize industry using actual data from JSON"""
        if pd.isna(industry) or str(industry).strip() == '' or str(industry).strip() == 'NULL':
            return "ไม่ระบุอุตสาหกรรม"
        return str(industry).strip()
    
    def _categorize_product(self, name: str) -> str:
        """Categorize product based on name"""
        if pd.isna(name) or str(name).strip() == '':
            return "ไม่ระบุผลิตภัณฑ์"
        
        name_lower = str(name).lower()
        
        # Product categorization based on keywords
        if any(word in name_lower for word in ['น้ำส้มสายชู', 'น้ำปลา', 'ซอส', 'เครื่องปรุง']):
            return "เครื่องปรุงรส"
        elif any(word in name_lower for word in ['อาหาร', 'ขนม', 'เครื่องดื่ม', 'นม']):
            return "อาหารและเครื่องดื่ม"
        elif any(word in name_lower for word in ['เคมี', 'สาร', 'น้ำมัน', 'chemical']):
            return "ผลิตภัณฑ์เคมี"
        elif any(word in name_lower for word in ['กล่อง', 'บรรจุภัณฑ์', 'ห่อ', 'ถุง']):
            return "บรรจุภัณฑ์"
        elif any(word in name_lower for word in ['ยา', 'เวชภัณฑ์', 'การแพทย์']):
            return "เวชภัณฑ์"
        elif any(word in name_lower for word in ['เสื้อ', 'กางเกง', 'ผ้า', 'เครื่องแต่งกาย']):
            return "เครื่องแต่งกาย"
        elif any(word in name_lower for word in ['โลหะ', 'เหล็ก', 'อลูมิเนียม']):
            return "ผลิตภัณฑ์โลหะ"
        else:
            return "ผลิตภัณฑ์อื่นๆ"
    
    def _categorize_company(self, company: str) -> str:
        """Categorize and simplify company names"""
        if pd.isna(company) or str(company).strip() == '':
            return "ไม่ระบุบริษัท"
        
        company_str = str(company).strip()
        
        # Major company groups
        if any(word in company_str for word in ['เอสซีจี', 'SCG']):
            return "กลุ่ม SCG"
        elif any(word in company_str for word in ['ซีพี', 'CP', 'เจริญโภคภัณฑ์']):
            return "กลุ่ม CP"
        elif any(word in company_str for word in ['ปตท', 'PTT']):
            return "กลุ่ม PTT"
        elif any(word in company_str for word in ['ไทยออยล์', 'Thai Oil']):
            return "กลุ่ม ไทยออยล์"
        else:
            # Simplify long company names
            if len(company_str) > 40:
                return company_str[:40] + "..."
            return company_str
    
    def _extract_year(self, date_str: str) -> str:
        """Extract Western year from Thai Buddhist date"""
        if pd.isna(date_str) or not str(date_str).strip():
            return "ไม่ระบุปี"
        
        try:
            date_parts = str(date_str).split('/')
            if len(date_parts) >= 3:
                buddhist_year = int(date_parts[-1])
                if buddhist_year > 2500:  # Thai Buddhist year
                    western_year = buddhist_year - 543
                    return str(western_year)
                else:
                    return str(buddhist_year)
            return "ไม่ระบุปี"
        except:
            return "ไม่ระบุปี"
    
    def _extract_buddhist_year(self, date_str: str) -> str:
        """Extract Buddhist year from date"""
        if pd.isna(date_str) or not str(date_str).strip():
            return "ไม่ระบุปี"
        
        try:
            date_parts = str(date_str).split('/')
            if len(date_parts) >= 3:
                return date_parts[-1]
            return "ไม่ระบุปี"
        except:
            return "ไม่ระบุปี"
    
    def _extract_keywords(self, name: str) -> List[str]:
        """Extract keywords from product names"""
        if pd.isna(name):
            return []
        
        keywords = []
        name_lower = str(name).lower()
        
        # Thai keywords
        thai_keywords = [
            'น้ำส้มสายชู', 'น้ำปลา', 'ซอส', 'กล่อง', 'บรรจุภัณฑ์',
            'เสื้อ', 'กางเกง', 'อาหาร', 'เครื่องดื่ม', 'เคมี', 'ยา'
        ]
        
        for keyword in thai_keywords:
            if keyword in name_lower:
                keywords.append(keyword)
        
        return keywords
    
    def _categorize_ef_range(self, ef_value) -> str:
        """Categorize EF values into ranges"""
        if pd.isna(ef_value):
            return "ไม่มีข้อมูล"
        
        try:
            val = float(ef_value)
            if val > 10:
                return "สูงมาก (>10)"
            elif val > 5:
                return "สูง (5-10)"
            elif val > 1:
                return "ปานกลาง (1-5)"
            else:
                return "ต่ำ (<1)"
        except:
            return "ไม่มีข้อมูล"
    
    def index_documents(self, df: pd.DataFrame):
        """Index documents into Elasticsearch"""
        logger.info(f"Starting to index {len(df)} documents...")
        
        # Verify index exists
        if not self.es.indices.exists(index=self.index_name):
            logger.error(f"Index {self.index_name} does not exist!")
            self.setup_index()
        
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                doc = {
                    # Original fields
                    "seq": str(row.get('seq', '')),
                    "license": str(row.get('license', '')),
                    "name": str(row.get('name', '')),
                    "detail": str(row.get('detail', '')),
                    "industrials": str(row.get('industrials', '')),
                    "company": str(row.get('company', '')),
                    "approve_date": str(row.get('approve_date', '')),
                    "ef_value": float(row.get('ef_value')) if pd.notna(row.get('ef_value')) else None,
                    "ef_value_original": str(row.get('ef_value_original', '')),
                    "unit": str(row.get('unit', '')),
                    "scope": str(row.get('scope', '')),
                    "contract": str(row.get('contract', '')),
                    "phone": str(row.get('phone', '')),
                    "mail": str(row.get('mail', '')),
                    
                    # Hierarchy
                    "hierarchy": {
                        "level1_industry": str(row.get('level1_industry', '')),
                        "level2_product_type": str(row.get('level2_product_type', '')),
                        "level3_company": str(row.get('level3_company', '')),
                        "full_path": str(row.get('full_path', ''))
                    },
                    
                    # Time filter
                    "time_filter": {
                        "year": str(row.get('year', '')),
                        "buddhist_year": str(row.get('buddhist_year', ''))
                    },
                    
                    # Search optimization
                    "all_hierarchy_text": str(row.get('all_hierarchy_text', '')),
                    "search_keywords": list(row.get('search_keywords', [])),
                    "ef_range": str(row.get('ef_range', '')),
                    "has_ef_data": bool(row.get('has_ef_data', False))
                }
                
                # Index document
                self.es.index(
                    index=self.index_name, 
                    id=f"doc_{idx}", 
                    body=doc
                )
                success_count += 1
                
                # Progress logging
                if success_count % 1000 == 0:
                    logger.info(f"Indexed {success_count} documents...")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to index document {idx}: {e}")
                if error_count > 100:
                    logger.error("Too many indexing errors. Stopping.")
                    break
                continue
        
        # Refresh index
        try:
            self.es.indices.refresh(index=self.index_name)
            logger.info("Index refreshed")
        except Exception as e:
            logger.error(f"Failed to refresh index: {e}")
        
        # Final status
        logger.info(f"Indexing completed!")
        logger.info(f"  Success: {success_count} documents")
        logger.info(f"  Errors: {error_count} documents")
        
        # Verify count
        try:
            count_response = self.es.count(index=self.index_name)
            doc_count = count_response['count']
            logger.info(f"Total documents in index: {doc_count}")
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
        
        return success_count, error_count
    
    def search(self, query: str = None, level: int = None, parent_path: str = None, size: int = 20):
        """Basic search functionality"""
        
        if not query and not level and not parent_path:
            # Get level 1 categories
            return self._get_level_aggregation(1)
        
        search_body = {
            "size": size,
            "query": {"match_all": {}}
        }
        
        if query:
            search_body["query"] = {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^3",
                        "all_hierarchy_text^2", 
                        "industrials^1.5",
                        "company"
                    ]
                }
            }
        
        try:
            response = self.es.search(index=self.index_name, body=search_body)
            return self._format_search_results(response)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e)}
    
    def _get_level_aggregation(self, level: int):
        """Get aggregation for specific level"""
        
        level_fields = {
            1: "hierarchy.level1_industry",
            2: "hierarchy.level2_product_type",
            3: "hierarchy.level3_company"
        }
        
        field = level_fields.get(level)
        if not field:
            return {"error": "Invalid level"}
        
        agg_body = {
            "size": 0,
            "aggs": {
                "categories": {
                    "terms": {
                        "field": field,
                        "size": 50
                    },
                    "aggs": {
                        "avg_ef": {
                            "avg": {"field": "ef_value"}
                        },
                        "count_with_ef": {
                            "value_count": {"field": "ef_value"}
                        }
                    }
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=agg_body)
            return self._format_aggregation_results(response, level)
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return {"error": str(e)}
    
    def _format_search_results(self, response):
        """Format search results"""
        results = {
            "total": response["hits"]["total"]["value"],
            "items": []
        }
        
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            item = {
                "name": source.get("name", ""),
                "industrials": source.get("industrials", ""),
                "company": source.get("company", ""),
                "ef_value": source.get("ef_value"),
                "unit": source.get("unit", ""),
                "full_path": source.get("hierarchy", {}).get("full_path", ""),
                "score": hit["_score"]
            }
            results["items"].append(item)
        
        return results
    
    def _format_aggregation_results(self, response, level):
        """Format aggregation results"""
        results = {
            "type": "level_aggregation",
            "level": level,
            "total": response["hits"]["total"]["value"],
            "categories": []
        }
        
        for bucket in response["aggregations"]["categories"]["buckets"]:
            category = {
                "name": bucket["key"],
                "count": bucket["doc_count"],
                "avg_ef": bucket.get("avg_ef", {}).get("value"),
                "count_with_ef": bucket.get("count_with_ef", {}).get("value", 0)
            }
            results["categories"].append(category)
        
        return results

def debug_elasticsearch():
    """Debug Elasticsearch connection"""
    logger.info("Debugging Elasticsearch connection...")
    
    try:
        es = ElasticsearchConnection.get_instance()
        
        if es.ping():
            logger.info("Elasticsearch is reachable")
        else:
            logger.error("Elasticsearch is not reachable")
            return False
        
        # Get cluster info
        cluster_info = es.info()
        logger.info(f"Elasticsearch version: {cluster_info['version']['number']}")
        
        # List indices
        indices = es.indices.get_alias(name="*")
        logger.info(f"Current indices: {list(indices.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Elasticsearch debug failed: {e}")
        return False

def process_json_cfp_complete(json_file_path: str):
    """Complete workflow to process JSON CFP data"""
    
    logger.info("Starting complete JSON CFP processing...")
    
    # Debug Elasticsearch
    if not debug_elasticsearch():
        logger.error("Elasticsearch issues. Please fix before continuing.")
        return None
    
    try:
        # Step 1: Load and process data
        processor = JSONCFPProcessor(json_file_path)
        raw_data = processor.load_json_data()
        df = processor.json_to_dataframe()
        df_clean = processor.clean_and_validate_data()
        
        # Step 2: Create hierarchical search system
        search_system = JSONCFPHierarchicalSearch()
        search_system.setup_index()
        
        # Step 3: Create hierarchy
        df_with_hierarchy = search_system.create_hierarchy(df_clean)
        
        # Step 4: Index documents
        success_count, error_count = search_system.index_documents(df_with_hierarchy)
        
        # Step 5: Final verification
        logger.info("Final verification...")
        debug_elasticsearch()
        
        logger.info("Processing completed successfully!")
        return {
            'processor': processor,
            'search_system': search_system,
            'dataframe': df_with_hierarchy,
            'indexed_docs': success_count,
            'errors': error_count
        }
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise

def test_search_functionality(search_system):
    """Test basic search functionality"""
    logger.info("Testing search functionality...")
    
    try:
        # Test level 1 aggregation
        level1_results = search_system.search()
        logger.info(f"Level 1 categories: {len(level1_results.get('categories', []))}")
        
        # Test text search
        search_results = search_system.search(query="น้ำส้มสายชู")
        logger.info(f"Search results for 'น้ำส้มสายชู': {search_results.get('total', 0)} items")
        
        return True
        
    except Exception as e:
        logger.error(f"Search test failed: {e}")
        return False

if __name__ == "__main__":
    # Main execution
    json_file_path = "cfp_label_20250525.json"  # Replace with your file path
    
    try:
        results = process_json_cfp_complete(json_file_path)
        
        if results:
            logger.info("Process completed successfully!")
            logger.info(f"Indexed documents: {results['indexed_docs']}")
            logger.info(f"Errors: {results['errors']}")
            
            # Test search functionality
            test_search_functionality(results['search_system'])
            
        else:
            logger.error("Process failed")
            
    except Exception as e:
        logger.error(f"Critical error: {e}")