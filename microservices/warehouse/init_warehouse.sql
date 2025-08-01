CREATE TABLE stores (
    id SERIAL PRIMARY KEY, 
    name VARCHAR
);

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    quantite INTEGER,
    product INTEGER NOT NULL,
    store INTEGER REFERENCES stores(id)
);

CREATE TABLE products_depot (
    id SERIAL PRIMARY KEY,
    quantite_depot INTEGER,
    product INTEGER NOT NULL
);

INSERT INTO stores (name) VALUES
('Magasin Centre-Ville'),
('Magasin Nord'),
('Magasin Sud'),
('Magasin Est'),
('Maison Mère');

INSERT INTO stocks (quantite, product, store) VALUES
(23, 1, 1), (2, 2, 1), (45, 3, 1), (2, 4, 1), (84, 5, 1), 
(34, 1, 2), (34, 2, 2), (73, 3, 2), (4, 4, 2), (24, 5, 2), 
(56, 1, 3), (8, 2, 3), (26, 3, 3), (89, 4, 3), (5, 5, 3), 
(5, 1, 4), (89, 2, 4), (6, 3, 4), (67, 4, 4), (7, 5, 4), 
(10, 1, 5), (25, 2, 5), (90, 3, 5), (5, 4, 5), (37, 5, 5);

INSERT INTO products_depot (quantite_depot, product) VALUES
(80, 1), (60, 2), (40, 3), (75, 4), (25, 5);