DROP TABLE IF EXISTS 'Store';
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