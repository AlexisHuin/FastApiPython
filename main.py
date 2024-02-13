from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import starlette.status as status
from faker import Faker
from fastapi_pagination.ext.sqlalchemy import paginate as paginate_sqlalchemy

app = FastAPI(debug=True)
fake = Faker()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)


Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    author= Column(String)
    description = Column(String)

Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    html_content = templates.TemplateResponse("index.html", {"request": request})
    return html_content

@app.post("/article", response_class=HTMLResponse)
async def read_article(request: Request, nom: str = Form(...), author: str = Form(...), description: str = Form(...)):
   
    db = SessionLocal()

   
    article = Article(nom=nom, author=author, description=description)
    db.add(article)
    db.commit()
    db.refresh(article)
    db.close()

  
    html_content = templates.TemplateResponse("article.html", {"request": request, "nom": nom, "author": author, "description": description})
    return html_content

@app.get("/liste", response_class=HTMLResponse)
async def read_liste(request: Request, db: SessionLocal = Depends(get_db)):
    list = db.query(Article).all()
    return templates.TemplateResponse("liste.html", {"request": request, "list": list})

@app.post("/delete/{article_id}", response_class=HTMLResponse)
async def delete_article(request: Request, article_id: int, db: SessionLocal = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        raise HTTPException(status_code=404, detail=f"Article avec l'ID {article_id} non trouvé.")
    db.delete(article)
    db.commit()
    return RedirectResponse(url="/liste", 
        status_code=status.HTTP_302_FOUND)

@app.get("/blog/{article_id}", response_class=HTMLResponse)
async def read_single_article(request: Request, article_id: int, db: SessionLocal = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if article is None:
    
        return f"Article avec l'ID {article_id} non trouvé."

    return templates.TemplateResponse("blog.html", {"request": request, "article": article})

@app.get("/generer_articles", response_class=HTMLResponse)
async def generer_articles(request: Request, db: SessionLocal = Depends(get_db)):

    for _ in range(100):
        nom = fake.word()
        author = fake.name()
        description = fake.text()

        article = Article(nom=nom, author=author, description=description)
        db.add(article)

    db.commit()

    return RedirectResponse(url="/liste", status_code=status.HTTP_302_FOUND)