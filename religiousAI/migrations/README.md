# Database Migrations

This directory is for future database migration files. The initial schema is in `db_schema.sql` in the parent directory.

## Initial Schema Setup

The main database schema is in `../db_schema.sql`. To apply it:

1. Go to Supabase Dashboard → SQL Editor
2. Copy and paste the contents of `db_schema.sql`
3. Click Run

See [SUPABASE_SETUP.md](../../SUPABASE_SETUP.md) for detailed instructions.

## Future Migrations

When you need to modify the database schema:

1. Create a new SQL file in this directory (e.g., `002_add_new_table.sql`)
2. Write your migration SQL
3. Run it in Supabase SQL Editor
4. Test thoroughly

## Best Practices

- Always backup your database before running migrations
- Test migrations on a development/staging environment first
- Use transactions where possible
- Document what each migration does
- Version your migrations (001_, 002_, etc.)

