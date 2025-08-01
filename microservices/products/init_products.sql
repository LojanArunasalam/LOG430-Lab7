CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    category VARCHAR,
    description VARCHAR,
    prix_unitaire FLOAT
);


INSERT INTO products (name, category, description, prix_unitaire) VALUES
('Timbits', 'Snacks', 'Tim Horton treats in the shape of a small ball', 0.25),
('Coffee', 'Beverages', 'Hot brewed coffee', 1.99),
('Donut', 'Snacks', 'Glazed donut', 1.25),
('Bagel', 'Snacks', 'Sesame seed bagel', 1.50),
('Muffin', 'Snacks', 'Blueberry muffin', 2.00);




