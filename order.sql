-- Create database
CREATE DATABASE IF NOT EXISTS my_database;
USE my_database;

-- Create Order table
CREATE TABLE Order (
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