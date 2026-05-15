import pathlib

def create_local_structure():
    # Get the directory where this script is located
    base_dir = pathlib.Path(__file__).parent.resolve()

    folders = [
        "_Automotive_",
        "_Employment_",
        "_General Sales_",
        "Donations",
        "Expense - Accessories",
        "Expense - Amazon",
        "Expense - Apartments",
        "Expense - Apparel",
        "Expense - Christmas",
        "Expense - Collectible",
        "Expense - Excursions",
        "Expense - Furniture",
        "Expense - Home",
        "Expense - Leisure",
        "Expense - Meals",
        "Expense - Movies",
        "Expense - Office",
        "Expense - Personal Care",
        "Expense - Relocation",
        "Expense - Technology",
        "Expense - Travel",
        "Expense - Vacation",
        "Financial",
        "Insurance",
        "Medical",
        "Taxation Without Representation",
        "Utility - Electric",
        "Utility - Internet",
        "Utility - Phone",
        "Utility - Streaming",
        "Utility - Transportation"
    ]

    print(f"Creating folder structure at: {base_dir}")

    for folder in folders:
        target_folder = base_dir / folder
        try:
            # exist_ok=True allows the script to run without erroring if folders exist
            target_folder.mkdir(parents=True, exist_ok=True)
            print(f"  [+] Synced: {folder}")
        except Exception as e:
            print(f"  [!] Error creating {folder}: {e}")

if __name__ == "__main__":
    create_local_structure()