insert into Usuarios(nombres, surnames, email, password) values ('Antony', 'Ruano', 'jruano@espol.edu.ec', '1234');

insert into Tareas(titulo, descripcion, fecha_limite, prioridad, id_usuario, id_estado) values
    ('Proyectos', 'Terminar los proyectos de la espol', '2024-08-19', 1, (select id from Usuarios where email like 'jruano%'), (select id from Estados where nombre='en progreso')),
    ('Proyecto de base de datos', 'Terminar las siguientes pantallas: \n\t - Tarea Individual\n\t - Dashboard\n\t - Export', '2024-08-05', 1, (select id from Usuarios where email like 'jruano%'), (select id from Estados where nombre='en progreso')),
    ('Proyecto de matematicas discretas', 'Investigar el algoritmo de Floyd Warshall, aplicado a redes de transporte', '2024-08-11', 1, (select id from Usuarios where email like 'jruano%'), (select id from Estados where nombre='pendiente')),
    ('Proyecto de computación y sociedad', 'Que materia más castrosa.', '2024-08-11', 1, (select id from Usuarios where email like 'jruano%'), (select id from Estados where nombre='pendiente')),
    ('Proyecto de comunicación', 'Prepararse para la exposición y hacer las diapositivas.', '2024-08-10', 1, (select id from Usuarios where email like 'jruano%'), (select id from Estados where nombre='pendiente')),
    ('Proyecto de OOP', 'Implementar tipos de datos custom en el parser.', '2024-08-09', 1, (select id from Usuarios where email like 'jruano%'), (select id from Estados where nombre='en progreso'));

insert into Subtareas(id_tarea, id_subtarea) values
    ((select id from Tareas where titulo='Proyectos'), (select id from Tareas where titulo='Proyecto de base de datos')),
    ((select id from Tareas where titulo='Proyectos'), (select id from Tareas where titulo='Proyecto de matematicas discretas')),
    ((select id from Tareas where titulo='Proyectos'), (select id from Tareas where titulo='Proyecto de computación y sociedad')),
    ((select id from Tareas where titulo='Proyectos'), (select id from Tareas where titulo='Proyecto de comunicación')),
    ((select id from Tareas where titulo='Proyectos'), (select id from Tareas where titulo='Proyecto de OOP'));