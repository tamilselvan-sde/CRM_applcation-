// CRM Application MongoDB Initialization Script
// This script initializes the MongoDB database with roles and permissions

// Switch to the CRM auth database
db = db.getSiblingDB('crm_auth');

// Create collections
db.createCollection('users');
db.createCollection('roles');
db.createCollection('permissions');

// Create indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });
db.roles.createIndex({ name: 1 }, { unique: true });

// Insert default roles
const roles = [
    {
        name: 'admin',
        description: 'Full system access - manage users, customers, products, and invoices',
        permissions: ['all'],
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        name: 'manager',
        description: 'Manage customers, products, and invoices',
        permissions: [
            'customers:read', 'customers:write', 'customers:delete',
            'products:read', 'products:write', 'products:delete',
            'invoices:read', 'invoices:write', 'invoices:delete'
        ],
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        name: 'staff',
        description: 'Create invoices and view data',
        permissions: [
            'customers:read',
            'products:read',
            'invoices:read', 'invoices:write'
        ],
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        name: 'viewer',
        description: 'Read-only access to view data and download invoices',
        permissions: [
            'customers:read',
            'products:read',
            'invoices:read'
        ],
        created_at: new Date(),
        updated_at: new Date()
    }
];

// Insert roles if they don't exist
roles.forEach(function(role) {
    db.roles.updateOne(
        { name: role.name },
        { $setOnInsert: role },
        { upsert: true }
    );
});

// Create default admin user (password: admin123)
// Password hash for 'admin123' using bcrypt
const adminPasswordHash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYWKQTLmLmHe';

db.users.updateOne(
    { email: 'admin@crm.local' },
    {
        $setOnInsert: {
            username: 'admin',
            email: 'admin@crm.local',
            password: adminPasswordHash,
            first_name: 'System',
            last_name: 'Administrator',
            role: 'admin',
            is_active: true,
            created_at: new Date(),
            updated_at: new Date()
        }
    },
    { upsert: true }
);

print('MongoDB initialization completed successfully');
print('Default admin user created: admin@crm.local / admin123');
print('Roles created: admin, manager, staff, viewer');
