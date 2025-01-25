# Tax Database Application

This application is designed to manage and calculate taxes for real estate and land parcels. It provides a user-friendly interface for adding, updating, and deleting records related to users, real estate, and land parcels. The application also supports exporting data to Excel and restoring database backups.

## Features

- **User Management**: Add, update, and delete user records.
- **Real Estate Management**: Manage real estate records, including tax calculations based on area and type.
- **Land Parcel Management**: Manage land parcel records, including tax calculations based on area and type.
- **Tax Calculation**: Automatically calculate taxes based on predefined rates and user inputs.
- **Data Export**: Export data to Excel files.
- **Database Backup and Restore**: Create and restore database backups.
- **Yearly Data Management**: Manage data for different years.

## Project Structure

```
app/
    base_repository.py
    database.py
    land_parcel_repository.py
    land_parcel_type_repository.py
    real_estate_repository.py
    real_estate_type_repository.py
    salary_repository.py
    user_repository.py
db/
    db.sql
main.py
main.spec
ui/
    add_person_ui.py
    change_estate_type_ui.py
    change_land_type_ui.py
    filterable_table_view.py
    land_parcel_ui.py
    main_window_ui.py
    min_salary_ui.py
    nmv_dialog.py
    real_estate_ui.py
    styles.py
    utils.py
    year_box.py
```

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Kolyanuss/IS_podatky.git
    cd IS_podatky
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```

2. The main window will open, allowing you to manage users, real estate, and land parcels.

## Database

The application uses SQLite for data storage. The database schema is defined in the `db/db.sql` file.

## Backup and Restore

- **Backup**: The application automatically creates a backup of the database when it is closed.
- **Restore**: You can restore a backup from the "Actions" menu in the application.

## Export to Excel

You can export the data to an Excel file from the "Actions" menu in the application.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any questions or suggestions, please contact Mykola Maksymovych.
