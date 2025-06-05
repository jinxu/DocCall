import pandas as pd

def get_sheet_data(sheet_url):
    """
    Read data from a Google Sheet using just the URL.
    
    Args:
        sheet_url (str): The URL of the Google Sheet
    
    Returns:
        dict: Dictionary containing all sheet data with first column as key
    """
    try:
        # Convert Google Sheet URL to CSV export URL
        if 'docs.google.com/spreadsheets/d/' in sheet_url:
            # Extract sheet ID from URL
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            # Create CSV export URL
            csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
            
            # Read CSV directly into pandas DataFrame
            df = pd.read_csv(csv_url)
            
            # Convert DataFrame to dictionary using first column as key
            data = {}
            for idx, row in df.iterrows():
                # Use first column value as key, append index to make it unique
                key = f"{row.iloc[0]}_{idx}"
                # Store all row data
                data[key] = row.to_dict()
            
            return data
        else:
            print("Invalid Google Sheet URL")
            return {}
            
    except Exception as error:
        print(f"An error occurred: {error}")
        return {} 