-- MariaDB dump 10.19  Distrib 10.6.12-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: test
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
-- Table structure for table `Autor`
--

DROP TABLE IF EXISTS `Autor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Autor` (
  `IDAutor` int(11) NOT NULL,
  `NombreAutor` varchar(255) DEFAULT NULL,
  `CorreoElectronico` varchar(255) DEFAULT NULL,
  `Afiliacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`IDAutor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Autor`
--

LOCK TABLES `Autor` WRITE;
/*!40000 ALTER TABLE `Autor` DISABLE KEYS */;
/*!40000 ALTER TABLE `Autor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Comuna`
--

DROP TABLE IF EXISTS `Comuna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Comuna` (
  `IDTerritorio` int(11) NOT NULL,
  `Nombre` varchar(50) DEFAULT NULL,
  `Region` varchar(50) DEFAULT NULL,
  `Latitud` decimal(10,6) DEFAULT NULL,
  `Longitud` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`IDTerritorio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Comuna`
--

LOCK TABLES `Comuna` WRITE;
/*!40000 ALTER TABLE `Comuna` DISABLE KEYS */;
/*!40000 ALTER TABLE `Comuna` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Concepto`
--

DROP TABLE IF EXISTS `Concepto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Concepto` (
  `IDConcepto` int(11) NOT NULL,
  `NombreConcepto` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`IDConcepto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Concepto`
--

LOCK TABLES `Concepto` WRITE;
/*!40000 ALTER TABLE `Concepto` DISABLE KEYS */;
/*!40000 ALTER TABLE `Concepto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Documento`
--

DROP TABLE IF EXISTS `Documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Documento` (
  `IDDocumento` int(11) NOT NULL,
  `DOI` varchar(50) DEFAULT NULL,
  `URL` varchar(255) DEFAULT NULL,
  `TipoDocumento` varchar(50) DEFAULT NULL,
  `AnoPublicacion` int(11) DEFAULT NULL,
  `Titulo` varchar(255) DEFAULT NULL,
  `Contenido` text DEFAULT NULL,
  PRIMARY KEY (`IDDocumento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Documento`
--

LOCK TABLES `Documento` WRITE;
/*!40000 ALTER TABLE `Documento` DISABLE KEYS */;
/*!40000 ALTER TABLE `Documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Documento_Autor`
--

DROP TABLE IF EXISTS `Documento_Autor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Documento_Autor` (
  `IDAutor` int(11) NOT NULL,
  `IDDocumento` int(11) NOT NULL,
  PRIMARY KEY (`IDAutor`,`IDDocumento`),
  KEY `IDDocumento` (`IDDocumento`),
  CONSTRAINT `Documento_Autor_ibfk_1` FOREIGN KEY (`IDAutor`) REFERENCES `Autor` (`IDAutor`),
  CONSTRAINT `Documento_Autor_ibfk_2` FOREIGN KEY (`IDDocumento`) REFERENCES `Documento` (`IDDocumento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Documento_Autor`
--

LOCK TABLES `Documento_Autor` WRITE;
/*!40000 ALTER TABLE `Documento_Autor` DISABLE KEYS */;
/*!40000 ALTER TABLE `Documento_Autor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Documento_Concepto`
--

DROP TABLE IF EXISTS `Documento_Concepto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Documento_Concepto` (
  `IDConcepto` int(11) NOT NULL,
  `IDDocumento` int(11) NOT NULL,
  PRIMARY KEY (`IDConcepto`,`IDDocumento`),
  KEY `IDDocumento` (`IDDocumento`),
  CONSTRAINT `Documento_Concepto_ibfk_1` FOREIGN KEY (`IDConcepto`) REFERENCES `Concepto` (`IDConcepto`),
  CONSTRAINT `Documento_Concepto_ibfk_2` FOREIGN KEY (`IDDocumento`) REFERENCES `Documento` (`IDDocumento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Documento_Concepto`
--

LOCK TABLES `Documento_Concepto` WRITE;
/*!40000 ALTER TABLE `Documento_Concepto` DISABLE KEYS */;
/*!40000 ALTER TABLE `Documento_Concepto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Documento_Organizacion`
--

DROP TABLE IF EXISTS `Documento_Organizacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Documento_Organizacion` (
  `IDDocumento` int(11) NOT NULL,
  `IDOrganizacion` int(11) NOT NULL,
  PRIMARY KEY (`IDDocumento`,`IDOrganizacion`),
  KEY `IDOrganizacion` (`IDOrganizacion`),
  CONSTRAINT `Documento_Organizacion_ibfk_1` FOREIGN KEY (`IDDocumento`) REFERENCES `Documento` (`IDDocumento`),
  CONSTRAINT `Documento_Organizacion_ibfk_2` FOREIGN KEY (`IDOrganizacion`) REFERENCES `Organizacion` (`IDOrganizacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Documento_Organizacion`
--

LOCK TABLES `Documento_Organizacion` WRITE;
/*!40000 ALTER TABLE `Documento_Organizacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `Documento_Organizacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Documento_Tematica`
--

DROP TABLE IF EXISTS `Documento_Tematica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Documento_Tematica` (
  `IDDocumento` int(11) NOT NULL,
  `NombreTematica` varchar(100) NOT NULL,
  PRIMARY KEY (`IDDocumento`,`NombreTematica`),
  KEY `NombreTematica` (`NombreTematica`),
  CONSTRAINT `Documento_Tematica_ibfk_1` FOREIGN KEY (`IDDocumento`) REFERENCES `Documento` (`IDDocumento`),
  CONSTRAINT `Documento_Tematica_ibfk_2` FOREIGN KEY (`NombreTematica`) REFERENCES `Tematica` (`NombreTematica`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Documento_Tematica`
--

LOCK TABLES `Documento_Tematica` WRITE;
/*!40000 ALTER TABLE `Documento_Tematica` DISABLE KEYS */;
/*!40000 ALTER TABLE `Documento_Tematica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Documento_Territorio`
--

DROP TABLE IF EXISTS `Documento_Territorio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Documento_Territorio` (
  `IDDocumento` int(11) NOT NULL,
  `IDTerritorio` int(11) NOT NULL,
  PRIMARY KEY (`IDDocumento`,`IDTerritorio`),
  KEY `IDTerritorio` (`IDTerritorio`),
  CONSTRAINT `Documento_Territorio_ibfk_1` FOREIGN KEY (`IDDocumento`) REFERENCES `Documento` (`IDDocumento`),
  CONSTRAINT `Documento_Territorio_ibfk_2` FOREIGN KEY (`IDTerritorio`) REFERENCES `Comuna` (`IDTerritorio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Documento_Territorio`
--

LOCK TABLES `Documento_Territorio` WRITE;
/*!40000 ALTER TABLE `Documento_Territorio` DISABLE KEYS */;
/*!40000 ALTER TABLE `Documento_Territorio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Organizacion`
--

DROP TABLE IF EXISTS `Organizacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Organizacion` (
  `IDOrganizacion` int(11) NOT NULL,
  `NombreOrganizacion` varchar(255) DEFAULT NULL,
  `TipoOrganizacion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`IDOrganizacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Organizacion`
--

LOCK TABLES `Organizacion` WRITE;
/*!40000 ALTER TABLE `Organizacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `Organizacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tematica`
--

DROP TABLE IF EXISTS `Tematica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Tematica` (
  `NombreTematica` varchar(100) NOT NULL,
  `IDTematicaPrincipal` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`NombreTematica`),
  KEY `IDTematicaPrincipal` (`IDTematicaPrincipal`),
  CONSTRAINT `Tematica_ibfk_1` FOREIGN KEY (`IDTematicaPrincipal`) REFERENCES `Tematica` (`NombreTematica`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tematica`
--

LOCK TABLES `Tematica` WRITE;
/*!40000 ALTER TABLE `Tematica` DISABLE KEYS */;
INSERT INTO `Tematica` VALUES ('LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA',NULL),('LT2: Cambio Global: interacción bosque, suelo y recursos hídricos',NULL),('LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA',NULL),('Geotermia y sistemas hidrotermales','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Mineralogía y Petrología','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Paleontología y Sedimentología','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Patrimonio Geológico','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Procesos de remoción en masa','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Tectónica y peligro sísmico','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Volcanología y peligro volcánico','LT1: EVOLUCIÓN Y HERENCIA GEOLÓGICA'),('Bosques templados, ecología y dinámica','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Cambio climático, perturbaciones naturales y antrópicas','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Fertilidad, química y biología del suelo','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Glaciares y recursos hídricos','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Historia evolutiva de la flora y la fauna','LT2: Cambio Global: interacción bosque, suelo y recursos hídricos'),('Conflictos socioambientales','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Desarrollo local y gobernanza','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Educación','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Historia y territorialidades','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA'),('Prácticas bioculturales','LT3: MODOS DE VIDA Y HABITAR DE MONTAÑA');
/*!40000 ALTER TABLE `Tematica` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-29 10:00:19
