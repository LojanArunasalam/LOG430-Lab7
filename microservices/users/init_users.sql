CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(255),
    address VARCHAR(255), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email, phone, address) VALUES
('John Doe', 'john.doe@email.com', '514-555-0101', '123 Rue Saint-Catherine, Montreal, QC H3B 1A1'),
('Jane Smith', 'jane.smith@email.com', '416-555-0102', '456 Queen Street West, Toronto, ON M5V 2A9'),
('Bob Johnson', 'bob.johnson@email.com', '604-555-0103', '789 Robson Street, Vancouver, BC V6Z 1A1'),
('Alice Williams', 'alice.williams@email.com', '514-555-0104', '321 Boulevard René-Lévesque, Montreal, QC H2Z 1A8'),
('Charlie Brown', 'charlie.brown@email.com', '403-555-0105', '654 Stephen Avenue, Calgary, AB T2P 1M7'),
('Diana Prince', 'diana.prince@email.com', '613-555-0106', '987 Sparks Street, Ottawa, ON K1A 0A6'),
('Frank Miller', 'frank.miller@email.com', '902-555-0107', '147 Barrington Street, Halifax, NS B3J 1Z2'),
('Grace Kelly', 'grace.kelly@email.com', '506-555-0108', '258 King Street, Fredericton, NB E3B 1E1');