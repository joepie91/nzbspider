SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE IF NOT EXISTS `releases` (
  `releaseid` int(11) NOT NULL AUTO_INCREMENT,
  `time` int(11) NOT NULL,
  `section` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `release` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`releaseid`),
  UNIQUE KEY `release` (`release`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
