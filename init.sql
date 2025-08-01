CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE stores (
    id SERIAL PRIMARY KEY, 
    name VARCHAR
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    total INTEGER,
    "user" INTEGER REFERENCES users(id),
    store INTEGER REFERENCES stores(id)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    category VARCHAR,
    description VARCHAR,
    prix_unitaire FLOAT
);

CREATE TABLE line_sales (
    id SERIAL PRIMARY KEY,
    quantite INTEGER,
    prix FLOAT,
    sale INTEGER REFERENCES sales(id),
    product INTEGER REFERENCES products(id)
);

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    quantite INTEGER,
    product INTEGER REFERENCES products(id),
    store INTEGER REFERENCES stores(id)
);

CREATE TABLE products_depot (
    id SERIAL PRIMARY KEY,
    quantite_depot INTEGER,
    product INTEGER REFERENCES products(id)
);

-- CREATE TABLE reports (
--     id SERIAL PRIMARY KEY,
--     store INTEGER REFERENCES stores(id),
--     total_sales FLOAT,
--     total_products_sold INTEGER,
--     total_stock_value FLOAT
-- );

-- CREATE TABLE performances (
--     id SERIAL PRIMARY KEY,
--     store INTEGER REFERENCES stores(id),
--     total_sales FLOAT,
--     total_products_sold INTEGER,
--     total_stock_value FLOAT
-- );



INSERT INTO stores (name) VALUES
('Magasin Centre-Ville'),
('Magasin Nord'),
('Magasin Sud'),
('Magasin Est'),
('Maison Mère');

INSERT INTO users (name) VALUES
('Alice Johnson'), ('Bob Smith'), ('Catherine Lee'), ('David Miller'), ('Emma Davis'),
('Frank Wilson'), ('Grace Thompson'), ('Henry Anderson'), ('Isla Moore'), ('Jack Taylor');

INSERT INTO products (name, category, description, prix_unitaire) VALUES
('Timbits', 'Snacks', 'Tim Horton treats in the shape of a small ball', 0.25),
('Coffee', 'Beverages', 'Hot brewed coffee', 1.99),
('Donut', 'Snacks', 'Glazed donut', 1.25),
('Bagel', 'Snacks', 'Sesame seed bagel', 1.50),
('Muffin', 'Snacks', 'Blueberry muffin', 2.00);

INSERT INTO stocks (quantite, product, store) VALUES
(23, 1, 1), (2, 2, 1), (45, 3, 1), (2, 4, 1), (84, 5, 1), 
(34, 1, 2), (34, 2, 2), (73, 3, 2), (4, 4, 2), (24, 5, 2), 
(56, 1, 3), (8, 2, 3), (26, 3, 3), (89, 4, 3), (5, 5, 3), 
(5, 1, 4), (89, 2, 4), (6, 3, 4), (67, 4, 4), (7, 5, 4), 
(10, 1, 5), (25, 2, 5), (90, 3, 5), (5, 4, 5), (37, 5, 5);

INSERT INTO sales (id, total, "user", store) VALUES
(1, 5, 1, 1),
(2, 7, 2, 1),
(3, 6, 3, 2),
(4, 4, 4, 3),
(5, 3, 5, 4),
(6, 6, 6, 4),
(7, 8, 7, 5);

INSERT INTO line_sales (quantite, prix, sale, product) VALUES
(2, 0.25, 1, 1),   -- 2 Timbits
(1, 1.99, 1, 2);   -- 1 Coffee

INSERT INTO line_sales (quantite, prix, sale, product) VALUES
(1, 2.00, 2, 5),   -- 1 Muffin
(2, 1.50, 2, 4);   -- 2 Bagels

INSERT INTO line_sales (quantite, prix, sale, product) VALUES
(2, 1.25, 3, 3),   -- 2 Donuts
(1, 1.99, 3, 2);   -- 1 Coffee

INSERT INTO line_sales (quantite, prix, sale, product) VALUES
(1, 2.00, 4, 5),   -- 1 Muffin
(1, 1.25, 4, 3);   -- 1 Donut

INSERT INTO line_sales (quantite, prix, sale, product) VALUES
(1, 1.99, 5, 2),   -- 1 Coffee
(1, 0.25, 5, 1);   -- 1 Timbits

INSERT INTO line_sales (quantite, prix, sale, product) VALUES
(2, 1.50, 6, 4),   -- 2 Bagels
(1, 2.00, 6, 5);   -- 1 Muffin

INSERT INTO line_sales (quantite, prix, sale, product) VALUES
(3, 0.25, 7, 1),   -- 3 Timbits
(1, 1.99, 7, 2),   -- 1 Coffee
(1, 1.25, 7, 3);   -- 1 Donut
INSERT INTO products_depot (quantite_depot, product) VALUES
(80, 1), (60, 2), (40, 3), (75, 4), (25, 5);




