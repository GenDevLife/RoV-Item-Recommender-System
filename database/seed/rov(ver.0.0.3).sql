-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: rov
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `heroes`
--

DROP TABLE IF EXISTS `heroes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `heroes` (
  `HeroID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Hero_Name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `First_Class` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Second_Class` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `First_Lane` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Second_Lane` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Attack_Range` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`HeroID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `heroes`
--

LOCK TABLES `heroes` WRITE;
/*!40000 ALTER TABLE `heroes` DISABLE KEYS */;
INSERT INTO `heroes` VALUES ('H001','Yue','Mage','','Mid','','Ranged'),('H002','Aya','Support','','Support','','Ranged'),('H003','Tachi','Fighter','','Dark Slayer','Farm','Melee'),('H004','Bright','Fighter','','Farm','Dark Slayer','Ranged'),('H005','Lorion','Mage','','Mid','','Ranged'),('H006','Iggy','Mage','','Mid','','Ranged'),('H007','Allain','Fighter','','Dark Slayer','Farm','Melee');
/*!40000 ALTER TABLE `heroes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `heroskills`
--

DROP TABLE IF EXISTS `heroskills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `heroskills` (
  `SkillID` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `HeroID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `SkillName` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `SkillType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Effect` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `RecommendItemType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Column7` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Column8` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Column9` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`SkillID`),
  KEY `fk_heroskills_heroes` (`HeroID`),
  CONSTRAINT `fk_heroskills_heroes` FOREIGN KEY (`HeroID`) REFERENCES `heroes` (`HeroID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `heroskills`
--

LOCK TABLES `heroskills` WRITE;
/*!40000 ALTER TABLE `heroskills` DISABLE KEYS */;
INSERT INTO `heroskills` VALUES ('S001','H001','Borrowed Might	','Passive','Gains a mark next skill usage is upgraded, and cooldowns are reset','Magic','','',''),('S002','H001','Aqua Force	','Magic','Deals magic damage in a curved pattern','Magic','','',''),('S003','H001','Mountain Crusher	','Magic','Deals magic damage in a curved pattern','Magic','','',''),('S004','H001','Rising Wind	','Magic','Knocks back enemies in front while retreating','Magic','','',''),('S005','H002','Squirrel Spirit	','Transform','Becomes untargetable when HP is low	','Defense, Support','','','');
/*!40000 ALTER TABLE `heroskills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `herostats`
--

DROP TABLE IF EXISTS `herostats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `herostats` (
  `HeroID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Level` int NOT NULL,
  `Phys_ATK` float DEFAULT NULL,
  `HP` int DEFAULT NULL,
  `Phys_Defense` float DEFAULT NULL,
  `Attack_Speed` float DEFAULT NULL,
  `Critical_Rate` float DEFAULT NULL,
  `HP_5_sec` int DEFAULT NULL,
  `Armor_Pierce` float DEFAULT NULL,
  `Life_Steal` float DEFAULT NULL,
  `Magic_Power` float DEFAULT NULL,
  `Max_Mana` int DEFAULT NULL,
  `Magic_Defense` float DEFAULT NULL,
  `Cooldown_Reduction` float DEFAULT NULL,
  `Movement_Speed` float DEFAULT NULL,
  `Mana_5_sec` int DEFAULT NULL,
  `Magic_Pierce` float DEFAULT NULL,
  `Magic_Life_Steal` float DEFAULT NULL,
  `Resistance` float DEFAULT NULL,
  PRIMARY KEY (`HeroID`,`Level`),
  CONSTRAINT `herostats_ibfk_1` FOREIGN KEY (`HeroID`) REFERENCES `heroes` (`HeroID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `herostats`
--

LOCK TABLES `herostats` WRITE;
/*!40000 ALTER TABLE `herostats` DISABLE KEYS */;
INSERT INTO `herostats` VALUES ('H001',1,169,3475,140,0,0,45,18,0,15,490,50,0,360,18,18,0,0),('H001',2,178,3742,158,0.01,0,46,21,0,18,597,63,0,360,19,21,0,0),('H001',3,188,4009,177,0.02,0,48,24,0,21,704,77,0,360,21,24,0,0),('H001',4,198,4276,196,0.03,0,50,27,0,24,811,90,0,360,23,27,0,0),('H001',5,208,4543,215,0.04,0,52,30,0,27,918,104,0,360,25,30,0,0),('H001',6,218,4810,234,0.05,0,54,33,0,30,1025,117,0,360,27,33,0,0),('H001',7,228,5077,253,0.06,0,56,36,0,33,1132,130,0,360,29,36,0,0),('H001',8,238,5344,272,0.07,0,58,39,0,36,1239,144,0,360,31,39,0,0),('H001',9,247,5611,290,0.08,0,59,42,0,39,1346,157,0,360,32,42,0,0),('H001',10,257,5878,309,0.09,0,61,45,0,42,1453,171,0,360,34,45,0,0),('H001',11,267,6145,328,0.1,0,63,48,0,45,1560,184,0,360,36,48,0,0),('H001',12,277,6412,347,0.11,0,65,51,0,48,1667,198,0,360,38,51,0,0),('H001',13,287,6679,366,0.12,0,67,54,0,51,1774,211,0,360,40,54,0,0),('H001',14,296,6946,384,0.13,0,68,57,0,54,1881,225,0,360,41,57,0,0),('H001',15,306,7213,403,0.14,0,70,60,0,57,1988,238,0,360,43,60,0,0);
/*!40000 ALTER TABLE `herostats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `itemcomposition`
--

DROP TABLE IF EXISTS `itemcomposition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `itemcomposition` (
  `Composite_ItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `BaseItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Quantity` int DEFAULT NULL,
  PRIMARY KEY (`Composite_ItemID`,`BaseItemID`),
  KEY `BaseItemID` (`BaseItemID`),
  CONSTRAINT `itemcomposition_ibfk_1` FOREIGN KEY (`Composite_ItemID`) REFERENCES `items` (`ItemID`),
  CONSTRAINT `itemcomposition_ibfk_2` FOREIGN KEY (`BaseItemID`) REFERENCES `items` (`ItemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `itemcomposition`
--

LOCK TABLES `itemcomposition` WRITE;
/*!40000 ALTER TABLE `itemcomposition` DISABLE KEYS */;
INSERT INTO `itemcomposition` VALUES ('I006','I001',1),('I007','I001',1),('I007','I002',1),('I008','I002',1),('I009','I001',2),('I010','I002',2),('I011','I002',1),('I011','I005',1),('I012','I001',1),('I012','I007',1),('I012','I032',1),('I013','I006',1),('I013','I034',1),('I013','I057',1),('I014','I001',1),('I014','I005',1),('I015','I003',1),('I015','I004',1),('I015','I006',1),('I016','I006',1),('I016','I030',1),('I016','I057',1),('I017','I003',1),('I017','I010',1),('I017','I011',1),('I018','I009',1),('I018','I030',1),('I018','I057',1);
/*!40000 ALTER TABLE `itemcomposition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `ItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ItemName` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Class` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `PassiveTag` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `EffectDesc` text COLLATE utf8mb4_general_ci,
  `DamageRatioPhysical` float DEFAULT NULL,
  `DamageRatioMagic` float DEFAULT NULL,
  `Price` int DEFAULT NULL,
  `Phys_ATK` float DEFAULT NULL,
  `HP` int DEFAULT NULL,
  `Phys_Defense` float DEFAULT NULL,
  `Attack_Speed` float DEFAULT NULL,
  `Critical_Rate` float DEFAULT NULL,
  `HP_5_sec` int DEFAULT NULL,
  `Armor_Pierce` float DEFAULT NULL,
  `Life_Steal` float DEFAULT NULL,
  `Magic_Power` float DEFAULT NULL,
  `Max_Mana` int DEFAULT NULL,
  `Magic_Defense` float DEFAULT NULL,
  `Cooldown_Reduction` float DEFAULT NULL,
  `Movement_Speed` float DEFAULT NULL,
  `Mana_5_sec` int DEFAULT NULL,
  `Magic_Pierce` float DEFAULT NULL,
  `Magic_Life_Steal` float DEFAULT NULL,
  `Resistance` float DEFAULT NULL,
  PRIMARY KEY (`ItemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES ('I001','Short Sword','Attack',NULL,NULL,NULL,NULL,250,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I002','Dagger','Attack',NULL,NULL,NULL,NULL,290,0,0,0,0.2,0,0,0,0,0,0,0,0,0,0,0,0,0),('I003','Gloves','Attack',NULL,NULL,NULL,NULL,300,0,0,0,0,0.08,0,0,0,0,0,0,0,0,0,0,0,0),('I004','Bloodied Club','Attack',NULL,NULL,NULL,NULL,410,10,0,0,0,0,0,0,0.08,0,0,0,0,0,0,0,0,0),('I005','Chain Hammer','Attack',NULL,NULL,NULL,NULL,450,40,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I006','Cleaving Claymore','Attack',NULL,NULL,NULL,NULL,910,80,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I007','Arcane Hammer','Attack',NULL,NULL,NULL,NULL,740,25,0,0,0.15,0,0,0,0,0,0,0,0,0,0,0,0,0),('I008','Tempest Blades','Attack',NULL,NULL,NULL,NULL,780,0,0,0,0.25,0,0,0,0,0,0,0,0,0.05,0,0,0,0),('I009','Astral Spear','Attack',NULL,NULL,NULL,NULL,830,50,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'rov'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-22 10:57:27
