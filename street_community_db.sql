-- Host: 127.0.0.1    Database: street_community_db
-- ------------------------------------------------------

CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
)

INSERT INTO `admins` VALUES (1,'admin','admin'),(3,'a','scrypt:32768:8:1$UaV7x5cSl5giZBaI$12cede560d2b2079aee1f917d8dd3ed4f1798f5274ba79cfe395b814a1150e1565489f875dbf1f73d565612e512b5f59c269f1e31639ae74671b4090ef017962');

CREATE TABLE `grievances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `status` enum('Pending','Resolved','Rejected') DEFAULT 'Pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `street_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `fk_street_id` (`street_id`),
  CONSTRAINT `fk_street_id` FOREIGN KEY (`street_id`) REFERENCES `streets` (`id`) ON DELETE SET NULL,
  CONSTRAINT `grievances_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
)

INSERT INTO `grievances` VALUES (1,5,'power issues ','power issues ','Resolved','2024-10-19 10:11:51',1),(2,5,'test','123','Pending','2024-10-20 06:28:13',1);

CREATE TABLE `maid_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `status` enum('pending','verified','rejected') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `maid_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)

INSERT INTO `maid_requests` VALUES (1,9,'verified','2024-10-19 10:11:51');

CREATE TABLE `maids` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `email` varchar(100) NOT NULL,
  `street_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `street_id` (`street_id`),
  CONSTRAINT `maids_ibfk_1` FOREIGN KEY (`street_id`) REFERENCES `streets` (`id`)
)

INSERT INTO `maids` VALUES (1,'qw','qw','qw@g',1),(2,'12','123','1@gmail.com',1),(3,'12','12','12@gmail.com',1),(4,'12','12','12@gmail.com',1),(5,'12','1','user@gmail.com',5);

CREATE TABLE `shops` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `street_name` varchar(255) DEFAULT 'Unknown',
  `street_id` int DEFAULT NULL,
  `shop_image` varchar(255) DEFAULT NULL,
  `shop_map_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_street` (`street_id`),
  CONSTRAINT `fk_street` FOREIGN KEY (`street_id`) REFERENCES `streets` (`id`)
)

INSERT INTO `shops` VALUES (3,'The Dreaming Tree Restaurant','test','Street 1',1,'Screenshot_2024-10-20_113741.png','https://maps.app.goo.gl/Tca24zUiabvcYLxj8');

CREATE TABLE `streets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `street_name` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`,`street_name`)
)

INSERT INTO `streets` VALUES (1,'Street 1',''),(2,'Main Street',''),(3,'Second Street',''),(4,'Third Street',''),(5,'Fourth Street',''),(6,'Fifth Street','');

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(255) NOT NULL,
  `age` int NOT NULL,
  `gender` enum('Male','Female','Other') NOT NULL,
  `id_proof` varchar(255) NOT NULL,
  `street_name` varchar(255) NOT NULL,
  `user_type` enum('Member','MaidMember') NOT NULL,
  `password` varchar(255) NOT NULL,
  `verified` tinyint(1) DEFAULT '0',
  `street_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `fk_users_street` (`street_id`),
  CONSTRAINT `fk_users_street` FOREIGN KEY (`street_id`) REFERENCES `streets` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) 

INSERT INTO `users` VALUES (1,'jk','9787530075','jiyathf@gmail.com',21,'Male','uploads\\15335.jpg','Street 2','MaidMember','scrypt:32768:8:1$pM1b15BxKIeED10y$ce0a1c4351ddb1b746f52452aad76645c7ac4e96d91eee7dc6de3a1ab4bfdc899fbaa89577ec21feabb4231caca4ae4ec3bbe6123f44a6124ce5d8e9cb780ecf',1,NULL),(2,'123','123','1@gmail.com',123,'Male','uploads\\15335.jpg','Street 1','Member','scrypt:32768:8:1$kSNlvuXbn73A5jj6$7497d97771294823c4c560f7630a980823dfda0004421b1c499411afb5ea9367e4562792dca0fccdb31cb7a5a1490a44ac76bc081df4f0edddc009a4366e22e7',1,NULL),(3,'John Doe','1234567890','1@m.com',30,'Male','id_proof_john.pdf','Street 1','Member','scrypt:16:f0bd40d0a6bd76dbaf85904f1227f2f8$ef1f8d2c6654c1855e4da9952ca00bec7109649a73cc64e2d22f65d1b28636c8c9eb2175e179bacb203b471d6f8d841d2693f9f153aaff3be091d723b9ad245c',1,NULL),(4,'Jane Smith','0987654321','2@m.com',28,'Female','id_proof_jane.pdf','Street 2','Member','scrypt:16:723ec78d0408336a41e4e251fb5c7251$dd70022748ad7d99679226970ed9782ac6f940c42b57b4d1ecc6af5bcf79fb15cd3c6e34f5870c25242295fbd6bfac67e9dd83bd1fcf8f0288c0495e5b4fe196',1,NULL),(5,'Emily White','1112223333','3@m.com',25,'Female','id_proof_emily.pdf','Street 3','MaidMember','scrypt:16:bd0bec56c262df3b97606b32ac24c9ed$be3614b17a67c0cff4588d6c13c57b047194363eca4315b6e046ed3871c8861e4cd0bd93c6bdb425e765a713293ec89c7494bf1d70f00aeb0584734461ce618f',0,NULL),(6,'Michael Brown','4445556666','4@m.com',35,'Male','id_proof_michael.pdf','Street 1','MaidMember','scrypt:16:75a7e602999254f7c16ea1386d192eb7$37bb07ba3a1b24adcfe485a7fcc3ae940d0500074e0304530a00a5a12ae947bf39868f863c0d3f11b80adbefac298fbc1d64637725d9740315402913d3a6a10f',0,NULL),(7,'1','1','13@gmail.com',1,'Male','uploads\\15335.jpg','Street 1','Member','scrypt:32768:8:1$zjb9nv9xUPu9a9o9$c1987a3055b4f953e306798f7066a5cb7d59368a76a3dad13b448481aeea6dda04293bf10205cfe2b84ef35a3cf42dd1a3c4dd431e305aa956fb4aca02dd8d39',0,NULL),(8,'2','22','22@gmail.com',32,'Male','WhatsApp Image 2024-10-17 at 14.33.29_60120443.jpg','Street 1','Member','scrypt:32768:8:1$MDFYvbaE47dM5tPQ$a37d84fcac93df6fc690f7536f9a4cc7051cd09238705ed79329de84a5e900727d3990c42ae72243ed68c40808cb3988dff756e21fe369034a6ee5d6c1b180a8',0,1),(9,'maid','1','maid@gmail.com',45,'Male','logo (2).png','Street 1','MaidMember','scrypt:32768:8:1$bsSme7XgvlNqXvhW$06d8c089713827fa56c99e723bc820a89b1aa964be36cd19b4a8503346b8996f229999f5dd85a9186c14d4580535f7718cc39f66028df7c25253adf867797eb3',0,1),(10,'test','1234567890','test@gmail.com',32,'Male','WhatsApp Image 2024-10-17 at 14.33.29_60120443.jpg','Street 1','Member','scrypt:32768:8:1$G9yh8s60LWBSFRrD$f2840e27698ad4ceacb47efe77e3be0052ed63ee97d78587fc3e2a37e144f6464806bc2c3ba51ee1d5b17588d30e140a600864138b735d2a18964d0ffdc5a319',0,1);

CREATE TABLE `utilities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) NOT NULL,
  `status` varchar(20) DEFAULT 'Active',
  PRIMARY KEY (`id`)
)
