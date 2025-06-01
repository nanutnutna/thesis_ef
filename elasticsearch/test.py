# Complete CFP Hierarchical Search System
# Elasticsearch + Python Implementation

from elasticsearch import Elasticsearch
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CFPHierarchicalSearch:
    """
    Complete CFP Hierarchical Search System
    3-Level Hierarchy: Industry → Product Type → Company
    Time Period as Filter (not hierarchy level)
    """
    
    def __init__(self, es_host="localhost:9200"):
        """Initialize the search system"""
        self.es = Elasticsearch([es_host])
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.index_name = "cfp_hierarchy"
        
        # Test connection
        if self.es.ping():
            logger.info("Connected to Elasticsearch")
        else:
            logger.error("Cannot connect to Elasticsearch")
            raise ConnectionError("Elasticsearch connection failed")
    
    def setup_hierarchical_index(self, index_name: str = None):
        """Setup Elasticsearch index with hierarchical structure"""
        
        if index_name:
            self.index_name = index_name
        
        mapping = {
            "mappings": {
                "properties": {
                    # Original fields
                    "license": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {
                                "type": "completion",
                                "analyzer": "simple"
                            }
                        }
                    },
                    "industrials": {"type": "keyword"},
                    "company": {"type": "keyword"},
                    "approve_date": {"type": "date", "format": "dd/MM/yyyy||strict_date_optional_time"},
                    "ef_value": {"type": "float"},
                    "unit": {"type": "keyword"},
                    
                    # 3-Level Hierarchy
                    "hierarchy": {
                        "properties": {
                            "level1_industry": {"type": "keyword"},      # กระดาษ และบรรจุภัณฑ์
                            "level2_product_type": {"type": "keyword"},  # Digital Printing, Die Cut
                            "level3_company": {"type": "keyword"},       # SCG, อื่นๆ
                            "full_path": {"type": "keyword"}             # Level1/Level2/Level3
                        }
                    },
                    
                    # Time as separate filter field (not hierarchy level)
                    "time_filter": {
                        "properties": {
                            "year": {"type": "keyword"},
                            "approve_date_formatted": {"type": "date"}
                        }
                    },
                    
                    # Navigation helpers
                    "parent_paths": {"type": "keyword"},      # Array of parent paths
                    "child_count": {"type": "integer"},       # จำนวน children
                    "leaf_node": {"type": "boolean"},         # เป็น leaf หรือไม่
                    
                    # Search optimization for cross-level search
                    "all_hierarchy_text": {"type": "text"},
                    "search_keywords": {"type": "keyword"},
                    
                    # Additional metadata
                    "ef_range": {"type": "keyword"},          # High, Medium, Low, None
                    "has_ef_data": {"type": "boolean"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "thai_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase"]
                        }
                    }
                }
            }
        }
        
        # Delete existing index if exists
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            logger.info(f"Deleted existing index: {self.index_name}")
        
        # Create new index
        self.es.indices.create(index=self.index_name, body=mapping)
        logger.info(f"Created hierarchical CFP index: {self.index_name}")
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process DataFrame and create hierarchy"""
        
        logger.info(f"Processing {len(df)} records...")
        
        # Create 3-level hierarchy
        df_processed = self.create_3level_hierarchy(df.copy())
        
        logger.info("Hierarchy created successfully")
        return df_processed
    
    def create_3level_hierarchy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create 3-level hierarchy structure"""
        
        logger.info("Creating 3-level hierarchy...")
        
        # Level 1: Industries (Static)
        df['level1_industry'] = df['industrials'].apply(self._categorize_industry)
        
        # Level 2: Product Types (Auto-Generated from names)
        df['level2_product_type'] = self._create_product_clusters(df)
        
        # Level 3: Companies (Static with grouping)
        df['level3_company'] = df['company'].apply(self._categorize_company)
        
        # Create full path
        df['full_path'] = (
            df['level1_industry'] + '/' +
            df['level2_product_type'] + '/' +
            df['level3_company']
        )
        
        # Create parent paths for navigation
        df['parent_paths'] = df.apply(self._create_parent_paths, axis=1)
        
        # Add time as separate filter field
        df['year'] = df['approve_date'].apply(self._extract_year)
        
        # Determine if leaf node
        df['leaf_node'] = True  # All documents are leaf nodes
        
        # Create search optimization fields
        df['all_hierarchy_text'] = (
            df['level1_industry'] + ' ' +
            df['level2_product_type'] + ' ' +
            df['level3_company'] + ' ' +
            df['name'].fillna('')
        )
        
        df['search_keywords'] = df['name'].apply(self._extract_search_keywords)
        
        # Create EF range categories
        df['ef_range'] = df['ef_value'].apply(self._categorize_ef_range)
        df['has_ef_data'] = df['ef_value'].notna()
        
        return df
    
    def _categorize_industry(self, industry: str) -> str:
        """Level 1: Industry categorization"""
        if pd.isna(industry):
            return "อื่นๆ"
        
        industry_str = str(industry)
        if "กระดาษ" in industry_str or "บรรจุภัณฑ์" in industry_str:
            return "กระดาษและบรรจุภัณฑ์"
        elif "เคมี" in industry_str or "ปิโตร" in industry_str:
            return "เคมีและปิโตรเคมี"
        else:
            return "อื่นๆ"
    
    def _create_product_clusters(self, df: pd.DataFrame) -> pd.Series:
        """Level 2: Auto-generate product type clusters"""
        
        logger.info("Creating product clusters...")
        
        # Extract features from product names
        names = df['name'].fillna('').astype(str).tolist()
        
        if len(names) == 0:
            return pd.Series(['Unknown'] * len(df))
        
        # Create TF-IDF features
        try:
            # Filter out empty names
            non_empty_names = [name for name in names if name.strip()]
            if len(non_empty_names) < 3:
                # Fallback to simple categorization if too few names
                return df['name'].apply(self._simple_product_categorization)
            
            tfidf_features = self.vectorizer.fit_transform(names)
            
            # Determine optimal number of clusters (max 8)
            n_samples = len(df)
            n_clusters = min(8, max(3, n_samples // 50))  # 1 cluster per ~50 items
            
            logger.info(f"Creating {n_clusters} product clusters")
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_features)
            
            # Generate meaningful cluster labels
            cluster_labels = self._generate_cluster_labels(df, clusters)
            
            return pd.Series([cluster_labels.get(c, f"Category_{c}") for c in clusters])
            
        except Exception as e:
            logger.warning(f"Clustering failed: {e}, using fallback categorization")
            # Fallback to simple keyword-based categorization
            return df['name'].apply(self._simple_product_categorization)
    
    def _generate_cluster_labels(self, df: pd.DataFrame, clusters: np.ndarray) -> Dict[int, str]:
        """Generate meaningful labels for clusters"""
        
        cluster_labels = {}
        
        for cluster_id in np.unique(clusters):
            cluster_mask = clusters == cluster_id
            cluster_names = df.loc[cluster_mask, 'name'].fillna('').astype(str).tolist()
            
            # Find common keywords
            common_keywords = self._find_common_keywords(cluster_names)
            
            if common_keywords:
                cluster_labels[cluster_id] = common_keywords[0].title()
            else:
                cluster_labels[cluster_id] = f"Product_Group_{cluster_id + 1}"
        
        return cluster_labels
    
    def _find_common_keywords(self, names: List[str]) -> List[str]:
        """Find common keywords in product names"""
        
        keyword_freq = {}
        important_keywords = [
            'digital', 'printing', 'die', 'cut', 'honey', 'comb', 'corrugated', 
            'carton', 'board', 'packaging', 'paper', 'กล่อง', 'บอร์ด', 'กระดาษ'
        ]
        
        for name in names:
            name_lower = str(name).lower()
            for keyword in important_keywords:
                if keyword in name_lower:
                    keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, freq in sorted_keywords if freq >= len(names) * 0.2]  # At least 20% frequency
    
    def _simple_product_categorization(self, name: str) -> str:
        """Simple fallback categorization"""
        if pd.isna(name):
            return "อื่นๆ"
        
        name_lower = str(name).lower()
        
        if 'digital' in name_lower and 'printing' in name_lower:
            return "Digital Printing"
        elif 'die' in name_lower and 'cut' in name_lower:
            return "Die Cut Products"
        elif 'honey' in name_lower and 'comb' in name_lower:
            return "Honey Comb Products"
        elif 'corrugated' in name_lower:
            return "Corrugated Products"
        elif 'กล่อง' in name_lower or 'carton' in name_lower:
            return "Carton Products"
        else:
            return "Mixed Products"
    
    def _categorize_company(self, company: str) -> str:
        """Level 3: Company categorization"""
        if pd.isna(company):
            return "อื่นๆ"
        
        company_str = str(company)
        if "เอสซีจี" in company_str or "SCG" in company_str.upper():
            return "SCG Group"
        else:
            # Simplify company name (take first meaningful part)
            company_parts = company_str.split()
            if company_parts:
                company_short = company_parts[0]
                return company_short[:30]  # Limit length
            return "อื่นๆ"
    
    def _create_parent_paths(self, row) -> List[str]:
        """Create parent paths for navigation"""
        level1 = row['level1_industry']
        level2 = row['level2_product_type']
        
        return [
            level1,
            f"{level1}/{level2}"
        ]
    
    def _extract_year(self, date_str: str) -> str:
        """Extract year for filtering (not hierarchy)"""
        if pd.isna(date_str) or not date_str:
            return "ไม่ระบุปี"
        
        try:
            # Assume format: dd/mm/yyyy (Thai year)
            date_parts = str(date_str).split('/')
            if len(date_parts) >= 3:
                year_str = date_parts[-1]
                if len(year_str) == 4:
                    thai_year = int(year_str)
                    western_year = thai_year - 543 if thai_year > 2500 else thai_year
                    return str(western_year)
            return "ไม่ระบุปี"
        except:
            return "ไม่ระบุปี"
    
    def _extract_search_keywords(self, name: str) -> List[str]:
        """Extract keywords for cross-level search"""
        if pd.isna(name):
            return []
        
        keywords = []
        name_lower = str(name).lower()
        
        # Common Thai/English keywords
        important_terms = [
            'กล่อง', 'บอร์ด', 'กระดาษ', 'carton', 'board', 'paper',
            'digital', 'printing', 'die', 'cut', 'packaging', 'น้ำส้มสายชู'
        ]
        
        for term in important_terms:
            if term in name_lower:
                keywords.append(term)
        
        return keywords
    
    def _categorize_ef_range(self, ef_value) -> str:
        """Categorize EF values into ranges"""
        if pd.isna(ef_value):
            return "ไม่มีข้อมูล"
        
        try:
            ef_val = float(ef_value)
            if ef_val > 1000:
                return "สูงมาก (>1000)"
            elif ef_val > 500:
                return "สูง (500-1000)"
            elif ef_val > 100:
                return "ปานกลาง (100-500)"
            else:
                return "ต่ำ (<100)"
        except:
            return "ไม่มีข้อมูล"
    
    def index_documents(self, df: pd.DataFrame):
        """Index processed documents into Elasticsearch"""
        
        logger.info(f"Indexing {len(df)} documents...")
        
        for idx, row in df.iterrows():
            doc = {
                # Original fields
                "license": row.get('license', ''),
                "name": row.get('name', ''),
                "industrials": row.get('industrials', ''),
                "company": row.get('company', ''),
                "approve_date": row.get('approve_date', ''),
                "ef_value": row.get('ef_value') if pd.notna(row.get('ef_value')) else None,
                "unit": row.get('unit', ''),
                
                # Hierarchy
                "hierarchy": {
                    "level1_industry": row.get('level1_industry', ''),
                    "level2_product_type": row.get('level2_product_type', ''),
                    "level3_company": row.get('level3_company', ''),
                    "full_path": row.get('full_path', '')
                },
                
                # Time filter
                "time_filter": {
                    "year": row.get('year', ''),
                    "approve_date_formatted": row.get('approve_date', '')
                },
                
                # Navigation helpers
                "parent_paths": row.get('parent_paths', []),
                "leaf_node": row.get('leaf_node', True),
                
                # Search optimization
                "all_hierarchy_text": row.get('all_hierarchy_text', ''),
                "search_keywords": row.get('search_keywords', []),
                
                # Additional metadata
                "ef_range": row.get('ef_range', ''),
                "has_ef_data": row.get('has_ef_data', False)
            }
            
            try:
                self.es.index(index=self.index_name, id=idx, body=doc)
            except Exception as e:
                logger.error(f"Failed to index document {idx}: {e}")
        
        # Refresh index
        self.es.indices.refresh(index=self.index_name)
        logger.info("Indexing completed successfully!")
    
    # SEARCH METHODS
    
    def hierarchical_search(self, query: str = None, level: int = None, 
                          parent_path: str = None, year_filter: str = None) -> Dict:
        """Main hierarchical search function"""
        
        if level is None and parent_path is None and query is None:
            # Root level - show level 1 categories
            return self._get_level_aggregation(1, year_filter)
        elif level and not parent_path:
            # Get specific level aggregation
            return self._get_level_aggregation(level, year_filter)
        elif parent_path:
            # Drill down into specific path
            return self._drill_down_search(parent_path, query, year_filter)
        else:
            # Cross-level search with query
            return self._cross_level_search(query, year_filter)
    
    def _get_level_aggregation(self, level: int, year_filter: str = None) -> Dict:
        """Get aggregation for specific hierarchy level"""
        
        level_field_map = {
            1: "hierarchy.level1_industry",
            2: "hierarchy.level2_product_type", 
            3: "hierarchy.level3_company"
        }
        
        field = level_field_map.get(level)
        if not field:
            return {"error": "Invalid level"}
        
        # Build query with year filter if provided
        query_body = {"match_all": {}}
        if year_filter and year_filter != "ไม่ระบุปี":
            query_body = {
                "term": {"time_filter.year": year_filter}
            }
        
        agg_body = {
            "size": 0,
            "query": query_body,
            "aggs": {
                "categories": {
                    "terms": {
                        "field": field,
                        "size": 20
                    },
                    "aggs": {
                        "avg_ef": {
                            "avg": {"field": "ef_value"}
                        },
                        "count_with_ef": {
                            "value_count": {"field": "ef_value"}
                        },
                        "sample_items": {
                            "top_hits": {
                                "size": 3,
                                "_source": ["name", "ef_value", "unit", "time_filter.year"]
                            }
                        },
                        # Add year distribution as additional info
                        "year_distribution": {
                            "terms": {"field": "time_filter.year", "size": 5}
                        }
                    }
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=agg_body)
            return self._format_level_results(response, level)
        except Exception as e:
            logger.error(f"Level aggregation search failed: {e}")
            return {"error": str(e)}
    
    def _drill_down_search(self, parent_path: str, query: str = None, year_filter: str = None) -> Dict:
        """Drill down into specific hierarchy path"""
        
        path_parts = parent_path.split('/')
        
        # Build filter based on path depth
        must_filters = []
        
        if len(path_parts) >= 1:
            must_filters.append({
                "term": {"hierarchy.level1_industry": path_parts[0]}
            })
        
        if len(path_parts) >= 2:
            must_filters.append({
                "term": {"hierarchy.level2_product_type": path_parts[1]}
            })
        
        if len(path_parts) >= 3:
            must_filters.append({
                "term": {"hierarchy.level3_company": path_parts[2]}
            })
        
        # Add year filter if provided
        if year_filter and year_filter != "ไม่ระบุปี":
            must_filters.append({
                "term": {"time_filter.year": year_filter}
            })
        
        search_body = {
            "size": 50,
            "query": {
                "bool": {
                    "must": must_filters if must_filters else [{"match_all": {}}]
                }
            },
            "sort": [
                {"ef_value": {"order": "desc", "missing": "_last"}},
                {"_score": {"order": "desc"}}
            ]
        }
        
        # Add text search if query provided
        if query:
            search_body["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["name^2", "all_hierarchy_text", "search_keywords^1.5"],
                    "fuzziness": "AUTO"
                }
            })
        
        # Add year filter aggregation
        search_body["aggs"] = {
            "year_filter": {
                "terms": {"field": "time_filter.year", "size": 10}
            }
        }
        
        # Add aggregation for next level (only if not at level 3)
        next_level = len(path_parts) + 1
        if next_level <= 3:
            level_field_map = {
                2: "hierarchy.level2_product_type",
                3: "hierarchy.level3_company"
            }
            
            next_field = level_field_map.get(next_level)
            if next_field:
                search_body["aggs"]["next_level"] = {
                    "terms": {"field": next_field, "size": 20},
                    "aggs": {
                        "avg_ef": {"avg": {"field": "ef_value"}},
                        "count": {"value_count": {"field": "ef_value"}}
                    }
                }
        
        try:
            response = self.es.search(index=self.index_name, body=search_body)
            return self._format_drill_down_results(response, parent_path, next_level)
        except Exception as e:
            logger.error(f"Drill down search failed: {e}")
            return {"error": str(e)}
    
    def _cross_level_search(self, query: str, year_filter: str = None) -> Dict:
        """Search across all hierarchy levels"""
        
        must_queries = [
            {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^3",
                        "all_hierarchy_text^2",
                        "search_keywords^2",
                        "industrials^1.5",
                        "company"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            }
        ]
        
        # Add year filter if provided
        if year_filter and year_filter != "ไม่ระบุปี":
            must_queries.append({
                "term": {"time_filter.year": year_filter}
            })
        
        search_body = {
            "size": 30,
            "query": {
                "bool": {
                    "must": must_queries
                }
            },
            "highlight": {
                "fields": {
                    "name": {},
                    "all_hierarchy_text": {}
                }
            },
            "aggs": {
                "by_level1": {
                    "terms": {"field": "hierarchy.level1_industry", "size": 10},
                    "aggs": {
                        "by_level2": {
                            "terms": {"field": "hierarchy.level2_product_type", "size": 5},
                            "aggs": {
                                "avg_ef": {"avg": {"field": "ef_value"}}
                            }
                        }
                    }
                },
                "by_year": {
                    "terms": {"field": "time_filter.year", "size": 10}
                },
                "ef_stats": {
                    "stats": {"field": "ef_value"}
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=search_body)
            return self._format_cross_level_results(response, query)
        except Exception as e:
            logger.error(f"Cross-level search failed: {e}")
            return {"error": str(e)}
    
    # RESULT FORMATTING METHODS
    
    def _format_level_results(self, response: Dict, level: int) -> Dict:
        """Format level aggregation results"""
        
        results = {
            "type": "level_aggregation",
            "level": level,
            "total_documents": response["hits"]["total"]["value"],
            "categories": []
        }
        
        for bucket in response["aggregations"]["categories"]["buckets"]:
            category = {
                "name": bucket["key"],
                "count": bucket["doc_count"],
                "avg_ef": bucket.get("avg_ef", {}).get("value"),
                "count_with_ef": bucket.get("count_with_ef", {}).get("value", 0),
                "year_distribution": [
                    {"year": y["key"], "count": y["doc_count"]} 
                    for y in bucket.get("year_distribution", {}).get("buckets", [])
                ],
                "sample_items": [
                    hit["_source"] for hit in bucket["sample_items"]["hits"]["hits"]
                ]
            }
            results["categories"].append(category)
        
        return results
    
    # UTILITY METHODS
    
    def get_hierarchy_statistics(self) -> Dict:
        """Get overall hierarchy statistics"""
        
        stats_body = {
            "size": 0,
            "aggs": {
                "total_documents": {
                    "value_count": {"field": "_id"}
                },
                "level1_count": {
                    "cardinality": {"field": "hierarchy.level1_industry"}
                },
                "level2_count": {
                    "cardinality": {"field": "hierarchy.level2_product_type"}
                },
                "level3_count": {
                    "cardinality": {"field": "hierarchy.level3_company"}
                },
                "year_range": {
                    "terms": {"field": "time_filter.year", "size": 20}
                },
                "ef_statistics": {
                    "stats": {"field": "ef_value"}
                },
                "documents_with_ef": {
                    "filter": {"exists": {"field": "ef_value"}}
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=stats_body)
            aggs = response["aggregations"]
            
            return {
                "total_documents": aggs["total_documents"]["value"],
                "hierarchy_levels": {
                    "level1_categories": aggs["level1_count"]["value"],
                    "level2_categories": aggs["level2_count"]["value"],
                    "level3_categories": aggs["level3_count"]["value"]
                },
                "year_distribution": [
                    {"year": bucket["key"], "count": bucket["doc_count"]}
                    for bucket in aggs["year_range"]["buckets"]
                ],
                "ef_statistics": {
                    "total_with_ef": aggs["documents_with_ef"]["doc_count"],
                    "average_ef": aggs["ef_statistics"]["avg"],
                    "min_ef": aggs["ef_statistics"]["min"],
                    "max_ef": aggs["ef_statistics"]["max"]
                }
            }
        except Exception as e:
            logger.error(f"Statistics query failed: {e}")
            return {"error": str(e)}
    
    def autocomplete_search(self, partial_query: str, limit: int = 10) -> List[str]:
        """Autocomplete suggestions for search"""
        
        suggest_body = {
            "suggest": {
                "name_suggest": {
                    "prefix": partial_query,
                    "completion": {
                        "field": "name.suggest",
                        "size": limit
                    }
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=suggest_body)
            suggestions = []
            
            for option in response["suggest"]["name_suggest"][0]["options"]:
                suggestions.append(option["text"])
            
            return suggestions
        except Exception as e:
            logger.error(f"Autocomplete search failed: {e}")
            return []
    
    def search_by_ef_range(self, ef_min: float = None, ef_max: float = None, 
                          limit: int = 20) -> Dict:
        """Search by EF value range"""
        
        range_filter = {}
        if ef_min is not None:
            range_filter["gte"] = ef_min
        if ef_max is not None:
            range_filter["lte"] = ef_max
        
        search_body = {
            "size": limit,
            "query": {
                "range": {"ef_value": range_filter}
            },
            "sort": [
                {"ef_value": {"order": "desc"}}
            ],
            "aggs": {
                "hierarchy_breakdown": {
                    "terms": {"field": "hierarchy.level1_industry"},
                    "aggs": {
                        "avg_ef": {"avg": {"field": "ef_value"}}
                    }
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=search_body)
            
            results = {
                "query": f"EF range: {ef_min or 0} - {ef_max or 'max'}",
                "total": response["hits"]["total"]["value"],
                "items": []
            }
            
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results["items"].append({
                    "name": source.get("name", ""),
                    "ef_value": source.get("ef_value"),
                    "unit": source.get("unit", ""),
                    "full_path": source.get("hierarchy", {}).get("full_path", "")
                })
            
            return results
        except Exception as e:
            logger.error(f"EF range search failed: {e}")
            return {"error": str(e)}
    
    def get_navigation_menu(self) -> Dict:
        """Get navigation menu structure"""
        
        menu_body = {
            "size": 0,
            "aggs": {
                "level1": {
                    "terms": {"field": "hierarchy.level1_industry", "size": 20},
                    "aggs": {
                        "level2": {
                            "terms": {"field": "hierarchy.level2_product_type", "size": 20},
                            "aggs": {
                                "level3": {
                                    "terms": {"field": "hierarchy.level3_company", "size": 20},
                                    "aggs": {
                                        "doc_count": {"value_count": {"field": "_id"}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=menu_body)
            menu = []
            
            for l1_bucket in response["aggregations"]["level1"]["buckets"]:
                l1_item = {
                    "name": l1_bucket["key"],
                    "count": l1_bucket["doc_count"],
                    "path": l1_bucket["key"],
                    "children": []
                }
                
                for l2_bucket in l1_bucket["level2"]["buckets"]:
                    l2_item = {
                        "name": l2_bucket["key"],
                        "count": l2_bucket["doc_count"],
                        "path": f"{l1_bucket['key']}/{l2_bucket['key']}",
                        "children": []
                    }
                    
                    for l3_bucket in l2_bucket["level3"]["buckets"]:
                        l3_item = {
                            "name": l3_bucket["key"],
                            "count": l3_bucket["doc_count"],
                            "path": f"{l1_bucket['key']}/{l2_bucket['key']}/{l3_bucket['key']}"
                        }
                        l2_item["children"].append(l3_item)
                    
                    l1_item["children"].append(l2_item)
                
                menu.append(l1_item)
            
            return {"navigation_menu": menu}
        except Exception as e:
            logger.error(f"Navigation menu query failed: {e}")
            return {"error": str(e)}

# USAGE EXAMPLES AND TESTING

def load_sample_data() -> pd.DataFrame:
    """Load sample CFP data for testing"""
    
    sample_data = {
        'license': [
            'TGO CFP FY25-182-02-1540',
            'TGO CFP FY24-142-1592', 
            'TGO CFP FY24-235-2311',
            'TGO CFP FY24-142-1589',
            'TGO CFP FY25-103-0830'
        ],
        'name': [
            'Die cut-Honey comb board',
            'Digital printing- Die cut-Corrugated Carton',
            'Digital printing- Die cut-Corrugated Carton', 
            'Digital printing- Die cut-Micro Flute Carton',
            'น้ำส้มสายชู'
        ],
        'industrials': [
            'กระดาษ และบรรจุภัณฑ์',
            'กระดาษ และบรรจุภัณฑ์',
            'กระดาษ และบรรจุภัณฑ์',
            'กระดาษ และบรรจุภัณฑ์', 
            'ปิโตรเคมี และเคมีภัณฑ์'
        ],
        'company': [
            'บริษัท เอสซีจี แพคเกจจิ้ง จำกัด (มหาชน)',
            'บริษัท เอสซีจี แพคเกจจิ้ง จำกัด (มหาชน)',
            'บริษัท เอสซีจี แพคเกจจิ้ง จำกัด (มหาชน)',
            'บริษัท เอสซีจี แพคเกจจิ้ง จำกัด (มหาชน)',
            'บริษัท อื่น จำกัด'
        ],
        'approve_date': [
            '22/04/2568',
            '09/05/2567', 
            '28/08/2567',
            '09/05/2567',
            '24/02/2568'
        ],
        'ef_value': [690, None, None, None, 1.51],
        'unit': ['1 ตัน', '1 ตัน', '1 ตัน', '1 ตัน', '1 กิโลกรัม']
    }
    
    return pd.DataFrame(sample_data)

def example_usage():
    """Complete usage example"""
    
    print("=== CFP Hierarchical Search System Demo ===\n")
    
    # Initialize system
    cfp_search = CFPHierarchicalSearch()
    
    # Setup index
    cfp_search.setup_hierarchical_index()
    
    # Load and process data
    df = load_sample_data()
    df_processed = cfp_search.process_dataframe(df)
    
    print("Processed DataFrame structure:")
    print(df_processed[['name', 'level1_industry', 'level2_product_type', 'level3_company', 'year']].head())
    print()
    
    # Index documents
    cfp_search.index_documents(df_processed)
    
    # Wait for indexing to complete
    import time
    time.sleep(2)
    
    # Example searches
    print("=== 1. Level 1 Categories ===")
    level1_results = cfp_search.hierarchical_search(level=1)
    print(json.dumps(level1_results, indent=2, ensure_ascii=False))
    print()
    
    print("=== 2. Drill down: กระดาษและบรรจุภัณฑ์ ===")
    drill_results = cfp_search.hierarchical_search(parent_path="กระดาษและบรรจุภัณฑ์")
    print(json.dumps(drill_results, indent=2, ensure_ascii=False))
    print()
    
    print("=== 3. Cross-level search: น้ำส้มสายชู ===")
    search_results = cfp_search.hierarchical_search(query="น้ำส้มสายชู")
    print(json.dumps(search_results, indent=2, ensure_ascii=False))
    print()
    
    print("=== 4. Search with year filter ===")
    year_results = cfp_search.hierarchical_search(query="carton", year_filter="2024")
    print(json.dumps(year_results, indent=2, ensure_ascii=False))
    print()
    
    print("=== 5. Hierarchy Statistics ===")
    stats = cfp_search.get_hierarchy_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print()
    
    print("=== 6. Navigation Menu ===")
    menu = cfp_search.get_navigation_menu()
    print(json.dumps(menu, indent=2, ensure_ascii=False))
    print()
    
    print("=== 7. EF Range Search ===")
    ef_results = cfp_search.search_by_ef_range(ef_min=500, ef_max=1000)
    print(json.dumps(ef_results, indent=2, ensure_ascii=False))
    print()
    
    print("=== 8. Autocomplete ===")
    suggestions = cfp_search.autocomplete_search("dig")
    print(f"Autocomplete suggestions for 'dig': {suggestions}")

def test_with_custom_data(csv_file_path: str):
    """Test with custom CSV data"""
    
    try:
        # Load CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} records from {csv_file_path}")
        
        # Initialize system
        cfp_search = CFPHierarchicalSearch()
        cfp_search.setup_hierarchical_index()
        
        # Process and index data
        df_processed = cfp_search.process_dataframe(df)
        cfp_search.index_documents(df_processed)
        
        print("Data indexed successfully!")
        
        # Get statistics
        stats = cfp_search.get_hierarchy_statistics()
        print(f"Hierarchy Statistics: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        return cfp_search
        
    except Exception as e:
        logger.error(f"Error processing custom data: {e}")
        return None

# FastAPI Integration

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

# Pydantic Models for API
class SearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    level: Optional[int] = Field(None, ge=1, le=3, description="Hierarchy level (1-3)")
    parent_path: Optional[str] = Field(None, description="Parent path for drill-down")
    year_filter: Optional[str] = Field(None, description="Year filter")

class SearchResponse(BaseModel):
    type: str
    total: Optional[int] = None
    items: List[dict] = []
    categories: Optional[List[dict]] = None
    hierarchy_breakdown: Optional[List[dict]] = None

class StatsResponse(BaseModel):
    total_documents: int
    hierarchy_levels: dict
    year_distribution: List[dict]
    ef_statistics: dict

class AutocompleteResponse(BaseModel):
    suggestions: List[str]

class NavigationResponse(BaseModel):
    navigation_menu: List[dict]

class EFRangeRequest(BaseModel):
    ef_min: Optional[float] = Field(None, description="Minimum EF value")
    ef_max: Optional[float] = Field(None, description="Maximum EF value")
    limit: int = Field(20, ge=1, le=100, description="Result limit")

def create_fastapi_app():
    """Create FastAPI application with CFP Hierarchical Search"""
    
    # Initialize FastAPI app
    app = FastAPI(
        title="CFP Hierarchical Search API",
        description="Advanced hierarchical search system for Carbon Footprint Product data",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure as needed for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize search system
    cfp_search = CFPHierarchicalSearch()
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize search system on startup"""
        try:
            # Setup index with sample data for demo
            cfp_search.setup_hierarchical_index()
            
            # Load sample data
            df = load_sample_data()
            df_processed = cfp_search.process_dataframe(df)
            cfp_search.index_documents(df_processed)
            
            logger.info("CFP Search API started successfully")
        except Exception as e:
            logger.error(f"Failed to initialize search system: {e}")
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "CFP Hierarchical Search API",
            "version": "1.0.0",
            "endpoints": {
                "search": "/api/search",
                "statistics": "/api/stats", 
                "navigation": "/api/menu",
                "autocomplete": "/api/autocomplete",
                "ef_range": "/api/ef-range"
            },
            "documentation": "/docs"
        }
    
    @app.get("/api/search", response_model=SearchResponse, tags=["Search"])
    async def search(
        q: Optional[str] = Query(None, description="Search query"),
        level: Optional[int] = Query(None, ge=1, le=3, description="Hierarchy level (1-3)"),
        parent_path: Optional[str] = Query(None, description="Parent path for drill-down"),
        year: Optional[str] = Query(None, description="Year filter")
    ):
        """
        Hierarchical search endpoint
        
        - **q**: Search query (e.g., "น้ำส้มสายชู", "carton")
        - **level**: Hierarchy level (1=Industry, 2=Product Type, 3=Company)
        - **parent_path**: Path for drill-down (e.g., "กระดาษและบรรจุภัณฑ์")
        - **year**: Year filter (e.g., "2024", "2025")
        """
        try:
            results = cfp_search.hierarchical_search(
                query=q,
                level=level,
                parent_path=parent_path,
                year_filter=year
            )
            
            if "error" in results:
                raise HTTPException(status_code=400, detail=results["error"])
            
            return SearchResponse(**results)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/search", response_model=SearchResponse, tags=["Search"])
    async def search_post(request: SearchRequest):
        """
        Hierarchical search endpoint (POST method)
        
        Accepts search parameters in request body
        """
        try:
            results = cfp_search.hierarchical_search(
                query=request.query,
                level=request.level,
                parent_path=request.parent_path,
                year_filter=request.year_filter
            )
            
            if "error" in results:
                raise HTTPException(status_code=400, detail=results["error"])
            
            return SearchResponse(**results)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/stats", response_model=StatsResponse, tags=["Statistics"])
    async def get_statistics():
        """
        Get hierarchy statistics
        
        Returns overall statistics about the hierarchy structure,
        document counts, and EF value distributions
        """
        try:
            stats = cfp_search.get_hierarchy_statistics()
            
            if "error" in stats:
                raise HTTPException(status_code=400, detail=stats["error"])
            
            return StatsResponse(**stats)
            
        except Exception as e:
            logger.error(f"Statistics failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/menu", response_model=NavigationResponse, tags=["Navigation"])
    async def get_navigation_menu():
        """
        Get navigation menu structure
        
        Returns the complete hierarchy tree for navigation purposes
        """
        try:
            menu = cfp_search.get_navigation_menu()
            
            if "error" in menu:
                raise HTTPException(status_code=400, detail=menu["error"])
            
            return NavigationResponse(**menu)
            
        except Exception as e:
            logger.error(f"Navigation menu failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/autocomplete", response_model=AutocompleteResponse, tags=["Search"])
    async def autocomplete(
        q: str = Query(..., min_length=1, description="Partial search query"),
        limit: int = Query(10, ge=1, le=50, description="Number of suggestions")
    ):
        """
        Get autocomplete suggestions
        
        - **q**: Partial query for suggestions
        - **limit**: Maximum number of suggestions to return
        """
        try:
            suggestions = cfp_search.autocomplete_search(q, limit)
            return AutocompleteResponse(suggestions=suggestions)
            
        except Exception as e:
            logger.error(f"Autocomplete failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/ef-range", response_model=dict, tags=["Search"])
    async def search_by_ef_range(request: EFRangeRequest):
        """
        Search by EF value range
        
        - **ef_min**: Minimum EF value
        - **ef_max**: Maximum EF value  
        - **limit**: Maximum number of results
        """
        try:
            results = cfp_search.search_by_ef_range(
                ef_min=request.ef_min,
                ef_max=request.ef_max,
                limit=request.limit
            )
            
            if "error" in results:
                raise HTTPException(status_code=400, detail=results["error"])
            
            return results
            
        except Exception as e:
            logger.error(f"EF range search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/ef-range", response_model=dict, tags=["Search"])
    async def search_by_ef_range_get(
        ef_min: Optional[float] = Query(None, description="Minimum EF value"),
        ef_max: Optional[float] = Query(None, description="Maximum EF value"),
        limit: int = Query(20, ge=1, le=100, description="Result limit")
    ):
        """
        Search by EF value range (GET method)
        
        - **ef_min**: Minimum EF value
        - **ef_max**: Maximum EF value
        - **limit**: Maximum number of results
        """
        try:
            results = cfp_search.search_by_ef_range(
                ef_min=ef_min,
                ef_max=ef_max,
                limit=limit
            )
            
            if "error" in results:
                raise HTTPException(status_code=400, detail=results["error"])
            
            return results
            
        except Exception as e:
            logger.error(f"EF range search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        try:
            # Test Elasticsearch connection
            if cfp_search.es.ping():
                return {
                    "status": "healthy",
                    "elasticsearch": "connected",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy", 
                    "elasticsearch": "disconnected",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @app.post("/api/data/upload", tags=["Data Management"])
    async def upload_data(data: List[dict]):
        """
        Upload new CFP data
        
        Accepts array of CFP records and indexes them
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Process and index
            df_processed = cfp_search.process_dataframe(df)
            cfp_search.index_documents(df_processed)
            
            return {
                "message": f"Successfully uploaded {len(data)} records",
                "count": len(data)
            }
            
        except Exception as e:
            logger.error(f"Data upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

# CLI Interface for FastAPI
def run_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run FastAPI server"""
    
    print(f"""
    🚀 Starting CFP Hierarchical Search API
    
    📍 Server: http://{host}:{port}
    📚 Documentation: http://{host}:{port}/docs
    📖 ReDoc: http://{host}:{port}/redoc
    
    🔍 Example API calls:
    • GET  /api/search?q=น้ำส้มสายชู
    • GET  /api/search?level=1
    • GET  /api/search?parent_path=กระดาษและบรรจุภัณฑ์
    • GET  /api/stats
    • GET  /api/menu
    • GET  /api/autocomplete?q=dig
    """)
    
    app = create_fastapi_app()
    uvicorn.run(app, host=host, port=port, reload=reload)

# Example usage for testing API
def test_api_endpoints():
    """Test API endpoints programmatically"""
    
    import requests
    import time
    
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("Testing API endpoints...")
    time.sleep(2)
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/api/health")
        print(f"Health Check: {response.status_code}")
        print(response.json())
        
        # Test level 1 search
        response = requests.get(f"{base_url}/api/search?level=1")
        print(f"Level 1 Search: {response.status_code}")
        
        # Test query search
        response = requests.get(f"{base_url}/api/search?q=น้ำส้มสายชู")
        print(f"Query Search: {response.status_code}")
        
        # Test statistics
        response = requests.get(f"{base_url}/api/stats")
        print(f"Statistics: {response.status_code}")
        
        # Test navigation menu
        response = requests.get(f"{base_url}/api/menu")
        print(f"Navigation Menu: {response.status_code}")
        
        print("All API tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("API server not running. Start with: python script.py --api")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        # Start FastAPI server
        run_api_server(reload=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-api":
        # Test API endpoints
        test_api_endpoints()
    else:
        # Run example usage
        example_usage()
    
    def _format_drill_down_results(self, response: Dict, parent_path: str, next_level: int) -> Dict:
        """Format drill-down results"""
        
        results = {
            "type": "drill_down",
            "parent_path": parent_path,
            "total": response["hits"]["total"]["value"],
            "items": [],
            "next_level_categories": [],
            "year_filters": []
        }
        
        # Format items
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            item = {
                "name": source.get("name", ""),
                "ef_value": source.get("ef_value"),
                "unit": source.get("unit", ""),
                "company": source.get("company", ""),
                "year": source.get("time_filter", {}).get("year", ""),
                "full_path": source.get("hierarchy", {}).get("full_path", ""),
                "score": hit["_score"]
            }
            results["items"].append(item)
        
        # Format year filters
        if "year_filter" in response.get("aggregations", {}):
            for bucket in response["aggregations"]["year_filter"]["buckets"]:
                year_filter = {
                    "year": bucket["key"],
                    "count": bucket["doc_count"]
                }
                results["year_filters"].append(year_filter)
        
        # Format next level categories
        if "next_level" in response.get("aggregations", {}):
            for bucket in response["aggregations"]["next_level"]["buckets"]:
                category = {
                    "name": bucket["key"],
                    "count": bucket["doc_count"],
                    "avg_ef": bucket.get("avg_ef", {}).get("value"),
                    "path": f"{parent_path}/{bucket['key']}"
                }
                results["next_level_categories"].append(category)
        
        return results
    
    def _format_cross_level_results(self, response: Dict, query: str) -> Dict:
        """Format cross-level search results"""
        
        results = {
            "type": "cross_level_search",
            "query": query,
            "total": response["hits"]["total"]["value"],
            "items": [],
            "hierarchy_breakdown": [],
            "year_breakdown": [],
            "ef_statistics": {}
        }
        
        # Format items
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            item = {
                "name": source.get("name", ""),
                "ef_value": source.get("ef_value"),
                "unit": source.get("unit", ""),
                "year": source.get("time_filter", {}).get("year", ""),
                "full_path": source.get("hierarchy", {}).get("full_path", ""),
                "score": hit["_score"],
                "highlight": hit.get("highlight", {})
            }
            results["items"].append(item)
        
        # Format hierarchy breakdown
        for l1_bucket in response["aggregations"]["by_level1"]["buckets"]:
            l1_item = {
                "level1": l1_bucket["key"],
                "count": l1_bucket["doc_count"],
                "level2_breakdown": []
            }
            
            for l2_bucket in l1_bucket["by_level2"]["buckets"]:
                l2_item = {
                    "level2": l2_bucket["key"],
                    "count": l2_bucket["doc_count"],
                    "avg_ef": l2_bucket.get("avg_ef", {}).get("value")
                }
                l1_item["level2_breakdown"].append(l2_item)
            
            results["hierarchy_breakdown"].append(l1_item)
        
        # Format year breakdown
        for year_bucket in response["aggregations"]["by_year"]["buckets"]:
            results["year_breakdown"].append({
                "year": year_bucket["key"],
                "count": year_bucket["doc_count"]
            })
        
        # Format EF statistics
        ef_stats = response["aggregations"].get("ef_stats", {})
        results["ef_statistics"] = {
            "average": ef_stats.get("avg"),
            "min": ef_stats.get("min"),
            "max": ef_stats.get("max"),
            "count": ef_stats.get("count", 0)
        }
        
        return results