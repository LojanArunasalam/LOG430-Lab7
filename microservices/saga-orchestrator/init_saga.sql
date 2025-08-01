CREATE TABLE IF NOT EXISTS saga_instances (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,          
    cart_id INTEGER NOT NULL,           
    quantity INTEGER NOT NULL,
    amount DECIMAL(10, 2),              -- Should be nullable, calculated later
    current_state VARCHAR(50) DEFAULT 'created',
    saga_status VARCHAR(50) DEFAULT 'started',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    compensation_actions TEXT,
    checkout_id INTEGER
);

CREATE TABLE IF NOT EXISTS saga_steps (
    id SERIAL PRIMARY KEY,
    saga_id INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    step_status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    request_data TEXT,
    response_data TEXT,
    FOREIGN KEY (saga_id) REFERENCES saga_instances(id)
);
