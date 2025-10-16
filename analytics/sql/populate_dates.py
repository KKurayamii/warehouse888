"""
Helper script to generate date dimension data for the sales analytics database.
This creates a comprehensive date dimension with various time attributes.
"""

from datetime import datetime, timedelta
import csv

def generate_date_dimension(start_year=2020, end_year=2030):
    """
    Generate date dimension records from start_year to end_year.

    Args:
        start_year: Starting year (default: 2020)
        end_year: Ending year (default: 2030)

    Returns:
        List of dictionaries containing date dimension records
    """
    dates = []

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

    # Thai public holidays (simplified - add more as needed)
    thai_holidays = [
        (1, 1),   # New Year's Day
        (4, 6),   # Chakri Memorial Day
        (4, 13),  # Songkran
        (4, 14),  # Songkran
        (4, 15),  # Songkran
        (5, 1),   # Labor Day
        (5, 4),   # Coronation Day
        (7, 28),  # King's Birthday
        (8, 12),  # Queen's Birthday
        (10, 13), # King Bhumibol Memorial Day
        (10, 23), # Chulalongkorn Day
        (12, 5),  # Father's Day
        (12, 10), # Constitution Day
        (12, 31), # New Year's Eve
    ]

    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    current_date = start_date

    while current_date <= end_date:
        # Calculate date attributes
        year = current_date.year
        month = current_date.month
        day = current_date.day
        day_of_week = current_date.isoweekday()  # 1=Monday, 7=Sunday
        quarter = (month - 1) // 3 + 1

        # Check if weekend (Saturday=6, Sunday=7)
        is_weekend = 1 if day_of_week in [6, 7] else 0

        # Check if holiday
        is_holiday = 1 if (month, day) in thai_holidays else 0

        # Create date_id in YYYYMMDD format
        date_id = int(current_date.strftime('%Y%m%d'))

        # Create month name (use English by default, can be changed to Thai)
        month_name = eng_months[month]
        # month_name = thai_months[month]  # Uncomment for Thai month names

        date_record = {
            'date_id': date_id,
            'date': current_date.strftime('%Y-%m-%d'),
            'year': year,
            'month': month,
            'day': day,
            'quarter': quarter,
            'day_of_week': day_of_week,
            'month_name': month_name,
            'is_weekend': is_weekend,
            'is_holiday': is_holiday
        }

        dates.append(date_record)
        current_date += timedelta(days=1)

    return dates


def export_to_csv(dates, filename='dim_dates.csv'):
    """
    Export date dimension data to CSV file.

    Args:
        dates: List of date dimension records
        filename: Output CSV filename
    """
    if not dates:
        return

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = dates[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for date in dates:
            writer.writerow(date)

    print(f"Exported {len(dates)} date records to {filename}")


def generate_insert_sql(dates, filename='insert_dates.sql'):
    """
    Generate SQL INSERT statements for ClickHouse.

    Args:
        dates: List of date dimension records
        filename: Output SQL filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("-- Insert date dimension data\n")
        f.write("INSERT INTO dim_dates (date_id, date, year, month, day, quarter, day_of_week, month_name, is_weekend, is_holiday) VALUES\n")

        for i, date in enumerate(dates):
            values = (
                f"({date['date_id']}, '{date['date']}', {date['year']}, "
                f"{date['month']}, {date['day']}, {date['quarter']}, "
                f"{date['day_of_week']}, '{date['month_name']}', "
                f"{date['is_weekend']}, {date['is_holiday']})"
            )

            if i < len(dates) - 1:
                f.write(f"    {values},\n")
            else:
                f.write(f"    {values};\n")

    print(f"Generated SQL INSERT statements in {filename}")


if __name__ == '__main__':
    # Generate date dimension for 10 years (2020-2030)
    print("Generating date dimension data...")
    dates = generate_date_dimension(2020, 2030)

    print(f"Generated {len(dates)} date records")
    print(f"Date range: {dates[0]['date']} to {dates[-1]['date']}")

    # Export to CSV
    export_to_csv(dates)

    # Generate SQL INSERT statements
    generate_insert_sql(dates)

    print("\nDone! You can now:")
    print("1. Use dim_dates.csv to bulk load data into ClickHouse")
    print("2. Execute insert_dates.sql in ClickHouse client")
