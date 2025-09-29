
├── schema.sql            # Main schema definition (tables, indexes, etc.)
├── data.sql              # Initial data (seed data)
├── functions/            # SQL files for stored procedures & functions
│   └── my_function.sql
├── triggers/             # SQL files for triggers
│   └── my_trigger.sql
├── migrations/           # Incremental migration scripts (if using migrations)
│   ├── 001_init.sql
│   └── 002_add_table.sql
├── views/                # SQL files for views
│   └── my_view.sql
├── README.md             # Documentation for the database structure
└── .env                  # Environment variables (e.g., connection strings)
