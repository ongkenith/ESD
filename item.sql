DROP TABLE IF EXISTS `Item`;
CREATE TABLE Item (
  `item_id` int(11) NOT NULL PRIMARY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT 'NEW',
  `store_id` int(11) NOT NULL,
  `price` float(53) NOT NULL DEFAULT 0,
  PRIMARY KEY (`item_id`)
  FOREIGN KEY (`store_id`) REFERENCES Store(`store_id`)
  
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

INSERT INTO `Item` (`item_id`, `name`, `store_id`, `price`) VALUES
(1, `Mala Soup`, `1`, 100);