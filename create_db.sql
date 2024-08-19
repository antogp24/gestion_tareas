-- create database gestion_tareas;
-- use gestion_tareas;

create table Usuarios(
	id integer primary key,
	nombres varchar(50) not null,
	surnames varchar(50) not null,
	email varchar(50) not null,
	password varchar(50) not null
);

create table Informes(
	id integer primary key,
	nombre varchar(50) not null,
	apellidos varchar(50) not null,
	fecha_creacion date not null
);

create table Estados(
	id integer primary key,
	nombre varchar(50) not null check(nombre in ('pendiente', 'en progreso', 'completada'))
);

insert into Estados values (1, 'pendiente'), (2, 'en progreso'), (3, 'completada');

create table Tareas(
	id integer primary key,
	titulo varchar(50) not null,
	descripcion varchar(1024) not null,
	fecha_limite date not null,
	prioridad integer not null,
	id_usuario integer,
	id_estado integer,
	foreign key (id_usuario) references Usuarios(id),
	foreign key (id_estado) references Estados(id)
);

create table Subtareas(
	id_tarea integer,
	id_subtarea integer,
	foreign key (id_tarea) references Tareas(id),
	foreign key (id_subtarea) references Tareas(id)
);

create table Recordatorio(
	id integer primary key,
	descripcion varchar(1024) not null,
	fecha date not null,
	id_tarea integer,
	foreign key (id_tarea) references Tareas(id)
);

