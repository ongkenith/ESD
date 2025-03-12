DROP TABLE IF EXISTS 'Drone';
CREATE TABLE IF NOT EXISTS 'Drone' (
    Drone_ID INT AUTO_INCREMENT PRIMARY KEY,
    Drone_Status VARCHAR(50)
);

-- Insert 5 drones into the Drone table
INSERT INTO Drone (DroneID, Drone_Status) VALUES 
(1, 'Available'),
(2, 'Under Maintenance'),
(3, 'On Delivery'),
(4, 'Available'),
(5, 'Available');