-- Create database
CREATE DATABASE OrderSystem;
USE OrderSystem;

-- Create Order table
CREATE TABLE OrderTable (
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

-- Create Customer table
CREATE TABLE Customer (
    Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255),
    Email VARCHAR(255) UNIQUE NOT NULL,
    Mobile_No VARCHAR(8)
);

-- Create Item table
CREATE TABLE Item (
    Item_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255),
    Store_ID VARCHAR(255),
    Price FLOAT(53),
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
);

-- Create Store table
CREATE TABLE Store (
    Store_ID VARCHAR(255) PRIMARY KEY,
    PickUpLocation INT
);