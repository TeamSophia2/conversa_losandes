-- MariaDB dump 10.19  Distrib 10.11.2-MariaDB, for osx10.18 (x86_64)
--
-- Host: localhost    Database: historia_de_usuario1
-- ------------------------------------------------------
-- Server version	8.0.31

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
-- Table structure for table `Autor`
--

DROP TABLE IF EXISTS `Autor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Autor` (
  `id` int NOT NULL,
  `afiliacion` varchar(255) DEFAULT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `apellido` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Autor`
--

LOCK TABLES `Autor` WRITE;
/*!40000 ALTER TABLE `Autor` DISABLE KEYS */;
/*!40000 ALTER TABLE `Autor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Categoria`
--

DROP TABLE IF EXISTS `Categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Categoria` (
  `id` int NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `linea_tematica` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Categoria`
--

LOCK TABLES `Categoria` WRITE;
/*!40000 ALTER TABLE `Categoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `Categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Comuna`
--

DROP TABLE IF EXISTS `Comuna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Comuna` (
  `id` int NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `latitud` decimal(9,6) DEFAULT NULL,
  `longitud` decimal(9,6) DEFAULT NULL,
  `region` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Comuna`
--

LOCK TABLES `Comuna` WRITE;
/*!40000 ALTER TABLE `Comuna` DISABLE KEYS */;
/*!40000 ALTER TABLE `Comuna` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Documento`
--

DROP TABLE IF EXISTS `Documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Documento` (
  `id` int NOT NULL,
  `doi` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `tipo` varchar(255) DEFAULT NULL,
  `año` int DEFAULT NULL,
  `titulo` varchar(255) DEFAULT NULL,
  `contenido` text,
  `resumen` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Documento`
--

LOCK TABLES `Documento` WRITE;
/*!40000 ALTER TABLE `Documento` DISABLE KEYS */;
/*!40000 ALTER TABLE `Documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Escribir`
--

DROP TABLE IF EXISTS `Escribir`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Escribir` (
  `id_documento` int DEFAULT NULL,
  `id_autor` int DEFAULT NULL,
  KEY `id_documento` (`id_documento`),
  KEY `id_autor` (`id_autor`),
  CONSTRAINT `escribir_ibfk_1` FOREIGN KEY (`id_documento`) REFERENCES `Documento` (`id`),
  CONSTRAINT `escribir_ibfk_2` FOREIGN KEY (`id_autor`) REFERENCES `Autor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Escribir`
--

LOCK TABLES `Escribir` WRITE;
/*!40000 ALTER TABLE `Escribir` DISABLE KEYS */;
/*!40000 ALTER TABLE `Escribir` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Referirse`
--

DROP TABLE IF EXISTS `Referirse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Referirse` (
  `id_documento` int DEFAULT NULL,
  `id_comuna` int DEFAULT NULL,
  KEY `id_documento` (`id_documento`),
  KEY `id_comuna` (`id_comuna`),
  CONSTRAINT `referirse_ibfk_1` FOREIGN KEY (`id_documento`) REFERENCES `Documento` (`id`),
  CONSTRAINT `referirse_ibfk_2` FOREIGN KEY (`id_comuna`) REFERENCES `Comuna` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Referirse`
--

LOCK TABLES `Referirse` WRITE;
/*!40000 ALTER TABLE `Referirse` DISABLE KEYS */;
/*!40000 ALTER TABLE `Referirse` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tratar`
--

DROP TABLE IF EXISTS `Tratar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Tratar` (
  `id_documento` int DEFAULT NULL,
  `id_categoria` int DEFAULT NULL,
  KEY `id_documento` (`id_documento`),
  KEY `id_categoria` (`id_categoria`),
  CONSTRAINT `tratar_ibfk_1` FOREIGN KEY (`id_documento`) REFERENCES `Documento` (`id`),
  CONSTRAINT `tratar_ibfk_2` FOREIGN KEY (`id_categoria`) REFERENCES `Categoria` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tratar`
--

LOCK TABLES `Tratar` WRITE;
/*!40000 ALTER TABLE `Tratar` DISABLE KEYS */;
/*!40000 ALTER TABLE `Tratar` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-13  9:29:21
