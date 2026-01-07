-- CRM Application PostgreSQL Schema
-- This script initializes the PostgreSQL database with required tables

-- Create extension for UUID generation (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    company VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE,
    price NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(50) DEFAULT 'unit' NOT NULL,
    is_service BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Invoice status enum type
DO $$ BEGIN
    CREATE TYPE invoice_status AS ENUM ('draft', 'pending', 'paid', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    status invoice_status DEFAULT 'draft' NOT NULL,
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    due_date TIMESTAMP,
    subtotal NUMERIC(12, 2) DEFAULT 0 NOT NULL,
    tax_rate NUMERIC(5, 2) DEFAULT 0 NOT NULL,
    tax_amount NUMERIC(12, 2) DEFAULT 0 NOT NULL,
    total NUMERIC(12, 2) DEFAULT 0 NOT NULL,
    notes TEXT,
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Invoice items table
CREATE TABLE IF NOT EXISTS invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    description TEXT,
    quantity NUMERIC(10, 2) DEFAULT 1 NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(12, 2) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX IF NOT EXISTS idx_invoice_items_product_id ON invoice_items(product_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_invoices_updated_at ON invoices;
CREATE TRIGGER update_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional - comment out for production)
-- INSERT INTO customers (name, email, phone, company) VALUES
--     ('John Doe', 'john@example.com', '+1-555-0100', 'Acme Corp'),
--     ('Jane Smith', 'jane@example.com', '+1-555-0101', 'Tech Solutions');

-- INSERT INTO products (name, description, sku, price, unit, is_service) VALUES
--     ('Web Development', 'Custom web development services', 'SVC-WEB-001', 150.00, 'hour', true),
--     ('Consulting', 'Business consulting services', 'SVC-CON-001', 200.00, 'hour', true),
--     ('Software License', 'Annual software license', 'PRD-LIC-001', 499.00, 'license', false);

COMMENT ON TABLE customers IS 'Customer information for CRM';
COMMENT ON TABLE products IS 'Products and services catalog';
COMMENT ON TABLE invoices IS 'Invoice headers with totals';
COMMENT ON TABLE invoice_items IS 'Line items for invoices';
