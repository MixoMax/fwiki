from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn

import json
import os
from tqdm import tqdm
import jsonlines

app = FastAPI()

json_path = "./jsons"

def build_index():
    index = {} # {char: {name: id}}
    # example:
    # index = {
    #     "a": {
    #         "aaron": 1,
    #         "abraham": 2
    #     },
    #     "b": {
    #         "bob": 3,
    #         "billy": 4
    #     }
    # }

    for file in tqdm(os.listdir("./index")):
        os.remove(f"./index/{file}")


    for file in tqdm(os.listdir(json_path)):

        data = json.load(open(f"{json_path}/{file}", "r", encoding="utf-8"))

        id = data["id"]
        title = data["title"]

        char = title[0].lower()

        if char not in index:
            index[char] = {}
        
        index[char][title] = id
    

    # save as ./index/{char}.json
    if not os.path.exists("index"):
        os.mkdir("index")
    
    for char in tqdm(index):
        with open(f"./index/{char}.json", "w", encoding="utf-8") as f:
            json.dump(index[char], f, ensure_ascii=False, indent=4)
        


def get_file_id(name: str) -> int:
    char = name[0].lower()
    if not os.path.exists(f"./index/{char}.json"):
        return -1
    
    index = json.load(open(f"./index/{char}.json", "r", encoding="utf-8"))
    if name not in index:
        return -1
    
    return int(index[name])


def search(name: str, limit: int) -> list[dict[int, str]]:
    result = []

    name = name.lower()

    for file in tqdm(os.listdir("./index")):
        with open(f"./index/{file}", "r", encoding="utf-8") as f:
            index = json.load(f)
            
            for key in index:
                if name in key.lower():
                    id = int(index[key])
                    result.append({
                        "id": id,
                        "name": key
                    })
                    if len(result) >= limit:
                        return result

    
    return result





@app.get("/search")
def search_api(q: str, limit: int = 100) -> JSONResponse:
    result = search(q, limit)
    print(len(result))
    return JSONResponse(content=result)


@app.get("/get")
def get_api(name: str) -> JSONResponse:
    id = get_file_id(name)
    if id == -1:
        return JSONResponse(content={"error": "not found"})
    
    return FileResponse(f"{json_path}/{id}.json")



@app.get("/{name}")
def get_html(name: str) -> HTMLResponse:
    with open("./index.html", "r", encoding="utf-8") as f:
        base_html = f.read()
    
    article_id = get_file_id(name)
    if article_id == -1:
        article = {
            "title": "Not Found",
            "text": "The article you are looking for is not found."
        }


    else:
        article = json.load(open(f"{json_path}/{article_id}.json", "r", encoding="utf-8"))
    
    
    base_html = base_html.replace("{TMP_ARTICLE_DATA}", json.dumps(article, ensure_ascii=False))
    
    return HTMLResponse(content=base_html, status_code=200)



if __name__ == "__main__":
    build_index()
    uvicorn.run(app, host="0.0.0.0", port=8000)
                