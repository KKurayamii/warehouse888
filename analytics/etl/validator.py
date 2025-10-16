"""
Data Validation Utility for ETL Pipeline

This module provides validation functions for uploaded CSV files.
"""

import pandas as pd
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validator for CSV data files.
    """

    # Required columns and their expected types (English)
    REQUIRED_COLUMNS = {
        'order_number': str,
        'order_date': str,  # Will be converted to datetime
        'product_name': str,
        'quantity': (int, float),
        'unit_price': (int, float),
        'total_amount': (int, float),
    }

    # Thai column mappings (Shopee format)
    THAI_COLUMN_MAPPING = {
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

    # Optional columns
    OPTIONAL_COLUMNS = {
        'sku': str,
        'category': str,
        'subcategory': str,
        'customer_name': str,
        'customer_email': str,
        'customer_phone': str,
        'province': str,
        'city': str,
        'district': str,
        'postal_code': str,
        'region': str,
        'payment_method': str,
        'promotion_code': str,
        'promotion_name': str,
        'discount_type': str,
        'discount_value': (int, float),
        'discount_amount': (int, float),
        'tax_amount': (int, float),
        'shipping_cost': (int, float),
    }

    @classmethod
    def validate_file(cls, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            # Detect file type and read accordingly
            if file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, engine='openpyxl' if file_path.endswith('.xlsx') else None)
                logger.info(f"Read Excel file with {len(df)} rows")
            else:
                # Try to read the file (utf-8-sig handles BOM characters)
                df = pd.read_csv(file_path, encoding='utf-8-sig')

            # Debug: log columns found
            logger.info(f"CSV columns found: {list(df.columns)}")
            logger.info(f"CSV shape: {df.shape}")

            # Check for empty file
            if len(df) == 0:
                errors.append("File is empty")
                return False, errors

            # Normalize Thai columns to English
            df = cls.normalize_columns(df)
            logger.info(f"Normalized columns: {list(df.columns)}")

            # Check required columns (excluding quantity as it can be defaulted)
            required_cols = {k: v for k, v in cls.REQUIRED_COLUMNS.items() if k != 'quantity'}
            missing_cols = cls.check_required_columns(df, required_cols)
            if missing_cols:
                logger.error(f"Missing columns: {missing_cols}. Found: {list(df.columns)}")
                errors.append(f"Missing required columns: {', '.join(missing_cols)}")

            # Check data types
            type_errors = cls.check_data_types(df)
            if type_errors:
                errors.extend(type_errors)

            # Check for duplicates
            duplicate_count = cls.check_duplicates(df)
            if duplicate_count > 0:
                errors.append(f"Warning: Found {duplicate_count} duplicate order numbers")

            # Check for negative values
            negative_errors = cls.check_negative_values(df)
            if negative_errors:
                errors.extend(negative_errors)

            # Check date format
            date_errors = cls.check_date_format(df)
            if date_errors:
                errors.extend(date_errors)

            # If only warnings (duplicates), still return True
            is_valid = len([e for e in errors if not e.startswith('Warning')]) == 0

            return is_valid, errors

        except Exception as e:
            errors.append(f"File reading error: {str(e)}")
            return False, errors

    @classmethod
    def normalize_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names from Thai to English.

        Args:
            df: DataFrame with original columns

        Returns:
            DataFrame with normalized column names
        """
        df = df.copy()

        # Create reverse mapping
        rename_map = {}
        for thai_col, english_col in cls.THAI_COLUMN_MAPPING.items():
            if thai_col in df.columns:
                rename_map[thai_col] = english_col

        if rename_map:
            df = df.rename(columns=rename_map)
            logger.info(f"Renamed {len(rename_map)} Thai columns to English")

        return df

    @classmethod
    def check_required_columns(cls, df: pd.DataFrame, required_cols: Dict = None) -> List[str]:
        """Check if all required columns are present."""
        if required_cols is None:
            required_cols = cls.REQUIRED_COLUMNS

        missing = []
        for col in required_cols.keys():
            if col not in df.columns:
                missing.append(col)
        return missing

    @classmethod
    def check_data_types(cls, df: pd.DataFrame) -> List[str]:
        """Check if columns have valid data types."""
        errors = []

        for col, expected_type in cls.REQUIRED_COLUMNS.items():
            if col not in df.columns:
                continue

            # Skip date columns (will be validated separately)
            if 'date' in col.lower():
                continue

            # Check if column can be converted to expected type
            try:
                if expected_type in [int, float, (int, float)]:
                    pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                errors.append(f"Column '{col}' has invalid data type: {str(e)}")

        return errors

    @classmethod
    def check_duplicates(cls, df: pd.DataFrame) -> int:
        """Check for duplicate order numbers."""
        if 'order_number' in df.columns:
            return df.duplicated(subset=['order_number']).sum()
        return 0

    @classmethod
    def check_negative_values(cls, df: pd.DataFrame) -> List[str]:
        """Check for negative values in numeric columns."""
        errors = []

        numeric_cols = ['quantity', 'unit_price', 'total_amount']

        for col in numeric_cols:
            if col in df.columns:
                negative_count = (pd.to_numeric(df[col], errors='coerce') < 0).sum()
                if negative_count > 0:
                    errors.append(f"Warning: Found {negative_count} negative values in '{col}'")

        return errors

    @classmethod
    def check_date_format(cls, df: pd.DataFrame) -> List[str]:
        """Check if date columns have valid format."""
        errors = []

        if 'order_date' in df.columns:
            try:
                pd.to_datetime(df['order_date'], errors='coerce')
                invalid_dates = df['order_date'].isna().sum()
                if invalid_dates > 0:
                    errors.append(f"Warning: Found {invalid_dates} invalid dates in 'order_date'")
            except Exception as e:
                errors.append(f"Date format error in 'order_date': {str(e)}")

        return errors

    @classmethod
    def get_file_summary(cls, file_path: str) -> Dict:
        """
        Get summary statistics for a CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            Dictionary with file statistics
        """
        try:
            df = pd.read_csv(file_path)

            summary = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'duplicates': cls.check_duplicates(df),
            }

            # Add numeric column statistics
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary['numeric_summary'] = df[numeric_cols].describe().to_dict()

            return summary

        except Exception as e:
            logger.error(f"Failed to generate file summary: {str(e)}")
            return {'error': str(e)}

    @classmethod
    def create_sample_csv(cls, output_path: str = 'sample_orders.csv'):
        """
        Create a sample CSV file with correct format.

        Args:
            output_path: Path where sample CSV will be saved
        """
        sample_data = {
            'order_number': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
            'order_date': ['2024-01-15', '2024-01-15', '2024-01-16', '2024-01-16', '2024-01-17'],
            'product_name': ['Laptop Computer', 'Wireless Mouse', 'USB Cable', 'Keyboard', 'Monitor'],
            'sku': ['LAP001', 'MOU001', 'CAB001', 'KEY001', 'MON001'],
            'category': ['Electronics', 'Electronics', 'Accessories', 'Electronics', 'Electronics'],
            'subcategory': ['Computers', 'Peripherals', 'Cables', 'Peripherals', 'Displays'],
            'quantity': [1, 2, 3, 1, 1],
            'unit_price': [25000.00, 450.00, 150.00, 1200.00, 8500.00],
            'discount_amount': [2000.00, 0.00, 15.00, 100.00, 500.00],
            'tax_amount': [1610.00, 63.00, 94.50, 77.00, 560.00],
            'shipping_cost': [0.00, 50.00, 50.00, 50.00, 200.00],
            'total_amount': [24610.00, 963.00, 469.50, 1227.00, 8760.00],
            'customer_name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams', 'Charlie Brown'],
            'customer_email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],
            'customer_phone': ['0812345678', '0823456789', '0834567890', '0845678901', '0856789012'],
            'province': ['Bangkok', 'Bangkok', 'Chiang Mai', 'Phuket', 'Bangkok'],
            'city': ['Bangkok', 'Bangkok', 'Chiang Mai', 'Phuket', 'Bangkok'],
            'district': ['Pathum Wan', 'Bang Rak', 'Mueang', 'Mueang', 'Pathum Wan'],
            'postal_code': ['10330', '10500', '50000', '83000', '10330'],
            'region': ['Central', 'Central', 'North', 'South', 'Central'],
            'payment_method': ['Credit Card', 'PromptPay', 'Cash on Delivery', 'Bank Transfer', 'Credit Card'],
            'promotion_code': ['WELCOME10', 'NONE', 'FREESHIP', 'SAVE100', 'NONE'],
        }

        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        logger.info(f"Sample CSV created at: {output_path}")
        print(f"Sample CSV file created: {output_path}")
        print(f"Total rows: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")


if __name__ == '__main__':
    # Create sample CSV
    DataValidator.create_sample_csv()
