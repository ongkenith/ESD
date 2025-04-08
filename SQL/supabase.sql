-- "Customer"

DROP TABLE IF EXISTS "Customer";
CREATE TABLE "Customer" (
    "Customer_ID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255) NOT NULL,
    "Email" VARCHAR(255) UNIQUE NOT NULL,
    "Mobile_No" VARCHAR(8) NOT NULL
);

INSERT INTO "Customer" ("Name", "Email", "Mobile_No") VALUES
('Tina', 'tina@email.com', '91234567'),
('Kenny', 'kenny@email.com', '92345678'),
('Jordan', 'jordan@email.com', '93456789'),
('Jasdev', 'jasdev@email.com', '94567890'),
('Zhengjie', 'zhengjie@email.com', '95678901'),
('Deshaun', 'deshaun@email.com', '96789012');

-- "Store"

DROP TABLE IF EXISTS "Store" CASCADE;
CREATE TABLE "Store" (
  "store_id" SERIAL PRIMARY KEY,
  "pickup_location" INTEGER NOT NULL
);

--
-- Dumping data for table `store`
--

INSERT INTO "Store" ("pickup_location") VALUES
(123456);


-- "Drone"

DROP TABLE IF EXISTS "Drone" CASCADE;
CREATE TABLE "Drone" (
    "droneID" SERIAL PRIMARY KEY,
    "drone_status" VARCHAR(50)
);

-- Insert 5 drones into the Drone table
INSERT INTO "Drone" ("droneID", "drone_status") VALUES 
(1, 'Available'),
(2, 'Under Maintenance'),
(3, 'On Delivery'),
(4, 'Available'),
(5, 'Available');

-- Item

DROP TABLE IF EXISTS "Item" CASCADE;
CREATE TABLE "Item" (
  "Item_ID" SERIAL PRIMARY KEY,
  "Name" varchar(255) NOT NULL DEFAULT 'NEW',
  "store_id" INTEGER NOT NULL,
  "Price" float NOT NULL DEFAULT 0,
  FOREIGN KEY ("store_id") REFERENCES "Store"("store_id")
  
);

INSERT INTO "Item" ("Name", "store_id", "Price") VALUES
('Mala Soup', 1, 100);


-- Order
DROP TABLE IF EXISTS "Order" CASCADE;
-- Create Order table
CREATE TABLE "Order" (
  "order_id" SERIAL PRIMARY KEY,
  "order_date" TIMESTAMP NOT NULL,
  "droneID" INTEGER,
  "total_amount" FLOAT,
  "payment_status" BOOLEAN,
  "deliveryLocation" INTEGER,
  "Customer_ID" INTEGER,
  "order_status" VARCHAR(255)
);

INSERT INTO "Order" ("order_date", "droneID", "total_amount", "payment_status", "deliveryLocation", "Customer_ID", "order_status")
VALUES
(NOW(), 1, 150.00, TRUE, 654321, 1, 'Pending'),
(NOW(), 4, 75.50, TRUE, 987654, 2, 'Processing'),
(NOW(), 5, 200.00, FALSE, 246810, 3, 'Confirmed');

-- Order Item
DROP TABLE IF EXISTS "Order_Item" CASCADE;
-- Create "Order Item" table
CREATE TABLE "Order_Item" (
  id SERIAL PRIMARY KEY,
  "order_id" INTEGER NOT NULL,
  item_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  FOREIGN KEY ("order_id") REFERENCES "Order"("order_id"),
  FOREIGN KEY (item_id) REFERENCES "Item"("Item_ID")
);

-- Schedule

DROP TABLE IF EXISTS "scheduling";

CREATE TABLE IF NOT EXISTS "scheduling" (
    "Schedule_ID" SERIAL PRIMARY KEY,
    "ScheduleDateTime" TIMESTAMP NOT NULL,
    "WeatherCheck" BOOLEAN NOT NULL,
    "store_id" INTEGER NOT NULL,
    "order_id" INTEGER NOT NULL,
    "droneID" INTEGER NOT NULL,
    "actual_pickup_location" INTEGER NOT NULL,
    "actual_delivery_location" INTEGER NOT NULL,
    FOREIGN KEY ("store_id") REFERENCES "Store"("store_id")
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("order_id") REFERENCES "Order"("order_id")
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("droneID") REFERENCES "Drone"("droneID")
        ON DELETE CASCADE ON UPDATE CASCADE
);

select * from "Customer";
SELECT column_name FROM information_schema.columns
WHERE table_name = 'scheduling';
