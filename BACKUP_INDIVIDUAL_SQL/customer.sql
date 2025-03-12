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
