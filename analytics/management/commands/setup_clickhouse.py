"""
Django management command to set up ClickHouse database.

Usage:
    python manage.py setup_clickhouse
    python manage.py setup_clickhouse --drop  # Drop existing tables first
    python manage.py setup_clickhouse --skip-dates  # Skip date dimension population
"""

from django.core.management.base import BaseCommand, CommandError
from analytics.database import ch_manager
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Set up ClickHouse database with tables and initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--drop',
            action='store_true',
            help='Drop existing tables before creating new ones',
        )
        parser.add_argument(
            '--skip-dates',
            action='store_true',
            help='Skip populating date dimension',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up ClickHouse database...'))

        # Test connection
        if not ch_manager.test_connection():
            raise CommandError('Failed to connect to ClickHouse. Please check your settings.')

        self.stdout.write(self.style.SUCCESS('[OK] Connected to ClickHouse'))

        # Drop tables if requested
        if options['drop']:
            self.drop_tables()

        # Create tables
        self.create_tables()

        # Populate initial data
        self.populate_initial_data()

        # Populate date dimension
        if not options['skip_dates']:
            self.populate_date_dimension()

        self.stdout.write(self.style.SUCCESS('\n[OK] Database setup completed successfully!'))

    def drop_tables(self):
        """Drop all existing tables."""
        self.stdout.write('Dropping existing tables...')

        tables = ['fact_orders', 'dim_products', 'dim_customers', 'dim_dates',
                  'dim_payments', 'dim_promotions', 'dim_locations']

        for table in tables:
            try:
                ch_manager.drop_table(table, if_exists=True)
                self.stdout.write(f'  [OK] Dropped {table}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  [WARN] Failed to drop {table}: {str(e)}'))

    def create_tables(self):
        """Create all database tables."""
        self.stdout.write('\nCreating tables...')

        # Read SQL file
        sql_file = Path(__file__).parent.parent.parent / 'sql' / 'create_tables.sql'

        if not sql_file.exists():
            raise CommandError(f'SQL file not found: {sql_file}')

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split into individual statements
        statements = []
        current_statement = []

        for line in sql_content.split('\n'):
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            current_statement.append(line)

            # Execute when we hit a semicolon
            if line.endswith(';'):
                statement = ' '.join(current_statement)
                if statement and not statement.startswith('USE '):
                    statements.append(statement)
                current_statement = []

        # Execute each statement
        for statement in statements:
            try:
                # Skip comments
                if 'CREATE VIEW' in statement or 'CREATE DATABASE' in statement:
                    continue  # Views will be created later

                ch_manager.execute(statement)

                # Extract table name for logging
                if 'CREATE TABLE' in statement:
                    table_name = statement.split('CREATE TABLE IF NOT EXISTS')[1].split('(')[0].strip()
                    self.stdout.write(f'  [OK] Created table: {table_name}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] Error executing statement: {str(e)}'))

    def populate_initial_data(self):
        """Populate initial/seed data."""
        self.stdout.write('\nPopulating initial data...')

        try:
            # Insert default promotion
            ch_manager.execute("""
                INSERT INTO dim_promotions (promotion_id, promo_code, promo_name, discount_type, discount_value, start_date, end_date)
                VALUES (0, 'NONE', 'No Promotion', 'none', 0.00, '2020-01-01', '2099-12-31')
            """)
            self.stdout.write('  [OK] Inserted default promotion')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  [WARN] Promotion insert failed (may already exist): {str(e)}'))

        try:
            # Insert payment methods
            payment_methods = [
                (1, 'Credit Card', 'Stripe', 1),
                (2, 'Debit Card', 'Stripe', 1),
                (3, 'PayPal', 'PayPal', 1),
                (4, 'Bank Transfer', 'SCB', 1),
                (5, 'Cash on Delivery', 'N/A', 0),
                (6, 'PromptPay', 'ThaiQR', 1),
                (7, 'TrueMoney Wallet', 'TrueMoney', 1),
            ]

            for pm in payment_methods:
                ch_manager.execute("""
                    INSERT INTO dim_payments (payment_id, payment_method, payment_gateway, is_online)
                    VALUES (%s, %s, %s, %s)
                """, pm)

            self.stdout.write('  [OK] Inserted payment methods')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  [WARN] Payment methods insert failed (may already exist): {str(e)}'))

        try:
            # Insert locations
            locations = [
                (1, 'Bangkok', 'Bangkok', 'Pathum Wan', '10330', 'Central'),
                (2, 'Bangkok', 'Bangkok', 'Bang Rak', '10500', 'Central'),
                (3, 'Chiang Mai', 'Chiang Mai', 'Mueang', '50000', 'North'),
                (4, 'Phuket', 'Phuket', 'Mueang', '83000', 'South'),
                (5, 'Khon Kaen', 'Khon Kaen', 'Mueang', '40000', 'Northeast'),
                (6, 'Chonburi', 'Pattaya', 'Bang Lamung', '20150', 'Central'),
                (7, 'Nonthaburi', 'Nonthaburi', 'Mueang', '11000', 'Central'),
            ]

            for loc in locations:
                ch_manager.execute("""
                    INSERT INTO dim_locations (location_id, province, city, district, postal_code, region)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, loc)

            self.stdout.write('  [OK] Inserted locations')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  [WARN] Locations insert failed (may already exist): {str(e)}'))

    def populate_date_dimension(self):
        """Populate date dimension table."""
        self.stdout.write('\nPopulating date dimension (2020-2030)...')

        try:
            from datetime import datetime, timedelta

            # Thai month names
            thai_months = {
                1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน',
                5: 'พฤษภาคม', 6: 'มิถุนายน', 7: 'กรกฎาคม', 8: 'สิงหาคม',
                9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม'
            }

            # English month names
            eng_months = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }

            # Thai holidays
            thai_holidays = {
                (1, 1), (4, 6), (4, 13), (4, 14), (4, 15), (5, 1), (5, 4),
                (7, 28), (8, 12), (10, 13), (10, 23), (12, 5), (12, 10), (12, 31)
            }

            start_date = datetime(2020, 1, 1)
            end_date = datetime(2030, 12, 31)
            current_date = start_date

            dates_data = []

            while current_date <= end_date:
                year = current_date.year
                month = current_date.month
                day = current_date.day
                day_of_week = current_date.isoweekday()
                quarter = (month - 1) // 3 + 1
                is_weekend = 1 if day_of_week in [6, 7] else 0
                is_holiday = 1 if (month, day) in thai_holidays else 0
                date_id = int(current_date.strftime('%Y%m%d'))
                month_name = eng_months[month]

                dates_data.append((
                    date_id,
                    current_date.strftime('%Y-%m-%d'),
                    year,
                    month,
                    day,
                    quarter,
                    day_of_week,
                    month_name,
                    is_weekend,
                    is_holiday
                ))

                current_date += timedelta(days=1)

            # Bulk insert
            columns = ['date_id', 'date', 'year', 'month', 'day', 'quarter',
                       'day_of_week', 'month_name', 'is_weekend', 'is_holiday']

            ch_manager.bulk_insert('dim_dates', columns, dates_data)

            self.stdout.write(f'  [OK] Inserted {len(dates_data)} date records')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Failed to populate date dimension: {str(e)}'))
            raise
