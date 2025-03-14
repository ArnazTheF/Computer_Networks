import subprocess
import uvicorn
import psycopg2

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from psycopg2 import extras


def connect_to_db():
    conn = psycopg2.connect(
        dbname='guitars',
        user='arnazthef',
        password='Artificial_Intelligence_Dude54',
        host='localhost',
        port='5432',
        client_encoding='UTF8'
    )
    return conn

app = FastAPI()
@app.get("/test")
def test():
    return "To sleep, perchance to dream."

@app.get("/parse")
def parser_start(url: str = Query(..., description="https://www.muztorg.ru/category/elektrogitary")):
    subprocess.run(
        ["python3", "parse_to_db.py", url], 
        capture_output=True, 
        text=True
    )
    return "Ay! There's the rub!"

@app.get("/data")
def get_data():
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)  
    try:
        cur.execute("SELECT * FROM guitars;")
        data = cur.fetchall()
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при извлечении данных: {e}")
    finally:
        cur.close()
        conn.close()

uvicorn.run(app, host="0.0.0.0", port=5000)