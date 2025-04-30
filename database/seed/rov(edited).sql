-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Apr 26, 2025 at 03:57 PM
-- Server version: 9.2.0
-- PHP Version: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rov`
--

-- --------------------------------------------------------

--
-- Table structure for table `heroes`
--

CREATE TABLE `heroes` (
  `HeroID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Hero_Name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `First_Class` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Second_Class` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `First_Lane` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Second_Lane` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Attack_Range` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `heroes`
--

INSERT INTO `heroes` (`HeroID`, `Hero_Name`, `First_Class`, `Second_Class`, `First_Lane`, `Second_Lane`, `Attack_Range`) VALUES
('H001', 'Yue', 'Mage', '', 'Mid', '', 'Ranged'),
('H002', 'Aya', 'Support', '', 'Support', '', 'Ranged'),
('H003', 'Tachi', 'Fighter', '', 'Dark Slayer', 'Farm', 'Melee'),
('H004', 'Bright', 'Fighter', '', 'Farm', 'Dark Slayer', 'Ranged'),
('H005', 'Lorion', 'Mage', '', 'Mid', '', 'Ranged'),
('H006', 'Iggy', 'Mage', '', 'Mid', '', 'Ranged');

-- --------------------------------------------------------

--
-- Table structure for table `heroskills`
--

CREATE TABLE `heroskills` (
  `SkillID` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `HeroID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `SkillName` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `SkillType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Effect` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `RecommendItemType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `heroskills`
--

INSERT INTO `heroskills` (`SkillID`, `HeroID`, `SkillName`, `SkillType`, `Effect`, `RecommendItemType`) VALUES
('S001', 'H001', 'Borrowed Might	', 'Passive', 'Gains a mark next skill usage is upgraded, and cooldowns are reset', 'Magic'),
('S002', 'H001', 'Aqua Force	', 'Magic', 'Deals magic damage in a curved pattern', 'Magic'),
('S003', 'H001', 'Mountain Crusher	', 'Magic', 'Deals magic damage in a curved pattern', 'Magic'),
('S004', 'H001', 'Rising Wind	', 'Magic', 'Knocks back enemies in front while retreating', 'Magic'),
('S005', 'H002', 'Squirrel Spirit	', 'Transform', 'Becomes untargetable when HP is low	', 'Defense, Support'),
('S006', 'H002', 'Sound Breaker	', 'Magic', 'Deals magic damage and slows enemies	', 'Magic'),
('S007', 'H002', 'Idol Love	', 'Magic', 'Jumps onto an ally and grants a shield	', 'Defense');

-- --------------------------------------------------------

--
-- Table structure for table `herostats`
--

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
  `Resistance` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `herostats`
--

INSERT INTO `herostats` (`HeroID`, `Level`, `Phys_ATK`, `HP`, `Phys_Defense`, `Attack_Speed`, `Critical_Rate`, `HP_5_sec`, `Armor_Pierce`, `Life_Steal`, `Magic_Power`, `Max_Mana`, `Magic_Defense`, `Cooldown_Reduction`, `Movement_Speed`, `Mana_5_sec`, `Magic_Pierce`, `Magic_Life_Steal`, `Resistance`) VALUES
('H001', 1, 169, 3475, 140, 0, 0, 45, 18, 0, 15, 490, 50, 0, 360, 18, 18, 0, 0),
('H001', 2, 178, 3742, 158, 0.01, 0, 46, 21, 0, 18, 597, 63, 0, 360, 19, 21, 0, 0),
('H001', 3, 188, 4009, 177, 0.02, 0, 48, 24, 0, 21, 704, 77, 0, 360, 21, 24, 0, 0),
('H001', 4, 198, 4276, 196, 0.03, 0, 50, 27, 0, 24, 811, 90, 0, 360, 23, 27, 0, 0),
('H001', 5, 208, 4543, 215, 0.04, 0, 52, 30, 0, 27, 918, 104, 0, 360, 25, 30, 0, 0),
('H001', 6, 218, 4810, 234, 0.05, 0, 54, 33, 0, 30, 1025, 117, 0, 360, 27, 33, 0, 0),
('H001', 7, 228, 5077, 253, 0.06, 0, 56, 36, 0, 33, 1132, 130, 0, 360, 29, 36, 0, 0),
('H001', 8, 238, 5344, 272, 0.07, 0, 58, 39, 0, 36, 1239, 144, 0, 360, 31, 39, 0, 0),
('H001', 9, 247, 5611, 290, 0.08, 0, 59, 42, 0, 39, 1346, 157, 0, 360, 32, 42, 0, 0),
('H001', 10, 257, 5878, 309, 0.09, 0, 61, 45, 0, 42, 1453, 171, 0, 360, 34, 45, 0, 0),
('H001', 11, 267, 6145, 328, 0.1, 0, 63, 48, 0, 45, 1560, 184, 0, 360, 36, 48, 0, 0),
('H001', 12, 277, 6412, 347, 0.11, 0, 65, 51, 0, 48, 1667, 198, 0, 360, 38, 51, 0, 0),
('H001', 13, 287, 6679, 366, 0.12, 0, 67, 54, 0, 51, 1774, 211, 0, 360, 40, 54, 0, 0),
('H001', 14, 296, 6946, 384, 0.13, 0, 68, 57, 0, 54, 1881, 225, 0, 360, 41, 57, 0, 0),
('H001', 15, 306, 7213, 403, 0.14, 0, 70, 60, 0, 57, 1988, 238, 0, 360, 43, 60, 0, 0),
('H002', 1, 170, 3558, 130, 0, 0, 55, 0, 0, 15, 470, 80, 0, 360, 17, 0, 0, 0),
('H002', 2, 180, 3813, 150, 0.01, 0, 57, 0, 0, 18, 574, 93, 0, 360, 18, 0, 0, 0),
('H002', 3, 191, 4069, 170, 0.02, 0, 60, 0, 0, 21, 678, 107, 0, 360, 20, 0, 0, 0),
('H002', 4, 202, 4325, 190, 0.03, 0, 63, 0, 0, 24, 782, 120, 0, 360, 22, 0, 0, 0),
('H002', 5, 213, 4581, 210, 0.04, 0, 66, 0, 0, 27, 886, 134, 0, 360, 24, 0, 0, 0),
('H002', 6, 224, 4837, 230, 0.05, 0, 69, 0, 0, 30, 990, 147, 0, 360, 26, 0, 0, 0),
('H002', 7, 235, 5093, 250, 0.06, 0, 72, 0, 0, 33, 1094, 160, 0, 360, 28, 0, 0, 0),
('H002', 8, 246, 5349, 270, 0.07, 0, 75, 0, 0, 36, 1198, 174, 0, 360, 30, 0, 0, 0),
('H002', 9, 256, 5604, 290, 0.08, 0, 77, 0, 0, 39, 1302, 187, 0, 360, 31, 0, 0, 0),
('H002', 10, 267, 5860, 310, 0.09, 0, 80, 0, 0, 42, 1406, 201, 0, 360, 33, 0, 0, 0),
('H002', 11, 278, 6116, 330, 0.1, 0, 83, 0, 0, 45, 1510, 214, 0, 360, 35, 0, 0, 0),
('H002', 12, 289, 6372, 350, 0.11, 0, 86, 0, 0, 48, 1614, 228, 0, 360, 37, 0, 0, 0),
('H002', 13, 300, 6628, 370, 0.12, 0, 89, 0, 0, 51, 1718, 241, 0, 360, 39, 0, 0, 0),
('H002', 14, 310, 6883, 390, 0.13, 0, 91, 0, 0, 54, 1822, 255, 0, 360, 40, 0, 0, 0),
('H002', 15, 321, 7139, 410, 0.14, 0, 94, 0, 0, 57, 1926, 268, 0, 360, 42, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `itemcomposition`
--

CREATE TABLE `itemcomposition` (
  `Composite_ItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `BaseItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Quantity` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `itemcomposition`
--

INSERT INTO `itemcomposition` (`Composite_ItemID`, `BaseItemID`, `Quantity`) VALUES
('I006', 'I001', 1),
('I007', 'I001', 1),
('I007', 'I002', 1),
('I008', 'I002', 1),
('I009', 'I001', 2),
('I010', 'I002', 2);

-- --------------------------------------------------------

--
-- Table structure for table `items`
--

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
  `Resistance` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `items`
--

INSERT INTO `items` (`ItemID`, `ItemName`, `Class`, `PassiveTag`, `EffectDesc`, `DamageRatioPhysical`, `DamageRatioMagic`, `Price`, `Phys_ATK`, `HP`, `Phys_Defense`, `Attack_Speed`, `Critical_Rate`, `HP_5_sec`, `Armor_Pierce`, `Life_Steal`, `Magic_Power`, `Max_Mana`, `Magic_Defense`, `Cooldown_Reduction`, `Movement_Speed`, `Mana_5_sec`, `Magic_Pierce`, `Magic_Life_Steal`, `Resistance`) VALUES
('I001', 'Short Sword', 'Attack', NULL, NULL, NULL, NULL, 250, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I002', 'Dagger', 'Attack', NULL, NULL, NULL, NULL, 290, 0, 0, 0, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I003', 'Gloves', 'Attack', NULL, NULL, NULL, NULL, 300, 0, 0, 0, 0, 0.08, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I004', 'Bloodied Club', 'Attack', NULL, NULL, NULL, NULL, 410, 10, 0, 0, 0, 0, 0, 0, 0.08, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I005', 'Chain Hammer', 'Attack', NULL, NULL, NULL, NULL, 450, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I006', 'Cleaving Claymore', 'Attack', NULL, NULL, NULL, NULL, 910, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I007', 'Arcane Hammer', 'Attack', NULL, NULL, NULL, NULL, 740, 25, 0, 0, 0.15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I008', 'Tempest Blades', 'Attack', NULL, NULL, NULL, NULL, 780, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0.05, 0, 0, 0, 0),
('I009', 'Astral Spear', 'Attack', NULL, NULL, NULL, NULL, 830, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I010', 'Shuriken', 'Attack', NULL, NULL, NULL, NULL, 750, 0, 0, 0, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('I011', 'Chaos Bow', 'Attack', NULL, NULL, NULL, NULL, 110, 40, 0, 0, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `item_effects`
--

CREATE TABLE `item_effects` (
  `ItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `EffectType` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Param1` float DEFAULT NULL,
  `Param2` float DEFAULT NULL,
  `Description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `item_effects`
--

INSERT INTO `item_effects` (`ItemID`, `EffectType`, `Param1`, `Param2`, `Description`) VALUES
('I007', 'Speed_Up', 10, NULL, 'เมื่อทำการโจมตีปกติ รับความเร็วเคลื่อนที่ +10%'),
('I010', 'Heel', 21, 35, 'การโจมตีปกติสร้างความเสียหายกายภาพเพิ่มขึ้น 21-35(ระยะใกล้)/42-70(ระยะไกล) CD 0.3 วินาที'),
('I011', 'Stab', 10, 2, 'เพิ่มเจาะเกราะ 10%(ฮีโร่ตีไกลได้รับผล 2 เท่า)'),
('I012', 'Savior\'s_Edge', 40, 600, 'เมื่อ HP ต่ำกว่า 40% จะสร้างโล่เวท(600-2000) เป็นเวลา 5 วิทนาที รวมถึงได้รับต้านสถานะ 25% และวิ่งเร็วขึ้น 30% เป็นเวลา 2 วินาที (CD 75 วินาที)'),
('I012', 'Speed_Up', 10, NULL, 'เมื่อทำการโจมตีปกติจะวิ่งเร็วขึ้น 10%'),
('I013', 'Soul_Prison', 40, 2, 'ลดการฟื้นฟูของเป้าหมายลง 40% เป็นเวลา 2 วินาที (หากความเสียหายมาจากการโจมตีปกติจะเพิ่มขึ้นเป็น 4 วินาทีแทน)'),
('I014', 'Divine_Intervention', 20, 1, 'อมตะเมื่อ HP ต่ำและวิ่งเร็วขึ้น 20% เป็นเวลา 1 วินาที CD 90 วินาที'),
('I015', '[Bloodthirst]', 60, 3, 'ดูดเลือดเพิ่มขึ้น 60% เป็นเวลา 3 วินาที(ระยะไกลเท่านั้น) CD 60 วินาที'),
('I016', 'Cripple', 30, 20, 'หากใช้สกิลฮีโร่ศัตรูตัวแรกที่โดนจะวิ่งช้าลง 30% และความเสียหายลดลง 20% เป็นเวลา 3 วินาที (CD: 8 วินาที)'),
('I016', '[Sturdy]', 40, 2, 'ลดความเสียหายที่ได้รับลง 40% เป็นเวลา 2 วินาที (สามารถใช้ได้ขณะถูกสถานะควบคุม) CD 90 วินาที');

-- --------------------------------------------------------

--
-- Table structure for table `item_passives`
--

CREATE TABLE `item_passives` (
  `ItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `PassiveTag` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `item_passives`
--

INSERT INTO `item_passives` (`ItemID`, `PassiveTag`) VALUES
('I108', ''),
('I018', 'Armor_Break'),
('I071', 'Bide'),
('I048', 'Biting_Cold'),
('I040', 'Blitz'),
('I016', 'Cripple'),
('I106', 'Curse_Power'),
('I017', 'Dawning_Star'),
('I028', 'Destroyer'),
('I014', 'Divine_Intervention'),
('I019', 'Dragon\'s_Breath');

-- --------------------------------------------------------

--
-- Table structure for table `item_synergy`
--

CREATE TABLE `item_synergy` (
  `SynergyGroup` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ItemID` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `BonusValue` float NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `item_synergy`
--

INSERT INTO `item_synergy` (`SynergyGroup`, `ItemID`, `BonusValue`) VALUES
('', 'I108', 60),
('Armor_Break', 'I018', 60),
('Barrier', 'I091', 680),
('Bide', 'I071', 30),
('Biting_Cold', 'I048', 25),
('Blitz', 'I040', 15),
('Cripple', 'I016', 30),
('Curse_Power', 'I106', 35),
('Dawning_Star', 'I017', 50),
('Destroyer', 'I028', 40),
('Divine_Intervention', 'I014', 20),
('Dragon\'s_Breath', 'I019', 8),
('Echo', 'I068', 180);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `heroes`
--
ALTER TABLE `heroes`
  ADD PRIMARY KEY (`HeroID`);

--
-- Indexes for table `heroskills`
--
ALTER TABLE `heroskills`
  ADD PRIMARY KEY (`SkillID`),
  ADD KEY `fk_heroskills_heroes` (`HeroID`);

--
-- Indexes for table `herostats`
--
ALTER TABLE `herostats`
  ADD PRIMARY KEY (`HeroID`,`Level`);

--
-- Indexes for table `itemcomposition`
--
ALTER TABLE `itemcomposition`
  ADD PRIMARY KEY (`Composite_ItemID`,`BaseItemID`),
  ADD KEY `BaseItemID` (`BaseItemID`);

--
-- Indexes for table `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`ItemID`);

--
-- Indexes for table `item_effects`
--
ALTER TABLE `item_effects`
  ADD PRIMARY KEY (`ItemID`,`EffectType`),
  ADD KEY `idx_effect_type` (`EffectType`);

--
-- Indexes for table `item_passives`
--
ALTER TABLE `item_passives`
  ADD PRIMARY KEY (`ItemID`,`PassiveTag`),
  ADD KEY `idx_passive_tag` (`PassiveTag`);

--
-- Indexes for table `item_synergy`
--
ALTER TABLE `item_synergy`
  ADD PRIMARY KEY (`SynergyGroup`,`ItemID`),
  ADD KEY `idx_synergy_item` (`ItemID`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `heroskills`
--
ALTER TABLE `heroskills`
  ADD CONSTRAINT `fk_heroskills_heroes` FOREIGN KEY (`HeroID`) REFERENCES `heroes` (`HeroID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `herostats`
--
ALTER TABLE `herostats`
  ADD CONSTRAINT `herostats_ibfk_1` FOREIGN KEY (`HeroID`) REFERENCES `heroes` (`HeroID`);

--
-- Constraints for table `itemcomposition`
--
ALTER TABLE `itemcomposition`
  ADD CONSTRAINT `itemcomposition_ibfk_1` FOREIGN KEY (`Composite_ItemID`) REFERENCES `items` (`ItemID`),
  ADD CONSTRAINT `itemcomposition_ibfk_2` FOREIGN KEY (`BaseItemID`) REFERENCES `items` (`ItemID`);

--
-- Constraints for table `item_effects`
--
ALTER TABLE `item_effects`
  ADD CONSTRAINT `fk_item_effects_item` FOREIGN KEY (`ItemID`) REFERENCES `items` (`ItemID`) ON DELETE CASCADE;

--
-- Constraints for table `item_passives`
--
ALTER TABLE `item_passives`
  ADD CONSTRAINT `fk_item_passives_item` FOREIGN KEY (`ItemID`) REFERENCES `items` (`ItemID`) ON DELETE CASCADE;

--
-- Constraints for table `item_synergy`
--
ALTER TABLE `item_synergy`
  ADD CONSTRAINT `fk_item_synergy_item` FOREIGN KEY (`ItemID`) REFERENCES `items` (`ItemID`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
