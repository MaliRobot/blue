-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 26, 2019 at 07:46 PM
-- Server version: 5.7.24
-- PHP Version: 7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `blue`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `admin` tinyint(1) NOT NULL,
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `admin`, `email`) VALUES
(18, 'test', 'pbkdf2:sha256:150000$1D8qrG27$da2f547419b9e81608432089bdc0deeff5fd51923a8bc2c98b76075de6a88f02', 1, 'test@test.com'),
(19, 'user1', 'pbkdf2:sha256:150000$THigpUHb$7d62e00fd8e9a288c4ef16193ce2266f7038f47741474c7ee0c6da7e75e81934', 0, 'testy@test.com'),
(20, 'admin1', 'pbkdf2:sha256:150000$ruk1MbYz$61ee36e03c9ba4f5550e4bd019b5ae0953c6621dee125eaa21e0bc865663170e', 1, 'admin3@test.com'),
(21, 'admin2', 'pbkdf2:sha256:150000$QPy0Je5a$dcef8861da6f5d67c2dd0935c27d1f5cbd4d1582a563e82f17b4b58f494b3184', 1, 'admin1@test.com'),
(24, 'new_user', 'pbkdf2:sha256:150000$6PVNapDv$98b0dfeacb29646f16fe2eb2be4f3edd38420de825dc11e1b64a2260d7c0299b', 1, 'new_user@example.com');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
