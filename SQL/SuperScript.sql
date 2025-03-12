-- Create database

DROP DATABASE IF EXISTS my_database;
CREATE DATABASE my_database;
USE my_database;


-- Customer

DROP TABLE IF EXISTS `Customer`;
CREATE TABLE Customer (
    Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Mobile_No VARCHAR(8) NOT NULL
);

INSERT INTO Customer (Name, Email, Mobile_No) VALUES
('Tina', 'tina@email.com', '91234567'),
('Kenny', 'kenny@email.com', '92345678'),
('Jordan', 'jordan@email.com', '93456789'),
('Jasdev', 'jasdev@email.com', '94567890'),
('Zhengjie', 'zhengjie@email.com', '95678901'),
('Deshaun', 'deshaun@email.com', '96789012');

-- Store

DROP TABLE IF EXISTS `Store`;
CREATE TABLE Store (
  `store_id` int(11) NOT NULL AUTO_INCREMENT,
  `pickup_location` int(6) NOT NULL,
  PRIMARY KEY (`store_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `store`
--

INSERT INTO `store` (`store_id`, `pickup_location`) VALUES
(1, 123456);


-- Drone

DROP TABLE IF EXISTS `Drone`;
CREATE TABLE IF NOT EXISTS `Drone` (
    DroneID INT AUTO_INCREMENT PRIMARY KEY,
    Drone_Status VARCHAR(50)
);

-- Insert 5 drones into the Drone table
INSERT INTO Drone (DroneID, Drone_Status) VALUES 
(1, 'Available'),
(2, 'Under Maintenance'),
(3, 'On Delivery'),
(4, 'Available'),
(5, 'Available');

-- Item

DROP TABLE IF EXISTS `Item`;
CREATE TABLE Item (
  `item_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT 'NEW',
  `store_id` int(11) NOT NULL,
  `price` float(53) NOT NULL DEFAULT 0,
  PRIMARY KEY (`item_id`),
  FOREIGN KEY (`store_id`) REFERENCES Store(`store_id`)
  
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

INSERT INTO `Item` (`item_id`, `name`, `store_id`, `price`) VALUES
(1, 'Mala Soup', 1, 100);


-- Order

-- Create Order table
CREATE TABLE `Order` (
  Order_ID INT AUTO_INCREMENT PRIMARY KEY,
  Order_Date DATETIME NOT NULL,
  Drone_ID INT,
  Total_Amount FLOAT,
  Payment_Status BOOLEAN,
  DeliveryLocation INT,
  Customer_ID INT,
  Item_list VARCHAR(255),
  Order_Status VARCHAR(255),
  FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);


-- Schedule


DROP TABLE IF EXISTS scheduling;


CREATE TABLE IF NOT EXISTS scheduling (
  Schedule_ID INT NOT NULL AUTO_INCREMENT,
  ScheduleName VARCHAR(255) NOT NULL,
  ScheduleDateTime DATETIME NOT NULL,
  WeatherCheck BOOLEAN NOT NULL,
  PickUpLocation INT NOT NULL,
  DeliveryLocation INT NOT NULL,
  DroneID INT NOT NULL,
  PRIMARY KEY (Schedule_ID),
  FOREIGN KEY (PickUpLocation) REFERENCES Store(store_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (DeliveryLocation) REFERENCES `Order`(Order_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (DroneID) REFERENCES drone(DroneID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


