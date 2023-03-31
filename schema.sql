drop table if exists people, places;

create table `people` (
  `id_people` int not null auto_increment,
  `given_name` varchar(80) default null,
  `family_name` varchar(80) default null,
  `date_of_birth` datetime default null,
  `place_of_birth` varchar(80) default null,
  primary key (`id_people`)
);

create table `places` (
  `id_places` int not null auto_increment,
  `city` varchar(80) default null,
  `county` varchar(80) default null,
  `country` varchar(80) default null,
  primary key (`id_places`)
);
