import sqlite3

conn = sqlite3.connect('biblioteca.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS libros (
    rfid TEXT PRIMARY KEY,
    titulo TEXT,
    apellido_autor TEXT,
    nombre_autor TEXT,
    area_conocimiento TEXT,
    publicador TEXT,
    tramo TEXT,
    estado TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE,
    libro_prestado TEXT,
    FOREIGN KEY (libro_prestado) REFERENCES libros(rfid)
)
''')

def agregar_libro():
    rfid = input("Ingrese el código del libro (RFID): ")
    titulo = input("Ingrese el título del libro: ")
    apellido_autor = input("Ingrese el apellido del autor: ")
    nombre_autor = input("Ingrese el nombre del autor: ")
    area_conocimiento = input("Ingrese el área de conocimiento: ")
    publicador = input("Ingrese el publicador: ")
    tramo = input("Ingrese el tramo asignado: ")
    
    c.execute('''
    INSERT INTO libros (rfid, titulo, apellido_autor, nombre_autor, area_conocimiento, publicador, tramo, estado)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (rfid, titulo, apellido_autor, nombre_autor, area_conocimiento, publicador, tramo, 'en sala'))
    
    conn.commit()
    print("Libro agregado exitosamente.")

def modificar_libro():
    rfid = input("Ingrese el código del libro (RFID) a modificar: ")
    c.execute('''
    SELECT * FROM libros WHERE rfid = ?
    ''', (rfid,))
    libro = c.fetchone()
    
    if libro:
        nuevo_titulo = input(f"Ingrese el nuevo título (anterior: {libro[1]}): ") or libro[1]
        nuevo_apellido_autor = input(f"Ingrese el nuevo apellido del autor (anterior: {libro[2]}): ") or libro[2]
        nuevo_nombre_autor = input(f"Ingrese el nuevo nombre del autor (anterior: {libro[3]}): ") or libro[3]
        nuevo_area_conocimiento = input(f"Ingrese la nueva área de conocimiento (anterior: {libro[4]}): ") or libro[4]
        nuevo_publicador = input(f"Ingrese el nuevo publicador (anterior: {libro[5]}): ") or libro[5]
        nuevo_tramo = input(f"Ingrese el nuevo tramo (anterior: {libro[6]}): ") or libro[6]
        nuevo_estado = input(f"Ingrese el nuevo estado (anterior: {libro[7]}): ") or libro[7]
        
        c.execute('''
        UPDATE libros
        SET titulo = ?, apellido_autor = ?, nombre_autor = ?, area_conocimiento = ?, publicador = ?, tramo = ?, estado = ?
        WHERE rfid = ?
        ''', (nuevo_titulo, nuevo_apellido_autor, nuevo_nombre_autor, nuevo_area_conocimiento, nuevo_publicador, nuevo_tramo, nuevo_estado, rfid))
        
        conn.commit()
        print("Libro modificado exitosamente.")
    else:
        print("Libro no encontrado.")

def listar_libros():
    c.execute('''
    SELECT * FROM libros
    ''')
    libros = c.fetchall()
    
    if not libros:
        print("No hay libros en la biblioteca.")
        return
    
    for libro in libros:
        print(f"RFID: {libro[0]}, Título: {libro[1]}, Apellido del Autor: {libro[2]}, Nombre del Autor: {libro[3]}, Área de Conocimiento: {libro[4]}, Publicador: {libro[5]}, Tramo: {libro[6]}, Estado: {libro[7]}")

def buscar_libro():
    rfid = input("Ingrese el código del libro (RFID) a buscar: ")
    c.execute('''
    SELECT * FROM libros WHERE rfid = ?
    ''', (rfid,))
    libro = c.fetchone()
    
    if libro:
        print(f"RFID: {libro[0]}, Título: {libro[1]}, Apellido del Autor: {libro[2]}, Nombre del Autor: {libro[3]}, Área de Conocimiento: {libro[4]}, Publicador: {libro[5]}, Tramo: {libro[6]}, Estado: {libro[7]}")
    else:
        print("Libro no encontrado.")

def eliminar_libro():
    rfid = input("Ingrese el código del libro (RFID) a eliminar: ")
    c.execute('''
    DELETE FROM libros WHERE rfid = ?
    ''', (rfid,))
    conn.commit()
    
    if c.rowcount > 0:
        print("Libro eliminado exitosamente.")
    else:
        print("Libro no encontrado.")

def cambiar_estado_libro():
    rfid = input("Ingrese el código del libro (RFID) para cambiar su estado: ")
    c.execute('''
    SELECT estado FROM libros WHERE rfid = ?
    ''', (rfid,))
    libro = c.fetchone()
    
    if libro:
        nuevo_estado = 'prestado' if libro[0] == 'en sala' else 'en sala'
        c.execute('''
        UPDATE libros SET estado = ? WHERE rfid = ?
        ''', (nuevo_estado, rfid))
        conn.commit()
        print(f"Estado del libro cambiado a {nuevo_estado}.")
    else:
        print("Libro no encontrado.")

def prestar_libro():
    nombre = input("Ingrese su nombre: ")
    rfid = input("Ingrese el código del libro (RFID) para préstamo: ")
    
    c.execute('''
    SELECT estado FROM libros WHERE rfid = ?
    ''', (rfid,))
    libro = c.fetchone()
    
    if libro:
        if libro[0] == 'en sala':
            c.execute('''
            SELECT id FROM estudiantes WHERE nombre = ?
            ''', (nombre,))
            estudiante = c.fetchone()
            
            if estudiante:
                estudiante_id = estudiante[0]
                c.execute('''
                UPDATE estudiantes SET libro_prestado = ? WHERE id = ?
                ''', (rfid, estudiante_id))
                conn.commit()
                c.execute('''
                UPDATE libros SET estado = 'prestado' WHERE rfid = ?
                ''', (rfid,))
                conn.commit()
                print("Libro prestado exitosamente.")
            else:
                c.execute('''
                INSERT INTO estudiantes (nombre, libro_prestado)
                VALUES (?, ?)
                ''', (nombre, rfid))
                conn.commit()
                c.execute('''
                UPDATE libros SET estado = 'prestado' WHERE rfid = ?
                ''', (rfid,))
                conn.commit()
                print("Libro prestado exitosamente y registro de estudiante creado.")
        else:
            print("El libro ya está prestado.")
    else:
        print("Libro no encontrado.")

def devolver_libro():
    nombre = input("Ingrese su nombre: ")
    
    c.execute('''
    SELECT libro_prestado FROM estudiantes WHERE nombre = ?
    ''', (nombre,))
    estudiante = c.fetchone()
    
    if estudiante:
        rfid = estudiante[0]
        if rfid:
            c.execute('''
            UPDATE libros SET estado = 'en sala' WHERE rfid = ?
            ''', (rfid,))
            conn.commit()
            c.execute('''
            UPDATE estudiantes SET libro_prestado = NULL WHERE nombre = ?
            ''', (nombre,))
            conn.commit()
            print("Libro devuelto exitosamente.")
        else:
            print("No hay libro prestado para este estudiante.")
    else:
        print("Estudiante no encontrado.")

def renovar_libro():
    nombre = input("Ingrese su nombre: ")
    
    c.execute('''
    SELECT libro_prestado FROM estudiantes WHERE nombre = ?
    ''', (nombre,))
    estudiante = c.fetchone()
    
    if estudiante:
        rfid = estudiante[0]
        if rfid:
            print("El libro ya está prestado. No se necesita renovar.")
        else:
            print("El libro no está prestado. No se puede renovar.")
    else:
        print("Estudiante no encontrado.")

def autoservicio():
    while True:
        print("\nAutoservicio")
        print("1. Préstamo de libro")
        print("2. Devolución de libro")
        print("3. Renovación de libro")
        print("4. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            prestar_libro()
        elif opcion == '2':
            devolver_libro()
        elif opcion == '3':
            renovar_libro()
        elif opcion == '4':
            break
        else:
            print("Opción no válida. Intente nuevamente.")

def administrador():
    while True:
        print("\nAdministrador")
        print("1. Agregar libro")
        print("2. Modificar libro")
        print("3. Listar libros")
        print("4. Buscar libro")
        print("5. Eliminar libro")
        print("6. Cambiar estado del libro")
        print("7. Mostrar lista de estudiantes")
        print("8. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            agregar_libro()
        elif opcion == '2':
            modificar_libro()
        elif opcion == '3':
            listar_libros()
        elif opcion == '4':
            buscar_libro()
        elif opcion == '5':
            eliminar_libro()
        elif opcion == '6':
            cambiar_estado_libro()
        elif opcion == '7':
            c.execute('''
            SELECT * FROM estudiantes
            ''')
            estudiantes = c.fetchall()
            
            if not estudiantes:
                print("No hay estudiantes registrados.")
            else:
                for estudiante in estudiantes:
                    print(f"ID: {estudiante[0]}, Nombre: {estudiante[1]}, Libro Prestado (RFID): {estudiante[2]}")
        elif opcion == '8':
            break
        else:
            print("Opción no válida. Intente nuevamente.")

def main():
    while True:
        print("\nSistema de Gestión de Biblioteca")
        print("1. Estudiante")
        print("2. Administrador")
        print("3. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            autoservicio()
        elif opcion == '2':
            administrador()
        elif opcion == '3':
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()

conn.close()
