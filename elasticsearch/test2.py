# JSON CFP Data Processor and Hierarchical Search
import json
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional

# Import the hierarchical search system
from elasticsearch import Elasticsearch
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from elastic_connection import ElasticsearchConnection

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSONCFPProcessor:
    """Process JSON CFP data and create hierarchical search system"""
    
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
            
            # Print sample data structure
            if self.raw_data:
                logger.info("Sample record structure:")
                sample = self.raw_data[0]
                for key, value in sample.items():
                    logger.info(f"  {key}: {value}")
            
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
        """Convert JSON data to pandas DataFrame with standardized columns"""
        
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
        
        # Rename columns to standardized names
        df_mapped = df_raw.rename(columns=column_mapping)
        
        # Create final DataFrame with required columns
        required_columns = ['license', 'name', 'industrials', 'company', 'approve_date', 'ef_value', 'unit']
        
        self.df = pd.DataFrame()
        
        for col in required_columns:
            if col in df_mapped.columns:
                self.df[col] = df_mapped[col]
            else:
                logger.warning(f"Column '{col}' not found, creating empty column")
                self.df[col] = ''
        
        # Add additional useful columns if available
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
            # Extract numeric values from EF field
            self.df['ef_value_clean'] = self.df['ef_value'].astype(str).str.extract(r'([0-9.]+)')[0]
            self.df['ef_value_clean'] = pd.to_numeric(self.df['ef_value_clean'], errors='coerce')
            
            # Keep original for reference, use clean for calculations
            self.df['ef_value_original'] = self.df['ef_value']
            self.df['ef_value'] = self.df['ef_value_clean']
        
        # Clean unit field
        if 'unit' in self.df.columns:
            self.df['unit'] = self.df['unit'].astype(str).str.strip()
        
        # Validate and clean dates
        if 'approve_date' in self.df.columns:
            self.df['approve_date'] = self.df['approve_date'].astype(str)
            # The dates appear to be in Thai format DD/MM/YYYY (Buddhist era)
            
        # Remove completely empty rows
        self.df = self.df.dropna(how='all')
        
        # Log data quality stats
        logger.info("Data Quality Summary:")
        logger.info(f"  Total records: {len(self.df)}")
        logger.info(f"  Records with EF values: {self.df['ef_value'].notna().sum()}")
        logger.info(f"  Unique industries: {self.df['industrials'].nunique()}")
        logger.info(f"  Unique companies: {self.df['company'].nunique()}")
        
        # Show sample of industries
        logger.info("Sample industries:")
        for industry in self.df['industrials'].value_counts().head().index:
            count = self.df['industrials'].value_counts()[industry]
            logger.info(f"  {industry}: {count} records")
        
        return self.df
    
    def explore_data_structure(self) -> Dict:
        """Explore and analyze data structure for hierarchy creation"""
        
        if self.df is None:
            self.clean_and_validate_data()
        
        logger.info("Exploring data structure...")
        
        analysis = {
            'total_records': len(self.df),
            'columns': list(self.df.columns),
            'industries': {},
            'companies': {},
            'ef_statistics': {},
            'date_range': {},
            'sample_names': []
        }
        
        # Analyze industries
        industry_counts = self.df['industrials'].value_counts()
        analysis['industries'] = {
            'unique_count': len(industry_counts),
            'top_industries': dict(industry_counts.head(10)),
            'distribution': 'คลิกเพื่อดูรายละเอียด'
        }
        
        # Analyze companies  
        company_counts = self.df['company'].value_counts()
        analysis['companies'] = {
            'unique_count': len(company_counts),
            'top_companies': dict(company_counts.head(10)),
            'distribution': 'คลิกเพื่อดูรายละเอียด'
        }
        
        # Analyze EF values
        ef_stats = self.df['ef_value'].describe()
        analysis['ef_statistics'] = {
            'count_with_values': self.df['ef_value'].notna().sum(),
            'mean': ef_stats.get('mean'),
            'median': ef_stats.get('50%'),
            'min': ef_stats.get('min'),
            'max': ef_stats.get('max'),
            'std': ef_stats.get('std')
        }
        
        # Analyze date range
        date_years = self.df['approve_date'].str.extract(r'/(\d{4})')[0]
        if not date_years.empty:
            analysis['date_range'] = {
                'years': sorted(date_years.dropna().unique().tolist()),
                'year_counts': dict(date_years.value_counts())
            }
        
        # Sample product names for clustering analysis
        sample_names = self.df['name'].dropna().head(20).tolist()
        analysis['sample_names'] = sample_names
        
        # Print analysis
        logger.info("=== DATA ANALYSIS RESULTS ===")
        logger.info(f"Total Records: {analysis['total_records']}")
        logger.info(f"Industries: {analysis['industries']['unique_count']} unique")
        logger.info(f"Companies: {analysis['companies']['unique_count']} unique") 
        logger.info(f"Records with EF: {analysis['ef_statistics']['count_with_values']}")
        
        return analysis

# Enhanced CFP Hierarchical Search for JSON data
class JSONCFPHierarchicalSearch:
    """Enhanced CFP Hierarchical Search specifically for JSON data"""
    
    def __init__(self, es_host=ElasticsearchConnection.get_instance()):
        self.es = es_host
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.index_name = "json_cfp_hierarchy"
        
        # Test connection
        if self.es.ping():
            logger.info("Connected to Elasticsearch")
        else:
            logger.error("Cannot connect to Elasticsearch")
    
    def setup_index_for_json_data(self):
        """Setup Elasticsearch index optimized for JSON CFP data"""
        
        mapping = {
            "mappings": {
                "properties": {
                    # Original JSON fields
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
                    "approve_date": {"type": "date", "format": "dd/MM/yyyy||strict_date_optional_time"},
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
        
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
        
        self.es.indices.create(index=self.index_name, body=mapping)
        logger.info(f"Created index: {self.index_name}")
    
    def create_hierarchy_from_json_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create 3-level hierarchy specifically for JSON CFP data"""
        
        logger.info("Creating hierarchy from JSON data...")
        
        # Level 1: Industries (Enhanced for Thai text)
        df['level1_industry'] = df['industrials'].apply(self._categorize_thai_industry)
        
        # Level 2: Product Types (Enhanced clustering for Thai product names)
        df['level2_product_type'] = self._create_thai_product_clusters(df)
        
        # Level 3: Companies (Enhanced for Thai company names)
        df['level3_company'] = df['company'].apply(self._categorize_thai_company)
        
        # Create full path
        df['full_path'] = (
            df['level1_industry'] + '/' +
            df['level2_product_type'] + '/' +
            df['level3_company']
        )
        
        # Time processing (Buddhist year to Western year)
        df['year'] = df['approve_date'].apply(self._extract_thai_year)
        df['buddhist_year'] = df['approve_date'].apply(self._extract_buddhist_year)
        
        # Search optimization
        df['all_hierarchy_text'] = (
            df['level1_industry'] + ' ' +
            df['level2_product_type'] + ' ' +
            df['level3_company'] + ' ' +
            df['name'].fillna('') + ' ' +
            df['detail'].fillna('')
        )
        
        df['search_keywords'] = df['name'].apply(self._extract_thai_keywords)
        df['ef_range'] = df['ef_value'].apply(self._categorize_ef_range)
        df['has_ef_data'] = df['ef_value'].notna()
        
        return df
    
    def _categorize_thai_industry(self, industry: str) -> str:
        """Enhanced industry categorization for Thai text"""
        if pd.isna(industry) or str(industry).strip() == '':
            return "ไม่ระบุอุตสาหกรรม"
        
        industry_str = str(industry).lower()
        
        # More comprehensive Thai industry categorization
        if any(word in industry_str for word in ['อาหาร', 'เครื่องดื่ม', 'อาหารและเครื่องดื่ม']):
            return "อาหารและเครื่องดื่ม"
        elif any(word in industry_str for word in ['เสื้อผ้า', 'สิ่งทอ', 'แฟชั่น']):
            return "สิ่งทอและเครื่องแต่งกาย"
        elif any(word in industry_str for word in ['โลหะ', 'เหล็ก', 'อลูมิเนียม']):
            return "โลหะและแร่ธาตุ"
        elif any(word in industry_str for word in ['พลาสติก', 'ยาง', 'เคมี']):
            return "เคมีและปิโตรเคมี"
        elif any(word in industry_str for word in ['กระดาษ', 'บรรจุภัณฑ์', 'กล่อง']):
            return "กระดาษและบรรจุภัณฑ์"
        elif any(word in industry_str for word in ['อิเล็กทรอนิกส์', 'คอมพิวเตอร์', 'ไฟฟ้า']):
            return "อิเล็กทรอนิกส์"
        elif any(word in industry_str for word in ['ยานยนต์', 'รถยนต์', 'อะไหล่']):
            return "ยานยนต์"
        elif any(word in industry_str for word in ['ก่อสร้าง', 'สถาปัตย', 'วัสดุก่อสร้าง']):
            return "ก่อสร้าง"
        else:
            return "อื่นๆ"
    
    def _create_thai_product_clusters(self, df: pd.DataFrame) -> pd.Series:
        """Enhanced product clustering for Thai product names"""
        
        names = df['name'].fillna('').astype(str).tolist()
        
        # Simple Thai keyword-based categorization first
        def categorize_thai_product(name):
            name_lower = str(name).lower()
            
            # Thai product categories
            if any(word in name_lower for word in ['น้ำส้มสายชู', 'น้ำปลา', 'ซอส', 'เครื่องปรุง']):
                return "เครื่องปรุงรส"
            elif any(word in name_lower for word in ['กล่อง', 'บรรจุภัณฑ์', 'ห่อ']):
                return "บรรจุภัณฑ์"
            elif any(word in name_lower for word in ['เสื้อ', 'กางเกง', 'เครื่องแต่งกาย']):
                return "เครื่องแต่งกาย"
            elif any(word in name_lower for word in ['อาหาร', 'ขนม', 'เครื่องดื่ม']):
                return "อาหารและเครื่องดื่ม"
            elif any(word in name_lower for word in ['เคมี', 'สาร', 'น้ำมัน']):
                return "ผลิตภัณฑ์เคมี"
            elif any(word in name_lower for word in ['โลหะ', 'เหล็ก', 'อลูมิเนียม']):
                return "ผลิตภัณฑ์โลหะ"
            else:
                return "ผลิตภัณฑ์อื่นๆ"
        
        return df['name'].apply(categorize_thai_product)
    
    def _categorize_thai_company(self, company: str) -> str:
        """Enhanced company categorization for Thai companies"""
        if pd.isna(company) or str(company).strip() == '':
            return "ไม่ระบุบริษัท"
        
        company_str = str(company)
        
        # Major Thai company groups
        if any(word in company_str for word in ['เอสซีจี', 'SCG']):
            return "กลุ่ม SCG"
        elif any(word in company_str for word in ['ซีพี', 'CP', 'เจริญโภคภัณฑ์']):
            return "กลุ่ม CP"
        elif any(word in company_str for word in ['ปตท', 'PTT']):
            return "กลุ่ม PTT"
        elif any(word in company_str for word in ['ไทยออยล์', 'Thai Oil']):
            return "กลุ่ม ไทยออยล์"
        else:
            # Simplify company name
            company_parts = company_str.split()
            if company_parts:
                return company_parts[0][:20]
            return "บริษัทอื่น"
    
    def _extract_thai_year(self, date_str: str) -> str:
        """Extract Western year from Thai Buddhist date"""
        if pd.isna(date_str) or not str(date_str).strip():
            return "ไม่ระบุปี"
        
        try:
            date_parts = str(date_str).split('/')
            if len(date_parts) >= 3:
                buddhist_year = int(date_parts[-1])
                western_year = buddhist_year - 543
                return str(western_year)
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
    
    def _extract_thai_keywords(self, name: str) -> List[str]:
        """Extract Thai keywords from product names"""
        if pd.isna(name):
            return []
        
        keywords = []
        name_lower = str(name).lower()
        
        # Thai keywords
        thai_keywords = [
            'น้ำส้มสายชู', 'น้ำปลา', 'ซอส', 'กล่อง', 'บรรจุภัณฑ์',
            'เสื้อ', 'กางเกง', 'อาหาร', 'เครื่องดื่ม', 'เคมี'
        ]
        
        for keyword in thai_keywords:
            if keyword in name_lower:
                keywords.append(keyword)
        
        return keywords
    
    def _categorize_ef_range(self, ef_value) -> str:
        """Categorize EF values"""
        if pd.isna(ef_value):
            return "ไม่มีข้อมูล EF"
        
        try:
            ef_val = float(ef_value)
            if ef_val > 10:
                return "สูงมาก (>10)"
            elif ef_val > 5:
                return "สูง (5-10)"
            elif ef_val > 1:
                return "ปานกลาง (1-5)"
            else:
                return "ต่ำ (<1)"
        except:
            return "ไม่มีข้อมูล EF"

# Complete workflow function
def process_json_cfp_data(json_file_path: str, start_api: bool = False):
    """Complete workflow to process JSON CFP data and create hierarchical search"""
    
    logger.info("=== Starting JSON CFP Data Processing ===")
    
    # Step 1: Load and process JSON data
    processor = JSONCFPProcessor(json_file_path)
    
    # Load JSON data
    raw_data = processor.load_json_data()
    
    # Convert to DataFrame
    df = processor.json_to_dataframe()
    
    # Clean and validate
    df_clean = processor.clean_and_validate_data()
    
    # Explore data structure
    analysis = processor.explore_data_structure()
    
    # Step 2: Create hierarchical search system
    search_system = JSONCFPHierarchicalSearch()
    
    # Setup index
    search_system.setup_index_for_json_data()
    
    # Create hierarchy
    df_with_hierarchy = search_system.create_hierarchy_from_json_data(df_clean)
    
    # Index documents (implementation needed)
    # search_system.index_documents(df_with_hierarchy)
    
    logger.info("=== Processing Complete ===")
    logger.info(f"Processed {len(df_with_hierarchy)} records")
    logger.info(f"Created hierarchy with:")
    logger.info(f"  - {df_with_hierarchy['level1_industry'].nunique()} Level 1 categories")
    logger.info(f"  - {df_with_hierarchy['level2_product_type'].nunique()} Level 2 categories") 
    logger.info(f"  - {df_with_hierarchy['level3_company'].nunique()} Level 3 categories")
    
    # Show sample hierarchy
    logger.info("\nSample hierarchy paths:")
    sample_paths = df_with_hierarchy['full_path'].value_counts().head()
    for path, count in sample_paths.items():
        logger.info(f"  {path}: {count} items")
    
    return {
        'processor': processor,
        'search_system': search_system,
        'dataframe': df_with_hierarchy,
        'analysis': analysis
    }

# Example usage
if __name__ == "__main__":
    # Replace with your JSON file path
    json_file_path = "cfp_label_20250525.json"
    
    try:
        results = process_json_cfp_data(json_file_path)
        
        # Access results
        df = results['dataframe']
        analysis = results['analysis']
        
        print("\n=== Final Results ===")
        print(f"Total records processed: {len(df)}")
        print(f"Industries: {df['level1_industry'].value_counts().to_dict()}")
        print(f"Year range: {sorted(df['year'].unique())}")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"Error: {e}")