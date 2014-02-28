CREATE TABLE `accounts` (
  `accountid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `password` varchar(64) NOT NULL,
  `contact` text,
  `email` text,
  `phone` text,
  PRIMARY KEY (`accountid`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3417 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `logs`;
CREATE TABLE `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message` varchar(255) DEFAULT NULL,
  `pid` int(11) DEFAULT NULL,
  `username` char(32) DEFAULT NULL,
  `host` char(128) DEFAULT NULL,
  `rhost` char(128) DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2047128 DEFAULT CHARSET=latin1;
