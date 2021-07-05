import cimpyorm as cpo
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
schema = cpo.Schema()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/class/{name}")
def class_(request: Request, name: str):
    try:
        class_ = vars(schema.model.classes)[name]
    except KeyError:
        return None
    return templates.TemplateResponse("classes.html", 
    {"request": request, "table": class_.to_html(
        classes=("table", "table-striped"))})


@app.get("/classes")
def all_classes():
    return [
        {
            "name": c.name,
            "namespace": c.namespace.short
        }
        for c in schema.class_hierarchy()]


@app.get("/classes/{classname}")
async def get_class(classname: str):
    """
    Returns the properties of a class.

    :param classname: The class to return
    """
    try:
        c = vars(schema.model)[classname]
        sc = c._schema_class
    except KeyError:
        return "No such element"

    return {
        "name": sc.name,
        "parent": sc.parent.name if sc.parent is not None else None,
        "properties": list(sc.all_props.keys())
    }


@app.get("/hierarchy")
def default_hierarchy():
    return hierarchy("IdentifiedObject")


@app.get("/hierarchy/{start}")
def hierarchy(start: str):
    start = vars(schema.model.classes)[start]
    res = _recurse_hierarchy(start)
    return res


def _recurse_hierarchy(node):
    _r = {}
    try:
        _r["properties"] = [p.name for p in node.props]
    except AttributeError:
        print(node)
    _r["children"] = {}
    for child in node.children:
        _r["children"][child.name] = _recurse_hierarchy(child)
    _r["children"] = {key: value for key, value in sorted(_r["children"].items())}
    return _r
