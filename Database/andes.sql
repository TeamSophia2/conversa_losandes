-- MariaDB dump 10.19  Distrib 10.6.12-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: andes
-- ------------------------------------------------------
-- Server version	10.6.12-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Author`
--

DROP TABLE IF EXISTS `Author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Author` (
  `authorId` int(11) NOT NULL AUTO_INCREMENT,
  `authorName` varchar(255) DEFAULT NULL,
  `emailAddress` varchar(255) DEFAULT NULL,
  `affiliation` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`authorId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Author`
--

LOCK TABLES `Author` WRITE;
/*!40000 ALTER TABLE `Author` DISABLE KEYS */;
/*!40000 ALTER TABLE `Author` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Category`
--

DROP TABLE IF EXISTS `Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Category` (
  `categoryName` varchar(100) NOT NULL,
  `principalCategoryId` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`categoryName`),
  KEY `principalCategoryId` (`principalCategoryId`),
  CONSTRAINT `Category_ibfk_1` FOREIGN KEY (`principalCategoryId`) REFERENCES `Category` (`categoryName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Category`
--

LOCK TABLES `Category` WRITE;
/*!40000 ALTER TABLE `Category` DISABLE KEYS */;
INSERT INTO `Category` VALUES ('LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA',NULL),('LT2: Cambio Global: interacción bosque, suelo y recursos hídricos',NULL),('LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA',NULL),('Geotermia y sistemas hidrotermales','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Mineralogía y Petrología','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Paleontología y Sedimentología','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Patrimonio Geológico','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Procesos de remoción en masa','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Tectónica y peligro sísmico','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Volcanología y peligro volcánico','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Bosques templados, ecología y dinámica','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Cambio climático, perturbaciones naturales y antrópicas','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Fertilidad, química y biología del suelo','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Glaciares y rrhh','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Historia evolutiva de la flora y la fauna','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Conflictos socioambientales','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Desarrollo local y gobernanza','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Educación','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Historia y territorialidades','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Prácticas bioculturales','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA');
/*!40000 ALTER TABLE `Category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Commune`
--

DROP TABLE IF EXISTS `Commune`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Commune` (
  `communeId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `region` varchar(50) DEFAULT NULL,
  `latitude` decimal(10,6) DEFAULT NULL,
  `longitude` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`communeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Commune`
--

LOCK TABLES `Commune` WRITE;
/*!40000 ALTER TABLE `Commune` DISABLE KEYS */;
/*!40000 ALTER TABLE `Commune` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Concept`
--

DROP TABLE IF EXISTS `Concept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Concept` (
  `conceptId` int(11) NOT NULL AUTO_INCREMENT,
  `conceptName` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`conceptId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Concept`
--

LOCK TABLES `Concept` WRITE;
/*!40000 ALTER TABLE `Concept` DISABLE KEYS */;
/*!40000 ALTER TABLE `Concept` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Document`
--

DROP TABLE IF EXISTS `Document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Document` (
  `documentId` int(11) NOT NULL AUTO_INCREMENT,
  `doi` varchar(100) DEFAULT NULL,
  `url` varchar(500) DEFAULT NULL,
  `documentType` varchar(50) DEFAULT NULL,
  `publicationYear` int(11) DEFAULT NULL,
  `title` varchar(500) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `abstract` text DEFAULT NULL,
  PRIMARY KEY (`documentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Document`
--

LOCK TABLES `Document` WRITE;
/*!40000 ALTER TABLE `Document` DISABLE KEYS */;
/*!40000 ALTER TABLE `Document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Document_Author`
--

DROP TABLE IF EXISTS `Document_Author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Document_Author` (
  `authorId` int(11) NOT NULL,
  `documentId` int(11) NOT NULL,
  PRIMARY KEY (`authorId`,`documentId`),
  KEY `documentId` (`documentId`),
  CONSTRAINT `Document_Author_ibfk_1` FOREIGN KEY (`authorId`) REFERENCES `Author` (`authorId`),
  CONSTRAINT `Document_Author_ibfk_2` FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Document_Author`
--

LOCK TABLES `Document_Author` WRITE;
/*!40000 ALTER TABLE `Document_Author` DISABLE KEYS */;
/*!40000 ALTER TABLE `Document_Author` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Document_Category`
--

DROP TABLE IF EXISTS `Document_Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Document_Category` (
  `documentId` int(11) NOT NULL,
  `categoryName` varchar(100) NOT NULL,
  PRIMARY KEY (`documentId`,`categoryName`),
  KEY `categoryName` (`categoryName`),
  CONSTRAINT `Document_Category_ibfk_1` FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`),
  CONSTRAINT `Documento_Category_ibfk_2` FOREIGN KEY (`categoryName`) REFERENCES `Category` (`categoryName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Document_Category`
--

LOCK TABLES `Document_Category` WRITE;
/*!40000 ALTER TABLE `Document_Category` DISABLE KEYS */;
/*!40000 ALTER TABLE `Document_Category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Document_Commune`
--

DROP TABLE IF EXISTS `Document_Commune`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Document_Commune` (
  `documentId` int(11) NOT NULL,
  `communeId` int(11) NOT NULL,
  PRIMARY KEY (`documentId`,`communeId`),
  KEY `communeId` (`communeId`),
  CONSTRAINT `Document_Commune_ibfk_1` FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`),
  CONSTRAINT `Document_Commune_ibfk_2` FOREIGN KEY (`communeId`) REFERENCES `Commune` (`communeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Document_Commune`
--

LOCK TABLES `Document_Commune` WRITE;
/*!40000 ALTER TABLE `Document_Commune` DISABLE KEYS */;
/*!40000 ALTER TABLE `Document_Commune` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Document_Concept`
--

DROP TABLE IF EXISTS `Document_Concept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Document_Concept` (
  `conceptId` int(11) NOT NULL,
  `documentId` int(11) NOT NULL,
  PRIMARY KEY (`conceptId`,`documentId`),
  KEY `documentId` (`documentId`),
  CONSTRAINT `Document_Concept_ibfk_1` FOREIGN KEY (`conceptId`) REFERENCES `Concept` (`conceptId`),
  CONSTRAINT `Document_Concept_ibfk_2` FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Document_Concept`
--

LOCK TABLES `Document_Concept` WRITE;
/*!40000 ALTER TABLE `Document_Concept` DISABLE KEYS */;
/*!40000 ALTER TABLE `Document_Concept` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Document_Organization`
--

DROP TABLE IF EXISTS `Document_Organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Document_Organization` (
  `documentId` int(11) NOT NULL,
  `organizationId` int(11) NOT NULL,
  PRIMARY KEY (`documentId`,`organizationId`),
  KEY `organizationId` (`organizationId`),
  CONSTRAINT `Document_Organization_ibfk_1` FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`),
  CONSTRAINT `Document_Organization_ibfk_2` FOREIGN KEY (`organizationId`) REFERENCES `Organization` (`organizationId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Document_Organization`
--

LOCK TABLES `Document_Organization` WRITE;
/*!40000 ALTER TABLE `Document_Organization` DISABLE KEYS */;
/*!40000 ALTER TABLE `Document_Organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Organization`
--

DROP TABLE IF EXISTS `Organization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Organization` (
  `organizationId` int(11) NOT NULL AUTO_INCREMENT,
  `organizationName` varchar(255) DEFAULT NULL,
  `organizationType` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`organizationId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Organization`
--

LOCK TABLES `Organization` WRITE;
/*!40000 ALTER TABLE `Organization` DISABLE KEYS */;
/*!40000 ALTER TABLE `Organization` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-07-19 23:52:18
