from flask import Blueprint, render_template, abort, Response
import sass
import dartsass
import glob

scss_manager = Blueprint('scssmanager', '__name__')

@scss_manager.route("/static/scss/<filename>")
def hide_scss(filename):
    return abort(404)

files = {}

@scss_manager.route("/static/css/<filename>")
def return_scss(filename):
    content = files.get(filename)
    if content == None:
        return abort(404)
    
    response = Response(content, mimetype="text/css")
    return response

def compile_scss():
    for file in glob.glob("server/static/scss/*.scss"):
        filename = file.split("\\")[-1].replace(".scss", ".css")
        content = open(file, "r", encoding="utf-8").read()
        compiled = dartsass.compile(string=content, charset="utf-8")
        files[filename] = compiled