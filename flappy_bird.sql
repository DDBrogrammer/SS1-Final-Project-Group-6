-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 16, 2021 at 09:23 AM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 8.0.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `flappy_bird`
--

-- --------------------------------------------------------

--
-- Table structure for table `score_record`
--

CREATE TABLE `score_record` (
  `id` bigint(20) NOT NULL,
  `player_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `score` bigint(255) NOT NULL,
  `play_date` date NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `score_record`
--

INSERT INTO `score_record` (`id`, `player_name`, `score`, `play_date`) VALUES
(11, 'one', 0, '2021-12-16'),
(12, 'three', 0, '2021-12-16'),
(13, 'OP man', 1, '2021-12-16'),
(14, 'dads', 2, '2021-12-16'),
(15, 'G9', 3, '2021-12-16'),
(16, 'musizzz', 3, '2021-12-16'),
(17, 'okeo', 4, '2021-12-16'),
(18, 'Auuu', 4, '2021-12-16'),
(19, 'helooo', 13, '2021-12-16'),
(20, 'ok', 6, '2021-12-16'),
(21, ':((', 1, '2021-12-16'),
(22, '', 1, '2021-12-16'),
(23, 'now', 2, '2021-12-16'),
(24, '', 0, '2021-12-16'),
(25, 'faker', 16, '2021-12-16'),
(26, '', 1, '2021-12-16'),
(27, 'nike', 9, '2021-12-16'),
(28, 'oke', 3, '2021-12-16'),
(29, 'auu', 11, '2021-12-16'),
(30, 'ok', 1, '2021-12-16'),
(31, '2k1', 6, '2021-12-16'),
(32, 'no name', 11, '2021-12-16'),
(33, 'five', 5, '2021-12-16');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `score_record`
--
ALTER TABLE `score_record`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `score_record`
--
ALTER TABLE `score_record`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
