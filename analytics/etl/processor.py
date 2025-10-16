"""
ETL Processor for Sales Data

This module handles the extraction, transformation, and loading of sales data
from CSV files into the ClickHouse data warehouse.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
from pathlib import Path
import hashlib

from analytics.database import ch_manager

logger = logging.getLogger(__name__)


class ETLProcessor:
    """
    Main ETL processor for sales data.
    """

    def __init__(self):
        self.stats = {
            'rows_processed': 0,
            'rows_inserted': 0,
            'rows_failed': 0,
            'errors': []
        }
        self.dimension_caches = {}

    def process_csv(self, file_path: str) -> Dict:
        """
        Process a CSV file through the complete ETL pipeline.

        Args:
            file_path: Path to the CSV file

        Returns:
            Dictionary with processing statistics

        Raises:
            Exception: If processing fails
        """
        logger.info(f"Starting ETL process for file: {file_path}")

        try:
            # Extract
            df = self.extract(file_path)
            logger.info(f"Extracted {len(df)} rows from CSV")

            # Transform
            transformed_data = self.transform(df)
            logger.info("Data transformation completed")

            # Load
            self.load(transformed_data)
            logger.info("Data loading completed")

            return self.stats

        except Exception as e:
            logger.error(f"ETL process failed: {str(e)}")
            self.stats['errors'].append(str(e))
            raise

    def extract(self, file_path: str) -> pd.DataFrame:
        """
        Extract data from CSV or Excel file.

        Args:
            file_path: Path to CSV or Excel file

        Returns:
            DataFrame with raw data

        Raises:
            Exception: If extraction fails
        """
        try:
            # Detect file type
            file_ext = Path(file_path).suffix.lower()

            if file_ext in ['.xlsx', '.xls']:
                # Read Excel file
                logger.info(f"Reading Excel file: {file_path}")
                df = pd.read_excel(file_path, engine='openpyxl' if file_ext == '.xlsx' else None)
                logger.info(f"Successfully read Excel file with {len(df)} rows")
            else:
                # Read CSV with multiple encoding attempts
                encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        logger.info(f"Successfully read CSV with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue

                if df is None:
                    raise ValueError("Failed to read CSV with any supported encoding")

            # Normalize Thai columns to English
            df = self.normalize_thai_columns(df)
            logger.info(f"Columns after normalization: {list(df.columns)}")

            # Add quantity column if missing (default to 1)
            if 'quantity' not in df.columns:
                df['quantity'] = 1
                logger.info("Added missing 'quantity' column with default value 1")

            # Validate required columns
            self.validate_columns(df)

            self.stats['rows_processed'] = len(df)

            return df

        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise

    def validate_columns(self, df: pd.DataFrame):
        """
        Validate that required columns exist in the DataFrame.

        Args:
            df: DataFrame to validate

        Raises:
            ValueError: If required columns are missing
        """
        # Define required columns (adjust based on your CSV format)
        required_columns = [
            'order_number',
            'order_date',
            'product_name',
            'quantity',
            'unit_price',
            'total_amount'
        ]

        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        logger.info("Column validation passed")

    def transform(self, df: pd.DataFrame) -> Dict[str, List]:
        """
        Transform raw data into dimensional model format.

        Args:
            df: Raw DataFrame

        Returns:
            Dictionary containing transformed dimension and fact data

        Raises:
            Exception: If transformation fails
        """
        try:
            # Clean data
            df = self.clean_data(df)

            # Build dimension tables and get IDs
            product_map = self.build_product_dimension(df)
            customer_map = self.build_customer_dimension(df)
            location_map = self.build_location_dimension(df)
            promotion_map = self.build_promotion_dimension(df)

            # Build fact table
            fact_data = self.build_fact_table(df, product_map, customer_map,
                                             location_map, promotion_map)

            return {
                'products': list(product_map.values()),
                'customers': list(customer_map.values()),
                'locations': list(location_map.values()),
                'promotions': list(promotion_map.values()),
                'facts': fact_data
            }

        except Exception as e:
            logger.error(f"Transformation failed: {str(e)}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the data.

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        df = df.copy()

        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['order_number'], keep='first')
        duplicates_removed = initial_count - len(df)

        if duplicates_removed > 0:
            logger.warning(f"Removed {duplicates_removed} duplicate orders")

        # Handle missing values
        df = df.fillna({
            'promotion_code': 'NONE',
            'discount_amount': 0.0,
            'tax_amount': 0.0,
            'shipping_cost': 0.0
        })

        # Convert dates
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])

        # Ensure numeric columns
        numeric_columns = ['quantity', 'unit_price', 'discount_amount',
                          'tax_amount', 'shipping_cost', 'total_amount']

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Remove negative quantities
        df = df[df['quantity'] > 0]

        return df

    def build_product_dimension(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Build product dimension from raw data.

        Args:
            df: Cleaned DataFrame

        Returns:
            Dictionary mapping product keys to product records
        """
        product_map = {}

        product_columns = ['product_name', 'sku', 'category', 'subcategory', 'unit_price']
        available_columns = [col for col in product_columns if col in df.columns]

        if not available_columns:
            logger.warning("No product columns found in data")
            return product_map

        # Get unique products
        products = df[available_columns].drop_duplicates()

        for idx, row in products.iterrows():
            # Create a unique key for the product
            product_key = f"{row.get('sku', '')}_{row.get('product_name', '')}"

            # Generate product_id using hash
            product_id = self.generate_id(product_key)

            product_map[product_key] = {
                'product_id': product_id,
                'sku': row.get('sku', f'SKU{product_id}'),
                'product_name': row.get('product_name', 'Unknown Product'),
                'category': row.get('category', 'General'),
                'subcategory': row.get('subcategory', 'Other'),
                'unit_price': float(row.get('unit_price', 0)),
                'cost': float(row.get('cost', row.get('unit_price', 0) * 0.6))  # Assume 40% margin
            }

        logger.info(f"Built {len(product_map)} unique products")
        return product_map

    def build_customer_dimension(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Build customer dimension from raw data.

        Args:
            df: Cleaned DataFrame

        Returns:
            Dictionary mapping customer keys to customer records
        """
        customer_map = {}

        customer_columns = ['customer_name', 'customer_email', 'customer_phone']
        available_columns = [col for col in customer_columns if col in df.columns]

        if not available_columns:
            logger.warning("No customer columns found in data")
            return customer_map

        # Get unique customers
        customers = df[available_columns].drop_duplicates()

        for idx, row in customers.iterrows():
            customer_key = row.get('customer_email', f"customer_{idx}")
            customer_id = self.generate_id(customer_key)

            # Get location_id (default to 1 if not found)
            location_id = self.get_location_id(row.get('province', ''), row.get('city', ''))

            customer_map[customer_key] = {
                'customer_id': customer_id,
                'customer_name': row.get('customer_name', 'Unknown Customer'),
                'email': row.get('customer_email', ''),
                'phone': row.get('customer_phone', ''),
                'location_id': location_id,
                'created_at': datetime.now()
            }

        logger.info(f"Built {len(customer_map)} unique customers")
        return customer_map

    def build_location_dimension(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Build location dimension from raw data.

        Args:
            df: Cleaned DataFrame

        Returns:
            Dictionary mapping location keys to location records
        """
        location_map = {}

        location_columns = ['province', 'city', 'district', 'postal_code', 'region']
        available_columns = [col for col in location_columns if col in df.columns]

        if not available_columns:
            logger.warning("No location columns found in data")
            return location_map

        # Get unique locations
        locations = df[available_columns].drop_duplicates()

        for idx, row in locations.iterrows():
            location_key = f"{row.get('province', '')}_{row.get('city', '')}"
            location_id = self.generate_id(location_key, max_id=65535)  # UInt16 max

            location_map[location_key] = {
                'location_id': location_id,
                'province': row.get('province', 'Unknown'),
                'city': row.get('city', 'Unknown'),
                'district': row.get('district', ''),
                'postal_code': row.get('postal_code', ''),
                'region': row.get('region', 'Unknown')
            }

        logger.info(f"Built {len(location_map)} unique locations")
        return location_map

    def build_promotion_dimension(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Build promotion dimension from raw data.

        Args:
            df: Cleaned DataFrame

        Returns:
            Dictionary mapping promotion codes to promotion records
        """
        promotion_map = {}

        # Add default "No Promotion"
        promotion_map['NONE'] = {
            'promotion_id': 0,
            'promo_code': 'NONE',
            'promo_name': 'No Promotion',
            'discount_type': 'none',
            'discount_value': 0.0,
            'start_date': '2020-01-01',
            'end_date': '2099-12-31'
        }

        if 'promotion_code' not in df.columns:
            return promotion_map

        # Get unique promotions
        promo_columns = ['promotion_code', 'promotion_name', 'discount_type', 'discount_value']
        available_columns = [col for col in promo_columns if col in df.columns]

        promotions = df[available_columns].drop_duplicates()

        for idx, row in promotions.iterrows():
            promo_code = row.get('promotion_code', 'NONE')

            if promo_code == 'NONE' or not promo_code:
                continue

            promotion_id = self.generate_id(promo_code, max_id=65535)

            promotion_map[promo_code] = {
                'promotion_id': promotion_id,
                'promo_code': promo_code,
                'promo_name': row.get('promotion_name', promo_code),
                'discount_type': row.get('discount_type', 'percentage'),
                'discount_value': float(row.get('discount_value', 0)),
                'start_date': '2020-01-01',  # Could be extracted from data if available
                'end_date': '2099-12-31'
            }

        logger.info(f"Built {len(promotion_map)} unique promotions")
        return promotion_map

    def build_fact_table(self, df: pd.DataFrame, product_map: Dict, customer_map: Dict,
                        location_map: Dict, promotion_map: Dict) -> List[Dict]:
        """
        Build fact table records.

        Args:
            df: Cleaned DataFrame
            product_map: Product dimension mapping
            customer_map: Customer dimension mapping
            location_map: Location dimension mapping
            promotion_map: Promotion dimension mapping

        Returns:
            List of fact table records
        """
        fact_data = []

        for idx, row in df.iterrows():
            try:
                # Get dimension IDs
                product_key = f"{row.get('sku', '')}_{row.get('product_name', '')}"
                customer_key = row.get('customer_email', f"customer_{idx}")
                location_key = f"{row.get('province', '')}_{row.get('city', '')}"
                promo_code = row.get('promotion_code', 'NONE')

                product_id = product_map.get(product_key, {}).get('product_id', 0)
                customer_id = customer_map.get(customer_key, {}).get('customer_id', 0)
                location_id = location_map.get(location_key, {}).get('location_id', 1)
                promotion_id = promotion_map.get(promo_code, {}).get('promotion_id', 0)
                payment_id = self.get_payment_id(row.get('payment_method', 'Cash on Delivery'))

                # Get or create date_id
                order_date = pd.to_datetime(row.get('order_date', datetime.now()))
                date_id = int(order_date.strftime('%Y%m%d'))

                # Build fact record
                fact_record = {
                    'order_id': self.generate_id(f"{row.get('order_number', idx)}", max_id=2**64-1),
                    'order_number': str(row.get('order_number', f'ORD{idx}')),
                    'date_id': date_id,
                    'product_id': product_id,
                    'customer_id': customer_id,
                    'payment_id': payment_id,
                    'promotion_id': promotion_id if promotion_id > 0 else None,
                    'location_id': location_id,
                    'quantity': int(row.get('quantity', 1)),
                    'unit_price': float(row.get('unit_price', 0)),
                    'discount_amount': float(row.get('discount_amount', 0)),
                    'tax_amount': float(row.get('tax_amount', 0)),
                    'shipping_cost': float(row.get('shipping_cost', 0)),
                    'total_amount': float(row.get('total_amount', 0)),
                    'created_at': order_date
                }

                fact_data.append(fact_record)

            except Exception as e:
                logger.error(f"Error processing row {idx}: {str(e)}")
                self.stats['rows_failed'] += 1
                continue

        logger.info(f"Built {len(fact_data)} fact records")
        return fact_data

    def load(self, transformed_data: Dict):
        """
        Load transformed data into ClickHouse.

        Args:
            transformed_data: Dictionary containing all transformed data

        Raises:
            Exception: If loading fails
        """
        try:
            # Load dimensions first (to ensure referential integrity)
            self.load_dimension('dim_products', transformed_data['products'])
            self.load_dimension('dim_customers', transformed_data['customers'])
            self.load_dimension('dim_locations', transformed_data['locations'])
            self.load_dimension('dim_promotions', transformed_data['promotions'])

            # Load facts
            self.load_facts(transformed_data['facts'])

            self.stats['rows_inserted'] = len(transformed_data['facts'])

        except Exception as e:
            logger.error(f"Loading failed: {str(e)}")
            raise

    def load_dimension(self, table_name: str, data: List[Dict]):
        """
        Load dimension data into ClickHouse with upsert logic.

        Args:
            table_name: Name of the dimension table
            data: List of dimension records
        """
        if not data:
            logger.info(f"No data to load into {table_name}")
            return

        try:
            # For ClickHouse, we'll use INSERT with deduplication
            # based on the primary key (first column)
            count = ch_manager.insert(table_name, data)
            logger.info(f"Loaded {count} records into {table_name}")

        except Exception as e:
            logger.warning(f"Failed to load {table_name}: {str(e)}")
            # Continue even if dimension load fails (may already exist)

    def load_facts(self, fact_data: List[Dict]):
        """
        Load fact data into ClickHouse.

        Args:
            fact_data: List of fact records
        """
        if not fact_data:
            logger.info("No fact data to load")
            return

        try:
            count = ch_manager.insert('fact_orders', fact_data)
            logger.info(f"Loaded {count} fact records")

        except Exception as e:
            logger.error(f"Failed to load fact data: {str(e)}")
            raise

    @staticmethod
    def generate_id(key: str, max_id: int = 2**32 - 1) -> int:
        """
        Generate a consistent numeric ID from a string key using hash.

        Args:
            key: String key to hash
            max_id: Maximum ID value (default: UInt32 max)

        Returns:
            Numeric ID
        """
        hash_object = hashlib.md5(key.encode())
        hash_int = int(hash_object.hexdigest(), 16)
        return hash_int % max_id

    @staticmethod
    def get_payment_id(payment_method: str) -> int:
        """
        Map payment method string to payment_id.

        Args:
            payment_method: Payment method name

        Returns:
            Payment ID
        """
        payment_mapping = {
            'credit card': 1,
            'debit card': 2,
            'paypal': 3,
            'bank transfer': 4,
            'cash on delivery': 5,
            'promptpay': 6,
            'truemoney': 7,
        }

        return payment_mapping.get(payment_method.lower(), 5)  # Default to COD

    @staticmethod
    def get_location_id(province: str, city: str) -> int:
        """
        Get location_id for a province/city combination.

        Args:
            province: Province name
            city: City name

        Returns:
            Location ID (default 1 if not found)
        """
        # Simple mapping - in production, query from dim_locations
        location_key = f"{province}_{city}"
        return ETLProcessor.generate_id(location_key, max_id=65535)

    @staticmethod
    def normalize_thai_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize Thai column names to English.

        Args:
            df: DataFrame with Thai column names

        Returns:
            DataFrame with English column names
        """
        # Thai to English column mapping (Shopee format)
        column_mapping = {
            'หมายเลขคำสั่งซื้อ': 'order_number',
            'วันที่ทำการสั่งซื้อ': 'order_date',
            'ชื่อสินค้า': 'product_name',
            'ราคาสินค้าที่ชำระโดยผู้ซื้อ (THB)': 'unit_price',
            'จำนวนเงินทั้งหมด': 'total_amount',
            'เลขอ้างอิง SKU (SKU ทั้งหมด)': 'sku',
            'ชื่อผู้รับ': 'customer_name',
            'หมายเลขโทรศัพท์': 'customer_phone',
            'จังหวัด': 'province',
            'เขต/อำเภอ': 'city',
            'รหัสไปรษณีย์': 'postal_code',
            'ช่องทางการชำระเงิน': 'payment_method',
            'ค่าจัดส่งที่ชำระโดยผู้ซื้อ': 'shipping_cost',
            'ค่าคอมมิชชั่น': 'commission',
            'Transaction Fee': 'transaction_fee',
        }

        # Rename columns that exist in the DataFrame
        rename_map = {}
        for thai_col, english_col in column_mapping.items():
            if thai_col in df.columns:
                rename_map[thai_col] = english_col

        if rename_map:
            df = df.rename(columns=rename_map)
            logger.info(f"Normalized {len(rename_map)} Thai columns to English")

        return df
