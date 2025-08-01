CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    total INTEGER,
    "user" INTEGER NOT NULL,
    store INTEGER NOT NULL
);

CREATE TABLE item_carts (
    id SERIAL PRIMARY KEY,
    quantite INTEGER,
    prix FLOAT DEFAULT 0.00,
    cart INTEGER REFERENCES carts(id),
    product INTEGER NOT NULL
);



CREATE TABLE checkout  (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id),
    current_status VARCHAR(50) NOT NULL DEFAULT 'pending'
);


-- INSERT INTO carts (id, total, "user", store) VALUES
-- (1, 5, 1, 1),
-- (2, 7, 2, 1),
-- (3, 6, 3, 2),
-- (4, 4, 4, 3),
-- (5, 3, 5, 4),
-- (6, 6, 6, 4),
-- (7, 8, 7, 5);

-- INSERT INTO item_carts (quantite, prix, cart, product) VALUES
-- (2, 0.25, 1, 1),   -- 2 Timbits
-- (1, 1.99, 1, 2);   -- 1 Coffee

-- INSERT INTO item_carts (quantite, prix, cart, product) VALUES
-- (1, 2.00, 2, 5),   -- 1 Muffin
-- (2, 1.50, 2, 4);   -- 2 Bagels

-- INSERT INTO item_carts (quantite, prix, cart, product) VALUES
-- (2, 1.25, 3, 3),   -- 2 Donuts
-- (1, 1.99, 3, 2);   -- 1 Coffee

-- INSERT INTO item_carts (quantite, prix, cart, product) VALUES
-- (1, 2.00, 4, 5),   -- 1 Muffin
-- (1, 1.25, 4, 3);   -- 1 Donut

-- INSERT INTO item_carts (quantite, prix, cart, product) VALUES
-- (1, 1.99, 5, 2),   -- 1 Coffee
-- (1, 0.25, 5, 1);   -- 1 Timbits

-- INSERT INTO item_carts (quantite, prix, cart, product) VALUES
-- (2, 1.50, 6, 4),   -- 2 Bagels
-- (1, 2.00, 6, 5);   -- 1 Muffin

-- INSERT INTO item_carts (quantite, prix, cart, product) VALUES
-- (3, 0.25, 7, 1),   -- 3 Timbits
-- (1, 1.99, 7, 2),   -- 1 Coffee
-- (1, 1.25, 7, 3);   -- 1 Donut

