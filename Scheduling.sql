-- Drop the table if it already exists
DROP TABLE IF EXISTS scheduling;

-- Create the scheduling table
CREATE TABLE IF NOT EXISTS scheduling (
  Schedule_ID INT NOT NULL AUTO_INCREMENT,
  ScheduleName VARCHAR(255) NOT NULL,
  ScheduleDateTime DATETIME NOT NULL,
  WeatherCheck BOOLEAN NOT NULL,
  PickUpLocation INT NOT NULL,
  DeliveryLocation INT NOT NULL,
  DroneID INT NOT NULL,
  PRIMARY KEY (Schedule_ID),
  -- Assuming a 'locations' table exists with a primary key 'Location_ID'
  FOREIGN KEY (PickUpLocation) REFERENCES locations(Location_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (DeliveryLocation) REFERENCES locations(Location_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  -- Assuming a 'drone' table exists with a primary key 'DroneID'
  FOREIGN KEY (DroneID) REFERENCES drone(DroneID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
