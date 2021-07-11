import cimpyorm as cpo
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

schema = cpo.Schema()

cnames = schema.model.classes.__dict__
enumnames = schema.model.enum.__dict__
dtypenames = schema.model.dt.__dict__
typemap = \
    {**{name: "Class" for name in cnames.keys()},
    **{name: "Enumeration" for name in enumnames.keys()},
    **{name: "Datatype" for name in dtypenames.keys()},}
model = {**cnames, **enumnames, **dtypenames}

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})


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



@app.get("/details/{objectname}")
def details(request: Request, objectname: str):
    if objectname in model.keys():
        try: 
            table = model[objectname].to_html(
                index=False, 
                classes=("table", "table-striped", "table-sm", "table-hover"), 
                table_id="description")
            return templates.TemplateResponse("table.html", 
            {
                "request": request, 
                "objectname": objectname, 
                "category": typemap[objectname],
                "table": table
            })
        except AttributeError:
            return templates.TemplateResponse("description.html", 
            {
                "request": request, 
                "description": str(model[objectname])
            }
            )


@app.get("/show_table")
def show_table_empty(request: Request):
    pass


@app.get("/classes")
def classes(request: Request):
    return templates.TemplateResponse("objects.html", {"request": request, "cnames": sorted(cnames.keys())})

@app.get("/enums")
def enums(request: Request):
    return templates.TemplateResponse("objects.html", {"request": request, "cnames": sorted(enumnames.keys())})

@app.get("/dtypes")
def dtypes(request: Request):
    return templates.TemplateResponse("objects.html", {"request": request, "cnames": sorted(dtypenames.keys())})


@app.get("/objectnames")
def objectnames():
    return list(model.keys())



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


def test_dummy():
    pass
