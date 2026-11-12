import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from database import obtener_conexion, crear_tabla

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-en-tu-proyecto"

# ----- Configuración de las fotos -----
CARPETA_FOTOS = os.path.join(app.root_path, "static", "uploads")
os.makedirs(CARPETA_FOTOS, exist_ok=True)          # crea static/uploads si no existe
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # máximo 2 MB por foto
EXTENSIONES = {"png", "jpg", "jpeg", "gif", "webp"}

# Crea la tabla al iniciar la aplicación.
crear_tabla()


def guardar_foto(archivo):
    """Guarda la foto con un nombre único y devuelve ese nombre (o None)."""
    if not archivo or archivo.filename == "":
        return None
    extension = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if extension not in EXTENSIONES:
        return None
    nombre = f"{uuid.uuid4().hex}.{extension}"
    archivo.save(os.path.join(CARPETA_FOTOS, nombre))
    return nombre


def borrar_foto(nombre):
    """Elimina el archivo de la carpeta uploads si existe."""
    if nombre:
        ruta = os.path.join(CARPETA_FOTOS, nombre)
        if os.path.exists(ruta):
            os.remove(ruta)


@app.errorhandler(413)
def foto_muy_pesada(error):
    flash("La foto pesa demasiado (máximo 2 MB).")
    return redirect(url_for("inicio"))


# READ: mostrar todos los contactos
@app.route("/")
def inicio():
    conexion = obtener_conexion()
    contactos = conexion.execute(
        "SELECT * FROM contactos ORDER BY nombre"
    ).fetchall()
    conexion.close()
    return render_template("index.html", contactos=contactos)


# CREATE: guardar un contacto nuevo
@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip()
    categoria = request.form.get("categoria", "").strip()
    archivo = request.files.get("foto")

    if not nombre or not telefono or not categoria:
        flash("Completa los campos obligatorios.")
        return redirect(url_for("inicio"))

    foto = guardar_foto(archivo)
    if archivo and archivo.filename and not foto:
        flash("La foto debe ser PNG, JPG, GIF o WEBP.")
        return redirect(url_for("inicio"))

    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO contactos (nombre, telefono, correo, categoria, foto)
        VALUES (?, ?, ?, ?, ?)
        """,
        (nombre, telefono, correo, categoria, foto)
    )
    conexion.commit()
    conexion.close()
    flash("¡Contacto guardado correctamente!")
    return redirect(url_for("inicio"))


# UPDATE: editar un contacto existente
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexion = obtener_conexion()
    contacto = conexion.execute(
        "SELECT * FROM contactos WHERE id = ?", (id,)
    ).fetchone()

    if contacto is None:
        conexion.close()
        flash("El contacto no existe.")
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        archivo = request.files.get("foto")

        if not nombre or not telefono or not categoria:
            conexion.close()
            flash("Completa los campos obligatorios.")
            return redirect(url_for("editar", id=id))

        foto = contacto["foto"]                    # por defecto conserva la actual
        nueva = guardar_foto(archivo)
        if archivo and archivo.filename and not nueva:
            conexion.close()
            flash("La foto debe ser PNG, JPG, GIF o WEBP.")
            return redirect(url_for("editar", id=id))
        if nueva:                                  # reemplaza la foto anterior
            borrar_foto(foto)
            foto = nueva
        elif request.form.get("quitar_foto"):      # casilla "quitar foto"
            borrar_foto(foto)
            foto = None

        conexion.execute(
            """
            UPDATE contactos
            SET nombre = ?, telefono = ?, correo = ?, categoria = ?, foto = ?
            WHERE id = ?
            """,
            (nombre, telefono, correo, categoria, foto, id)
        )
        conexion.commit()
        conexion.close()
        flash("Contacto actualizado.")
        return redirect(url_for("inicio"))

    conexion.close()
    return render_template("form.html", contacto=contacto)


# DELETE: eliminar un contacto (y su foto)
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conexion = obtener_conexion()
    contacto = conexion.execute(
        "SELECT foto FROM contactos WHERE id = ?", (id,)
    ).fetchone()
    if contacto:
        borrar_foto(contacto["foto"])
    conexion.execute("DELETE FROM contactos WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    flash("Contacto eliminado.")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)