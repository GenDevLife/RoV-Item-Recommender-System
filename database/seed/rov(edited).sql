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
INSERT INTO `heroes` VALUES 
('H001','Yue','Mage','','Mid','','Ranged'),
('H002','Aya','Support','','Support','','Ranged'),
('H003','Tachi','Fighter','','Dark Slayer','Farm','Melee');
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
INSERT INTO `heroskills` VALUES 
('S001','H001','Borrowed Might','Passive','Gains a mark next skill usage is upgraded, and cooldowns are reset','Magic','','',''),
('S002','H001','Aqua Force','Magic','Deals magic damage in a curved pattern','Magic','','','');
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
INSERT INTO `herostats` VALUES 
('H001',1,169,3475,140,0,0,45,18,0,15,490,50,0,360,18,18,0,0),
('H001',2,178,3742,158,0.01,0,46,21,0,18,597,63,0,360,19,21,0,0),
('H002',1,170,3558,130,0,0,55,0,0,15,470,80,0,360,17,0,0,0);
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
INSERT INTO `itemcomposition` VALUES 
('I006','I001',1),
('I007','I001',1),
('I007','I002',1);
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
INSERT INTO `items` VALUES ('I001','Short Sword','Attack',250,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I002','Dagger','Attack',290,0,0,0,0.2,0,0,0,0,0,0,0,0,0,0,0,0,0),('I003','Gloves','Attack',300,0,0,0,0,0.08,0,0,0,0,0,0,0,0,0,0,0,0),('I004','Bloodied Club','Attack',410,10,0,0,0,0,0,0,0.08,0,0,0,0,0,0,0,0,0),('I005','Chain Hammer','Attack',450,40,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I006','Cleaving Claymore','Attack',910,80,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I007','Arcane Hammer','Attack',740,25,0,0,0.15,0,0,0,0,0,0,0,0,0,0,0,0,0),('I008','Tempest Blades','Attack',780,0,0,0,0.25,0,0,0,0,0,0,0,0,0.05,0,0,0,0),('I009','Astral Spear','Attack',830,50,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I010','Shuriken','Attack',750,0,0,0,0.2,0,0,0,0,0,0,0,0,0,0,0,0,0),('I011','Chaos Bow','Attack',110,40,0,0,0.1,0,0,0,0,0,0,0,0,0,0,0,0,0),('I012','Uriel\'s Brand','Attack',2020,60,0,0,0.25,0,0,0,0,0,0,180,0,0,0,0,0,0),('I013','Curse of Death','Attack',1900,80,800,0,0,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I014','Death Sickle','Attack',2000,60,0,0,0,0,0,0,0,0,0,0,0.05,0,0,0,0,0),('I015','Bow of Slaughter','Attack',2250,90,0,0,0,0.1,0,0,0.1,0,0,0,0,0,0,0,0,0),('I016','The Diminisher','Attack',2120,100,0,0,0,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I017','The Morning Star','Attack',2980,50,0,0,0.3,0.1,0,0,0,0,0,0,0,0,0,0,0,0),('I018','Spear of Longinus','Attack',2030,80,500,0,0,0,0,0,0,0,0,0,0.15,0,0,0,0,0),('I019','Fafnir\'s Talon','Attack',2040,60,0,0,0.3,0,0,0,0,0,0,0,0,0,0,0,0,0),('I020','Claves Sancti','Attack',2120,100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I021','Muramasa','Attack',2020,75,0,0,0,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I022','The Beast','Attack',1740,100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I023','Omni Arms','Attack',2150,70,600,0,0.15,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I024','Slikk\'s String','Attack',1920,0,0,0,0.35,0.25,0,0,0,0,0,0,0,0.07,0,0,0,0),('I025','Fenrir\'s Tooth','Attack',2950,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I026','Blitz Blade','Attack',1900,0,0,0,0.35,0.15,0,0,0,0,0,0,0,0.05,0,0,0,0),('I027','Ifrit\'s Claw','Attack',1960,0,0,0,0.3,0.2,0,0,0,0,0,0,0,0.05,0,0,0,0),('I028','Broken Spears','Attack',1900,110,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I029','Eclipsing Bow','Attack',2000,0,0,0,0.3,0.1,0,0,0,0,0,0,0,0.05,0,0,0,0),('I030','Ring of Vitality','Defense',300,0,300,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I031','Light Armor','Defense',220,0,0,90,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I032','Gladitor Gauntlets','Defense',220,0,0,0,0,0,0,0,0,0,0,90,0,0,0,0,0,0),('I033','Tailsman of Strenght','Defense',140,0,0,0,0,0,30,0,0,0,0,0,0,0,0,0,0,0),('I034','Necklace of Vitality','Defense',540,0,600,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I035','Greaves of Protection','Defense',900,0,1000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I036','Heart of Incubus','Defense',720,0,0,150,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I037','Belt of Clarity','Defense',1000,0,700,0,0,0,0,0,0,0,0,110,0,0,0,0,0,0),('I038','Platinum Gauntlets','Defense',660,0,0,110,0,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I039','Knight\'s Plate','Defense',730,0,0,210,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I040','Mail of Pain','Defense',1940,0,1200,300,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I041','Hercules\' Madness','Defense',2080,80,0,180,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I042','Odin\'s Will','Defense',1900,0,1200,225,0,0,0,0,0,0,0,0,0,0.05,0,0,0,0),('I043','Mantle of Ra','Defense',1900,0,1000,225,0,0,60,0,0,0,0,0,0,0,0,0,0,0),('I044','Shield of the Lost','Defense',2100,0,1200,275,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I045','The Aegis','Defense',2180,0,0,360,0,0,0,0,0,0,400,0,0.2,0,0,0,0,0),('I046','Gaia\'s Standard','Defense',1960,0,1200,0,0,0,0,0,0,0,0,200,0,0.05,0,0,0,0),('I047','Medallion of Troy','Defense',2320,0,1000,0,0,0,0,0,0,0,0,200,0.1,0,0,0,0,0),('I048','Hyoga\'s Edge','Defense',1920,0,1200,100,0,0,0,0,0,0,0,100,0,0,0,0,0,0),('I049','Blade of Eternity','Defense',2400,0,0,120,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I050','Frost Cape','Defense',1970,0,800,200,0,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I051','Amulet of Longevity','Defense',1980,0,2000,0,0,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I052','Rock Shield','Defense',1980,0,1000,240,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I053','Spell Tome','Magic',300,0,0,0,0,0,0,0,0,40,0,0,0,0,0,0,0,0),('I054','Lapis Ring','Magic',220,0,0,0,0,0,0,0,0,0,300,0,0,0,0,0,0,0),('I055','Pendant of Faith','Magic',120,0,0,0,0,0,0,0,0,0,0,0,0,0,10,0,0,0),('I056','Ancient Scriptures','Magic',540,0,0,0,0,0,0,0,0,80,0,0,0,0,0,0,0,0),('I057','Magic Ring','Magic',300,0,0,0,0,0,0,0,0,0,0,0,0.05,0,0,0,0,0),('I058','Enchanted Scroll','Magic',820,0,0,0,0,0,0,0,0,120,0,0,0,0,0,0,0,0),('I059','Trick Blade','Magic',820,0,0,0,0,0,0,0,0,40,0,0,0.1,0,0,0,0,0),('I060','Spoonky Mask','Magic',960,0,0,0,0,0,0,0,0,100,0,0,0,0,0,0,0,0),('I061','Phoenix Tear','Magic',500,0,0,0,0,0,0,0,0,50,0,0,0,0,0,0,0,0),('I062','Virtue\'s Bracelet','Magic',720,0,0,0,0,0,0,0,0,60,0,0,0.05,0,20,0,0,0),('I063','Vlad\'s Impaler','Magic',900,0,0,0,0,0,0,0,0,60,0,0,0.05,0,0,0,0,0),('I064','Staff of Nuul','Magic',2050,0,0,0,0,0,0,0,0,180,0,0,0.1,0,0,0,0,0),('I065','Evil Secrets','Magic',1980,0,0,0,0,0,0,0,0,180,0,0,0,0,0,0,0,0),('I066','Soul Scroll','Magic',1900,0,600,0,0,0,0,0,0,140,0,0,0.1,0,0,0,0,0),('I067','Virtue\'s Necklace','Magic',1800,0,0,0,0,0,0,0,0,160,0,0,0.15,0,25,0,0,0),('I068','Orrery','Magic',800,0,0,0,0,0,0,0,0,80,0,0,0,0,0,0,0,0),('I069','Boomstick','Magic',1800,0,0,0,0,0,0,0,0,200,0,0,0,0.05,0,0,0,0),('I070','Hecate\'s Diadem','Magic',2400,0,0,0,0,0,0,0,0,240,0,0,0,0,0,0,0,0),('I071','Orb of the Magi','Magic',1900,0,0,0,0,0,0,0,0,140,0,0,0.1,0,0,0,0,0),('I072','Rhea\'s Blessing','Magic',2050,0,600,0,0,0,0,0,0,140,0,0,0.1,0,0,0,0,0),('I073','Zewihander','Magic',1900,0,0,0,0.2,0,0,0,0,180,0,0,0,0.05,0,0,0,0),('I074','Frosty Revenge','Magic',2020,0,850,0,0,0,0,0,0,140,0,0,0,0.05,0,0,0,0),('I075','Berith\'s Agony','Magic',1800,0,600,0,0,0,0,0,0,140,0,0,0.1,0,0,0,0,0),('I076','Apocalypse','Magic',1900,0,0,0,0,0,0,0,0,180,0,0,0.1,0.05,0,0,0,0),('I077','Soring Aura','Magic',2100,0,600,0,0,0,0,0,0,140,0,0,0.1,0,0,0,0,0),('I078','Holy of Holies','Magic',2990,0,0,0,0,0,0,0,0,400,0,0,0,0,0,0,0,0),('I079','Arctic Orbs','Magic',2200,0,0,0,0,0,0,0,0,240,0,0,0,0,0,0,0,0),('I080','Frostguard','Magic',2100,0,600,0,0,0,0,0,0,140,0,0,0.05,0,0,0,0,0),('I081','Boots of Speed','Movement',250,0,0,0,0,0,0,0,0,0,0,0,0,30,0,0,0,0),('I082','Sonic Boots','Movement',700,0,0,110,0,0,0,0,0,0,0,0,0,60,0,0,0,0),('I083','Gilded Greaves','Movement',700,0,0,0,0,0,0,0,0,0,0,90,60,0,0,0,0,0.35),('I084','Flashy Boots','Movement',700,0,0,0,0,0,0,0,0,0,0,0,0.15,60,0,0,0,0),('I085','Enchanted Kicks','Movement',700,0,0,0,0,0,0,0,0,0,0,0,0,60,0,0,0,0),('I086','War Boots','Movement',700,0,0,0,0.25,0,0,0,0,0,0,0,0,60,0,75,0,0),('I087','Hermes\'s Select','Movement',700,0,0,0,0,0,0,0,0,0,0,0,0,60,0,0,0,0),('I088','Elemental Stone','Support',300,0,0,0,0,0,0,0,0,0,0,0,0,0.05,0,0,0,0),('I089','Earth Gem','Support',900,0,400,0,0,0,0,0,0,0,0,0,0.05,0.05,0,0,0,0),('I090','Fire Gem','Support',900,20,0,0,0,0,0,0,0,0,0,0,0.05,0.05,0,0,0,0),('I091','Mother Earth: Barrier','Support',1600,0,400,0,0,0,0,0,0,0,0,0,0.1,0.05,0,0,0,0),('I092','Mother Earth: Magic Eye','Support',1600,0,400,0,0,0,0,0,0,0,0,0,0.1,0.05,0,0,0,0),('I093','Mother Earth: Accelerate','Support',1600,0,400,0,0,0,0,0,0,0,0,0,0.1,0.05,0,0,0,0),('I094','Mother Earth: Cleansing','Support',1600,0,400,0,0,0,0,0,0,0,0,0,0.1,0.05,0,0,0,0),('I095','Mother Earth: Rejuvenate','Support',1600,0,400,0,0,0,0,0,0,0,0,0,0.1,0.05,0,0,0,0),('I096','Wildfire: Barrier','Support',1600,0,600,0,0.05,0,0,0,0,0,0,0,0,0,0,0,0,0),('I097','Wildfire: Magic Eye','Support',1600,0,600,0,0.05,0,0,0,0,0,0,0,0,0,0,0,0,0),('I098','Wildfire: Accelerate','Support',1600,0,600,0,0.05,0,0,0,0,0,0,0,0,0,0,0,0,0),('I099','Wildfire: Cleansing','Support',1600,0,600,0,0.05,0,0,0,0,0,0,0,0,0,0,0,0,0),('I100','Wildfire: Rejuvenate','Support',1600,0,600,0,0.05,0,0,0,0,0,0,0,0,0,0,0,0,0),('I101','Hunter\'s Knife','Jungle',250,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I102','Monster\'s Bane','Jungle',750,0,0,0,0,0,0,0,0,40,0,0,0,0,0,0,0,0),('I103','Gnoll Cleaver','Jungle',750,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I104','Mr. Stabby','Jungle',750,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I105','Stormy Bow','Jungle',750,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I106','Loki\'s Curse','Jungle',1750,0,0,0,0,0,0,0,0,140,0,0,0.1,0,0,0,0,0),('I107','Leviathan','Jungle',1750,0,600,120,0,0,0,0,0,0,0,0,0,0,0,0,0,0),('I108','Soulreaver','Jungle',1750,80,0,0,0,0,0,0,0,0,0,0,0.1,0,0,0,0,0),('I109','FireStorm Bow','Jungle',1750,30,0,0,0.2,0,0,0,0.1,0,0,0,0,0,0,0,0,0);
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

-- Dump completed on 2025-04-11 14:52:04
